
from __future__ import annotations

import pandas as pd


def prepare_weekly_demand_base(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # NOTE: current canonical weekly demand base table
    df["week"] = pd.to_datetime(df["week"])
    df = df.sort_values(["sku_id", "region", "week"]).reset_index(drop=True)

    return df


def add_calendar_features(df: pd.DataFrame, date_col: str = "week") -> pd.DataFrame:
    df = df.copy()

    dt = pd.to_datetime(df[date_col])
    df["year"] = dt.dt.year
    df["month"] = dt.dt.month
    df["quarter"] = dt.dt.quarter
    df["weekofyear"] = dt.dt.isocalendar().week.astype(int)

    return df


def add_lag_features(
    df: pd.DataFrame,
    group_cols=None,
    target_col: str = "units_ordered",
    lags=None,
) -> pd.DataFrame:
    df = df.copy()

    if group_cols is None:
        group_cols = ["sku_id", "region"]

    if lags is None:
        lags = [1, 2, 4]

    for lag in lags:
        df[f"lag_{lag}"] = df.groupby(group_cols)[target_col].shift(lag)

    return df


def add_rolling_features(
    df: pd.DataFrame,
    group_cols=None,
    target_col: str = "units_ordered",
    windows=None,
) -> pd.DataFrame:
    df = df.copy()

    if group_cols is None:
        group_cols = ["sku_id", "region"]

    if windows is None:
        windows = [2, 4, 8]

    for window in windows:
        df[f"roll_{window}_mean"] = (
            df.groupby(group_cols)[target_col]
              .transform(lambda s: s.shift(1).rolling(window=window).mean())
        )

    return df


def prepare_modeling_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = prepare_weekly_demand_base(df)
    df = add_calendar_features(df, date_col="week")
    df = add_lag_features(df, group_cols=["sku_id", "region"], target_col="units_ordered")
    df = add_rolling_features(df, group_cols=["sku_id", "region"], target_col="units_ordered")

    return df
