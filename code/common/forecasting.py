"""严格无前视的季节朴素与扩展窗 HistGBR 日前预测。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor


SLOTS = 144
MIN_HISTORY_DAYS = 14


def _calendar_features(day: date, slot: int) -> list[float]:
    minute = (slot + 1) * 10
    day_fraction = minute / 1440.0
    year_fraction = day.timetuple().tm_yday / 365.25
    return [
        np.sin(2 * np.pi * day_fraction), np.cos(2 * np.pi * day_fraction),
        np.sin(4 * np.pi * day_fraction), np.cos(4 * np.pi * day_fraction),
        np.sin(2 * np.pi * year_fraction), np.cos(2 * np.pi * year_fraction),
        day.weekday() / 6.0,
    ]


def _calendar_matrix(day: date) -> np.ndarray:
    """一次生成全天144格日历特征，避免训练时逐格重复计算。"""
    minutes = (np.arange(SLOTS, dtype=float) + 1.0) * 10.0
    day_fraction = minutes / 1440.0
    year_fraction = day.timetuple().tm_yday / 365.25
    return np.column_stack([
        np.sin(2 * np.pi * day_fraction), np.cos(2 * np.pi * day_fraction),
        np.sin(4 * np.pi * day_fraction), np.cos(4 * np.pi * day_fraction),
        np.full(SLOTS, np.sin(2 * np.pi * year_fraction)),
        np.full(SLOTS, np.cos(2 * np.pi * year_fraction)),
        np.full(SLOTS, day.weekday() / 6.0),
    ])


def _day_feature_matrix(values: np.ndarray, days: list[date], index: int) -> np.ndarray:
    """用严格早于 ``index`` 的数据生成该日144格特征。"""
    if index < MIN_HISTORY_DAYS:
        raise ValueError("HistGBR特征至少需要14天历史")
    history = np.asarray(values[:index], dtype=float)
    return np.column_stack([
        _calendar_matrix(days[index]),
        history[index - 1], history[index - 7], history[index - 14],
        history[index - 7:index].mean(axis=0),
        history[index - 14:index].mean(axis=0),
        np.full(SLOTS, history[index - 1].mean()),
        np.full(SLOTS, history[index - 7].mean()),
    ])


def _row_features(series: list[np.ndarray], days: list[date], index: int, slot: int) -> list[float]:
    if index < MIN_HISTORY_DAYS:
        raise ValueError("HistGBR特征至少需要14天历史")
    history = np.vstack(series[:index])
    return _calendar_features(days[index], slot) + [
        series[index - 1][slot], series[index - 7][slot], series[index - 14][slot],
        float(history[-7:, slot].mean()), float(history[-14:, slot].mean()),
        float(series[index - 1].mean()), float(series[index - 7].mean()),
    ]


def seasonal_naive(values: np.ndarray, start_index: int, horizon_days: int = 2) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or values.shape[1] != SLOTS:
        raise ValueError("values必须为(days,144)")
    working = [row.copy() for row in values[:start_index]]
    output = []
    for _ in range(horizon_days):
        index = len(working)
        lag = 7 if index >= 7 else 1
        prediction = working[index - lag].copy()
        output.append(prediction)
        working.append(prediction)
    return np.vstack(output)


@dataclass
class ExpandingHistGBR:
    random_state: int = 20260910
    max_iter: int = 200
    learning_rate: float = 0.05
    max_depth: int = 6
    l2_regularization: float = 1.0
    retrain_days: int = 7
    _model: HistGradientBoostingRegressor | None = None
    _fit_cutoff: int | None = None
    _feature_cache: np.ndarray | None = None
    _target_cache: np.ndarray | None = None
    _cache_length: int | None = None

    def _prepare_training_cache(self, values: np.ndarray, days: list[date]) -> None:
        """预生成所有仅依赖过去观测的训练行；切片截止日仍保持无前视。"""
        if self._feature_cache is not None and self._cache_length == len(values):
            return
        features = [
            _day_feature_matrix(values, days, index)
            for index in range(MIN_HISTORY_DAYS, len(values))
        ]
        self._feature_cache = np.vstack(features)
        self._target_cache = values[MIN_HISTORY_DAYS:].reshape(-1)
        self._cache_length = len(values)

    def _fit(self, values: np.ndarray, days: list[date], cutoff: int) -> None:
        self._prepare_training_cache(values, days)
        row_count = (cutoff - MIN_HISTORY_DAYS) * SLOTS
        if row_count <= 0 or self._feature_cache is None or self._target_cache is None:
            raise ValueError("没有足够历史训练HistGBR")
        self._model = HistGradientBoostingRegressor(
            max_iter=self.max_iter, learning_rate=self.learning_rate, max_depth=self.max_depth,
            l2_regularization=self.l2_regularization, random_state=self.random_state,
        ).fit(self._feature_cache[:row_count], self._target_cache[:row_count])
        self._fit_cutoff = cutoff

    def predict(self, values: np.ndarray, dates: list[date], start_index: int,
                horizon_days: int = 2) -> np.ndarray:
        values = np.asarray(values, dtype=float)
        if start_index < MIN_HISTORY_DAYS + 1:
            return seasonal_naive(values, start_index, horizon_days)
        if self._model is None or self._fit_cutoff is None or start_index - self._fit_cutoff >= self.retrain_days:
            self._fit(values, dates, start_index)
        working = [row.copy() for row in values[:start_index]]
        working_days = list(dates[:start_index])
        output = []
        for step in range(horizon_days):
            index = len(working)
            next_day = dates[index] if index < len(dates) else working_days[-1] + timedelta(days=1)
            working_days.append(next_day)
            features = _day_feature_matrix(np.vstack(working), working_days, index)
            prediction = np.maximum(self._model.predict(features), 0.0)
            output.append(prediction)
            working.append(prediction)
        return np.vstack(output)


def causal_backtest(values: np.ndarray, dates: list[date], start_index: int,
                    end_index: int, use_hist_gbr: bool) -> tuple[np.ndarray, np.ndarray]:
    model = ExpandingHistGBR() if use_hist_gbr else None
    predictions, residuals = [], []
    for index in range(start_index, end_index):
        prediction = model.predict(values, dates, index, 1)[0] if model else seasonal_naive(values, index, 1)[0]
        predictions.append(prediction)
        residuals.append(values[index] - prediction)
    return np.vstack(predictions), np.vstack(residuals)


def metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    error = predicted - actual
    mae = float(np.mean(np.abs(error)))
    return {
        "mae": mae,
        "rmse": float(np.sqrt(np.mean(error ** 2))),
        "nmae": float(mae / max(np.mean(np.abs(actual)), 1e-12)),
    }


def choose_forecaster(values: np.ndarray, dates: list[date], start_index: int = 15,
                      end_index: int = 31) -> tuple[str, dict[str, dict[str, float]]]:
    actual = values[start_index:end_index]
    baseline, _ = causal_backtest(values, dates, start_index, end_index, False)
    main, _ = causal_backtest(values, dates, start_index, end_index, True)
    scores = {"seasonal": metrics(actual, baseline), "hist_gbr": metrics(actual, main)}
    choice = "hist_gbr" if scores["hist_gbr"]["nmae"] < scores["seasonal"]["nmae"] else "seasonal"
    return choice, scores


def build_forecast_cache(values: np.ndarray, dates: list[date], mode: str,
                         fallback: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """逐日生成未来两日预测和当日残差；缓存仍严格只用每个截止日前历史。"""
    values = np.asarray(values, dtype=float)
    fallback = np.asarray(fallback, dtype=float).reshape(SLOTS)
    points = np.empty((len(values), 2, SLOTS), dtype=float)
    residuals = np.empty_like(values)
    model = ExpandingHistGBR() if mode == "hist_gbr" else None
    for index in range(len(values)):
        if index == 0:
            prediction = np.vstack([fallback, fallback])
        elif model is not None:
            prediction = model.predict(values, dates, index, 2)
        else:
            prediction = seasonal_naive(values, index, 2)
        points[index] = prediction
        residuals[index] = values[index] - prediction[0]
    return points, residuals
