import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    os.chdir(root)

    print("=== 写论文前工作流：生成 docs/paper_materials.md ===")
    result = subprocess.run([sys.executable, "code/run_all.py"], check=False)
    if result.returncode == 0:
        print("✅ 已生成：docs/paper_materials.md")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
