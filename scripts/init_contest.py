#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


REGISTRIES = {
    "run_record.csv": ["run_id", "problem_id", "model_version", "command", "input_files", "parameters", "seed", "solver", "solver_status", "output_tables", "output_figures", "log_path", "run_status", "superseded_by", "notes"],
    "result_registry.csv": ["result_id", "problem_id", "scenario_id", "metric", "value", "unit", "comparison_or_baseline", "source_table", "source_figure", "source_script", "run_id", "validation_status", "frozen_at", "superseded_by", "notes"],
    "figure_evidence.csv": ["figure_id", "claim_id", "figure_path", "source_table", "source_script", "run_id", "caption", "post_figure_conclusion", "render_check_status", "human_visual_check", "visual_check_note", "validation_status"],
    "claim_ledger.csv": ["claim_id", "location", "claim_text", "metric", "value", "unit", "scenario", "evidence_id", "evidence_type", "body_location", "status", "risk_note"],
    "math_verification.csv": ["check_id", "subquestion", "artifact", "location", "claim_id", "check_type", "expected_relation", "observed", "status", "severity", "minimum_fix", "owner"],
    "consistency_audit.csv": ["audit_id", "claim_id", "artifact_a", "location_a", "artifact_b", "location_b", "mismatch_type", "expected", "observed", "severity", "minimum_fix", "owner", "status"],
}


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Initialize an isolated mathematical-modeling contest project.")
    ap.add_argument("output")
    ap.add_argument("--contest-name", required=True)
    ap.add_argument("--year", required=True, type=int)
    ap.add_argument("--problem-id", required=True)
    ap.add_argument("--question-count", required=True, type=int)
    ap.add_argument("--mode", choices=["rapid", "full", "local_repair"], default="rapid")
    args = ap.parse_args()

    if args.question_count < 1:
        raise SystemExit("question-count must be positive")

    root = Path(args.output).resolve()
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"refusing to initialize non-empty directory: {root}")
    root.mkdir(parents=True, exist_ok=True)

    dirs = [
        "data/raw", "data/external", "data/processed", "data/metadata",
        "docs", "registries", "logs", "paper/sections", "paper/drafts",
        "paper/reviews", "tmp",
    ]
    for q in range(1, args.question_count + 1):
        dirs.extend([f"code/q{q}", f"results/q{q}", f"figures/q{q}"])
    for name in dirs:
        (root / name).mkdir(parents=True, exist_ok=True)

    enabled = ", ".join(str(i) for i in range(1, args.question_count + 1))
    config = f'''schema_version: 2
project:
  name: "{args.year} {args.contest_name} {args.problem_id}题"
  language: "zh-CN"
  mode: "{args.mode}"
competition:
  name: "{args.contest_name}"
  year: {args.year}
  problem_id: "{args.problem_id}"
  question_count: {args.question_count}
  official_rules_url: "TODO"
submission:
  primary_format: "markdown"
  page_limit: null
  page_scope: "TODO"
  filename_rule: "TODO"
  anonymity_rule: "TODO"
  support_material_rule: "TODO"
  ai_disclosure_rule: "TODO"
workflow:
  enabled_questions: [{enabled}]
  require_official_rule_lock: true
  require_result_registry: true
  require_final_submission_gate: true
visualization:
  vector_format: "svg"
  raster_fallback: "png"
  raster_dpi: 600
  final_size_check_required: true
'''
    write_new(root / "project_config.yaml", config)
    write_new(root / "docs/hub_state.md", "# Hub state\n\nStatus: initialized\n\nOfficial rules: TODO -> blocked\n\nAllowed next module: math-compliance\n")
    write_new(root / "docs/submission_checklist.md", "# Submission checklist\n\n- [ ] Official rules verified\n- [ ] Page scope and limit locked\n- [ ] Filename and anonymity rules locked\n- [ ] Support-material rule locked\n- [ ] AI-disclosure rule locked\n")
    write_new(root / "docs/problem_brief.md", "# Problem brief\n\nStatus: TODO\n")
    write_new(root / "docs/deliverable_matrix.csv", "subquestion,required_output,source,dependency,artifact,status,blocker\n")
    write_new(root / "docs/model_handoff.md", "# Model handoff\n\nStatus: TODO\n")

    for name, header in REGISTRIES.items():
        path = root / "registries" / name
        with path.open("x", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(header)

    write_new(root / ".gitignore", "__pycache__/\n*.pyc\ntmp/*\n!tmp/.gitkeep\n")
    write_new(root / "README.md", "# Contest project\n\nStart from the workflow repository's `AI_WORKFLOW.md`.\n")
    (root / "tmp/.gitkeep").touch(exist_ok=False)
    print(f"Initialized isolated contest project: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

