from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code.common.io_utils import ensure_dir, read_json, write_text


def main() -> int:
    result = read_json("docs/results/q3_results.json", {})
    out_dir = ensure_dir("figures/q3")
    fig_path = out_dir / "q3_fig01_workflow_placeholder.png"
    try:
        import matplotlib.pyplot as plt

        from code.common.plot_style import apply_plot_style

        apply_plot_style()
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.axis("off")
        ax.text(0.5, 0.5, "问题三图表占位\n确认模型与数据后替换为正式结果图", ha="center", va="center", fontsize=14)
        fig.tight_layout()
        fig.savefig(fig_path)
        plt.close(fig)
        figure_note = f"- 图表文件：`{fig_path}`"
    except ModuleNotFoundError as exc:
        figure_note = f"- 图表文件：待生成（缺少依赖 `{exc.name}`）"
    write_text(
        "docs/figures/q3_figures.md",
        f"# 问题三图表说明\n\n{figure_note}\n- 论文位置：问题三结果分析与可视化\n- 当前状态：{result.get('status', '待补充')}\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
