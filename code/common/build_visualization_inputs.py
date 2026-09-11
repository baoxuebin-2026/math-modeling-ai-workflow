"""Build strictly causal forecast snapshots used only by visualization scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.annual_context import build_annual_context


DATES = ("2025-03-20", "2025-06-21", "2025-09-23", "2025-12-21")


def main() -> None:
    context = build_annual_context(include_price_forecast=True)
    index_by_date = {day.isoformat(): i for i, day in enumerate(context.dates)}
    snapshots = {}
    for day in DATES:
        index = index_by_date[day]
        load_point = context.points["load"][index].reshape(-1, 144)[0]
        pv_point = context.points["pv"][index].reshape(-1, 144)[0]
        price_point = context.points["price"][index].reshape(-1, 144)[0]
        snapshots[day] = {
            "information_cutoff": f"{day} 00:00:00",
            "forecast_modes": context.forecast_modes,
            "load_forecast_kwh": load_point.tolist(),
            "pv_forecast_kwh": pv_point.tolist(),
            "price_forecast_cny_per_kwh": price_point.tolist(),
            "load_actual_kwh": context.load[index].tolist(),
            "pv_actual_kwh": context.pv[index].tolist(),
            "price_actual_cny_per_kwh": context.price[index].tolist(),
        }
    output = ROOT / "docs/results/forecast_snapshots.json"
    output.write_text(
        json.dumps({"status": "checked", "dates": snapshots}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
