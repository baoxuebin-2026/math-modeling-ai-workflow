"""Generate the confirmed Q2 forecast-risk evidence figures."""

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


OUT = ROOT / "figures/q2"


def representative_day(result: dict) -> str:
    return max(
        result["specified_days"],
        key=lambda day: float(np.sum(result["specified_days"][day]["actual"]["emergency_kwh"])),
    )


def plot_forecast_and_execution(result: dict, snapshots: dict) -> str:
    day = representative_day(result)
    selected = result["specified_days"][day]
    snapshot = snapshots["dates"][day]
    x = time_hours()
    forecast_net = np.asarray(snapshot["load_forecast_kwh"]) - np.asarray(snapshot["pv_forecast_kwh"])
    actual_net = np.asarray(snapshot["load_actual_kwh"]) - np.asarray(snapshot["pv_actual_kwh"])
    plan = np.asarray(selected["plan"]["grid_kwh"])
    emergency = np.asarray(selected["actual"]["emergency_kwh"])
    total_grid = plan + emergency

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 4.7), sharex=True)
    ax1.plot(x, actual_net, color=COLORS["primary"], label="Realized net demand")
    ax1.plot(x, forecast_net, color=COLORS["orange"], ls="--", label="Day-ahead forecast")
    ax1.fill_between(x, forecast_net, actual_net, color=COLORS["orange_light"], alpha=0.55)
    ax1.axhline(0, color="#9AA1A8", lw=0.7)
    ax1.set_ylabel("Net demand / kWh")
    polish_axes(ax1)
    legend_above(ax1, ncol=2)

    ax2.plot(x, plan, color=COLORS["gray"], label="Planned grid")
    ax2.plot(x, total_grid, color=COLORS["primary"], label="Grid incl. emergency")
    ax2.fill_between(x, 0, emergency, color="#F1D4D1", edgecolor=COLORS["red"],
                     linewidth=0.7, label="Emergency purchase")
    ax2.set_ylabel("Grid energy / kWh")
    polish_axes(ax2)
    hour_axis(ax2)
    legend_above(ax2, ncol=3)
    ax2.text(0.995, 0.96, day, transform=ax2.transAxes, ha="right", va="top",
             color=COLORS["gray"], fontsize=8)
    fig.subplots_adjust(hspace=0.22)
    savefig(fig, OUT / "q2_fig01_forecast_execution.png")
    return day


def plot_emergency_heatmap(detail: pd.DataFrame) -> None:
    detail = detail.copy()
    dates = pd.to_datetime(detail["date"])
    detail["month"] = dates.dt.month
    detail["hour"] = (detail["slot"] - 1) // 6
    pivot = detail.pivot_table(
        index="month", columns="hour", values="emergency_kwh", aggfunc="sum", fill_value=0,
    ).reindex(index=range(2, 13), columns=range(24), fill_value=0)
    matrix = pivot.to_numpy() / 1000

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    image = ax.imshow(matrix, aspect="auto", cmap="YlOrBr", interpolation="nearest")
    ax.set_xticks(np.arange(0, 24, 2), [f"{h:02d}" for h in range(0, 24, 2)])
    ax.set_yticks(np.arange(11), [f"{m:02d}" for m in range(2, 13)])
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Month")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(image, ax=ax, fraction=0.025, pad=0.025)
    cbar.set_label("Emergency purchase / MWh")
    cbar.outline.set_visible(False)
    savefig(fig, OUT / "q2_fig02_emergency_heatmap.png")


def main() -> None:
    setup_plot()
    result = load_json(ROOT / "docs/results/q2_results.json")
    snapshots = load_json(ROOT / "docs/results/forecast_snapshots.json")
    detail = pd.read_csv(ROOT / "data/processed/q2_full_detail.csv")
    day = plot_forecast_and_execution(result, snapshots)
    plot_emergency_heatmap(detail)
    print(f"generated 2 Q2 figures; representative day={day}")


if __name__ == "__main__":
    main()
