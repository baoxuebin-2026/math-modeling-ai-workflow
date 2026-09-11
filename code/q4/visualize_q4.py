"""Generate the confirmed Q4 price-uncertainty evidence figures."""

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


OUT = ROOT / "figures/q4"


def representative_day(result: dict) -> str:
    return max(
        result["specified_days"],
        key=lambda day: float(np.sum(result["specified_days"][day]["q4_2"]["actual"]["emergency_kwh"])),
    )


def plot_price_and_response(result: dict, snapshots: dict) -> str:
    day_text = representative_day(result)
    day = result["specified_days"][day_text]
    snapshot = snapshots["dates"][day_text]
    x = time_hours()
    price_actual = np.asarray(snapshot["price_actual_cny_per_kwh"])
    price_forecast = np.asarray(snapshot["price_forecast_cny_per_kwh"])
    q42_plan = np.asarray(day["q4_2"]["plan_grid_kwh"])
    q43_plan = np.asarray(day["q4_3"]["final_active_grid_kwh"])
    q42_soc = 100 * np.asarray(day["q4_2"]["actual"]["soc_kwh"]) / 12000
    q43_soc = 100 * np.asarray(day["q4_3"]["actual"]["soc"]) / 12000

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 4.9), sharex=True)
    ax1.plot(x, price_actual, color=COLORS["primary"], label="Realized price")
    ax1.plot(x, price_forecast, color=COLORS["orange"], ls="--", label="00:00 forecast")
    ax1.fill_between(x, price_actual, price_forecast, color=COLORS["orange_light"], alpha=0.6)
    ax1.set_ylabel("Price / CNY per kWh")
    polish_axes(ax1)
    legend_above(ax1, ncol=2)

    ax2.plot(x, q42_plan, color=COLORS["gray"], label="Q4-2 grid plan")
    ax2.plot(x, q43_plan, color=COLORS["primary"], label="Q4-3 active plan")
    ax2.set_ylabel("Grid energy / kWh")
    polish_axes(ax2)
    hour_axis(ax2)
    ax2b = ax2.twinx()
    soc_x = np.linspace(0, 24, len(q42_soc))
    ax2b.plot(soc_x, q42_soc, color=COLORS["gray"], ls=":", lw=1.1, label="Q4-2 SOC")
    ax2b.plot(soc_x, q43_soc, color=COLORS["green"], ls="--", lw=1.2, label="Q4-3 SOC")
    ax2b.set_ylabel("SOC / % of capacity")
    ax2b.set_ylim(5, 95)
    ax2b.spines["top"].set_visible(False)
    ax2b.spines["right"].set_color("#9AA1A8")
    handles1, labels1 = ax2.get_legend_handles_labels()
    handles2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(handles1 + handles2, labels1 + labels2, loc="lower left",
               bbox_to_anchor=(0, 1.01), ncol=4, frameon=False, borderaxespad=0)
    ax2.text(0.995, 0.95, day_text, transform=ax2.transAxes, ha="right", va="top",
             color=COLORS["gray"], fontsize=8)
    fig.subplots_adjust(hspace=0.24)
    savefig(fig, OUT / "q4_fig01_price_response.png")
    return day_text


def plot_q42_q43_comparison(result: dict) -> None:
    a, b = result["q4_2"]["totals"], result["q4_3"]["totals"]
    labels = ["Q4-2: no update", "Q4-3: rolling updates"]
    plan = np.array([a["plan_cny"], b["plan_cny"]]) / 10000
    adjustment = np.array([0, b["upward_cny"] + b["downward_cny"]]) / 10000
    emergency_cost = np.array([a["emergency_cny"], b["emergency_cny"]]) / 10000
    emergency_energy = np.array([a["emergency_kwh"], b["emergency_kwh"]]) / 1000

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.8), gridspec_kw={"width_ratios": [1.25, 1]})
    x = np.arange(2)
    ax1.bar(x, plan, color=COLORS["primary"], label="Plan")
    ax1.bar(x, adjustment, bottom=plan, color=COLORS["orange"], label="Adjustment")
    ax1.bar(x, emergency_cost, bottom=plan + adjustment, color=COLORS["red"], label="Emergency")
    ax1.set_xticks(x, labels)
    ax1.set_ylabel("Annual cost / 10,000 CNY")
    polish_axes(ax1)
    legend_above(ax1, ncol=3)
    cost_reduction = 100 * (1 - b["total_cny"] / a["total_cny"])
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
    savefig(fig, OUT / "q4_fig02_q42_q43_comparison.png")


def main() -> None:
    setup_plot()
    result = load_json(ROOT / "docs/results/q4_results.json")
    snapshots = load_json(ROOT / "docs/results/forecast_snapshots.json")
    day = plot_price_and_response(result, snapshots)
    plot_q42_q43_comparison(result)
    print(f"generated 2 Q4 figures; representative day={day}")


if __name__ == "__main__":
    main()
