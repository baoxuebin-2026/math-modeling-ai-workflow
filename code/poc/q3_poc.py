"""Q3真实日期PoC：验证三次调整、分段状态连续与结算。"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from code.q3.solve_q3 import run_day

r = run_day("2025-03-20", scenario_count=3)
assert len(r["adjustments"]) == 3
assert [x["issue_hour"] for x in r["adjustments"]] == [6, 12, 18]
assert len(r["original_plan_grid_kwh"]) == len(r["final_active_grid_kwh"]) == 144
assert len(r["actual"]["soc"]) == 145
assert r["diagnostics"]["cross_segment_soc_continuity"]
assert r["diagnostics"]["simultaneous_charge_discharge_slots"] == 0
assert all(x["max_balance_residual_kwh"] <= 1e-5 for x in r["adjustments"])
assert r["costs"]["total_cny"] >= r["costs"]["plan_cny"]
print(f"passed,total={r['costs']['total_cny']:.6f},adjustments={len(r['adjustments'])}")
