from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_step(label: str, script: str) -> int:
    print(f"\n=== {label} ===")
    result = subprocess.run([sys.executable, script], cwd=ROOT, check=False)
    if result.returncode != 0:
        print(f"步骤失败：{label}")
    return result.returncode


def main() -> int:
    steps = [
        ("初始化阶段文档", "code/01_initialize_docs.py"),
        ("数据清洗与报告", "code/00_prepare_data.py"),
        ("问题一求解", "code/q1/solve_q1.py"),
        ("问题一可视化", "code/q1/visualize_q1.py"),
        ("问题二求解", "code/q2/solve_q2.py"),
        ("问题二可视化", "code/q2/visualize_q2.py"),
        ("问题三求解", "code/q3/solve_q3.py"),
        ("问题三可视化", "code/q3/visualize_q3.py"),
        ("流程审计与验证", "code/validation/validate_all.py"),
        ("生成论文素材包", "code/07_build_materials.py"),
    ]

    for label, script in steps:
        code = run_step(label, script)
        if code != 0:
            return code

    print("\n完成：docs/paper_materials.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
