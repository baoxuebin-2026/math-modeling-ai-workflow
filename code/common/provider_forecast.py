"""附件3多发布时间光伏预报的因果对齐、插值与历史残差。"""

from __future__ import annotations

from datetime import date, datetime, time

import numpy as np
import pandas as pd

from code.common.prepare_data import interpolate_hourly_forecast


def _actual_at_issue(pv_actual: np.ndarray, day_index: int, issue_hour: int) -> float:
    if issue_hour == 0:
        return 0.0 if day_index == 0 else float(pv_actual[day_index - 1, -1] * 6)
    return float(pv_actual[day_index, issue_hour * 6 - 1] * 6)


def provider_curve(hourly: pd.DataFrame, pv_actual: np.ndarray, day: date,
                   day_index: int, issue_hour: int) -> np.ndarray:
    """返回发布时间后24小时的144格预测电量（kWh）。"""
    issue_ts = datetime.combine(day, time(hour=issue_hour))
    group = hourly.loc[hourly["issue_timestamp"] == pd.Timestamp(issue_ts)].sort_values("horizon_hour")
    if len(group) != 24:
        raise ValueError(f"找不到完整的附件3发布记录：{issue_ts}")
    anchor_kw = _actual_at_issue(pv_actual, day_index, issue_hour)
    forecast_kw = group["pv_forecast_kw"].to_numpy(float).tolist()
    return np.asarray(interpolate_hourly_forecast(anchor_kw, forecast_kw), dtype=float) / 6.0


def provider_residual_history(hourly: pd.DataFrame, pv_actual: np.ndarray, dates: list[date],
                              current_index: int, issue_hour: int, start_index: int) -> np.ndarray:
    """返回历史同发布时间至当日末的光伏电量残差，行严格早于当前日。"""
    start_slot = issue_hour * 6
    rows = []
    for index in range(start_index, current_index):
        forecast = provider_curve(hourly, pv_actual, dates[index], index, issue_hour)
        remaining = 144 - start_slot
        rows.append(pv_actual[index, start_slot:] - forecast[:remaining])
    if not rows:
        raise ValueError("附件3没有足够的历史发布残差")
    return np.vstack(rows)
