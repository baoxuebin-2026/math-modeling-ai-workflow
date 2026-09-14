---
name: math-compliance
description: Use when a mathematical-modeling contest needs official-rule verification, page-scope and file-format checks, anonymity review, Word/LaTeX/PDF readiness, support-package validation, AI-use disclosure, or a final submission gate.
---

# Mathematical Modeling Submission Compliance

## Purpose

Lock current official rules before modeling decisions depend on them, and audit the final exported submission before it is called ready. This skill checks compliance; it does not invent contest rules or alter mathematical results to fit layout.

## Rule Lock

Use the current competition's official primary source. Record the URL or document, date checked, and exact rule for:

- page limit and what pages count;
- abstract, contents, references, appendix and cover-page scope;
- file type, naming and upload limits;
- anonymity and metadata;
- support material and source-code requirements;
- AI-use permission and disclosure location;
- deadline and electronic/paper consistency when applicable.

If a rule cannot be verified, write `unknown -> blocked`. Do not substitute a previous year's rule.

## Final Format Gate

Inspect the actual final DOCX, LaTeX output or PDF—not only Markdown source. Check:

- page count under the verified scope;
- title/abstract placement and required sections;
- equations after MathType or LaTeX conversion, including unmatched brackets and broken symbols;
- figure readability at final inserted size, SVG/font compatibility and raster fallback;
- table width, page breaks, captions and numbering;
- cross-references and bibliography mapping;
- filename, document properties, comments, tracked changes and anonymity;
- support package, reproduction entry and AI disclosure.

Formatting may compress whitespace or reflow content, but it must not change frozen values, units, formulas, required tables or claim status. Any mathematical or numerical change returns to `math-hub` and the owning skill.

## Output

Maintain `docs/submission_checklist.md` and, at final gate, `docs/final_submission_manifest.md`. Report P0/P1 blockers, the exact source rule, inspected final-file path, page count and smallest repair.

Return to `math-hub` after the audit. Mark `submission_ready` only when no P0/P1 item remains.

## Red Lines

- Do not guess page scope, naming, anonymity or AI-disclosure rules.
- Do not call a Markdown draft submission-ready without inspecting the exported final file.
- Do not remove an official deliverable merely to meet a page target.
- Do not hide unresolved formula, figure, reference or metadata failures behind a successful export.

