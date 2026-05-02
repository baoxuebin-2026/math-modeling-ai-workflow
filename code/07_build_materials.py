from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.io_utils import project_path, read_json, write_text


def read_text_if_exists(path: str) -> str:
    p = project_path(path)
    return p.read_text(encoding="utf-8") if p.exists() else f"# {path}\n\n待补充。\n"


def main() -> int:
    sections = [
        ("题目信息提取", read_text_if_exists("docs/00_problem_extracted.md")),
        ("逐问任务对齐", read_text_if_exists("docs/01_task_alignment.md")),
        ("模型路线", read_text_if_exists("docs/02_model_plan.md")),
        ("数据报告", read_text_if_exists("docs/03_data_report.md")),
        ("结果汇总", read_text_if_exists("docs/04_result_summary.md")),
        ("图表计划", read_text_if_exists("docs/05_visualization_plan.md")),
        ("模型检验", read_text_if_exists("docs/06_validation_report.md")),
    ]

    chunks = [
        "# 写论文前素材包",
        "",
        "本文件由 `code/run_all.py` 汇总生成。它不是最终论文，而是论文写作前的模型、结果和图表素材底稿。",
        "",
        "## 分问代码索引",
        "",
        "| 问题 | 求解代码 | 可视化代码 | 结果文件 | 图表说明 |",
        "|---|---|---|---|---|",
        "| 问题一 | `code/q1/solve_q1.py` | `code/q1/visualize_q1.py` | `docs/results/q1_results.json` | `docs/figures/q1_figures.md` |",
        "| 问题二 | `code/q2/solve_q2.py` | `code/q2/visualize_q2.py` | `docs/results/q2_results.json` | `docs/figures/q2_figures.md` |",
        "| 问题三 | `code/q3/solve_q3.py` | `code/q3/visualize_q3.py` | `docs/results/q3_results.json` | `docs/figures/q3_figures.md` |",
        "",
        "## 分问结果索引",
        "",
    ]

    for q in ("q1", "q2", "q3"):
        result = read_json(f"docs/results/{q}_results.json", {})
        chunks.append(f"### {q.upper()}")
        chunks.append("")
        chunks.append(f"- 状态：{result.get('status', '待补充')}")
        chunks.append(f"- 论文位置：{result.get('paper_position', '待确认')}")
        chunks.append(f"- 主模型：{result.get('model', {}).get('selected', '待用户决策') if isinstance(result.get('model'), dict) else '待用户决策'}")
        chunks.append("")

    for title, content in sections:
        chunks.append(f"## {title}")
        chunks.append("")
        body = content.strip()
        if body.startswith("#"):
            body = "\n".join(body.splitlines()[1:]).strip()
        chunks.append(body or "待补充。")
        chunks.append("")

    write_text("docs/paper_materials.md", "\n".join(chunks).strip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
