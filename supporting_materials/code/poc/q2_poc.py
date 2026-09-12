"""Q2真实日期PoC：验证无前视预测、场景计划和实际结算可行。"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from code.q2.solve_q2 import run_day

r = run_day("2025-03-20", scenario_count=3)
assert r["information_cutoff"] == "2025-03-20 00:00:00"
assert r["plan"]["max_balance_residual_kwh"] <= 1e-5
assert r["plan"]["max_state_residual_kwh"] <= 1e-5
assert r["actual"]["max_balance_residual_kwh"] <= 1e-5
assert r["actual"]["max_state_residual_kwh"] <= 1e-5
assert min(r["actual"]["soc_kwh"]) >= 1200 - 1e-6
assert max(r["actual"]["soc_kwh"]) <= 10800 + 1e-6
assert r["actual"]["total_cost_cny"] >= 0
print(f"passed,date={r['date']},cost={r['actual']['total_cost_cny']:.6f},"
      f"emergency={sum(r['actual']['emergency_kwh']):.6f}")
