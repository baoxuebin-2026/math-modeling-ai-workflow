from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from code.common.io_utils import ensure_dir, list_data_files, read_table, write_json, write_text


def main() -> int:
    processed_dir = ensure_dir("data/processed")
    files = list_data_files()
    profiles = []

    if not files:
        write_text(
            "docs/03_data_report.md",
            "# 数据报告\n\n当前 `data/raw/` 与 `data/external/` 中未发现 CSV、Excel 或 TXT 数据文件。请补充赛题附件后重新运行。\n",
        )
        return 0

    try:
        from code.common.data_utils import clean_dataframe, dataframe_profile
    except ModuleNotFoundError as exc:
        write_text(
            "docs/03_data_report.md",
            "# 数据报告\n\n"
            f"发现数据文件，但当前 Python 环境缺少数据处理依赖：`{exc.name}`。\n\n"
            "请安装 pandas/numpy，或使用带数据科学依赖的 Python 环境后重新运行。\n",
        )
        return 0

    for file_path in files:
        try:
            raw = read_table(file_path)
            cleaned = clean_dataframe(raw)
            out_path = processed_dir / f"{file_path.stem}_processed.csv"
            cleaned.to_csv(out_path, index=False, encoding="utf-8-sig")
            profiles.append(
                {
                    "source": str(file_path),
                    "output": str(out_path),
                    "raw": dataframe_profile(raw),
                    "processed": dataframe_profile(cleaned),
                }
            )
        except Exception as exc:
            profiles.append({"source": str(file_path), "error": str(exc)})

    write_json("data/metadata/data_profile.json", profiles)

    lines = ["# 数据报告", ""]
    for item in profiles:
        lines.append(f"## {Path(item['source']).name}")
        lines.append("")
        if "error" in item:
            lines.append(f"- 读取失败：{item['error']}")
        else:
            lines.append(f"- 原始路径：`{item['source']}`")
            lines.append(f"- 清洗输出：`{item['output']}`")
            lines.append(f"- 原始规模：{item['raw']['rows']} 行，{item['raw']['columns']} 列")
            lines.append(f"- 清洗后规模：{item['processed']['rows']} 行，{item['processed']['columns']} 列")
            lines.append(f"- 数值列：{', '.join(item['processed']['numeric_columns']) or '无'}")
            lines.append(f"- 分类型列：{', '.join(item['processed']['categorical_columns']) or '无'}")
        lines.append("")
    write_text("docs/03_data_report.md", "\n".join(lines).strip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
