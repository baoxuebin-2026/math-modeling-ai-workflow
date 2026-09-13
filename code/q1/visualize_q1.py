"""Generate the confirmed framework and Q1 evidence figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.plot_utils import (
    COLORS, hour_axis, legend_above, load_json, polish_axes, savefig, setup_plot, time_hours,
)


OUT = ROOT / "figures/q1"


def plot_dispatch(result: dict, data: pd.DataFrame) -> None:
    output = result["outputs"]
    x = time_hours()
    load = data["load_kwh"].to_numpy()
    pv = data["pv_forecast_kwh"].to_numpy()
    grid = np.asarray(output["plan_grid_kwh"])
    charge = np.asarray(output["charge_kwh"])
    discharge = np.asarray(output["discharge_kwh"])
    soc = np.asarray(output["soc_kwh"])
    price = data["price_cny_per_kwh"].to_numpy()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.8, 6.0), sharex=True,
                                   gridspec_kw={"height_ratios": [1.35, 1.0]})
    ax1.plot(x, load, color=COLORS["primary"], label="负荷", zorder=4)
    ax1.plot(x, pv, color=COLORS["orange"], label="光伏出力", zorder=3)
    ax1.plot(x, grid, color=COLORS["gray"], label="计划购电", zorder=2)
    ax1.fill_between(x, 0, discharge, color=COLORS["green_light"],
                     edgecolor=COLORS["green"], linewidth=0.7, label="储能放电")
    ax1.fill_between(x, 0, -charge, color=COLORS["orange_light"],
                     edgecolor=COLORS["orange"], linewidth=0.7, label="储能充电")
    ax1.axhline(0, color="#9AA1A8", lw=0.7)
    ax1.set_ylabel("10 min电量 / kWh")
    polish_axes(ax1)
    legend_above(ax1, ncol=5)

    levels = np.unique(np.round(price, 8))
    bands = [COLORS["blue_light"], COLORS["orange_light"], "#F1D4D1"]
    for i, value in enumerate(levels):
        mask = np.isclose(price, value)
        ax2.fill_between(x, 1200, 10800, where=mask, color=bands[min(i, 2)], alpha=0.55,
                         step="mid", linewidth=0)
    ax2.plot(np.linspace(0, 24, len(soc)), soc, color=COLORS["primary"], label="储能SOC")
    ax2.axhline(1200, color=COLORS["gray"], ls="--", lw=0.8)
    ax2.axhline(10800, color=COLORS["gray"], ls="--", lw=0.8)
    ax2.set_ylim(700, 11300)
    ax2.set_ylabel("储能电量 / kWh")
    polish_axes(ax2)
    hour_axis(ax2)
    ax2.text(23.75, 10800, "上限", ha="right", va="bottom", fontsize=15, color=COLORS["gray"])
    ax2.text(23.75, 1375, "下限", ha="right", va="bottom", fontsize=15, color=COLORS["gray"])
    fig.subplots_adjust(hspace=0.32)
    savefig(fig, OUT / "q1_fig01_dispatch_soc.png")


def plot_cost_by_block(result: dict, data: pd.DataFrame) -> None:
    price = data["price_cny_per_kwh"].to_numpy()
    load = data["load_kwh"].to_numpy()
    pv = data["pv_forecast_kwh"].to_numpy()
    baseline_grid = np.maximum(load - pv, 0)
    optimized_grid = np.asarray(result["outputs"]["plan_grid_kwh"])
    baseline = np.array([(price[i:i + 24] * baseline_grid[i:i + 24]).sum() for i in range(0, 144, 24)])
    optimized = np.array([(price[i:i + 24] * optimized_grid[i:i + 24]).sum() for i in range(0, 144, 24)])
    labels = ["00–04", "04–08", "08–12", "12–16", "16–20", "20–24"]
    baseline_k = baseline / 1000
    optimized_k = optimized / 1000
    matrix = np.vstack((baseline_k, optimized_k))
    delta = baseline_k - optimized_k

    fig, ax1 = plt.subplots(figsize=(8.2, 4.6))
    x = np.arange(len(labels))
    width = 0.34
    bars_a = ax1.bar(x - width / 2, baseline_k, width, label="无储能",
                     color=COLORS["gray"], alpha=0.78)
    bars_b = ax1.bar(x + width / 2, optimized_k, width, label="优化调度",
                     color=COLORS["primary"])
    ax1.set_ylabel("费用 / 千元")
    ax1.set_xticks(x, labels)
    ax1.set_xlabel("4 h时段")
    ax1.set_ylim(0, max(baseline_k.max(), optimized_k.max()) * 1.22)
    polish_axes(ax1)
    legend_above(ax1, ncol=2)
    for bars in (bars_a, bars_b):
        for bar in bars:
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                     f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=14)
    ax2 = ax1.twinx()
    ax2.plot(x, delta, color=COLORS["orange"], marker="o", linewidth=1.8,
             label="节省费用", zorder=5)
    ax2.axhline(0, color="#9AA1A8", linewidth=0.7)
    ax2.set_ylabel("节省费用 / 千元", color=COLORS["orange"])
    ax2.tick_params(axis="y", colors=COLORS["orange"])
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color(COLORS["orange"])
    for xi, value in zip(x, delta):
        ax2.annotate(f"{value:+.1f}", (xi, value), xytext=(0, 7),
                     textcoords="offset points", ha="center", fontsize=14,
                     color=COLORS["orange"])
    saving = 100 * result["outputs"]["cost_saving_rate"]
    ax1.text(0.99, 0.72, f"总节省率：{saving:.2f}%", transform=ax1.transAxes,
             ha="right", va="top", color=COLORS["green"], weight="bold")
    fig.subplots_adjust(top=0.78, right=0.88)
    savefig(fig, OUT / "q1_fig02_cost_comparison.png")


def main() -> None:
    setup_plot()
    result = load_json(ROOT / "docs/results/q1_results.json")
    data = pd.read_csv(ROOT / "data/processed/q1_timeseries.csv")
    plot_dispatch(result, data)
    plot_cost_by_block(result, data)
    print("generated 3 Q1/overview figures")


if __name__ == "__main__":
    main()
