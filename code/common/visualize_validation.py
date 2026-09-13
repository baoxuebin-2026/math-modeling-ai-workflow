"""Generate the three confirmed CP-06 validation figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.plot_utils import COLORS, legend_above, load_json, polish_axes, savefig, setup_plot


OUT = ROOT / "figures/validation"


def plot_calibration(results: dict) -> None:
    convergence = pd.DataFrame(results["v3_scenario_convergence"]).sort_values("scenario_count")
    risk = pd.DataFrame(results["v4_risk_weight_grid"])
    risk = risk[(risk["terminal_half_width_kwh"] == 600) & (risk["scenario_count"] == 20)].sort_values("risk_weight")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.8), constrained_layout=True)
    n_ref_cost = convergence.loc[convergence["scenario_count"] == 60, "mean_daily_cost_cny"].iloc[0]
    n_ref_emg = convergence.loc[convergence["scenario_count"] == 60, "total_emergency_kwh"].iloc[0]
    ax1.plot(convergence["scenario_count"], 100 * convergence["mean_daily_cost_cny"] / n_ref_cost,
             marker="o", color=COLORS["primary"], label="平均费用指数")
    ax1.plot(convergence["scenario_count"], 100 * convergence["total_emergency_kwh"] / n_ref_emg,
             marker="s", color=COLORS["orange"], label="紧急购电指数")
    ax1.axvline(40, color=COLORS["green"], ls="--", lw=0.9)
    ax1.set_xlabel("场景数量")
    ax1.set_ylabel("指数 / %（N=60时为100）")
    ax1.set_xticks(convergence["scenario_count"])
    polish_axes(ax1)
    ax1.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=8.5)

    base_cost = risk.loc[risk["risk_weight"] == 0, "mean_daily_cost_cny"].iloc[0]
    base_emg = risk.loc[risk["risk_weight"] == 0, "total_emergency_kwh"].iloc[0]
    ax2.plot(risk["risk_weight"], 100 * risk["mean_daily_cost_cny"] / base_cost,
             marker="o", color=COLORS["primary"], label="平均费用指数")
    ax2.plot(risk["risk_weight"], 100 * risk["total_emergency_kwh"] / base_emg,
             marker="s", color=COLORS["orange"], label="紧急购电指数")
    ax2.set_xlabel("CVaR权重")
    ax2.set_ylabel("指数 / %（权重=0时为100）")
    ax2.set_xticks(risk["risk_weight"])
    polish_axes(ax2)
    ax2.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=8.5)
    savefig(fig, OUT / "validation_fig01_calibration.png")


def plot_physical_sensitivity(results: dict) -> None:
    terminal = pd.DataFrame(results["v5_terminal_sensitivity"])
    terminal = terminal.groupby("terminal_half_width_kwh", as_index=False).agg(
        cost=("total_cost_cny", "mean"), emergency=("emergency_kwh", "sum")
    )
    eta = pd.DataFrame(results["v6_efficiency_sensitivity"]["q1_reoptimized"])
    labels = ["0.85/0.85", "0.90/0.90", "往返效率=0.90", "0.95/0.95"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.8, 4.3))
    ref_cost = terminal.loc[terminal["terminal_half_width_kwh"] == 600, "cost"].iloc[0]
    ref_emg = terminal.loc[terminal["terminal_half_width_kwh"] == 600, "emergency"].iloc[0]
    ax1.plot(terminal["terminal_half_width_kwh"], 100 * (terminal["cost"] / ref_cost - 1),
             marker="o", color=COLORS["primary"], label="平均费用指数")
    ax1.plot(terminal["terminal_half_width_kwh"], 100 * (terminal["emergency"] / ref_emg - 1),
             marker="s", color=COLORS["orange"], label="紧急购电指数")
    ax1.set_xlabel("末端带宽 / kWh")
    ax1.set_ylabel("相对600 kWh方案的变化 / %")
    ax1.set_xticks(terminal["terminal_half_width_kwh"])
    ax1.set_ylim(-0.06, 0.04)
    ax1.axhline(0, color="#9AA1A8", lw=0.7)
    polish_axes(ax1)
    legend_above(ax1, ncol=2)

    x = np.arange(len(eta))
    costs = eta["total_cost_cny"].to_numpy() / 1000
    ax2.plot(x, costs, color=COLORS["primary"], marker="o", zorder=2)
    ax2.scatter(x, costs, s=55,
                color=[COLORS["gray"], COLORS["primary"], COLORS["green"], COLORS["orange"]],
                edgecolor="white", linewidth=0.7, zorder=3)
    ax2.set_xticks(x, labels, rotation=18, ha="right")
    ax2.set_xlabel("充/放电效率")
    ax2.set_ylabel("Q1优化费用 / 千元")
    polish_axes(ax2)
    offsets = [(0, 8), (0, 8), (0, 8), (0, 8)]
    for xi, cost, saving, offset in zip(x, costs, 100 * eta["saving_rate"], offsets):
        ax2.annotate(f"节省{saving:.1f}%", (xi, cost), xytext=offset,
                     textcoords="offset points", ha="center", va="bottom", fontsize=8)
    span = float(costs.max() - costs.min())
    ax2.set_ylim(float(costs.min()) - 0.18 * span, float(costs.max()) + 0.26 * span)
    fig.subplots_adjust(wspace=0.40)
    savefig(fig, OUT / "validation_fig02_physical_sensitivity.png")


def plot_update_ablation(results: dict) -> None:
    source = results["v8_update_ablation"]["seasonal_risk_days"]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.2), sharey=False)
    for ax, problem in zip(axes, ("q3", "q4")):
        frame = pd.DataFrame(source[problem])
        grouped = frame.groupby("updates_used", as_index=False).agg(
            emergency=("emergency_kwh", "sum"), cost=("total_cost_cny", "mean")
        )
        ax.plot(grouped["updates_used"], grouped["emergency"] / 1000, marker="o",
                color=COLORS["primary"])
        ax.fill_between(grouped["updates_used"], 0, grouped["emergency"] / 1000,
                        color=COLORS["blue_light"], alpha=0.8)
        ax.set_xticks(grouped["updates_used"], ["00", "+06", "+12", "+18"])
        ax.set_xlabel(f"{problem.upper()}信息更新")
        ax.set_ylabel("紧急购电量 / MWh")
        polish_axes(ax)
        reduction = 100 * (1 - grouped["emergency"].iloc[-1] / grouped["emergency"].iloc[0])
        cost_change = 100 * (grouped["cost"].iloc[-1] / grouped["cost"].iloc[0] - 1)
        ax.text(0.98, 0.97, f"紧急购电 −{reduction:.1f}%\n费用 {cost_change:+.1f}%",
                transform=ax.transAxes, ha="right", va="top", color=COLORS["green"],
                fontsize=9, weight="bold")
    fig.subplots_adjust(wspace=0.38)
    savefig(fig, OUT / "validation_fig03_update_ablation.png")


def main() -> None:
    setup_plot()
    results = load_json(ROOT / "docs/results/validation_results.json")
    plot_calibration(results)
    plot_physical_sensitivity(results)
    plot_update_ablation(results)
    print("generated 3 validation figures")


if __name__ == "__main__":
    main()
