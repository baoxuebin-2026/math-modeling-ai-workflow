"""Generate the confirmed Q3 rolling-update evidence figures."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.common.plot_utils import (
    COLORS, hour_axis, legend_above, load_json, polish_axes, savefig, setup_plot, time_hours,
)


OUT = ROOT / "figures/q3"


def adjustment_size(day: dict) -> float:
    return float(sum(np.sum(item["upward_kwh"]) + np.sum(item["downward_kwh"])
                     for item in day["adjustments"]))


def plot_revision_trajectory(result: dict) -> str:
    day_text = max(result["specified_days"], key=lambda d: adjustment_size(result["specified_days"][d]))
    day = result["specified_days"][day_text]
    x = time_hours()
    original = np.asarray(day["original_plan_grid_kwh"])
    final = np.asarray(day["final_active_grid_kwh"])

    fig, (ax, delta_ax) = plt.subplots(
        2, 1, figsize=(8.8, 5.4), sharex=True, gridspec_kw={"height_ratios": [1.45, 0.75]},
    )
    ax.plot(x, original, color=COLORS["gray"], ls="--", label="00:00原始计划")
    palette = [COLORS["orange"], COLORS["green"], COLORS["purple"]]
    for item, color in zip(day["adjustments"], palette):
        start = int(item["start_slot"]) - 1
        values = np.asarray(item["adjusted_grid_kwh"])
        ax.plot(x[start:start + len(values)], values, color=color, alpha=0.82,
                label=f"{item['issue_hour']:02d}:00修正")
        ax.axvline(item["issue_hour"], color=color, lw=0.7, alpha=0.45)
    ax.plot(x, final, color=COLORS["primary"], lw=1.8, label="最终执行计划")
    ax.set_ylabel("计划购电量 / kWh")
    polish_axes(ax)
    legend_above(ax, ncol=5)
    ax.text(0.82, 0.98, day_text, transform=ax.transAxes, ha="right", va="top",
            color=COLORS["gray"], fontsize=11)
    delta = final - original
    delta_ax.fill_between(x, 0, np.maximum(delta, 0), color=COLORS["green_light"],
                          edgecolor=COLORS["green"], linewidth=0.7,
                          label="净上调" if not np.any(delta < -1e-6) else "上调")
    if np.any(delta < -1e-6):
        delta_ax.fill_between(x, 0, np.minimum(delta, 0), color=COLORS["orange_light"],
                              edgecolor=COLORS["orange"], linewidth=0.7, label="下调")
    delta_ax.axhline(0, color="#9AA1A8", lw=0.7)
    delta_ax.set_ylabel("计划修正量 / kWh")
    polish_axes(delta_ax)
    hour_axis(delta_ax)
    legend_above(delta_ax, ncol=2)
    fig.subplots_adjust(hspace=0.32)
    savefig(fig, OUT / "q3_fig01_plan_revisions.png")
    return day_text


def plot_q2_q3_comparison(q2: dict, q3: dict) -> None:
    q2t, q3t = q2["totals"], q3["totals"]
    q2_values = np.array([q2t["total_cost_cny"] / 10000, q2t["emergency_kwh"] / 1000])
    q3_values = np.array([q3t["total_cny"] / 10000, q3t["emergency_kwh"] / 1000])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.8))
    panels = (
        (ax1, q2_values[0], q3_values[0], "年总费用 / 万元"),
        (ax2, q2_values[1], q3_values[1], "紧急购电量 / MWh"),
    )
    for ax, before, after, xlabel in panels:
        ax.hlines(0, min(before, after), max(before, after), color=COLORS["blue_light"],
                  linewidth=7, zorder=1)
        ax.scatter(before, 0, s=95, color=COLORS["gray"], edgecolor="white",
                   linewidth=0.8, label="Q2 日前计划", zorder=3)
        ax.scatter(after, 0, s=95, marker="D", color=COLORS["primary"], edgecolor="white",
                   linewidth=0.8, label="Q3 滚动修正", zorder=3)
        ax.annotate(f"Q2  {before:.1f}", (before, 0), xytext=(0, 14),
                    textcoords="offset points", ha="center", color=COLORS["gray"], weight="bold")
        ax.annotate(f"Q3  {after:.1f}", (after, 0), xytext=(0, -17),
                    textcoords="offset points", ha="center", color=COLORS["primary"], weight="bold")
        span = abs(before - after)
        ax.set_xlim(min(before, after) - 0.30 * span, max(before, after) + 0.30 * span)
        ax.set_ylim(-0.35, 0.35)
        ax.set_yticks([])
        ax.set_xlabel(xlabel)
        ax.grid(True, axis="x", color=COLORS["grid"], linewidth=0.65)
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    cost_reduction = 100 * (1 - q3t["total_cny"] / q2t["total_cost_cny"])
    reduction = 100 * (1 - q3_values[1] / q2_values[1])
    ax1.text(0.5, 0.92, f"−{cost_reduction:.2f}%", transform=ax1.transAxes,
             ha="center", va="top", color=COLORS["green"], weight="bold", fontsize=14)
    ax2.text(0.5, 0.92, f"−{reduction:.2f}%", transform=ax2.transAxes,
             ha="center", va="top", color=COLORS["green"], weight="bold", fontsize=14)
    handles, legend_labels = ax1.get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="upper center", bbox_to_anchor=(0.5, 1.03),
               ncol=2, frameon=False)
    fig.subplots_adjust(wspace=0.40)
    savefig(fig, OUT / "q3_fig02_q2_q3_comparison.png")


def main() -> None:
    setup_plot()
    q2 = load_json(ROOT / "docs/results/q2_results.json")
    q3 = load_json(ROOT / "docs/results/q3_results.json")
    day = plot_revision_trajectory(q3)
    plot_q2_q3_comparison(q2, q3)
    print(f"generated 2 Q3 figures; representative day={day}")


if __name__ == "__main__":
    main()
