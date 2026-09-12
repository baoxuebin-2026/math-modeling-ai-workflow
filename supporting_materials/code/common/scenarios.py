"""用历史联合整日残差块生成严格因果场景。"""

from __future__ import annotations

import numpy as np


def bootstrap_joint_blocks(
    point_forecasts: dict[str, np.ndarray],
    residual_history: dict[str, np.ndarray],
    scenario_count: int,
    seed: int,
) -> dict[str, np.ndarray]:
    if scenario_count < 1:
        raise ValueError("场景数必须为正")
    names = list(point_forecasts)
    if set(names) != set(residual_history):
        raise ValueError("中心预测与残差历史字段不一致")
    horizon_days = next(iter(point_forecasts.values())).shape[0]
    history_days = next(iter(residual_history.values())).shape[0]
    for name in names:
        if point_forecasts[name].shape[1] != 144 or residual_history[name].shape[1] != 144:
            raise ValueError(f"{name}必须按(days,144)组织")
        if point_forecasts[name].shape[0] != horizon_days or residual_history[name].shape[0] != history_days:
            raise ValueError("各字段日期维度不一致")
    if history_days < horizon_days:
        raise ValueError("历史残差不足以抽取连续块")
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, history_days - horizon_days + 1, size=scenario_count)
    output: dict[str, np.ndarray] = {}
    for name in names:
        point = np.asarray(point_forecasts[name], dtype=float)
        residual = np.asarray(residual_history[name], dtype=float)
        samples = np.stack([point + residual[start:start + horizon_days] for start in starts])
        output[name] = np.maximum(samples.reshape(scenario_count, -1), 0.0)
    output["_sample_starts"] = starts
    return output


def bootstrap_aligned_rows(
    point_forecasts: dict[str, np.ndarray],
    residual_history: dict[str, np.ndarray],
    scenario_count: int,
    seed: int,
) -> dict[str, np.ndarray]:
    """从同一历史日期行抽样，适用于发布时刻到当日末的变长时域。"""
    names = list(point_forecasts)
    if set(names) != set(residual_history) or scenario_count < 1:
        raise ValueError("字段集合或场景数非法")
    horizon = next(iter(point_forecasts.values())).size
    history_rows = next(iter(residual_history.values())).shape[0]
    if history_rows < 1:
        raise ValueError("没有可用历史残差")
    for name in names:
        if np.asarray(point_forecasts[name]).size != horizon:
            raise ValueError("中心预测长度不一致")
        if np.asarray(residual_history[name]).shape != (history_rows, horizon):
            raise ValueError("历史残差必须严格按日期对齐")
    rng = np.random.default_rng(seed)
    selected = rng.integers(0, history_rows, size=scenario_count)
    result = {
        name: np.maximum(np.asarray(point_forecasts[name])[None, :] +
                         np.asarray(residual_history[name])[selected], 0.0)
        for name in names
    }
    result["selected_rows"] = selected
    return result
