"""Rebuild visualization inputs and all confirmed CP-04 figures."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    scripts = [
        ROOT / "code/common/build_visualization_inputs.py",
        ROOT / "code/q1/visualize_q1.py",
        ROOT / "code/q2/visualize_q2.py",
        ROOT / "code/q3/visualize_q3.py",
        ROOT / "code/q4/visualize_q4.py",
    ]
    for script in scripts:
        print(f"running {script.relative_to(ROOT)}", flush=True)
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
