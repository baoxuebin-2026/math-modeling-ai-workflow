import unittest

import numpy as np

from code.common.dispatch_lp import solve_adjustment_plan


class AdjustmentSettlementTest(unittest.TestCase):
    def test_downward_adjustment_pays_half_price_penalty(self) -> None:
        result = solve_adjustment_plan(
            original_plan=np.array([10.0]),
            price_scenarios=np.array([[1.0]]),
            load_scenarios=np.array([[5.0]]),
            pv_scenarios=np.array([[0.0]]),
            initial_soc=1200.0,
            terminal_bounds=(1200.0, 1200.0),
            risk_weight=0.0,
        )

        self.assertAlmostEqual(result.adjusted_grid[0], 5.0, places=7)
        self.assertAlmostEqual(result.upward[0], 0.0, places=7)
        self.assertAlmostEqual(result.downward[0], 5.0, places=7)
        self.assertAlmostEqual(result.scenario_incremental_costs[0], -2.5, places=7)

    def test_upward_adjustment_keeps_one_point_five_multiplier(self) -> None:
        result = solve_adjustment_plan(
            original_plan=np.array([5.0]),
            price_scenarios=np.array([[1.0]]),
            load_scenarios=np.array([[10.0]]),
            pv_scenarios=np.array([[0.0]]),
            initial_soc=1200.0,
            terminal_bounds=(1200.0, 1200.0),
            risk_weight=0.0,
        )

        self.assertAlmostEqual(result.adjusted_grid[0], 10.0, places=7)
        self.assertAlmostEqual(result.upward[0], 5.0, places=7)
        self.assertAlmostEqual(result.downward[0], 0.0, places=7)
        self.assertAlmostEqual(result.scenario_incremental_costs[0], 7.5, places=7)


if __name__ == "__main__":
    unittest.main()
