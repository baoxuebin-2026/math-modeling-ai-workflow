"""Generate the confirmed framework and Q1 evidence figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.plot_utils import (
    COLORS, hour_axis, legend_above, load_json, polish_axes, savefig, setup_plot, time_hours,
)


OUT = ROOT / "figures/q1"


def plot_framework() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    nodes = [
        (0.55, 3.75, 2.35, 1.15, "历史数据\n与已发布预测", COLORS["blue_light"]),
        (3.82, 3.75, 2.35, 1.15, "因果点预测\n与残差场景", COLORS["green_light"]),
        (7.10, 3.75, 2.35, 1.15, "48 h统一计划\n（仅执行首日）", COLORS["orange_light"]),
        (2.15, 1.15, 2.55, 1.15, "在线调度\nSOC状态传递", "#EEF0F2"),
        (5.95, 1.15, 2.55, 1.15, "结算与证据\n成本、风险、可行性", "#EEF0F2"),
    ]
    for x, y, w, h, label, color in nodes:
        box = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.08",
            facecolor=color, edgecolor=COLORS["primary"], linewidth=1.0,
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color="#27323A")
    arrows = [
        ((2.92, 4.33), (3.78, 4.33)), ((6.18, 4.33), (7.06, 4.33)),
        ((8.25, 3.72), (4.15, 2.34)), ((4.72, 1.72), (5.91, 1.72)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={
            "arrowstyle": "-|>", "color": COLORS["gray"], "lw": 1.2,
            "connectionstyle": "arc3,rad=0.0",
        })
    ax.text(5.0, 5.55, "决策仅使用当前时点已知信息",
            ha="center", va="center", color=COLORS["primary"], weight="bold", fontsize=10)
    ax.text(5.0, 0.45, "Q1：确定性基准   |   Q2–Q4：滚动预测与计划修正",
            ha="center", va="center", color=COLORS["gray"], fontsize=8.5)
    savefig(fig, OUT / "q1_fig00_model_framework.png")


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

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=True,
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
    ax2.text(23.75, 10800, "上限", ha="right", va="bottom", fontsize=7, color=COLORS["gray"])
    ax2.text(23.75, 1375, "下限", ha="right", va="bottom", fontsize=7, color=COLORS["gray"])
    fig.subplots_adjust(hspace=0.18)
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

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(6.8, 3.55), sharex=True,
        gridspec_kw={"height_ratios": [1.55, 0.78]},
    )
    cost_cmap = LinearSegmentedColormap.from_list(
        "cost_tiles", ["#F4F7F8", COLORS["blue_light"], COLORS["primary"]],
    )
    image = ax1.imshow(matrix, aspect="auto", cmap=cost_cmap, vmin=0,
                       vmax=float(matrix.max()) * 1.05)
    ax1.set_yticks([0, 1], ["无储能", "优化调度"])
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            color = "white" if matrix[row, col] > 0.64 * matrix.max() else "#27323A"
            ax1.text(col, row, f"{matrix[row, col]:.1f}", ha="center", va="center",
                     color=color, fontsize=8, weight="bold")
    cbar = fig.colorbar(image, ax=ax1, fraction=0.025, pad=0.025)
    cbar.set_label("费用 / 千元", fontsize=8)
    cbar.outline.set_linewidth(0.5)

    limit = max(float(np.max(np.abs(delta))), 1e-6)
    saving_cmap = LinearSegmentedColormap.from_list(
        "saving_tiles", [COLORS["orange"], "#FAFAFA", COLORS["green"]],
    )
    ax2.imshow(delta[np.newaxis, :], aspect="auto", cmap=saving_cmap,
               norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit))
    ax2.set_yticks([0], ["节省费用"])
    for col, value in enumerate(delta):
        ax2.text(col, 0, f"{value:+.1f}", ha="center", va="center",
                 color="#27323A", fontsize=8, weight="bold")
    ax2.set_xticks(np.arange(6), labels)
    ax2.set_xlabel("4 h时段")
    for ax in (ax1, ax2):
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks(np.arange(-0.5, 6, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, ax.get_images()[0].get_array().shape[0], 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=2)
        ax.tick_params(which="minor", bottom=False, left=False)
    saving = 100 * result["outputs"]["cost_saving_rate"]
    ax2.text(0.99, -0.46, f"总节省率：{saving:.2f}%", transform=ax2.transAxes,
             ha="right", va="bottom", color=COLORS["green"], weight="bold")
    fig.subplots_adjust(hspace=0.16)
    savefig(fig, OUT / "q1_fig02_cost_comparison.png")


def main() -> None:
    setup_plot()
    result = load_json(ROOT / "docs/results/q1_results.json")
    data = pd.read_csv(ROOT / "data/processed/q1_timeseries.csv")
    plot_framework()
    plot_dispatch(result, data)
    plot_cost_by_block(result, data)
    print("generated 3 Q1/overview figures")


if __name__ == "__main__":
    main()
