from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code.common.io_utils import project_path, write_json


def main() -> int:
    processed_files = sorted(project_path("data/processed").glob("*.csv"))
    write_json(
        "docs/results/q2_results.json",
        {
            "question": "问题二",
            "status": "待补充" if not processed_files else "已生成基础占位结果",
            "paper_position": "问题二模型建立与求解",
            "code": "code/q2/solve_q2.py",
            "visualization_code": "code/q2/visualize_q2.py",
            "input_files": [str(p) for p in processed_files],
            "model": {"baseline": "待根据题意确认", "selected": "待用户决策"},
            "outputs": {},
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
