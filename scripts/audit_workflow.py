#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SKILLS = {
    "math-hub", "math-problem-reader", "math-literature", "math-model",
    "math-code", "math-verifier", "math-figure", "math-table",
    "math-abstract", "math-consistency", "math-review", "math-templates",
    "math-compliance",
}
FORBIDDEN_PROJECT_PATHS = ["project_config.yaml", "code", "data", "results", "figures", "paper", "supporting_materials"]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"[FAIL] {message}")


def main() -> int:
    failures: list[str] = []
    for path in ["AI_WORKFLOW.md", "README.md", "project_config.example.yaml", "docs/workflow/skill_routing.md", "docs/workflow/competition_retrospective.md"]:
        if (ROOT / path).exists():
            print(f"[PASS] {path}")
        else:
            fail(f"missing {path}", failures)

    for path in FORBIDDEN_PROJECT_PATHS:
        if (ROOT / path).exists():
            fail(f"competition artifact exists in workflow root: {path}", failures)

    available = {p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()}
    for name in sorted(REQUIRED_SKILLS - available):
        fail(f"routed skill is missing: {name}", failures)

    tasks_path = ROOT / "docs/workflow/tasks.json"
    try:
        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
        if tasks.get("questions") != []:
            fail("workflow tasks must not contain an active contest question", failures)
        else:
            print("[PASS] no active contest questions in workflow manifest")
    except Exception as exc:
        fail(f"invalid tasks.json: {exc}", failures)

    workflow_text = (ROOT / "AI_WORKFLOW.md").read_text(encoding="utf-8") if (ROOT / "AI_WORKFLOW.md").exists() else ""
    if re.search(r"微网|CP-0[1-9]|result[1-9]\.xlsx", workflow_text):
        fail("active-contest residue found in AI_WORKFLOW.md", failures)
    else:
        print("[PASS] no known active-contest residue in workflow entry")

    print(f"Audit complete: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

