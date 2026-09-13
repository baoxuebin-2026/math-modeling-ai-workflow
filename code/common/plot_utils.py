"""Shared, restrained plotting style for paper-ready figures."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager


COLORS = {
    "primary": "#264653",
    "orange": "#E9A03A",
    "green": "#4F7F62",
    "gray": "#7C8792",
    "blue_light": "#DDEAF1",
    "orange_light": "#F7E2C3",
    "green_light": "#E5EFE8",
    "red": "#B65C55",
    "purple": "#75658A",
    "grid": "#E6E8EB",
}

FONT_PATH = Path(__file__).resolve().parents[2] / "assets/fonts/NotoSansCJKsc-Regular.otf"


def setup_plot() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"缺少绘图中文字体：{FONT_PATH}")
    font_manager.fontManager.addfont(str(FONT_PATH))
    font_name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    plt.rcParams.update({
        "font.family": font_name,
        "font.sans-serif": [font_name],
        "font.size": 10.5,
        "axes.labelsize": 10.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.fontsize": 9,
        "axes.edgecolor": "#9AA1A8",
        "axes.linewidth": 0.7,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": 300,
        "lines.linewidth": 1.5,
        "axes.unicode_minus": False,
    })


def polish_axes(ax, *, grid_axis: str = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis=grid_axis, color=COLORS["grid"], linewidth=0.65, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=3, color="#9AA1A8")


def hour_axis(ax, *, label: bool = True) -> None:
    ax.set_xlim(0, 24)
    ax.set_xticks(np.arange(0, 25, 3))
    if label:
        ax.set_xlabel("时间 / h")


def legend_above(ax, *, ncol: int = 3) -> None:
    ax.legend(
        loc="lower left", bbox_to_anchor=(0, 1.01), ncol=ncol,
        frameon=False, borderaxespad=0, handlelength=1.8, columnspacing=1.0,
    )


def savefig(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def time_hours(n: int = 144) -> np.ndarray:
    return (np.arange(n) + 0.5) / 6.0
