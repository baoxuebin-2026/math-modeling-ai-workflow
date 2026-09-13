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

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.8, 5.5), sharex=True)
    ax1.plot(x, price_actual, color=COLORS["primary"], label="实际电价")
    ax1.plot(x, price_forecast, color=COLORS["orange"], ls="--", label="00:00电价预测")
    ax1.fill_between(x, price_actual, price_forecast, color=COLORS["orange_light"], alpha=0.6)
    ax1.set_ylabel("电价 /（元/kWh）")
    polish_axes(ax1)
    legend_above(ax1, ncol=2)

    ax2.plot(x, q42_plan, color=COLORS["gray"], label="Q4-2购电计划")
    ax2.plot(x, q43_plan, color=COLORS["primary"], label="Q4-3滚动计划")
    ax2.set_ylabel("购电量 / kWh")
    polish_axes(ax2)
    hour_axis(ax2)
    ax2b = ax2.twinx()
    soc_x = np.linspace(0, 24, len(q42_soc))
    ax2b.plot(soc_x, q42_soc, color=COLORS["gray"], ls=":", lw=1.1, label="Q4-2 SOC")
    ax2b.plot(soc_x, q43_soc, color=COLORS["green"], ls="--", lw=1.2, label="Q4-3 SOC")
    ax2b.set_ylabel("SOC / %")
    ax2b.set_ylim(5, 95)
    ax2b.spines["top"].set_visible(False)
    ax2b.spines["right"].set_color("#9AA1A8")
    handles1, labels1 = ax2.get_legend_handles_labels()
    handles2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(handles1 + handles2, labels1 + labels2, loc="lower left",
               bbox_to_anchor=(0, 1.01), ncol=4, frameon=False, borderaxespad=0)
    fig.text(0.98, 0.50, day_text, ha="right", va="bottom",
             color=COLORS["gray"], fontsize=11)
    fig.subplots_adjust(hspace=0.32)
    savefig(fig, OUT / "q4_fig01_price_response.png")
    return day_text


def plot_q42_q43_comparison(result: dict) -> None:
    a, b = result["q4_2"]["totals"], result["q4_3"]["totals"]
    cost = np.array([a["total_cny"], b["total_cny"]]) / 10000
    emergency = np.array([a["emergency_kwh"], b["emergency_kwh"]]) / 1000

    fig, ax = plt.subplots(figsize=(7.6, 4.5))
    ax.annotate("", xy=(cost[1], emergency[1]), xytext=(cost[0], emergency[0]),
                arrowprops={"arrowstyle": "-|>", "color": COLORS["blue_light"],
                            "lw": 8, "shrinkA": 8, "shrinkB": 8}, zorder=1)
    ax.scatter(cost[0], emergency[0], s=125, color=COLORS["gray"], edgecolor="white",
               linewidth=0.9, zorder=3)
    ax.scatter(cost[1], emergency[1], s=125, marker="D", color=COLORS["primary"],
               edgecolor="white", linewidth=0.9, zorder=3)
    ax.annotate(f"Q4-2  不修正\n{cost[0]:.1f}万元，{emergency[0]:.1f} MWh",
                (cost[0], emergency[0]), xytext=(-8, 12), textcoords="offset points",
                ha="right", va="bottom", color=COLORS["gray"], weight="bold")
    ax.annotate(f"Q4-3  滚动修正\n{cost[1]:.1f}万元，{emergency[1]:.1f} MWh",
                (cost[1], emergency[1]), xytext=(8, -12), textcoords="offset points",
                ha="left", va="top", color=COLORS["primary"], weight="bold")
    ax.set_xlabel("年总费用 / 万元（越低越优）")
    ax.set_ylabel("紧急购电量 / MWh（越低越优）")
    x_span = float(np.ptp(cost))
    y_span = float(np.ptp(emergency))
    ax.set_xlim(float(cost.min()) - 0.28 * x_span, float(cost.max()) + 0.28 * x_span)
    ax.set_ylim(max(0, float(emergency.min()) - 0.28 * y_span),
                float(emergency.max()) + 0.28 * y_span)
    polish_axes(ax)
    cost_reduction = 100 * (1 - b["total_cny"] / a["total_cny"])
    reduction = 100 * (1 - emergency[1] / emergency[0])
    ax.text(0.98, 0.08, f"费用 −{cost_reduction:.2f}%\n紧急购电 −{reduction:.2f}%",
            transform=ax.transAxes, ha="right", va="bottom", color=COLORS["green"],
            weight="bold", fontsize=12)
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
