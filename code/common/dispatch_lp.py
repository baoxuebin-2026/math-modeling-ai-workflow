"""储能调度的确定性与场景连续线性规划。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import OptimizeResult, linprog
from scipy.sparse import coo_matrix, csr_matrix, vstack


SOC_MIN = 1200.0
SOC_MAX = 10800.0
FLOW_MAX = 5000.0 / 6.0
ETA_C = 0.9
ETA_D = 0.9
FEAS_TOL = 1e-7
BALANCE_TOL = 1e-5


@dataclass(frozen=True)
class DispatchResult:
    objective: float
    primary_objective: float
    grid: np.ndarray
    emergency: np.ndarray
    charge: np.ndarray
    discharge: np.ndarray
    pv_used: np.ndarray
    pv_spill: np.ndarray
    grid_spill: np.ndarray
    soc: np.ndarray
    max_balance_residual: float
    max_state_residual: float
    solver_message: str


@dataclass(frozen=True)
class ScenarioPlanResult:
    risk_objective: float
    plan_grid: np.ndarray
    mean_emergency: np.ndarray
    mean_charge: np.ndarray
    mean_discharge: np.ndarray
    mean_pv_spill: np.ndarray
    mean_grid_spill: np.ndarray
    mean_soc: np.ndarray
    scenario_costs: np.ndarray
    var_cost: float | None
    cvar_cost: float | None
    max_balance_residual: float
    max_state_residual: float
    solver_message: str


@dataclass(frozen=True)
class AdjustmentPlanResult:
    risk_objective: float
    adjusted_grid: np.ndarray
    upward: np.ndarray
    downward: np.ndarray
    mean_emergency: np.ndarray
    mean_soc: np.ndarray
    scenario_incremental_costs: np.ndarray
    max_balance_residual: float
    max_state_residual: float
    solver_message: str


def _as_vector(name: str, values: np.ndarray | list[float], length: int | None = None) -> np.ndarray:
    vector = np.asarray(values, dtype=float).reshape(-1)
    if length is not None and len(vector) != length:
        raise ValueError(f"{name}长度应为{length}，实际{len(vector)}")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name}含非有限值")
    return vector


def _solve(c: np.ndarray, a_eq: csr_matrix, b_eq: np.ndarray, bounds: list[tuple[float | None, float | None]],
           a_ub: csr_matrix | None = None, b_ub: np.ndarray | None = None) -> OptimizeResult:
    result = linprog(c, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq,
                     bounds=bounds, method="highs", options={"dual_feasibility_tolerance": FEAS_TOL,
                                                               "primal_feasibility_tolerance": FEAS_TOL})
    if not result.success:
        raise RuntimeError(f"HiGHS求解失败 status={result.status}: {result.message}")
    return result


def solve_deterministic(
    price: np.ndarray,
    load: np.ndarray,
    pv: np.ndarray,
    initial_soc: float,
    terminal_bounds: tuple[float, float],
    fixed_grid: np.ndarray | None = None,
    allow_emergency: bool = False,
    emergency_multiplier: float = 5.0,
    lexicographic: bool = True,
    eta_charge: float = ETA_C,
    eta_discharge: float = ETA_D,
) -> DispatchResult:
    """求解一个已知轨迹；fixed_grid用于计划确定后的实际结算。"""
    price = _as_vector("price", price)
    horizon = len(price)
    load = _as_vector("load", load, horizon)
    pv = _as_vector("pv", pv, horizon)
    if np.min(price) < 0 or np.min(load) < 0 or np.min(pv) < 0:
        raise ValueError("价格、负载和光伏必须非负")
    if not (0 < eta_charge <= 1 and 0 < eta_discharge <= 1):
        raise ValueError("充放电效率必须位于(0,1]")
    if not SOC_MIN <= initial_soc <= SOC_MAX:
        raise ValueError("初始储电量越界")
    lo, hi = terminal_bounds
    if lo > hi or lo < SOC_MIN or hi > SOC_MAX:
        raise ValueError("末端储电量区间非法")

    # 每组长度T：grid, emergency, charge, discharge, pv_used, pv_spill, grid_spill；最后soc长度T+1。
    offsets = {name: i * horizon for i, name in enumerate(
               ["grid", "emergency", "charge", "discharge", "pv_used", "pv_spill", "grid_spill"])}
    soc0 = 7 * horizon
    nvar = soc0 + horizon + 1
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    b_eq = np.zeros(3 * horizon)
    for t in range(horizon):
        # grid + emergency + discharge + pv_used - charge - grid_spill = load
        for name, coefficient in (("grid", 1), ("emergency", 1), ("discharge", 1),
                                  ("pv_used", 1), ("charge", -1), ("grid_spill", -1)):
            rows.append(t); cols.append(offsets[name] + t); data.append(coefficient)
        b_eq[t] = load[t]
        # pv_used + pv_spill = pv
        rows += [horizon + t, horizon + t]
        cols += [offsets["pv_used"] + t, offsets["pv_spill"] + t]
        data += [1, 1]
        b_eq[horizon + t] = pv[t]
        # soc[t+1] - soc[t] - eta_c*charge + discharge/eta_d = 0
        row = 2 * horizon + t
        rows += [row, row, row, row]
        cols += [soc0 + t + 1, soc0 + t, offsets["charge"] + t, offsets["discharge"] + t]
        data += [1, -1, -eta_charge, 1 / eta_discharge]
    a_eq = coo_matrix((data, (rows, cols)), shape=(3 * horizon, nvar)).tocsr()

    bounds: list[tuple[float | None, float | None]] = [(0, None)] * nvar
    if fixed_grid is not None:
        fixed_grid = _as_vector("fixed_grid", fixed_grid, horizon)
        if np.min(fixed_grid) < 0:
            raise ValueError("计划购电量必须非负")
        for t, value in enumerate(fixed_grid):
            bounds[offsets["grid"] + t] = (value, value)
    for t in range(horizon):
        bounds[offsets["emergency"] + t] = (0, load[t]) if allow_emergency else (0, 0)
        bounds[offsets["charge"] + t] = (0, FLOW_MAX)
        bounds[offsets["discharge"] + t] = (0, FLOW_MAX)
        bounds[offsets["pv_used"] + t] = (0, pv[t])
        bounds[offsets["pv_spill"] + t] = (0, pv[t])
    for t in range(horizon + 1):
        bounds[soc0 + t] = (SOC_MIN, SOC_MAX)
    bounds[soc0] = (initial_soc, initial_soc)
    bounds[soc0 + horizon] = (lo, hi)

    primary = np.zeros(nvar)
    primary[offsets["grid"]:offsets["grid"] + horizon] = price
    primary[offsets["emergency"]:offsets["emergency"] + horizon] = emergency_multiplier * price
    first = _solve(primary, a_eq, b_eq, bounds)
    chosen = first
    if lexicographic:
        secondary = np.zeros(nvar)
        for name in ("charge", "discharge"):
            secondary[offsets[name]:offsets[name] + horizon] = 0.6
        for name in ("pv_spill", "grid_spill"):
            secondary[offsets[name]:offsets[name] + horizon] = 1.1
        tolerance = FEAS_TOL * max(1.0, abs(first.fun))
        a_ub = csr_matrix(primary.reshape(1, -1))
        chosen = _solve(secondary, a_eq, b_eq, bounds, a_ub, np.array([first.fun + tolerance]))

    x = chosen.x
    result = {name: x[start:start + horizon] for name, start in offsets.items()}
    soc = x[soc0:soc0 + horizon + 1]
    balance_residual = result["grid"] + result["emergency"] + result["discharge"] + result["pv_used"] \
        - result["charge"] - result["grid_spill"] - load
    state_residual = soc[1:] - soc[:-1] - eta_charge * result["charge"] \
        + result["discharge"] / eta_discharge
    max_balance = float(np.max(np.abs(balance_residual)))
    max_state = float(np.max(np.abs(state_residual)))
    if max(max_balance, max_state) > BALANCE_TOL:
        raise RuntimeError(f"求解后残差超限：balance={max_balance}, state={max_state}")
    return DispatchResult(
        objective=float(primary @ x), primary_objective=float(first.fun),
        grid=result["grid"], emergency=result["emergency"], charge=result["charge"],
        discharge=result["discharge"], pv_used=result["pv_used"], pv_spill=result["pv_spill"],
        grid_spill=result["grid_spill"], soc=soc, max_balance_residual=max_balance,
        max_state_residual=max_state, solver_message=chosen.message,
    )


def no_storage_baseline(price: np.ndarray, load: np.ndarray, pv: np.ndarray) -> dict[str, float]:
    net = np.maximum(np.asarray(load) - np.asarray(pv), 0.0)
    pv_spill = np.maximum(np.asarray(pv) - np.asarray(load), 0.0)
    return {
        "grid_kwh": float(net.sum()),
        "pv_spill_kwh": float(pv_spill.sum()),
        "cost_cny": float(np.asarray(price) @ net),
    }


def solve_scenario_plan(
    price_scenarios: np.ndarray,
    load_scenarios: np.ndarray,
    pv_scenarios: np.ndarray,
    initial_soc: float,
    terminal_bounds: tuple[float, float],
    risk_weight: float = 0.25,
    cvar_alpha: float = 0.9,
    emergency_multiplier: float = 5.0,
    lexicographic: bool = True,
) -> ScenarioPlanResult:
    """两阶段场景LP：计划购电跨场景一致，运行变量按场景补救。"""
    prices = np.asarray(price_scenarios, dtype=float)
    loads = np.asarray(load_scenarios, dtype=float)
    pvs = np.asarray(pv_scenarios, dtype=float)
    if loads.ndim != 2 or pvs.shape != loads.shape:
        raise ValueError("load_scenarios和pv_scenarios必须为相同的二维矩阵")
    scenarios, horizon = loads.shape
    if prices.ndim == 1:
        prices = np.repeat(prices.reshape(1, -1), scenarios, axis=0)
    if prices.shape != loads.shape:
        raise ValueError("price_scenarios必须为(T,)或(N,T)")
    if scenarios < 1 or horizon < 1:
        raise ValueError("场景数和时域必须为正")
    if not (0 <= risk_weight <= 1) or not (0 < cvar_alpha < 1):
        raise ValueError("风险权重或CVaR置信度非法")
    if np.min(prices) < 0 or np.min(loads) < 0 or np.min(pvs) < 0:
        raise ValueError("场景价格、负载和光伏必须非负")
    lo, hi = terminal_bounds
    if not (SOC_MIN <= initial_soc <= SOC_MAX and SOC_MIN <= lo <= hi <= SOC_MAX):
        raise ValueError("初始或末端储电量区间非法")

    block = 7 * horizon + 1
    scenario_start = horizon
    risk_start = scenario_start + scenarios * block
    use_cvar = risk_weight > 0
    tau_index = risk_start if use_cvar else None
    z_start = risk_start + 1 if use_cvar else None
    nvar = risk_start + (1 + scenarios if use_cvar else 0)

    def offset(w: int, group: int) -> int:
        # group: 0 emg, 1 charge, 2 discharge, 3 pv_used, 4 pv_spill, 5 grid_spill, 6 soc
        return scenario_start + w * block + group * horizon

    eq_rows: list[int] = []
    eq_cols: list[int] = []
    eq_data: list[float] = []
    b_eq = np.zeros(scenarios * 3 * horizon)
    for w in range(scenarios):
        row_base = w * 3 * horizon
        for t in range(horizon):
            row = row_base + t
            for col, coefficient in (
                (t, 1), (offset(w, 0) + t, 1), (offset(w, 2) + t, 1),
                (offset(w, 3) + t, 1), (offset(w, 1) + t, -1), (offset(w, 5) + t, -1),
            ):
                eq_rows.append(row); eq_cols.append(col); eq_data.append(coefficient)
            b_eq[row] = loads[w, t]
            row = row_base + horizon + t
            eq_rows += [row, row]
            eq_cols += [offset(w, 3) + t, offset(w, 4) + t]
            eq_data += [1, 1]
            b_eq[row] = pvs[w, t]
            row = row_base + 2 * horizon + t
            eq_rows += [row, row, row, row]
            eq_cols += [offset(w, 6) + t + 1, offset(w, 6) + t,
                        offset(w, 1) + t, offset(w, 2) + t]
            eq_data += [1, -1, -ETA_C, 1 / ETA_D]
    a_eq = coo_matrix(
        (eq_data, (eq_rows, eq_cols)), shape=(scenarios * 3 * horizon, nvar)
    ).tocsr()

    bounds: list[tuple[float | None, float | None]] = [(0, None)] * nvar
    for w in range(scenarios):
        for t in range(horizon):
            bounds[offset(w, 0) + t] = (0, loads[w, t])
            bounds[offset(w, 1) + t] = (0, FLOW_MAX)
            bounds[offset(w, 2) + t] = (0, FLOW_MAX)
            bounds[offset(w, 3) + t] = (0, pvs[w, t])
            bounds[offset(w, 4) + t] = (0, pvs[w, t])
        for t in range(horizon + 1):
            bounds[offset(w, 6) + t] = (SOC_MIN, SOC_MAX)
        bounds[offset(w, 6)] = (initial_soc, initial_soc)
        bounds[offset(w, 6) + horizon] = (lo, hi)
    if use_cvar:
        bounds[tau_index] = (None, None)
        for w in range(scenarios):
            bounds[z_start + w] = (0, None)

    # 计划价在场景中也可不同；计划部分使用各场景价格均值。
    mean_price = prices.mean(axis=0)
    primary = np.zeros(nvar)
    primary[:horizon] = (1 - risk_weight) * mean_price
    expected_factor = (1 - risk_weight) / scenarios
    for w in range(scenarios):
        primary[offset(w, 0):offset(w, 0) + horizon] = expected_factor * emergency_multiplier * prices[w]

    a_ub = None
    b_ub = None
    if use_cvar:
        primary[tau_index] = risk_weight
        primary[z_start:z_start + scenarios] = risk_weight / ((1 - cvar_alpha) * scenarios)
        ub_rows: list[int] = []
        ub_cols: list[int] = []
        ub_data: list[float] = []
        for w in range(scenarios):
            for t in range(horizon):
                ub_rows.append(w); ub_cols.append(t); ub_data.append(prices[w, t])
                ub_rows.append(w); ub_cols.append(offset(w, 0) + t)
                ub_data.append(emergency_multiplier * prices[w, t])
            ub_rows += [w, w]
            ub_cols += [tau_index, z_start + w]
            ub_data += [-1, -1]
        a_ub = coo_matrix((ub_data, (ub_rows, ub_cols)), shape=(scenarios, nvar)).tocsr()
        b_ub = np.zeros(scenarios)

    first = _solve(primary, a_eq, b_eq, bounds, a_ub, b_ub)
    chosen = first
    if lexicographic:
        secondary = np.zeros(nvar)
        for w in range(scenarios):
            for group in (1, 2):
                secondary[offset(w, group):offset(w, group) + horizon] = 0.6 / scenarios
            for group in (4, 5):
                secondary[offset(w, group):offset(w, group) + horizon] = 1.1 / scenarios
        tolerance = FEAS_TOL * max(1.0, abs(first.fun))
        cost_row = csr_matrix(primary.reshape(1, -1))
        a2 = cost_row if a_ub is None else vstack([a_ub, cost_row], format="csr")
        b2 = np.array([first.fun + tolerance]) if b_ub is None else np.r_[b_ub, first.fun + tolerance]
        chosen = _solve(secondary, a_eq, b_eq, bounds, a2, b2)

    x = chosen.x
    plan = x[:horizon]
    emg = np.vstack([x[offset(w, 0):offset(w, 0) + horizon] for w in range(scenarios)])
    charge = np.vstack([x[offset(w, 1):offset(w, 1) + horizon] for w in range(scenarios)])
    discharge = np.vstack([x[offset(w, 2):offset(w, 2) + horizon] for w in range(scenarios)])
    pv_used = np.vstack([x[offset(w, 3):offset(w, 3) + horizon] for w in range(scenarios)])
    pv_spill = np.vstack([x[offset(w, 4):offset(w, 4) + horizon] for w in range(scenarios)])
    grid_spill = np.vstack([x[offset(w, 5):offset(w, 5) + horizon] for w in range(scenarios)])
    soc = np.vstack([x[offset(w, 6):offset(w, 6) + horizon + 1] for w in range(scenarios)])
    balance = plan[None, :] + emg + discharge + pv_used - charge - grid_spill - loads
    state = soc[:, 1:] - soc[:, :-1] - ETA_C * charge + discharge / ETA_D
    scenario_costs = np.sum(prices * plan[None, :], axis=1) + np.sum(
        emergency_multiplier * prices * emg, axis=1
    )
    if use_cvar:
        var_cost = float(x[tau_index])
        cvar_cost = float(x[tau_index] + np.maximum(scenario_costs - x[tau_index], 0).mean() / (1 - cvar_alpha))
    else:
        var_cost = cvar_cost = None
    max_balance = float(np.max(np.abs(balance)))
    max_state = float(np.max(np.abs(state)))
    if max(max_balance, max_state) > BALANCE_TOL:
        raise RuntimeError(f"场景求解后残差超限：balance={max_balance}, state={max_state}")
    return ScenarioPlanResult(
        risk_objective=float(first.fun), plan_grid=plan, mean_emergency=emg.mean(axis=0),
        mean_charge=charge.mean(axis=0), mean_discharge=discharge.mean(axis=0),
        mean_pv_spill=pv_spill.mean(axis=0), mean_grid_spill=grid_spill.mean(axis=0),
        mean_soc=soc.mean(axis=0), scenario_costs=scenario_costs,
        var_cost=var_cost, cvar_cost=cvar_cost, max_balance_residual=max_balance,
        max_state_residual=max_state, solver_message=chosen.message,
    )


def solve_adjustment_plan(
    original_plan: np.ndarray,
    price_scenarios: np.ndarray,
    load_scenarios: np.ndarray,
    pv_scenarios: np.ndarray,
    initial_soc: float,
    terminal_bounds: tuple[float, float],
    risk_weight: float = 0.25,
    cvar_alpha: float = 0.9,
    upward_multiplier: float = 1.5,
    downward_penalty_multiplier: float = 0.5,
    emergency_multiplier: float = 5.0,
) -> AdjustmentPlanResult:
    """对未执行时段求调整购电量；下调部分仅支付50%违约费。

    原计划费用在日初记账。若取消downward，原全价购电费减少一份，
    同时支付downward_penalty_multiplier倍的违约费，因此下调相对
    原计划的净费用系数为downward_penalty_multiplier - 1。
    """
    plan = _as_vector("original_plan", original_plan)
    horizon = len(plan)
    loads = np.asarray(load_scenarios, dtype=float)
    pvs = np.asarray(pv_scenarios, dtype=float)
    prices = np.asarray(price_scenarios, dtype=float)
    if loads.ndim != 2 or loads.shape[1] != horizon or pvs.shape != loads.shape:
        raise ValueError("调整场景的源荷维度非法")
    scenarios = loads.shape[0]
    if prices.ndim == 1:
        prices = np.repeat(prices.reshape(1, -1), scenarios, axis=0)
    if prices.shape != loads.shape or np.min(prices) < 0 or np.min(loads) < 0 or np.min(pvs) < 0:
        raise ValueError("调整场景的价格或数值非法")
    lo, hi = terminal_bounds
    if not (SOC_MIN <= initial_soc <= SOC_MAX and SOC_MIN <= lo <= hi <= SOC_MAX):
        raise ValueError("调整阶段储能边界非法")
    if not (0 <= risk_weight <= 1 and 0 < cvar_alpha < 1):
        raise ValueError("调整阶段风险参数非法")
    if not 0 <= downward_penalty_multiplier <= 1:
        raise ValueError("下调违约费比例必须位于[0,1]")

    # common: adjusted, upward, downward；scenario block同场景计划的7T+1。
    common = 3 * horizon
    block = 7 * horizon + 1
    risk_start = common + scenarios * block
    use_cvar = risk_weight > 0
    tau = risk_start if use_cvar else None
    z0 = risk_start + 1 if use_cvar else None
    nvar = risk_start + (1 + scenarios if use_cvar else 0)

    def off(w: int, group: int) -> int:
        return common + w * block + group * horizon

    eq_rows: list[int] = []
    eq_cols: list[int] = []
    eq_data: list[float] = []
    b_eq = np.zeros(horizon + scenarios * 3 * horizon)
    # adjusted - upward + downward = original plan
    for t in range(horizon):
        eq_rows += [t, t, t]
        eq_cols += [t, horizon + t, 2 * horizon + t]
        eq_data += [1, -1, 1]
        b_eq[t] = plan[t]
    for w in range(scenarios):
        base_row = horizon + w * 3 * horizon
        for t in range(horizon):
            row = base_row + t
            for col, coefficient in (
                (t, 1), (off(w, 0) + t, 1), (off(w, 2) + t, 1),
                (off(w, 3) + t, 1), (off(w, 1) + t, -1), (off(w, 5) + t, -1),
            ):
                eq_rows.append(row); eq_cols.append(col); eq_data.append(coefficient)
            b_eq[row] = loads[w, t]
            row = base_row + horizon + t
            eq_rows += [row, row]
            eq_cols += [off(w, 3) + t, off(w, 4) + t]
            eq_data += [1, 1]
            b_eq[row] = pvs[w, t]
            row = base_row + 2 * horizon + t
            eq_rows += [row, row, row, row]
            eq_cols += [off(w, 6) + t + 1, off(w, 6) + t, off(w, 1) + t, off(w, 2) + t]
            eq_data += [1, -1, -ETA_C, 1 / ETA_D]
    a_eq = coo_matrix((eq_data, (eq_rows, eq_cols)), shape=(len(b_eq), nvar)).tocsr()

    bounds: list[tuple[float | None, float | None]] = [(0, None)] * nvar
    for w in range(scenarios):
        for t in range(horizon):
            bounds[off(w, 0) + t] = (0, loads[w, t])
            bounds[off(w, 1) + t] = (0, FLOW_MAX)
            bounds[off(w, 2) + t] = (0, FLOW_MAX)
            bounds[off(w, 3) + t] = (0, pvs[w, t])
            bounds[off(w, 4) + t] = (0, pvs[w, t])
        for t in range(horizon + 1):
            bounds[off(w, 6) + t] = (SOC_MIN, SOC_MAX)
        bounds[off(w, 6)] = (initial_soc, initial_soc)
        bounds[off(w, 6) + horizon] = (lo, hi)
    if use_cvar:
        bounds[tau] = (None, None)

    mean_price = prices.mean(axis=0)
    downward_net_multiplier = downward_penalty_multiplier - 1.0
    primary = np.zeros(nvar)
    primary[horizon:2 * horizon] = (1 - risk_weight) * upward_multiplier * mean_price
    primary[2 * horizon:3 * horizon] = (1 - risk_weight) * downward_net_multiplier * mean_price
    expected_factor = (1 - risk_weight) / scenarios
    for w in range(scenarios):
        primary[off(w, 0):off(w, 0) + horizon] = expected_factor * emergency_multiplier * prices[w]

    a_ub = None
    b_ub = None
    if use_cvar:
        primary[tau] = risk_weight
        primary[z0:z0 + scenarios] = risk_weight / ((1 - cvar_alpha) * scenarios)
        rows: list[int] = []
        cols: list[int] = []
        values: list[float] = []
        for w in range(scenarios):
            for t in range(horizon):
                rows += [w, w, w]
                cols += [horizon + t, 2 * horizon + t, off(w, 0) + t]
                values += [upward_multiplier * prices[w, t], downward_net_multiplier * prices[w, t],
                           emergency_multiplier * prices[w, t]]
            rows += [w, w]
            cols += [tau, z0 + w]
            values += [-1, -1]
        a_ub = coo_matrix((values, (rows, cols)), shape=(scenarios, nvar)).tocsr()
        b_ub = np.zeros(scenarios)
    result = _solve(primary, a_eq, b_eq, bounds, a_ub, b_ub)
    x = result.x
    adjusted, upward, downward = x[:horizon], x[horizon:2 * horizon], x[2 * horizon:3 * horizon]
    emg = np.vstack([x[off(w, 0):off(w, 0) + horizon] for w in range(scenarios)])
    charge = np.vstack([x[off(w, 1):off(w, 1) + horizon] for w in range(scenarios)])
    discharge = np.vstack([x[off(w, 2):off(w, 2) + horizon] for w in range(scenarios)])
    pv_used = np.vstack([x[off(w, 3):off(w, 3) + horizon] for w in range(scenarios)])
    grid_spill = np.vstack([x[off(w, 5):off(w, 5) + horizon] for w in range(scenarios)])
    soc = np.vstack([x[off(w, 6):off(w, 6) + horizon + 1] for w in range(scenarios)])
    balance = adjusted[None, :] + emg + discharge + pv_used - charge - grid_spill - loads
    state = soc[:, 1:] - soc[:, :-1] - ETA_C * charge + discharge / ETA_D
    costs = np.sum(prices * (upward_multiplier * upward + downward_net_multiplier * downward)[None, :], axis=1) \
        + np.sum(emergency_multiplier * prices * emg, axis=1)
    max_balance = float(np.max(np.abs(balance)))
    max_state = float(np.max(np.abs(state)))
    if max(max_balance, max_state) > BALANCE_TOL:
        raise RuntimeError(f"调整LP残差超限：balance={max_balance}, state={max_state}")
    return AdjustmentPlanResult(
        risk_objective=float(result.fun), adjusted_grid=adjusted, upward=upward, downward=downward,
        mean_emergency=emg.mean(axis=0), mean_soc=soc.mean(axis=0),
        scenario_incremental_costs=costs, max_balance_residual=max_balance,
        max_state_residual=max_state, solver_message=result.message,
    )
