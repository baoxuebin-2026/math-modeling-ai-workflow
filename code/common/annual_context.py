"""一次构建全年严格因果预测与附件3预报缓存，供Q2–Q4复用。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np

from code.common.data_io import load_annual, load_hourly_pv_forecasts, load_q1
from code.common.forecasting import build_forecast_cache, choose_forecaster
from code.common.provider_forecast import provider_curve


ISSUE_HOURS = (0, 6, 12, 18)


@dataclass(frozen=True)
class AnnualContext:
    dates: list[date]
    load: np.ndarray
    pv: np.ndarray
    price: np.ndarray
    fixed_price: np.ndarray
    forecast_modes: dict[str, str]
    forecast_scores: dict[str, dict[str, dict[str, float]]]
    points: dict[str, np.ndarray]
    residuals: dict[str, np.ndarray]
    provider_curves: dict[int, np.ndarray]
    provider_residuals: dict[int, np.ndarray]


def build_annual_context(include_price_forecast: bool = True) -> AnnualContext:
    annual, q1 = load_annual(), load_q1()
    dates = [date.fromisoformat(value) for value in annual["dates"].tolist()]
    modes: dict[str, str] = {}
    scores: dict[str, dict[str, dict[str, float]]] = {}
    points: dict[str, np.ndarray] = {}
    residuals: dict[str, np.ndarray] = {}
    names = ["load", "pv"] + (["price"] if include_price_forecast else [])
    fallback = {"load": q1["load"], "pv": q1["pv"], "price": q1["price"]}
    for name in names:
        modes[name], scores[name] = choose_forecaster(annual[name], dates)
        points[name], residuals[name] = build_forecast_cache(
            annual[name], dates, modes[name], fallback[name]
        )

    hourly = load_hourly_pv_forecasts()
    curves: dict[int, np.ndarray] = {}
    provider_residuals: dict[int, np.ndarray] = {}
    for issue_hour in ISSUE_HOURS:
        start = issue_hour * 6
        curve_rows = np.vstack([
            provider_curve(hourly, annual["pv"], day, index, issue_hour)
            for index, day in enumerate(dates)
        ])
        curves[issue_hour] = curve_rows
        provider_residuals[issue_hour] = annual["pv"][:, start:] - curve_rows[:, :144 - start]
    return AnnualContext(
        dates=dates, load=annual["load"], pv=annual["pv"], price=annual["price"],
        fixed_price=q1["price"], forecast_modes=modes, forecast_scores=scores,
        points=points, residuals=residuals, provider_curves=curves,
        provider_residuals=provider_residuals,
    )
