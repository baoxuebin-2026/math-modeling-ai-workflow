from __future__ import annotations

import re

import numpy as np
import pandas as pd


def slugify(value: object) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "column"


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.dropna(how="all", axis=0).dropna(how="all", axis=1)
    out.columns = [slugify(c) for c in out.columns]

    for col in out.columns:
        if out[col].dtype == object:
            converted = pd.to_numeric(out[col], errors="coerce")
            if converted.notna().mean() >= 0.5:
                out[col] = converted

    num_cols = out.select_dtypes(include=[np.number]).columns
    cat_cols = out.select_dtypes(exclude=[np.number]).columns

    for col in num_cols:
        if out[col].isna().any():
            out[col] = out[col].fillna(out[col].median())

    for col in cat_cols:
        if out[col].isna().any():
            mode = out[col].mode(dropna=True)
            out[col] = out[col].fillna(mode.iloc[0] if not mode.empty else "Unknown")

    return out.drop_duplicates()


def dataframe_profile(df: pd.DataFrame) -> dict:
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "numeric_columns": list(map(str, df.select_dtypes(include=[np.number]).columns)),
        "categorical_columns": list(map(str, df.select_dtypes(exclude=[np.number]).columns)),
        "missing_cells": int(df.isna().sum().sum()),
    }
