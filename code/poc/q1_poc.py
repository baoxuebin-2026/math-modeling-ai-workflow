"""Q1真实附件PoC：验证LP可行性、单位、余额和费用改善。"""
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from code.common.data_io import load_q1
from code.common.dispatch_lp import no_storage_baseline, solve_deterministic

data = load_q1()
result = solve_deterministic(data["price"], data["load"], data["pv"], 6000, (6000, 6000))
base = no_storage_baseline(data["price"], data["load"], data["pv"])
assert len(result.grid) == 144
assert result.max_balance_residual <= 1e-5
assert result.max_state_residual <= 1e-5
assert np.min(result.soc) >= 1200 - 1e-6 and np.max(result.soc) <= 10800 + 1e-6
assert abs(result.soc[0] - result.soc[-1]) <= 1e-6
assert not np.any((result.charge > 1e-6) & (result.discharge > 1e-6))
assert result.primary_objective <= base["cost_cny"] + 1e-6
print(f"passed,cost={result.primary_objective:.6f},baseline={base['cost_cny']:.6f},"
      f"balance={result.max_balance_residual:.3e},state={result.max_state_residual:.3e}")
