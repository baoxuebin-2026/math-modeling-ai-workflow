from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code.common.io_utils import project_path, read_json, write_text


def main() -> int:
    checks = []
    for q in ("q1", "q2", "q3"):
        result_path = project_path(f"docs/results/{q}_results.json")
        figure_doc_path = project_path(f"docs/figures/{q}_figures.md")
        figure_dir = project_path(f"figures/{q}")
        result = read_json(result_path, {})
        checks.append(
            {
                "question": q.upper(),
                "result_json": result_path.exists(),
                "figure_doc": figure_doc_path.exists(),
                "figure_count": len(list(figure_dir.glob("*.png"))) if figure_dir.exists() else 0,
                "status": result.get("status", "待补充"),
            }
        )

    lines = ["# 模型检验与流程审计报告", ""]
    lines.append("## 文件完整性")
    lines.append("")
    lines.append("| 问题 | 结果 JSON | 图表说明 | PNG 数量 | 当前状态 |")
    lines.append("|---|---:|---:|---:|---|")
    for item in checks:
        lines.append(
            f"| {item['question']} | {'是' if item['result_json'] else '否'} | "
            f"{'是' if item['figure_doc'] else '否'} | {item['figure_count']} | {item['status']} |"
        )
    lines.append("")
    lines.append("## 待人工确认")
    lines.append("")
    lines.append("- 每一问的题型判断是否准确。")
    lines.append("- 每一问主模型是否由用户确认。")
    lines.append("- 图表是否真正支撑论文结论，是否存在凑图。")
    lines.append("- 结果单位、保留位数和统计口径是否统一。")
    lines.append("- 是否需要补充误差分析、敏感性分析或鲁棒性检验。")
    write_text("docs/06_validation_report.md", "\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
