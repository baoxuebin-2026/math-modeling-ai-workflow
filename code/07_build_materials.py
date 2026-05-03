from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.io_utils import project_path, read_json, write_text


def read_text_if_exists(path: str) -> str:
    p = project_path(path)
    return p.read_text(encoding="utf-8") if p.exists() else f"# {path}\n\n待补充。\n"


def main() -> int:
    tasks = read_json("docs/workflow/tasks.json", {}).get("questions", [])
    question_ids = [item.get("id") for item in tasks if item.get("id")]
    if not question_ids:
        question_ids = ["q1", "q2", "q3"]

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
    ]

    for q in question_ids:
        chunks.append(
            f"| {q.upper()} | `code/{q}/solve_{q}.py` | `code/{q}/visualize_{q}.py` | "
            f"`docs/results/{q}_results.json` | `docs/figures/{q}_figures.md` |"
        )
    chunks.extend(["", "## 分问结果索引", ""])

    for q in question_ids:
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

    full_text = "\n".join(chunks)
    if "待确认" in full_text or "待补充" in full_text or "待用户决策" in full_text:
        chunks.insert(
            4,
            "> 注意：本素材包仍包含 `待确认`、`待补充` 或 `待用户决策` 内容，只能作为过程草稿，不能直接进入论文写作阶段。",
        )
        chunks.insert(5, "")

    write_text("docs/paper_materials.md", "\n".join(chunks).strip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
