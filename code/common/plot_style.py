from __future__ import annotations

import platform

import matplotlib.pyplot as plt
import seaborn as sns


def apply_plot_style() -> None:
    system = platform.system()
    if system == "Windows":
        fonts = ["Microsoft YaHei", "SimHei", "KaiTi"]
    elif system == "Darwin":
        fonts = ["PingFang SC", "Arial Unicode MS"]
    else:
        fonts = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans"]

    plt.rcParams["font.sans-serif"] = fonts
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["savefig.dpi"] = 300
    sns.set_theme(style="whitegrid", palette="colorblind")
