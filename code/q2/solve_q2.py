"""问题2：严格无前视源荷预测、联合残差场景和计划购电。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.annual_context import AnnualContext, build_annual_context
from code.common.data_io import load_annual, load_q1
from code.common.dispatch_lp import SOC_MAX, SOC_MIN, solve_deterministic, solve_scenario_plan
from code.common.forecasting import ExpandingHistGBR, causal_backtest, choose_forecaster, seasonal_naive
from code.common.scenarios import bootstrap_joint_blocks


SEED = 20260910
TRAIN_START = 15


def forecast_and_residuals(values: np.ndarray, dates: list[date], day_index: int,
                           mode: str) -> tuple[np.ndarray, np.ndarray]:
    """单日烟雾测试兼容入口；全年运行使用预计算缓存。"""
    use_hist = mode == "hist_gbr"
    _, residuals = causal_backtest(values, dates, TRAIN_START, day_index, use_hist)
    point = ExpandingHistGBR().predict(values, dates, day_index, 2) if use_hist \
        else seasonal_naive(values, day_index, 2)
    return point, residuals
def run_day(day_text: str, scenario_count: int = 3, risk_weight: float = 0.25,
            terminal_half_width: float = 1200.0, initial_soc: float = 6000.0,
            context: AnnualContext | None = None,
            lexicographic_plan: bool = True) -> dict[str, object]:
    if context is None:
        annual, q1 = load_annual(), load_q1()
        dates = [date.fromisoformat(value) for value in annual["dates"].tolist()]
    else:
        dates = context.dates
    target = date.fromisoformat(day_text)
    if target not in dates:
        raise ValueError("日期必须在2025-01-01至2025-12-31")
    index = dates.index(target)
    if context is None:
        modes, scores, point, history = {}, {}, {}, {}
        for name in ("load", "pv"):
            modes[name], scores[name] = choose_forecaster(annual[name], dates)
            point[name], history[name] = forecast_and_residuals(annual[name], dates, index, modes[name])
        fixed_price, actual_load, actual_pv = q1["price"], annual["load"][index], annual["pv"][index]
    else:
        modes = {name: context.forecast_modes[name] for name in ("load", "pv")}
        scores = {name: context.forecast_scores[name] for name in ("load", "pv")}
        point = {name: context.points[name][index] for name in ("load", "pv")}
        history = {name: context.residuals[name][:index] for name in point}
        fixed_price, actual_load, actual_pv = context.fixed_price, context.load[index], context.pv[index]
    if index >= 2:
        sampled = bootstrap_joint_blocks(
            point, history,
            scenario_count, SEED + index,
        )
        active_scenarios, active_risk = scenario_count, risk_weight
    else:
        sampled = {name: values.reshape(1, -1) for name, values in point.items()}
        active_scenarios, active_risk = 1, 0.0
    price = np.tile(fixed_price, 2)
    plan = solve_scenario_plan(
        np.tile(price, (active_scenarios, 1)), sampled["load"], sampled["pv"], initial_soc,
        (6000 - terminal_half_width, 6000 + terminal_half_width),
        risk_weight=active_risk, lexicographic=lexicographic_plan,
    )
    actual = solve_deterministic(
        fixed_price, actual_load, actual_pv, initial_soc,
        (SOC_MIN, SOC_MAX), fixed_grid=plan.plan_grid[:144], allow_emergency=True,
    )
    plan_cost = float(fixed_price @ plan.plan_grid[:144])
    emergency_cost = float(5 * fixed_price @ actual.emergency)
    return {
        "date": day_text,
        "information_cutoff": f"{day_text} 00:00:00",
        "forecast_selection": modes,
        "forecast_metrics_january": scores,
        "parameters": {"scenarios": active_scenarios, "risk_weight": active_risk,
                       "cvar_alpha": 0.9, "terminal_half_width_kwh": terminal_half_width,
                       "seed": SEED + index},
        "plan": {
            "risk_objective_48h": plan.risk_objective,
            "grid_kwh": plan.plan_grid[:144].tolist(),
            "expected_soc_kwh": plan.mean_soc[:145].tolist(),
            "expected_terminal_soc_kwh": float(plan.mean_soc[-1]),
            "max_balance_residual_kwh": plan.max_balance_residual,
            "max_state_residual_kwh": plan.max_state_residual,
        },
        "actual": {
            "grid_kwh": actual.grid.tolist(), "emergency_kwh": actual.emergency.tolist(),
            "charge_kwh": actual.charge.tolist(), "discharge_kwh": actual.discharge.tolist(),
            "pv_spill_kwh": actual.pv_spill.tolist(), "unused_grid_kwh": actual.grid_spill.tolist(),
            "soc_kwh": actual.soc.tolist(), "plan_cost_cny": plan_cost,
            "emergency_cost_cny": emergency_cost, "total_cost_cny": plan_cost + emergency_cost,
            "max_balance_residual_kwh": actual.max_balance_residual,
            "max_state_residual_kwh": actual.max_state_residual,
        },
    }


def run_full(scenario_count: int, risk_weight: float, terminal_half_width: float,
             output_json: Path, output_csv: Path) -> dict[str, object]:
    context = build_annual_context(include_price_forecast=False)
    soc = 6000.0
    rows, selected_days, daily = [], {}, []
    specified = {"2025-03-20", "2025-06-21", "2025-09-23", "2025-12-21"}
    for index, day in enumerate(context.dates):
        result = run_day(
            day.isoformat(), scenario_count, risk_weight, terminal_half_width, soc, context,
            lexicographic_plan=False,
        )
        soc = float(result["actual"]["soc_kwh"][-1])
        if day < date(2025, 2, 1):
            continue
        if day.isoformat() in specified:
            selected_days[day.isoformat()] = result
        daily.append({
            "date": day.isoformat(),
            "plan_cost_cny": result["actual"]["plan_cost_cny"],
            "emergency_cost_cny": result["actual"]["emergency_cost_cny"],
            "total_cost_cny": result["actual"]["total_cost_cny"],
            "emergency_kwh": float(np.sum(result["actual"]["emergency_kwh"])),
            "emergency_slots": int(np.count_nonzero(np.asarray(result["actual"]["emergency_kwh"]) > 1e-6)),
            "soc_end_kwh": soc,
        })
        for slot in range(144):
            rows.append([
                day.isoformat(), slot + 1, result["actual"]["grid_kwh"][slot],
                result["actual"]["charge_kwh"][slot], result["actual"]["discharge_kwh"][slot],
                result["actual"]["emergency_kwh"][slot], result["actual"]["pv_spill_kwh"][slot],
                result["actual"]["unused_grid_kwh"][slot], result["actual"]["soc_kwh"][slot + 1],
            ])
        if (index + 1) % 25 == 0 or index + 1 == len(context.dates):
            print(f"Q2 progress: {index + 1}/{len(context.dates)}", flush=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["date", "slot", "plan_grid_kwh", "charge_kwh", "discharge_kwh",
                         "emergency_kwh", "pv_spill_kwh", "unused_grid_kwh", "soc_end_kwh"])
        writer.writerows(rows)
    total_plan = float(sum(item["plan_cost_cny"] for item in daily))
    total_emergency_cost = float(sum(item["emergency_cost_cny"] for item in daily))
    total_emergency = float(sum(item["emergency_kwh"] for item in daily))
    day_costs = np.asarray([item["total_cost_cny"] for item in daily])
    summary = {
        "question": "问题二", "status": "computed", "model_version": "C-M1-v1",
        "forecast_selection": context.forecast_modes,
        "parameters": {"scenario_count": scenario_count, "risk_weight": risk_weight,
                       "terminal_half_width_kwh": terminal_half_width},
        "full_detail_csv": str(output_csv.relative_to(ROOT)), "specified_days": selected_days,
        "days": len(daily), "final_soc_kwh": soc,
        "totals": {
            "plan_cost_cny": total_plan, "emergency_cost_cny": total_emergency_cost,
            "total_cost_cny": total_plan + total_emergency_cost,
            "emergency_kwh": total_emergency,
            "emergency_slots": int(sum(item["emergency_slots"] for item in daily)),
            "daily_cost_p50_cny": float(np.quantile(day_costs, 0.5)),
            "daily_cost_p90_cny": float(np.quantile(day_costs, 0.9)),
            "daily_cost_p95_cny": float(np.quantile(day_costs, 0.95)),
        },
        "daily_summary": daily,
        "diagnostics": {
            "scenario_lexicographic_skipped": True,
            "actual_dispatch_lexicographic": True,
            "note": "场景LP只提取共同计划，实际执行LP仍进行词典序去退化。",
        },
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default="2025-03-20")
    parser.add_argument("--scenarios", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--risk-weight", type=float, default=0.25)
    parser.add_argument("--terminal-half-width", type=float, default=1200.0)
    parser.add_argument("--detail-csv", type=Path, default=ROOT / "data/processed/q2_full_detail.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.full:
        result = run_full(
            args.scenarios, args.risk_weight, args.terminal_half_width,
            args.output or ROOT / "docs/results/q2_results.json", args.detail_csv,
        )
        print(json.dumps({"status": result["status"], "days": result["days"],
                          "final_soc_kwh": result["final_soc_kwh"]}, ensure_ascii=False, indent=2))
        return
    result = run_day(args.date, args.scenarios, args.risk_weight, args.terminal_half_width)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "date": result["date"], "forecast_selection": result["forecast_selection"],
        "plan_residual": result["plan"]["max_balance_residual_kwh"],
        "actual_residual": result["actual"]["max_balance_residual_kwh"],
        "plan_cost_cny": result["actual"]["plan_cost_cny"],
        "emergency_cost_cny": result["actual"]["emergency_cost_cny"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
