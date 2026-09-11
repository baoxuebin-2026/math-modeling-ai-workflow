"""用2025年1月严格滚动回测选择风险权重、场景数和48小时末端带宽。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.annual_context import AnnualContext, build_annual_context
from code.q2.solve_q2 import run_day


RISK_WEIGHTS = (0.0, 0.1, 0.25, 0.5)
TERMINAL_WIDTHS = (600.0, 1200.0, 2400.0)
SCENARIO_COUNTS = (20, 40, 60)
EVALUATION_START = date(2025, 1, 8)
EVALUATION_END = date(2025, 1, 31)


def evaluate(context: AnnualContext, scenario_count: int, risk_weight: float,
             terminal_half_width: float) -> dict[str, float | int]:
    soc = 6000.0
    daily_costs: list[float] = []
    emergencies: list[float] = []
    terminal_hits = 0
    for index, day in enumerate(context.dates[:31]):
        result = run_day(
            day.isoformat(), scenario_count, risk_weight, terminal_half_width, soc,
            context, lexicographic_plan=False,
        )
        soc = float(result["actual"]["soc_kwh"][-1])
        if day < EVALUATION_START:
            continue
        daily_costs.append(float(result["actual"]["total_cost_cny"]))
        emergencies.append(float(np.sum(result["actual"]["emergency_kwh"])))
        terminal = float(result["plan"]["expected_terminal_soc_kwh"])
        lo, hi = 6000 - terminal_half_width, 6000 + terminal_half_width
        terminal_hits += int(min(abs(terminal - lo), abs(terminal - hi)) <= 1e-4)
    values = np.asarray(daily_costs)
    return {
        "scenario_count": scenario_count,
        "risk_weight": risk_weight,
        "terminal_half_width_kwh": terminal_half_width,
        "evaluation_days": len(values),
        "mean_daily_cost_cny": float(values.mean()),
        "p95_daily_cost_cny": float(np.quantile(values, 0.95)),
        "total_emergency_kwh": float(sum(emergencies)),
        "terminal_boundary_days": terminal_hits,
        "final_january_soc_kwh": soc,
    }


def select_risk_and_width(records: list[dict[str, float | int]]) -> dict[str, float | int]:
    baselines = {
        float(row["terminal_half_width_kwh"]): row
        for row in records if float(row["risk_weight"]) == 0.0
    }
    eligible = [
        row for row in records
        if float(row["total_emergency_kwh"])
        <= float(baselines[float(row["terminal_half_width_kwh"])]["total_emergency_kwh"]) + 1e-6
        and int(row["terminal_boundary_days"]) <= 12
    ]
    candidates = eligible or records
    return min(
        candidates,
        key=lambda row: (
            float(row["mean_daily_cost_cny"]),
            float(row["p95_daily_cost_cny"]),
            int(row["terminal_boundary_days"]),
        ),
    )


def select_scenario_count(records: list[dict[str, float | int]]) -> dict[str, float | int]:
    reference = next(row for row in records if int(row["scenario_count"]) == 60)
    reference_cost = float(reference["mean_daily_cost_cny"])
    reference_emergency = float(reference["total_emergency_kwh"])
    for row in sorted(records, key=lambda item: int(item["scenario_count"])):
        cost_gap = abs(float(row["mean_daily_cost_cny"]) - reference_cost) / max(reference_cost, 1e-9)
        emergency_gap = abs(float(row["total_emergency_kwh"]) - reference_emergency) / max(reference_emergency, 1.0)
        if cost_gap <= 0.02 and emergency_gap <= 0.10:
            return row
    return reference


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/results/parameter_calibration.json")
    args = parser.parse_args()
    context = build_annual_context(include_price_forecast=False)
    grid: list[dict[str, float | int]] = []
    for width in TERMINAL_WIDTHS:
        for risk in RISK_WEIGHTS:
            row = evaluate(context, 20, risk, width)
            grid.append(row)
            print(f"calibration N=20 lambda={risk} b={width}: {row['mean_daily_cost_cny']:.2f}", flush=True)
    selected_grid = select_risk_and_width(grid)
    convergence: list[dict[str, float | int]] = []
    for count in SCENARIO_COUNTS:
        row = evaluate(
            context, count, float(selected_grid["risk_weight"]),
            float(selected_grid["terminal_half_width_kwh"]),
        )
        convergence.append(row)
        print(f"convergence N={count}: {row['mean_daily_cost_cny']:.2f}", flush=True)
    selected = select_scenario_count(convergence)
    payload = {
        "status": "checked",
        "evaluation_period": [EVALUATION_START.isoformat(), EVALUATION_END.isoformat()],
        "selection_rule": (
            "先在N=20下选平均费用最低、紧急购电不高于同带宽lambda=0且末端贴边不超过半数的组合；"
            "再选与N=60平均费用差不超过2%、紧急购电差不超过10%的最小场景数。"
        ),
        "risk_width_grid": grid,
        "scenario_convergence": convergence,
        "selected": {
            "scenario_count": int(selected["scenario_count"]),
            "risk_weight": float(selected_grid["risk_weight"]),
            "terminal_half_width_kwh": float(selected_grid["terminal_half_width_kwh"]),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["selected"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
