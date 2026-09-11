"""求解问题1并输出结构化JSON；不负责绘图或Excel格式。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.data_io import load_q1
from code.common.dispatch_lp import no_storage_baseline, solve_deterministic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/results/q1_results.json")
    return parser.parse_args()


def clean(values: np.ndarray) -> list[float]:
    return [round(float(value), 8) for value in values]


def main() -> None:
    args = parse_args()
    data = load_q1()
    result = solve_deterministic(
        price=data["price"], load=data["load"], pv=data["pv"], initial_soc=6000.0,
        terminal_bounds=(6000.0, 6000.0), allow_emergency=False,
    )
    baseline = no_storage_baseline(data["price"], data["load"], data["pv"])
    payload = {
        "question": "问题一",
        "status": "computed",
        "evidence_status": "checked",
        "paper_position": "问题一模型建立与求解",
        "code": "code/q1/solve_q1.py",
        "visualization_code": "code/q1/visualize_q1.py",
        "input_files": ["data/processed/q1_timeseries.csv"],
        "model": {
            "version": "C-M1-v1",
            "baseline": "无储能净购电",
            "selected": "确定性连续线性规划 + 词典序去退化",
            "reason": "价格和物理约束均为线性，不需要整数或启发式算法",
        },
        "parameters": {
            "dt_hours": 1 / 6, "eta_charge": 0.9, "eta_discharge": 0.9,
            "soc_min_kwh": 1200, "soc_max_kwh": 10800,
            "flow_max_kwh_per_slot": 5000 / 6,
        },
        "outputs": {
            "plan_grid_kwh": clean(result.grid),
            "emergency_kwh": clean(result.emergency),
            "charge_kwh": clean(result.charge),
            "discharge_kwh": clean(result.discharge),
            "soc_kwh": clean(result.soc),
            "pv_used_kwh": clean(result.pv_used),
            "pv_spill_kwh": clean(result.pv_spill),
            "unused_grid_kwh": clean(result.grid_spill),
            "total_grid_kwh": float(result.grid.sum()),
            "total_cost_cny": float(result.primary_objective),
            "baseline": baseline,
            "cost_saving_cny": float(baseline["cost_cny"] - result.primary_objective),
            "cost_saving_rate": float((baseline["cost_cny"] - result.primary_objective) / baseline["cost_cny"]),
        },
        "diagnostics": {
            "solver": "scipy.optimize.linprog(method=highs)",
            "solver_message": result.solver_message,
            "max_balance_residual_kwh": result.max_balance_residual,
            "max_state_residual_kwh": result.max_state_residual,
            "soc_start_kwh": float(result.soc[0]),
            "soc_end_kwh": float(result.soc[-1]),
            "simultaneous_charge_discharge_slots": int(np.sum((result.charge > 1e-6) & (result.discharge > 1e-6))),
        },
        "notes": ["正式论文结论仍需通过图表、独立复算与验证门。"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"], "cost_cny": payload["outputs"]["total_cost_cny"],
        "saving_rate": payload["outputs"]["cost_saving_rate"], "diagnostics": payload["diagnostics"],
        "output": str(args.output.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
