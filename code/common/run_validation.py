"""Run the confirmed CP-06 validation package without overwriting formal results."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.annual_context import build_annual_context
from code.common.data_io import load_q1
from code.common.dispatch_lp import FLOW_MAX, SOC_MAX, SOC_MIN, no_storage_baseline, solve_deterministic
from code.q2.solve_q2 import run_day as run_q2_day


DATES = ("2025-03-20", "2025-06-21", "2025-09-23", "2025-12-21")
WIDTHS = (600.0, 1200.0, 2400.0)
ETA_CASES = {
    "both_0.85": (0.85, 0.85),
    "both_0.90": (0.90, 0.90),
    "roundtrip_0.90": (math.sqrt(0.90), math.sqrt(0.90)),
    "both_0.95": (0.95, 0.95),
}


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def physical_checks(context, q1_result: dict) -> dict:
    actual = pd.read_csv(ROOT / "data/processed/annual_actual.csv")
    actual["date"] = actual["date"].astype(str)
    fixed_price = np.asarray(load_q1()["price"])
    date_index = {day.isoformat(): i for i, day in enumerate(context.dates)}
    outputs: dict[str, object] = {
        "q1": {
            "max_balance_residual_kwh": q1_result["diagnostics"]["max_balance_residual_kwh"],
            "max_state_residual_kwh": q1_result["diagnostics"]["max_state_residual_kwh"],
            "simultaneous_charge_discharge_slots": q1_result["diagnostics"]["simultaneous_charge_discharge_slots"],
        }
    }
    configs = {
        "q2": ("q2_full_detail.csv", "plan_grid_kwh", "fixed"),
        "q3": ("q3_full_detail.csv", "final_adjusted_kwh", "fixed"),
        "q4_2": ("q4_2_full_detail.csv", "plan_grid_kwh", "actual"),
        "q4_3": ("q4_3_full_detail.csv", "final_adjusted_kwh", "actual"),
    }
    expected = {
        "q2": read_json("docs/results/q2_results.json")["totals"]["total_cost_cny"],
        "q3": read_json("docs/results/q3_results.json")["totals"]["total_cny"],
        "q4_2": read_json("docs/results/q4_results.json")["q4_2"]["totals"]["total_cny"],
        "q4_3": read_json("docs/results/q4_results.json")["q4_3"]["totals"]["total_cny"],
    }
    for name, (filename, grid_col, price_mode) in configs.items():
        detail = pd.read_csv(ROOT / "data/processed" / filename)
        detail["date"] = detail["date"].astype(str)
        merged = detail.merge(
            actual[["date", "slot", "load_kwh", "pv_actual_kwh"]], on=["date", "slot"],
            how="left", validate="one_to_one",
        ).sort_values(["date", "slot"]).reset_index(drop=True)
        pv_used = merged["pv_actual_kwh"].to_numpy() - merged["pv_spill_kwh"].to_numpy()
        balance = (
            merged[grid_col].to_numpy() + merged["emergency_kwh"].to_numpy()
            + merged["discharge_kwh"].to_numpy() + pv_used
            - merged["charge_kwh"].to_numpy() - merged["unused_grid_kwh"].to_numpy()
            - merged["load_kwh"].to_numpy()
        )
        soc = merged["soc_end_kwh"].to_numpy()
        state = soc[1:] - soc[:-1] - 0.9 * merged["charge_kwh"].to_numpy()[1:] \
            + merged["discharge_kwh"].to_numpy()[1:] / 0.9
        simultaneous = int(np.count_nonzero(
            (merged["charge_kwh"].to_numpy() > 1e-6)
            & (merged["discharge_kwh"].to_numpy() > 1e-6)
        ))
        price = fixed_price[merged["slot"].to_numpy(dtype=int) - 1] if price_mode == "fixed" \
            else context.price[np.array([date_index[d] for d in merged["date"]]),
                               merged["slot"].to_numpy(dtype=int) - 1]
        if name in ("q2", "q4_2"):
            recalculated = float(np.sum(price * merged[grid_col]) + np.sum(5 * price * merged["emergency_kwh"]))
        else:
            original = merged["original_plan_kwh"].to_numpy()
            active = merged["final_adjusted_kwh"].to_numpy()
            recalculated = float(
                np.sum(price * original)
                + np.sum(1.5 * price * np.maximum(active - original, 0))
                + np.sum(0.5 * price * np.maximum(original - active, 0))
                + np.sum(5 * price * merged["emergency_kwh"])
            )
        outputs[name] = {
            "max_balance_residual_kwh": float(np.max(np.abs(balance))),
            "max_state_residual_kwh_excluding_first_interval": float(np.max(np.abs(state))),
            "soc_min_kwh": float(soc.min()), "soc_max_kwh": float(soc.max()),
            "max_charge_kwh": float(merged["charge_kwh"].max()),
            "max_discharge_kwh": float(merged["discharge_kwh"].max()),
            "simultaneous_charge_discharge_slots": simultaneous,
            "fee_recalculation_abs_diff_cny": abs(recalculated - expected[name]),
            "passed": bool(
                np.max(np.abs(balance)) <= 1e-5 and np.max(np.abs(state)) <= 1e-5
                and soc.min() >= SOC_MIN - 1e-5 and soc.max() <= SOC_MAX + 1e-5
                and merged["charge_kwh"].max() <= FLOW_MAX + 1e-5
                and merged["discharge_kwh"].max() <= FLOW_MAX + 1e-5
                and simultaneous == 0 and abs(recalculated - expected[name]) <= 1e-4
            ),
        }
    return outputs


def forecast_checks(q2: dict, q4: dict) -> dict:
    selections = {
        "load": (q2["forecast_selection"]["load"], q2["specified_days"][DATES[0]]["forecast_metrics_january"]["load"]),
        "pv": (q2["forecast_selection"]["pv"], q2["specified_days"][DATES[0]]["forecast_metrics_january"]["pv"]),
        "price": (q4["forecast_selection"]["price"], q4["forecast_metrics_january"]["price"]),
    }
    output = {}
    for name, (selected, metrics) in selections.items():
        output[name] = {
            "selected": selected,
            "selected_nmae": metrics[selected]["nmae"],
            "alternatives": {model: values["nmae"] for model, values in metrics.items()},
            "passed": metrics[selected]["nmae"] <= min(values["nmae"] for values in metrics.values()) + 1e-12,
        }
    return output


def terminal_sensitivity(context, q2: dict) -> list[dict]:
    output = []
    for day in DATES:
        initial_soc = float(q2["specified_days"][day]["plan"]["expected_soc_kwh"][0])
        for width in WIDTHS:
            result = run_q2_day(
                day, scenario_count=10, risk_weight=0.0, terminal_half_width=width,
                initial_soc=initial_soc, context=context, lexicographic_plan=False,
            )
            output.append({
                "date": day, "scenario_count": 10, "terminal_half_width_kwh": width,
                "total_cost_cny": result["actual"]["total_cost_cny"],
                "emergency_kwh": float(np.sum(result["actual"]["emergency_kwh"])),
                "actual_terminal_soc_kwh": result["actual"]["soc_kwh"][-1],
                "planned_terminal_soc_kwh": result["plan"]["expected_terminal_soc_kwh"],
            })
            print(f"terminal sensitivity {day} width={width:.0f}", flush=True)
    return output


def efficiency_sensitivity(context, q1_data: dict, q2: dict) -> dict:
    baseline = no_storage_baseline(q1_data["price"], q1_data["load"], q1_data["pv"])
    q1_cases = []
    for label, (eta_c, eta_d) in ETA_CASES.items():
        result = solve_deterministic(
            q1_data["price"], q1_data["load"], q1_data["pv"], 6000.0, (6000.0, 6000.0),
            eta_charge=eta_c, eta_discharge=eta_d,
        )
        q1_cases.append({
            "case": label, "eta_charge": eta_c, "eta_discharge": eta_d,
            "total_cost_cny": result.primary_objective,
            "saving_rate": 1 - result.primary_objective / baseline["cost_cny"],
        })
    seasonal = []
    fixed_price = q1_data["price"]
    date_index = {d.isoformat(): i for i, d in enumerate(context.dates)}
    for day in DATES:
        item = q2["specified_days"][day]
        idx = date_index[day]
        plan = np.asarray(item["plan"]["grid_kwh"])
        initial_soc = float(item["plan"]["expected_soc_kwh"][0])
        for label, (eta_c, eta_d) in ETA_CASES.items():
            result = solve_deterministic(
                fixed_price, context.load[idx], context.pv[idx], initial_soc,
                (SOC_MIN, SOC_MAX), fixed_grid=plan, allow_emergency=True,
                eta_charge=eta_c, eta_discharge=eta_d,
            )
            seasonal.append({
                "date": day, "case": label, "total_cost_cny": float(fixed_price @ plan + 5 * fixed_price @ result.emergency),
                "emergency_kwh": float(result.emergency.sum()), "terminal_soc_kwh": float(result.soc[-1]),
            })
    return {"q1_reoptimized": q1_cases, "q2_fixed_plan_stress": seasonal}


def extreme_error_stress(context, q2: dict, q1_data: dict) -> list[dict]:
    output = []
    fixed_price = q1_data["price"]
    date_index = {d.isoformat(): i for i, d in enumerate(context.dates)}
    for day in DATES:
        item = q2["specified_days"][day]
        idx = date_index[day]
        plan = np.asarray(item["plan"]["grid_kwh"])
        load, pv = context.load[idx], context.pv[idx]
        net = load - pv
        initial_soc = float(item["plan"]["expected_soc_kwh"][0])
        for bias in (-0.20, -0.10, 0.0, 0.10, 0.20):
            stressed_load = np.maximum(pv + net * (1 + bias), 0)
            result = solve_deterministic(
                fixed_price, stressed_load, pv, initial_soc, (SOC_MIN, SOC_MAX),
                fixed_grid=plan, allow_emergency=True,
            )
            output.append({
                "date": day, "net_demand_bias": bias,
                "total_cost_cny": float(fixed_price @ plan + 5 * fixed_price @ result.emergency),
                "emergency_kwh": float(result.emergency.sum()),
                "terminal_soc_kwh": float(result.soc[-1]),
            })
    return output


def evaluate_progressive_updates(branch: dict, load: np.ndarray, pv: np.ndarray,
                                 price: np.ndarray) -> list[dict]:
    original_key = "original_plan_grid_kwh"
    original = np.asarray(branch[original_key])
    initial_soc = float(branch["diagnostics"]["soc_start_kwh"])
    records = sorted(branch["adjustments"], key=lambda row: row["issue_hour"])
    output = []
    for max_update in (0, 6, 12, 18):
        selected = [row for row in records if row["issue_hour"] <= max_update]
        active = original.copy()
        for row in selected:
            start = int(row["start_slot"]) - 1
            active[start:] = np.asarray(row["adjusted_grid_kwh"])
        cutoffs = [0] + [row["issue_hour"] for row in selected] + [24]
        soc = initial_soc
        emergencies = []
        for start_hour, end_hour in zip(cutoffs[:-1], cutoffs[1:]):
            start, end = start_hour * 6, end_hour * 6
            actual = solve_deterministic(
                price[start:end], load[start:end], pv[start:end], soc,
                (SOC_MIN, SOC_MAX), fixed_grid=active[start:end], allow_emergency=True,
            )
            emergencies.append(actual.emergency)
            soc = float(actual.soc[-1])
        emergency = np.concatenate(emergencies)
        upward = np.maximum(active - original, 0)
        downward = np.maximum(original - active, 0)
        plan_cost = float(price @ original)
        adjustment_cost = float(1.5 * price @ upward + 0.5 * price @ downward)
        emergency_cost = float(5 * price @ emergency)
        output.append({
            "max_update_hour": max_update, "updates_used": len(selected),
            "plan_cost_cny": plan_cost, "adjustment_cost_cny": adjustment_cost,
            "emergency_cost_cny": emergency_cost,
            "total_cost_cny": plan_cost + adjustment_cost + emergency_cost,
            "emergency_kwh": float(emergency.sum()), "terminal_soc_kwh": soc,
        })
    return output


def _risk_dates(daily: list[dict]) -> list[str]:
    frame = pd.DataFrame(daily)
    frame["month"] = pd.to_datetime(frame["date"]).dt.month
    periods = ((2, 4), (5, 7), (8, 10), (11, 12))
    return [
        str(frame.loc[frame["month"].between(lo, hi), :].sort_values("emergency_kwh").iloc[-1]["date"])
        for lo, hi in periods
    ]


def _branch_from_csv(detail_file: str, adjustment_file: str, day: str) -> dict:
    detail = pd.read_csv(ROOT / "data/processed" / detail_file)
    detail = detail[detail["date"].astype(str) == day].sort_values("slot")
    adjustments = pd.read_csv(ROOT / "data/processed" / adjustment_file)
    adjustments = adjustments[adjustments["date"].astype(str) == day]
    records = []
    for issue_hour, group in adjustments.groupby("issue_hour"):
        group = group.sort_values("slot")
        records.append({
            "issue_hour": int(issue_hour), "start_slot": int(group["slot"].iloc[0]),
            "adjusted_grid_kwh": group["adjusted_grid_kwh"].tolist(),
        })
    initial_soc = float(
        detail["soc_end_kwh"].iloc[0] - 0.9 * detail["charge_kwh"].iloc[0]
        + detail["discharge_kwh"].iloc[0] / 0.9
    )
    return {
        "original_plan_grid_kwh": detail["original_plan_kwh"].tolist(),
        "adjustments": records,
        "diagnostics": {"soc_start_kwh": initial_soc},
    }


def update_ablation(context, q2: dict, q3: dict, q4: dict, q1_data: dict) -> dict:
    date_index = {d.isoformat(): i for i, d in enumerate(context.dates)}
    output = {"seasonal_anchors": {"q3": [], "q4": []}, "seasonal_risk_days": {"q3": [], "q4": []}}
    for day_text in DATES:
        idx = date_index[day_text]
        for row in evaluate_progressive_updates(
            q3["specified_days"][day_text], context.load[idx], context.pv[idx], q1_data["price"]
        ):
            output["seasonal_anchors"]["q3"].append({"date": day_text, **row})
        for row in evaluate_progressive_updates(
            q4["specified_days"][day_text]["q4_3"], context.load[idx], context.pv[idx], context.price[idx]
        ):
            output["seasonal_anchors"]["q4"].append({"date": day_text, **row})
    risk_sets = {
        "q3": _risk_dates(q2["daily_summary"]),
        "q4": _risk_dates(q4["q4_2"]["daily_summary"]),
    }
    for problem, days in risk_sets.items():
        for day_text in days:
            idx = date_index[day_text]
            if problem == "q3":
                branch = _branch_from_csv("q3_full_detail.csv", "q3_adjustments.csv", day_text)
                price = q1_data["price"]
            else:
                branch = _branch_from_csv("q4_3_full_detail.csv", "q4_3_adjustments.csv", day_text)
                price = context.price[idx]
            for row in evaluate_progressive_updates(branch, context.load[idx], context.pv[idx], price):
                output["seasonal_risk_days"][problem].append({"date": day_text, **row})
    output["risk_dates"] = risk_sets
    return output


def main() -> None:
    q1_result = read_json("docs/results/q1_results.json")
    q2 = read_json("docs/results/q2_results.json")
    q3 = read_json("docs/results/q3_results.json")
    q4 = read_json("docs/results/q4_results.json")
    calibration = read_json("docs/results/parameter_calibration.json")
    q1_data = load_q1()
    print("building annual causal context", flush=True)
    context = build_annual_context(include_price_forecast=True)
    print("running independent physical checks", flush=True)
    results = {
        "status": "checked", "dates": list(DATES),
        "v1_physical_and_accounting": physical_checks(context, q1_result),
        "v2_forecast_selection": forecast_checks(q2, q4),
        "v3_scenario_convergence": calibration["scenario_convergence"],
        "v4_risk_weight_grid": calibration["risk_width_grid"],
    }
    results["v5_terminal_sensitivity"] = terminal_sensitivity(context, q2)
    print("running efficiency sensitivity", flush=True)
    results["v6_efficiency_sensitivity"] = efficiency_sensitivity(context, q1_data, q2)
    print("running extreme-error stress", flush=True)
    results["v7_extreme_error_stress"] = extreme_error_stress(context, q2, q1_data)
    print("running progressive-update ablation", flush=True)
    results["v8_update_ablation"] = update_ablation(context, q2, q3, q4, q1_data)
    output = ROOT / "docs/results/validation_results.json"
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
