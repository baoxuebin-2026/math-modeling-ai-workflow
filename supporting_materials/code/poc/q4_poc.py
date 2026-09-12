"""Q4真实日期PoC：验证波动价格下Q2/Q3两种策略。"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from code.q4.solve_q4 import run_day

r = run_day("2025-03-20", scenario_count=3)
assert len(r["q4_2"]["plan_grid_kwh"]) == 144
assert r["q4_2"]["diagnostics"]["plan_balance_residual"] <= 1e-5
assert r["q4_2"]["diagnostics"]["actual_balance_residual"] <= 1e-5
assert len(r["q4_3"]["adjustments"]) == 3
assert len(r["q4_3"]["actual"]["soc"]) == 145
assert r["q4_3"]["diagnostics"]["simultaneous_charge_discharge_slots"] == 0
assert r["q4_2"]["costs"]["total_cny"] >= 0 and r["q4_3"]["costs"]["total_cny"] >= 0
print(f"passed,q42={r['q4_2']['costs']['total_cny']:.6f},q43={r['q4_3']['costs']['total_cny']:.6f}")
