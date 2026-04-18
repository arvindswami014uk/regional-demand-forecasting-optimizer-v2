
from __future__ import annotations

import pandas as pd


ID_CANDIDATE_GROUPS = [
    ["week", "sku_id", "region"],
    ["date", "sku_id", "region"],
    ["date", "region", "category"],
]

TARGET_CANDIDATES = ["units_ordered", "demand", "weekly_demand"]


def infer_target_column(df: pd.DataFrame) -> str:
    for col in TARGET_CANDIDATES:
        if col in df.columns:
            return col
    raise ValueError(f"No target column found. Expected one of: {TARGET_CANDIDATES}")


def infer_key_columns(df: pd.DataFrame) -> list:
    for cols in ID_CANDIDATE_GROUPS:
        if all(col in df.columns for col in cols):
            return cols
    raise ValueError(
        f"No recognized key column set found. Tried: {ID_CANDIDATE_GROUPS}"
    )


def validate_core_schema(df: pd.DataFrame) -> dict:
    key_cols = infer_key_columns(df)
    target_col = infer_target_column(df)

    return {
        "key_cols": key_cols,
        "target_col": target_col,
    }


def validate_no_duplicate_keys(df: pd.DataFrame, key_cols=None) -> None:
    if key_cols is None:
        schema = validate_core_schema(df)
        key_cols = schema["key_cols"]

    dupes = df.duplicated(subset=key_cols).sum()
    if dupes > 0:
        raise ValueError(f"Found {dupes} duplicate rows on key columns: {key_cols}")


def validate_target_nonnegative(df: pd.DataFrame) -> None:
    target_col = infer_target_column(df)
    if (df[target_col] < 0).any():
        raise ValueError(f"Negative values found in target column: {target_col}")


def validate_week_parseable(df: pd.DataFrame) -> None:
    if "week" in df.columns:
        pd.to_datetime(df["week"], errors="raise")


def summarize_missingness(df: pd.DataFrame) -> dict:
    return df.isnull().sum().to_dict()


def run_basic_validation(df: pd.DataFrame) -> dict:
    schema = validate_core_schema(df)
    validate_no_duplicate_keys(df, schema["key_cols"])
    validate_target_nonnegative(df)
    validate_week_parseable(df)

    return {
        "status": "ok",
        "rows": len(df),
        "columns": len(df.columns),
        "key_cols": schema["key_cols"],
        "target_col": schema["target_col"],
        "missingness": summarize_missingness(df),
    }
