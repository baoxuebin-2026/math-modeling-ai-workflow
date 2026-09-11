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
        2, 1, figsize=(7.2, 4.8), sharex=True, gridspec_kw={"height_ratios": [1.45, 0.75]},
    )
    ax.plot(x, original, color=COLORS["gray"], ls="--", label="00:00 original plan")
    palette = [COLORS["orange"], COLORS["green"], COLORS["purple"]]
    for item, color in zip(day["adjustments"], palette):
        start = int(item["start_slot"]) - 1
        values = np.asarray(item["adjusted_grid_kwh"])
        ax.plot(x[start:start + len(values)], values, color=color, alpha=0.82,
                label=f"{item['issue_hour']:02d}:00 update")
        ax.axvline(item["issue_hour"], color=color, lw=0.7, alpha=0.45)
    ax.plot(x, final, color=COLORS["primary"], lw=1.8, label="Executed active plan")
    ax.set_ylabel("Planned grid energy / kWh")
    polish_axes(ax)
    legend_above(ax, ncol=5)
    ax.text(0.995, 0.98, day_text, transform=ax.transAxes, ha="right", va="top",
            color=COLORS["gray"], fontsize=8)
    delta = final - original
    delta_ax.fill_between(x, 0, np.maximum(delta, 0), color=COLORS["green_light"],
                          edgecolor=COLORS["green"], linewidth=0.7,
                          label="Net upward revision" if not np.any(delta < -1e-6) else "Upward revision")
    if np.any(delta < -1e-6):
        delta_ax.fill_between(x, 0, np.minimum(delta, 0), color=COLORS["orange_light"],
                              edgecolor=COLORS["orange"], linewidth=0.7, label="Downward revision")
    delta_ax.axhline(0, color="#9AA1A8", lw=0.7)
    delta_ax.set_ylabel("Revision / kWh")
    polish_axes(delta_ax)
    hour_axis(delta_ax)
    legend_above(delta_ax, ncol=2)
    fig.subplots_adjust(hspace=0.24)
    savefig(fig, OUT / "q3_fig01_plan_revisions.png")
    return day_text


def plot_q2_q3_comparison(q2: dict, q3: dict) -> None:
    q2t, q3t = q2["totals"], q3["totals"]
    labels = ["Q2: day-ahead", "Q3: rolling updates"]
    plan = np.array([q2t["plan_cost_cny"], q3t["plan_cny"]]) / 10000
    adjustment = np.array([0, q3t["upward_cny"] + q3t["downward_cny"]]) / 10000
    emergency_cost = np.array([q2t["emergency_cost_cny"], q3t["emergency_cny"]]) / 10000
    emergency_energy = np.array([q2t["emergency_kwh"], q3t["emergency_kwh"]]) / 1000

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.8), gridspec_kw={"width_ratios": [1.25, 1]})
    x = np.arange(2)
    ax1.bar(x, plan, color=COLORS["primary"], label="Plan")
    ax1.bar(x, adjustment, bottom=plan, color=COLORS["orange"], label="Adjustment")
    ax1.bar(x, emergency_cost, bottom=plan + adjustment, color=COLORS["red"], label="Emergency")
    ax1.set_xticks(x, labels)
    ax1.set_ylabel("Annual cost / 10,000 CNY")
    polish_axes(ax1)
    legend_above(ax1, ncol=3)
    cost_reduction = 100 * (1 - q3t["total_cny"] / q2t["total_cost_cny"])
    ax1.text(0.98, 0.97, f"Total cost: −{cost_reduction:.2f}%", transform=ax1.transAxes,
             ha="right", va="top", color=COLORS["green"], weight="bold")

    bars = ax2.bar(x, emergency_energy, color=[COLORS["gray"], COLORS["green"]], width=0.58)
    ax2.set_xticks(x, labels)
    ax2.set_ylabel("Emergency purchase / MWh")
    polish_axes(ax2)
    for bar, value in zip(bars, emergency_energy):
        ax2.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.1f}",
                 ha="center", va="bottom", fontsize=8)
    reduction = 100 * (1 - emergency_energy[1] / emergency_energy[0])
    ax2.text(0.98, 0.97, f"Reduction: {reduction:.2f}%", transform=ax2.transAxes,
             ha="right", va="top", color=COLORS["green"], weight="bold")
    fig.subplots_adjust(wspace=0.36)
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
