"""问题4：在未来价格未知条件下重算Q2与Q3策略。"""

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
from code.common.data_io import load_annual, load_hourly_pv_forecasts
from code.common.dispatch_lp import SOC_MAX, SOC_MIN, solve_adjustment_plan, solve_deterministic, solve_scenario_plan
from code.common.provider_forecast import provider_curve, provider_residual_history
from code.common.scenarios import bootstrap_aligned_rows, bootstrap_joint_blocks
from code.q2.solve_q2 import choose_forecaster, forecast_and_residuals


SEED = 20260910
START_HISTORY = 15


def _merge(parts: dict[str, list[np.ndarray]]) -> dict[str, np.ndarray]:
    return {name: np.concatenate(values) for name, values in parts.items()}


def run_day(day_text: str, scenario_count: int = 3, risk_weight: float = 0.25,
            terminal_half_width: float = 1200.0, initial_soc: float = 6000.0,
            context: AnnualContext | None = None,
            lexicographic_plan: bool = True,
            initial_soc_q43: float | None = None) -> dict[str, object]:
    if context is None:
        annual, hourly = load_annual(), load_hourly_pv_forecasts()
        dates = [date.fromisoformat(value) for value in annual["dates"].tolist()]
    else:
        dates = context.dates
    target = date.fromisoformat(day_text)
    if target not in dates:
        raise ValueError("日期必须位于2025年")
    index = dates.index(target)
    q43_initial_soc = initial_soc if initial_soc_q43 is None else initial_soc_q43

    if context is None:
        modes, scores, points, residuals = {}, {}, {}, {}
        for name in ("load", "pv", "price"):
            modes[name], scores[name] = choose_forecaster(annual[name], dates)
            points[name], residuals[name] = forecast_and_residuals(annual[name], dates, index, modes[name])
        actual_load, actual_pv, actual_price = (
            annual["load"][index], annual["pv"][index], annual["price"][index]
        )
    else:
        modes = {name: context.forecast_modes[name] for name in ("load", "pv", "price")}
        scores = {name: context.forecast_scores[name] for name in ("load", "pv", "price")}
        points = {name: context.points[name][index] for name in ("load", "pv", "price")}
        residuals = {name: context.residuals[name][:index] for name in ("load", "pv", "price")}
        actual_load, actual_pv, actual_price = context.load[index], context.pv[index], context.price[index]

    # Q4-2：未知未来价格与源荷共同进入0:00场景计划。
    history_count = min(len(residuals[name]) for name in residuals)
    q42_scenarios = bootstrap_joint_blocks(
        {name: points[name] for name in ("load", "pv", "price")},
        {name: residuals[name][-history_count:] for name in ("load", "pv", "price")},
        scenario_count, SEED + index,
    )
    q42_plan = solve_scenario_plan(
        q42_scenarios["price"], q42_scenarios["load"], q42_scenarios["pv"], initial_soc,
        (6000 - terminal_half_width, 6000 + terminal_half_width), risk_weight=risk_weight,
        lexicographic=lexicographic_plan,
    )
    q42_actual = solve_deterministic(
        actual_price, actual_load, actual_pv, initial_soc,
        (SOC_MIN, SOC_MAX), fixed_grid=q42_plan.plan_grid[:144], allow_emergency=True,
    )
    q42_plan_cost = float(actual_price @ q42_plan.plan_grid[:144])
    q42_emergency_cost = float(5 * actual_price @ q42_actual.emergency)

    # Q4-3：0:00采用附件3，6/12/18按新光伏预报和已实现价格偏差更新。
    pv_issue0 = (provider_curve(hourly, annual["pv"], target, index, 0)
                 if context is None else context.provider_curves[0][index])
    q43_pv_point = np.vstack([pv_issue0, points["pv"][1]])
    provider0 = (provider_residual_history(hourly, annual["pv"], dates, index, 0, START_HISTORY)
                 if context is None else context.provider_residuals[0][START_HISTORY:index])
    aligned = min(len(residuals["load"]), len(residuals["price"]), len(provider0))
    q43_scenarios = bootstrap_joint_blocks(
        {"load": points["load"], "pv": q43_pv_point, "price": points["price"]},
        {"load": residuals["load"][-aligned:], "pv": provider0[-aligned:],
         "price": residuals["price"][-aligned:]},
        scenario_count, SEED + index + 10000,
    )
    q43_plan = solve_scenario_plan(
        q43_scenarios["price"], q43_scenarios["load"], q43_scenarios["pv"], q43_initial_soc,
        (6000 - terminal_half_width, 6000 + terminal_half_width), risk_weight=risk_weight,
        lexicographic=lexicographic_plan,
    )
    original, active = q43_plan.plan_grid[:144].copy(), q43_plan.plan_grid[:144].copy()
    issue_hours = [0, 6, 12, 18]
    soc = q43_initial_soc
    parts = {name: [] for name in ("grid", "emergency", "charge", "discharge", "pv_spill", "grid_spill", "soc")}
    adjustments = []
    for segment_index, issue_hour in enumerate(issue_hours):
        start = issue_hour * 6
        end = 144 if segment_index == 3 else issue_hours[segment_index + 1] * 6
        if issue_hour > 0:
            remaining = 144 - start
            if context is None:
                pv_center = provider_curve(hourly, annual["pv"], target, index, issue_hour)[:remaining]
                pv_hist = provider_residual_history(
                    hourly, annual["pv"], dates, index, issue_hour, START_HISTORY
                )
            else:
                pv_center = context.provider_curves[issue_hour][index][:remaining]
                pv_hist = context.provider_residuals[issue_hour][START_HISTORY:index]
            # 已实现价格只用于估计当日剩余价格的加性偏差，不读取未来实测。
            realized_bias = float(np.mean(actual_price[:start] - points["price"][0, :start]))
            price_center = np.maximum(points["price"][0, start:] + realized_bias, 0.0)
            aligned = min(len(residuals["load"]), len(residuals["price"]), len(pv_hist))
            update_scenarios = bootstrap_aligned_rows(
                {"load": points["load"][0, start:], "pv": pv_center, "price": price_center},
                {"load": residuals["load"][-aligned:, start:], "pv": pv_hist[-aligned:],
                 "price": residuals["price"][-aligned:, start:]},
                scenario_count, SEED + index * 10 + issue_hour + 10000,
            )
            update = solve_adjustment_plan(
                original[start:], update_scenarios["price"], update_scenarios["load"],
                update_scenarios["pv"], soc,
                (6000 - terminal_half_width, 6000 + terminal_half_width), risk_weight=risk_weight,
            )
            active[start:] = update.adjusted_grid
            adjustments.append({
                "issue_hour": issue_hour, "realized_price_bias": realized_bias,
                "start_slot": start + 1,
                "adjusted_grid_kwh": update.adjusted_grid.tolist(),
                "upward_kwh": update.upward.tolist(), "downward_kwh": update.downward.tolist(),
                "max_balance_residual_kwh": update.max_balance_residual,
                "max_state_residual_kwh": update.max_state_residual,
            })
        actual = solve_deterministic(
            actual_price[start:end], actual_load[start:end],
            actual_pv[start:end], soc, (SOC_MIN, SOC_MAX),
            fixed_grid=active[start:end], allow_emergency=True,
        )
        for name in ("grid", "emergency", "charge", "discharge", "pv_spill", "grid_spill"):
            parts[name].append(getattr(actual, name))
        parts["soc"].append(actual.soc if segment_index == 0 else actual.soc[1:])
        soc = float(actual.soc[-1])
    actual43 = _merge(parts)
    upward, downward = np.maximum(active - original, 0), np.maximum(original - active, 0)
    cancelled_plan_cost = float(actual_price @ downward)
    down_penalty_cost = float(0.5 * actual_price @ downward)
    costs43 = {
        "plan_cny": float(actual_price @ original),
        "upward_cny": float(1.5 * actual_price @ upward),
        "cancelled_plan_cny": cancelled_plan_cost,
        "downward_cny": down_penalty_cost,
        "downward_net_cny": down_penalty_cost - cancelled_plan_cost,
        "emergency_cny": float(5 * actual_price @ actual43["emergency"]),
    }
    costs43["total_cny"] = (
        costs43["plan_cny"] + costs43["upward_cny"]
        + costs43["downward_net_cny"] + costs43["emergency_cny"]
    )

    return {
        "date": day_text,
        "forecast_selection": modes,
        "forecast_metrics_january": scores,
        "parameters": {"scenarios": scenario_count, "risk_weight": risk_weight,
                       "terminal_half_width_kwh": terminal_half_width},
        "q4_2": {
            "plan_grid_kwh": q42_plan.plan_grid[:144].tolist(),
            "actual": {"grid_kwh": q42_actual.grid.tolist(), "emergency_kwh": q42_actual.emergency.tolist(),
                       "charge_kwh": q42_actual.charge.tolist(), "discharge_kwh": q42_actual.discharge.tolist(),
                       "pv_spill_kwh": q42_actual.pv_spill.tolist(),
                       "unused_grid_kwh": q42_actual.grid_spill.tolist(), "soc_kwh": q42_actual.soc.tolist()},
            "costs": {"plan_cny": q42_plan_cost, "emergency_cny": q42_emergency_cost,
                      "total_cny": q42_plan_cost + q42_emergency_cost},
            "diagnostics": {"plan_balance_residual": q42_plan.max_balance_residual,
                            "actual_balance_residual": q42_actual.max_balance_residual,
                            "simultaneous_charge_discharge_slots": int(np.sum(
                                (q42_actual.charge > 1e-6) & (q42_actual.discharge > 1e-6)))},
        },
        "q4_3": {
            "original_plan_grid_kwh": original.tolist(), "final_active_grid_kwh": active.tolist(),
            "adjustments": adjustments,
            "actual": {name: values.tolist() for name, values in actual43.items()},
            "costs": costs43,
            "diagnostics": {"soc_start_kwh": q43_initial_soc, "soc_end_kwh": soc,
                            "simultaneous_charge_discharge_slots": int(np.sum((actual43["charge"] > 1e-6) &
                                                                               (actual43["discharge"] > 1e-6)))},
        },
    }


def _run_q42_warm_day(context: AnnualContext, index: int, initial_soc: float,
                      scenario_count: int, risk_weight: float,
                      terminal_half_width: float) -> object:
    """Q4-2的1月热启动；早期历史不足时自动退化为单场景。"""
    point = {name: context.points[name][index] for name in ("load", "pv", "price")}
    if index >= 2:
        sampled = bootstrap_joint_blocks(
            point, {name: context.residuals[name][:index] for name in point},
            scenario_count, SEED + index,
        )
        active_scenarios, active_risk = scenario_count, risk_weight
    else:
        sampled = {name: values.reshape(1, -1) for name, values in point.items()}
        active_scenarios, active_risk = 1, 0.0
    plan = solve_scenario_plan(
        sampled["price"], sampled["load"], sampled["pv"], initial_soc,
        (6000 - terminal_half_width, 6000 + terminal_half_width),
        risk_weight=active_risk, lexicographic=False,
    )
    return solve_deterministic(
        context.price[index], context.load[index], context.pv[index], initial_soc,
        (SOC_MIN, SOC_MAX), fixed_grid=plan.plan_grid[:144], allow_emergency=True,
    )


def run_full(scenario_count: int, risk_weight: float, terminal_half_width: float,
             output_json: Path, q42_csv: Path, q43_csv: Path,
             adjustment_csv: Path) -> dict[str, object]:
    context = build_annual_context(include_price_forecast=True)
    soc42 = soc43 = 6000.0
    rows42: list[list[object]] = []
    rows43: list[list[object]] = []
    adjustment_rows: list[list[object]] = []
    daily42: list[dict[str, object]] = []
    daily43: list[dict[str, object]] = []
    selected_days: dict[str, object] = {}
    specified = {"2025-03-20", "2025-06-21", "2025-09-23", "2025-12-21"}
    for index, day in enumerate(context.dates):
        if day < date(2025, 2, 1):
            warm = _run_q42_warm_day(
                context, index, soc42, scenario_count, risk_weight, terminal_half_width
            )
            soc42 = float(warm.soc[-1])
            soc43 = soc42
            continue
        result = run_day(
            day.isoformat(), scenario_count, risk_weight, terminal_half_width, soc42, context,
            lexicographic_plan=False, initial_soc_q43=soc43,
        )
        q42, q43 = result["q4_2"], result["q4_3"]
        soc42 = float(q42["actual"]["soc_kwh"][-1])
        soc43 = float(q43["actual"]["soc"][-1])
        if day.isoformat() in specified:
            selected_days[day.isoformat()] = result
        emg42 = np.asarray(q42["actual"]["emergency_kwh"], dtype=float)
        emg43 = np.asarray(q43["actual"]["emergency"], dtype=float)
        daily42.append({
            "date": day.isoformat(), **q42["costs"], "emergency_kwh": float(emg42.sum()),
            "emergency_slots": int(np.count_nonzero(emg42 > 1e-6)), "soc_end_kwh": soc42,
        })
        daily43.append({
            "date": day.isoformat(), **q43["costs"], "emergency_kwh": float(emg43.sum()),
            "emergency_slots": int(np.count_nonzero(emg43 > 1e-6)), "soc_end_kwh": soc43,
        })
        for slot in range(144):
            rows42.append([
                day.isoformat(), slot + 1, q42["plan_grid_kwh"][slot],
                q42["actual"]["charge_kwh"][slot], q42["actual"]["discharge_kwh"][slot],
                q42["actual"]["emergency_kwh"][slot], q42["actual"]["pv_spill_kwh"][slot],
                q42["actual"]["unused_grid_kwh"][slot], q42["actual"]["soc_kwh"][slot + 1],
            ])
            rows43.append([
                day.isoformat(), slot + 1, q43["original_plan_grid_kwh"][slot],
                q43["final_active_grid_kwh"][slot], q43["actual"]["charge"][slot],
                q43["actual"]["discharge"][slot], q43["actual"]["emergency"][slot],
                q43["actual"]["pv_spill"][slot], q43["actual"]["grid_spill"][slot],
                q43["actual"]["soc"][slot + 1],
            ])
        for record in q43["adjustments"]:
            start = int(record["start_slot"])
            for offset, adjusted in enumerate(record["adjusted_grid_kwh"]):
                adjustment_rows.append([
                    day.isoformat(), record["issue_hour"], start + offset, adjusted,
                    record["upward_kwh"][offset], record["downward_kwh"][offset],
                    record["realized_price_bias"],
                ])
        if (index + 1) % 20 == 0 or index + 1 == len(context.dates):
            print(f"Q4 progress: {index + 1}/{len(context.dates)}", flush=True)

    q42_csv.parent.mkdir(parents=True, exist_ok=True)
    with q42_csv.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["date", "slot", "plan_grid_kwh", "charge_kwh", "discharge_kwh",
                         "emergency_kwh", "pv_spill_kwh", "unused_grid_kwh", "soc_end_kwh"])
        writer.writerows(rows42)
    with q43_csv.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["date", "slot", "original_plan_kwh", "final_adjusted_kwh", "charge_kwh",
                         "discharge_kwh", "emergency_kwh", "pv_spill_kwh", "unused_grid_kwh", "soc_end_kwh"])
        writer.writerows(rows43)
    with adjustment_csv.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["date", "issue_hour", "slot", "adjusted_grid_kwh", "upward_kwh",
                         "downward_kwh", "realized_price_bias"])
        writer.writerows(adjustment_rows)

    costs42 = np.asarray([item["total_cny"] for item in daily42])
    costs43 = np.asarray([item["total_cny"] for item in daily43])
    summary = {
        "question": "问题四", "status": "computed", "model_version": "C-M1-v2",
        "forecast_selection": context.forecast_modes,
        "forecast_metrics_january": context.forecast_scores,
        "parameters": {"scenario_count": scenario_count, "risk_weight": risk_weight,
                       "terminal_half_width_kwh": terminal_half_width},
        "specified_days": selected_days, "days": len(daily42),
        "q4_2": {
            "full_detail_csv": str(q42_csv.relative_to(ROOT)), "final_soc_kwh": soc42,
            "totals": {
                "plan_cny": float(sum(item["plan_cny"] for item in daily42)),
                "emergency_cny": float(sum(item["emergency_cny"] for item in daily42)),
                "total_cny": float(costs42.sum()),
                "emergency_kwh": float(sum(item["emergency_kwh"] for item in daily42)),
                "emergency_slots": int(sum(item["emergency_slots"] for item in daily42)),
                "daily_cost_p95_cny": float(np.quantile(costs42, 0.95)),
            },
            "daily_summary": daily42,
        },
        "q4_3": {
            "full_detail_csv": str(q43_csv.relative_to(ROOT)),
            "adjustment_detail_csv": str(adjustment_csv.relative_to(ROOT)),
            "final_soc_kwh": soc43,
            "totals": {
                "plan_cny": float(sum(item["plan_cny"] for item in daily43)),
                "upward_cny": float(sum(item["upward_cny"] for item in daily43)),
                "cancelled_plan_cny": float(sum(item["cancelled_plan_cny"] for item in daily43)),
                "downward_cny": float(sum(item["downward_cny"] for item in daily43)),
                "downward_net_cny": float(sum(item["downward_net_cny"] for item in daily43)),
                "emergency_cny": float(sum(item["emergency_cny"] for item in daily43)),
                "total_cny": float(costs43.sum()),
                "emergency_kwh": float(sum(item["emergency_kwh"] for item in daily43)),
                "emergency_slots": int(sum(item["emergency_slots"] for item in daily43)),
                "daily_cost_p95_cny": float(np.quantile(costs43, 0.95)),
            },
            "daily_summary": daily43,
        },
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
    parser.add_argument("--q42-csv", type=Path, default=ROOT / "data/processed/q4_2_full_detail.csv")
    parser.add_argument("--q43-csv", type=Path, default=ROOT / "data/processed/q4_3_full_detail.csv")
    parser.add_argument("--adjustment-csv", type=Path, default=ROOT / "data/processed/q4_3_adjustments.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.full:
        result = run_full(
            args.scenarios, args.risk_weight, args.terminal_half_width,
            args.output or ROOT / "docs/results/q4_results.json", args.q42_csv,
            args.q43_csv, args.adjustment_csv,
        )
        print(json.dumps({"status": result["status"], "days": result["days"],
                          "q4_2_final_soc_kwh": result["q4_2"]["final_soc_kwh"],
                          "q4_3_final_soc_kwh": result["q4_3"]["final_soc_kwh"]},
                         ensure_ascii=False, indent=2))
        return
    result = run_day(args.date, args.scenarios, args.risk_weight, args.terminal_half_width)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"date": result["date"], "forecast_selection": result["forecast_selection"],
                      "q4_2_costs": result["q4_2"]["costs"], "q4_3_costs": result["q4_3"]["costs"],
                      "q4_3_diagnostics": result["q4_3"]["diagnostics"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
