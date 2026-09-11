"""问题3：利用0/6/12/18时光伏预报进行分段滚动调整。"""

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

from code.common.data_io import load_annual, load_hourly_pv_forecasts, load_q1
from code.common.annual_context import AnnualContext, build_annual_context
from code.common.dispatch_lp import SOC_MAX, SOC_MIN, solve_adjustment_plan, solve_deterministic, solve_scenario_plan
from code.common.provider_forecast import provider_curve, provider_residual_history
from code.common.scenarios import bootstrap_aligned_rows, bootstrap_joint_blocks
from code.q2.solve_q2 import choose_forecaster, forecast_and_residuals, run_day as run_q2_day


SEED = 20260910
START_HISTORY = 15


def run_day(day_text: str, scenario_count: int = 3, risk_weight: float = 0.25,
            terminal_half_width: float = 1200.0, initial_soc: float = 6000.0,
            context: AnnualContext | None = None,
            lexicographic_plan: bool = True) -> dict[str, object]:
    if context is None:
        annual, q1, hourly = load_annual(), load_q1(), load_hourly_pv_forecasts()
        dates = [date.fromisoformat(value) for value in annual["dates"].tolist()]
    else:
        dates = context.dates
    target = date.fromisoformat(day_text)
    if target not in dates or target < date(2025, 2, 1):
        raise ValueError("测试日期必须位于正式回测区间")
    index = dates.index(target)
    if context is None:
        load_mode, load_scores = choose_forecaster(annual["load"], dates)
        pv_mode, pv_scores = choose_forecaster(annual["pv"], dates)
        load_point, load_residuals = forecast_and_residuals(annual["load"], dates, index, load_mode)
        pv_fallback, _ = forecast_and_residuals(annual["pv"], dates, index, pv_mode)
        pv_issue0 = provider_curve(hourly, annual["pv"], target, index, 0)
        provider0_residuals = provider_residual_history(
            hourly, annual["pv"], dates, index, 0, START_HISTORY
        )
        fixed_price, actual_load, actual_pv = q1["price"], annual["load"][index], annual["pv"][index]
    else:
        load_mode, pv_mode = context.forecast_modes["load"], context.forecast_modes["pv"]
        load_scores, pv_scores = context.forecast_scores["load"], context.forecast_scores["pv"]
        load_point, pv_fallback = context.points["load"][index], context.points["pv"][index]
        load_residuals = context.residuals["load"][:index]
        pv_issue0 = context.provider_curves[0][index]
        provider0_residuals = context.provider_residuals[0][START_HISTORY:index]
        fixed_price = context.fixed_price
        actual_load, actual_pv = context.load[index], context.pv[index]
    pv_point = np.vstack([pv_issue0, pv_fallback[1]])
    history_count = min(len(load_residuals), len(provider0_residuals))
    sampled = bootstrap_joint_blocks(
        {"load": load_point, "pv": pv_point},
        {"load": load_residuals[-history_count:], "pv": provider0_residuals[-history_count:]},
        scenario_count, SEED + index,
    )
    price48 = np.tile(fixed_price, 2)
    initial_plan = solve_scenario_plan(
        np.tile(price48, (scenario_count, 1)), sampled["load"], sampled["pv"], initial_soc,
        (6000 - terminal_half_width, 6000 + terminal_half_width), risk_weight=risk_weight,
        lexicographic=lexicographic_plan,
    )
    original = initial_plan.plan_grid[:144].copy()
    active = original.copy()
    issue_hours = [0, 6, 12, 18]
    soc = initial_soc
    actual_parts: dict[str, list[np.ndarray]] = {
        name: [] for name in ("grid", "emergency", "charge", "discharge", "pv_spill", "grid_spill", "soc")
    }
    adjustment_records: list[dict[str, object]] = []

    for segment_index, issue_hour in enumerate(issue_hours):
        start = issue_hour * 6
        end = 144 if segment_index == len(issue_hours) - 1 else issue_hours[segment_index + 1] * 6
        if issue_hour > 0:
            remaining = 144 - start
            if context is None:
                pv_point_remaining = provider_curve(hourly, annual["pv"], target, index, issue_hour)[:remaining]
                pv_history = provider_residual_history(
                    hourly, annual["pv"], dates, index, issue_hour, START_HISTORY
                )
            else:
                pv_point_remaining = context.provider_curves[issue_hour][index][:remaining]
                pv_history = context.provider_residuals[issue_hour][START_HISTORY:index]
            aligned = min(len(load_residuals), len(pv_history))
            sampled_update = bootstrap_aligned_rows(
                {"load": load_point[0, start:], "pv": pv_point_remaining},
                {"load": load_residuals[-aligned:, start:], "pv": pv_history[-aligned:]},
                scenario_count, SEED + index * 10 + issue_hour,
            )
            update = solve_adjustment_plan(
                original[start:], np.tile(fixed_price[start:], (scenario_count, 1)),
                sampled_update["load"], sampled_update["pv"], soc,
                (6000 - terminal_half_width, 6000 + terminal_half_width), risk_weight=risk_weight,
            )
            active[start:] = update.adjusted_grid
            adjustment_records.append({
                "issue_hour": issue_hour, "start_slot": start + 1,
                "adjusted_grid_kwh": update.adjusted_grid.tolist(),
                "upward_kwh": update.upward.tolist(), "downward_kwh": update.downward.tolist(),
                "risk_objective": update.risk_objective,
                "max_balance_residual_kwh": update.max_balance_residual,
                "max_state_residual_kwh": update.max_state_residual,
            })
        actual = solve_deterministic(
            fixed_price[start:end], actual_load[start:end], actual_pv[start:end],
            soc, (SOC_MIN, SOC_MAX), fixed_grid=active[start:end], allow_emergency=True,
        )
        for name in ("grid", "emergency", "charge", "discharge", "pv_spill", "grid_spill"):
            actual_parts[name].append(getattr(actual, name))
        actual_parts["soc"].append(actual.soc if segment_index == 0 else actual.soc[1:])
        soc = float(actual.soc[-1])

    merged = {name: np.concatenate(parts) for name, parts in actual_parts.items()}
    upward = np.maximum(active - original, 0)
    downward = np.maximum(original - active, 0)
    plan_cost = float(fixed_price @ original)
    up_cost = float(1.5 * fixed_price @ upward)
    down_cost = float(0.5 * fixed_price @ downward)
    emergency_cost = float(5 * fixed_price @ merged["emergency"])
    return {
        "date": day_text, "information_cutoffs": [f"{day_text} {h:02d}:00:00" for h in issue_hours],
        "forecast_selection": {"load": load_mode, "pv_fallback": pv_mode},
        "forecast_metrics_january": {"load": load_scores, "pv_fallback": pv_scores},
        "parameters": {"scenarios": scenario_count, "risk_weight": risk_weight,
                       "terminal_half_width_kwh": terminal_half_width},
        "original_plan_grid_kwh": original.tolist(), "final_active_grid_kwh": active.tolist(),
        "adjustments": adjustment_records,
        "actual": {name: values.tolist() for name, values in merged.items()},
        "costs": {"plan_cny": plan_cost, "upward_cny": up_cost, "downward_cny": down_cost,
                  "emergency_cny": emergency_cost,
                  "total_cny": plan_cost + up_cost + down_cost + emergency_cost},
        "diagnostics": {
            "soc_start_kwh": initial_soc, "soc_end_kwh": soc,
            "cross_segment_soc_continuity": True,
            "simultaneous_charge_discharge_slots": int(np.sum((merged["charge"] > 1e-6) & (merged["discharge"] > 1e-6))),
        },
    }


def run_full(scenario_count: int, risk_weight: float, terminal_half_width: float,
             output_json: Path, detail_csv: Path, adjustment_csv: Path) -> dict[str, object]:
    """1月热启动、2月起输出Q3逐日策略与全部调整记录。"""
    context = build_annual_context(include_price_forecast=False)
    soc = 6000.0
    rows: list[list[object]] = []
    adjustment_rows: list[list[object]] = []
    daily: list[dict[str, object]] = []
    selected_days: dict[str, object] = {}
    specified = {"2025-03-20", "2025-06-21", "2025-09-23", "2025-12-21"}
    for index, day in enumerate(context.dates):
        if day < date(2025, 2, 1):
            warm = run_q2_day(
                day.isoformat(), scenario_count, risk_weight, terminal_half_width, soc, context,
                lexicographic_plan=False,
            )
            soc = float(warm["actual"]["soc_kwh"][-1])
            continue
        result = run_day(
            day.isoformat(), scenario_count, risk_weight, terminal_half_width, soc, context,
            lexicographic_plan=False,
        )
        soc = float(result["actual"]["soc"][-1])
        if day.isoformat() in specified:
            selected_days[day.isoformat()] = result
        emergency = np.asarray(result["actual"]["emergency"], dtype=float)
        daily.append({
            "date": day.isoformat(), **result["costs"],
            "emergency_kwh": float(emergency.sum()),
            "emergency_slots": int(np.count_nonzero(emergency > 1e-6)),
            "adjustment_count": len(result["adjustments"]),
            "soc_end_kwh": soc,
        })
        for slot in range(144):
            rows.append([
                day.isoformat(), slot + 1, result["original_plan_grid_kwh"][slot],
                result["final_active_grid_kwh"][slot], result["actual"]["charge"][slot],
                result["actual"]["discharge"][slot], result["actual"]["emergency"][slot],
                result["actual"]["pv_spill"][slot], result["actual"]["grid_spill"][slot],
                result["actual"]["soc"][slot + 1],
            ])
        for record in result["adjustments"]:
            start = int(record["start_slot"])
            for offset, adjusted in enumerate(record["adjusted_grid_kwh"]):
                adjustment_rows.append([
                    day.isoformat(), record["issue_hour"], start + offset, adjusted,
                    record["upward_kwh"][offset], record["downward_kwh"][offset],
                ])
        if (index + 1) % 20 == 0 or index + 1 == len(context.dates):
            print(f"Q3 progress: {index + 1}/{len(context.dates)}", flush=True)

    detail_csv.parent.mkdir(parents=True, exist_ok=True)
    with detail_csv.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "date", "slot", "original_plan_kwh", "final_adjusted_kwh", "charge_kwh",
            "discharge_kwh", "emergency_kwh", "pv_spill_kwh", "unused_grid_kwh", "soc_end_kwh",
        ])
        writer.writerows(rows)
    with adjustment_csv.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["date", "issue_hour", "slot", "adjusted_grid_kwh", "upward_kwh", "downward_kwh"])
        writer.writerows(adjustment_rows)

    day_costs = np.asarray([item["total_cny"] for item in daily])
    summary = {
        "question": "问题三", "status": "computed", "model_version": "C-M1-v1",
        "forecast_selection": context.forecast_modes,
        "forecast_metrics_january": context.forecast_scores,
        "parameters": {"scenario_count": scenario_count, "risk_weight": risk_weight,
                       "terminal_half_width_kwh": terminal_half_width},
        "full_detail_csv": str(detail_csv.relative_to(ROOT)),
        "adjustment_detail_csv": str(adjustment_csv.relative_to(ROOT)),
        "specified_days": selected_days, "days": len(daily), "final_soc_kwh": soc,
        "totals": {
            "plan_cny": float(sum(item["plan_cny"] for item in daily)),
            "upward_cny": float(sum(item["upward_cny"] for item in daily)),
            "downward_cny": float(sum(item["downward_cny"] for item in daily)),
            "emergency_cny": float(sum(item["emergency_cny"] for item in daily)),
            "total_cny": float(day_costs.sum()),
            "emergency_kwh": float(sum(item["emergency_kwh"] for item in daily)),
            "emergency_slots": int(sum(item["emergency_slots"] for item in daily)),
            "daily_cost_p50_cny": float(np.quantile(day_costs, 0.5)),
            "daily_cost_p90_cny": float(np.quantile(day_costs, 0.9)),
            "daily_cost_p95_cny": float(np.quantile(day_costs, 0.95)),
        },
        "daily_summary": daily,
        "diagnostics": {"scenario_lexicographic_skipped": True, "actual_dispatch_lexicographic": True},
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
    parser.add_argument("--detail-csv", type=Path, default=ROOT / "data/processed/q3_full_detail.csv")
    parser.add_argument("--adjustment-csv", type=Path, default=ROOT / "data/processed/q3_adjustments.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.full:
        result = run_full(
            args.scenarios, args.risk_weight, args.terminal_half_width,
            args.output or ROOT / "docs/results/q3_results.json",
            args.detail_csv, args.adjustment_csv,
        )
        print(json.dumps({"status": result["status"], "days": result["days"],
                          "final_soc_kwh": result["final_soc_kwh"]}, ensure_ascii=False, indent=2))
        return
    result = run_day(args.date, args.scenarios, args.risk_weight, args.terminal_half_width)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"date": result["date"], "costs": result["costs"],
                      "diagnostics": result["diagnostics"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
