from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(*parts: str | Path) -> Path:
    return ROOT.joinpath(*map(Path, parts))


def ensure_dir(path: str | Path) -> Path:
    p = project_path(path) if not Path(path).is_absolute() else Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_json(path: str | Path, default: Any = None) -> Any:
    p = project_path(path) if not Path(path).is_absolute() else Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> Path:
    p = project_path(path) if not Path(path).is_absolute() else Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def write_text(path: str | Path, text: str) -> Path:
    p = project_path(path) if not Path(path).is_absolute() else Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def list_data_files() -> list[Path]:
    exts = {".csv", ".xlsx", ".xls", ".txt"}
    roots = [project_path("data/raw"), project_path("data/external")]
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts and not p.name.startswith("~"):
                files.append(p)
    return sorted(files, key=lambda x: str(x))


def read_table(path: str | Path):
    import pandas as pd

    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".csv":
        for encoding in ("utf-8-sig", "utf-8", "gbk"):
            try:
                return pd.read_csv(p, encoding=encoding)
            except UnicodeDecodeError:
                continue
        return pd.read_csv(p)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(p)
    if suffix == ".txt":
        try:
            return pd.read_csv(p, sep="\t")
        except Exception:
            return pd.read_csv(p, sep=",")
    raise ValueError(f"Unsupported table format: {p}")
