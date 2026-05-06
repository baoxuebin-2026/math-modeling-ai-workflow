from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.io_utils import list_data_files, write_json, write_json_if_missing, write_text, write_text_if_missing


def main() -> int:
    force = "--force" in sys.argv
    data_files = list_data_files()
    problem_lines = [
        "# 题目信息提取",
        "",
        "## 当前状态",
        "",
        "待补充赛题原文或赛题文件后，由 AI 提取背景、任务要求、附件说明、约束条件和关键词。",
        "",
        "## 已发现数据文件",
        "",
    ]
    if data_files:
        problem_lines.extend([f"- `{p}`" for p in data_files])
    else:
        problem_lines.append("- 未发现数据文件。请将赛题附件放入 `data/raw/`。")
    writer_text = write_text if force else write_text_if_missing
    writer_json = write_json if force else write_json_if_missing

    writer_text("docs/00_problem_extracted.md", "\n".join(problem_lines) + "\n")

    alignment = [
        "# 逐问任务对齐",
        "",
        "| 问题 | 任务类型 | 输入 | 输出 | 关键约束 | 验证方式 | 用户决策点 |",
        "|---|---|---|---|---|---|---|",
        "| 问题一 | 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | 是否作为基础模型/基线 |",
        "| 问题二 | 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | 是否在问题一基础上递进 |",
        "| 问题三 | 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | 是否承担综合评价/推广/鲁棒性 |",
        "",
    ]
    writer_text("docs/01_task_alignment.md", "\n".join(alignment))

    model_plan = [
        "# 模型路线",
        "",
        "## 决策原则",
        "",
        "- 适配性优先于复杂度。",
        "- 可解释性优先于微小精度提升。",
        "- 每一问至少保留一个基线模型，便于对照。",
        "- 只有当数据规模、非线性或任务结构确实需要时，才使用组合模型或黑箱模型。",
        "",
        "## 分问模型计划",
        "",
        "| 问题 | 基线模型 | 改进模型 | 推荐主模型 | 选择理由 | 风险 |",
        "|---|---|---|---|---|---|",
        "| 问题一 | 待确认 | 待确认 | 待用户决策 | 待题意解析后确认 | 待确认 |",
        "| 问题二 | 待确认 | 待确认 | 待用户决策 | 待题意解析后确认 | 待确认 |",
        "| 问题三 | 待确认 | 待确认 | 待用户决策 | 待题意解析后确认 | 待确认 |",
        "",
    ]
    writer_text("docs/02_model_plan.md", "\n".join(model_plan))

    writer_text(
        "docs/checkpoints.md",
        "# 工作流检查点\n\n用于记录每个等待用户确认的阶段。详见仓库模板中的默认表格。\n",
    )
    writer_text(
        "docs/findings.md",
        "# 跨阶段发现记录\n\n用于记录模型、数据、工程和论文写作中的关键发现。\n",
    )
    writer_text(
        "docs/experiment_log.md",
        "# 实验日志\n\n用于记录每次模型运行、参数扰动、图表生成或检验实验。\n",
    )
    writer_text(
        "docs/active_solution_contract.md",
        "# 当前确认方案契约\n\n用于记录当前已确认的主模型、假设、结果和论文主线。\n",
    )
    writer_text(
        "docs/claim_evidence_map.md",
        "# 论文结论证据映射表\n\n用于连接论文结论与模型、结果、图表和检验证据。\n",
    )

    writer_json(
        "docs/workflow/tasks.json",
        [
            {"id": "q1", "solve": "code/q1/solve_q1.py", "visualize": "code/q1/visualize_q1.py"},
            {"id": "q2", "solve": "code/q2/solve_q2.py", "visualize": "code/q2/visualize_q2.py"},
            {"id": "q3", "solve": "code/q3/solve_q3.py", "visualize": "code/q3/visualize_q3.py"},
        ],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
