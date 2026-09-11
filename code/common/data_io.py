"""读取 CP-02 锁定的标准化数据；所有优化量统一使用 kWh。"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
METADATA = ROOT / "data" / "metadata"


def require_preprocessed() -> None:
    required = [
        PROCESSED / "q1_timeseries.csv",
        PROCESSED / "annual_actual.csv",
        PROCESSED / "annual_price.csv",
        PROCESSED / "pv_forecasts_hourly.csv",
        METADATA / "data_profile.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"缺少预处理文件：{missing}；先运行 code/common/prepare_data.py"
        )
    profile = json.loads((METADATA / "data_profile.json").read_text(encoding="utf-8"))
    if profile.get("status") != "checked":
        raise ValueError("data_profile.json 未通过检查")


def load_q1() -> dict[str, np.ndarray]:
    require_preprocessed()
    frame = pd.read_csv(PROCESSED / "q1_timeseries.csv", encoding="utf-8-sig")
    if len(frame) != 144 or frame["slot"].tolist() != list(range(1, 145)):
        raise ValueError("Q1标准表必须恰含连续144格")
    return {
        "price": frame["price_cny_per_kwh"].to_numpy(float),
        "load": frame["load_kwh"].to_numpy(float),
        "pv": frame["pv_forecast_kwh"].to_numpy(float),
        "frame": frame,
    }


def load_annual() -> dict[str, object]:
    require_preprocessed()
    actual = pd.read_csv(
        PROCESSED / "annual_actual.csv", encoding="utf-8-sig", parse_dates=["interval_start", "interval_end"]
    )
    prices = pd.read_csv(
        PROCESSED / "annual_price.csv", encoding="utf-8-sig", parse_dates=["interval_end"]
    )
    if len(actual) != 365 * 144 or len(prices) != 365 * 144:
        raise ValueError("年度标准表应各有52560行")
    if not np.array_equal(actual[["date", "slot"]].to_numpy(), prices[["date", "slot"]].to_numpy()):
        raise ValueError("附件2与附件4在日期/时段上未对齐")
    dates = pd.Index(actual["date"].drop_duplicates(), name="date")
    return {
        "dates": dates,
        "load": actual["load_kwh"].to_numpy(float).reshape(365, 144),
        "pv": actual["pv_actual_kwh"].to_numpy(float).reshape(365, 144),
        "price": prices["price_cny_per_kwh"].to_numpy(float).reshape(365, 144),
        "actual_frame": actual,
        "price_frame": prices,
    }


def load_hourly_pv_forecasts() -> pd.DataFrame:
    require_preprocessed()
    frame = pd.read_csv(
        PROCESSED / "pv_forecasts_hourly.csv",
        encoding="utf-8-sig",
        parse_dates=["issue_timestamp", "target_timestamp"],
    )
    if len(frame) != 365 * 4 * 24:
        raise ValueError("光伏小时预报应有35040行")
    return frame
