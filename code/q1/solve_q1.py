from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code.common.io_utils import project_path, write_json


QUESTION_ID = "q1"


def main() -> int:
    processed_files = sorted(project_path("data/processed").glob("*.csv"))
    result = {
        "question": "问题一",
        "status": "待补充" if not processed_files else "已生成基础占位结果",
        "paper_position": "问题一模型建立与求解",
        "code": "code/q1/solve_q1.py",
        "visualization_code": "code/q1/visualize_q1.py",
        "input_files": [str(p) for p in processed_files],
        "model": {
            "baseline": "待根据题意确认",
            "selected": "待用户决策",
            "reason": "需先完成题意解析与模型路线确认",
        },
        "outputs": {},
        "notes": [
            "本文件是问题一求解代码入口。",
            "确认模型后，应在此处实现读数据、建模、求解和结果落盘。",
        ],
    }
    write_json("docs/results/q1_results.json", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
