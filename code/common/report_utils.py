from __future__ import annotations

from pathlib import Path

from .io_utils import project_path, write_text


def status_line(path: str | Path, exists_label: str = "已生成", missing_label: str = "待补充") -> str:
    p = project_path(path) if not Path(path).is_absolute() else Path(path)
    return f"- `{path}`：{exists_label if p.exists() else missing_label}"


def write_markdown_report(path: str | Path, title: str, sections: list[tuple[str, str]]) -> Path:
    chunks = [f"# {title}", ""]
    for heading, body in sections:
        chunks.extend([f"## {heading}", "", body.strip(), ""])
    return write_text(path, "\n".join(chunks).strip() + "\n")
