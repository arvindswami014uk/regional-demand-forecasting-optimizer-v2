
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd


@dataclass
class DataLoadResult:
    df: pd.DataFrame
    path: Path
    file_type: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _candidate_paths(
    filename_candidates: Optional[List[str]] = None,
    external_base_paths: Optional[List[Union[str, Path]]] = None,
) -> List[Path]:
    repo_root = _repo_root()

    if filename_candidates is None:
        filename_candidates = [
            "weekly_demand_aggregated.csv",
            "processed_demand_data.parquet",
            "processed_demand_data.csv",
            "featured_data.parquet",
            "featured_data.csv",
            "modeling_dataset.parquet",
            "modeling_dataset.csv",
            "final_dataset.parquet",
            "final_dataset.csv",
        ]

    candidate_dirs = [
        repo_root / "data" / "processed",
    ]

    if external_base_paths:
        for base in external_base_paths:
            base_path = Path(base)
            candidate_dirs.extend([
                base_path,
                base_path / "data" / "processed",
                base_path / "processed",
            ])

    paths = []
    for d in candidate_dirs:
        for fname in filename_candidates:
            paths.append(d / fname)

    return paths


def find_processed_dataset(
    filename_candidates: Optional[List[str]] = None,
    external_base_paths: Optional[List[Union[str, Path]]] = None,
    must_exist: bool = True,
) -> Optional[Path]:
    candidate_paths = _candidate_paths(
        filename_candidates=filename_candidates,
        external_base_paths=external_base_paths,
    )

    for path in candidate_paths:
        if path.exists():
            return path

    if must_exist:
        searched = "\n".join(str(p) for p in candidate_paths)
        raise FileNotFoundError(
            f"Processed dataset not found. Searched:\n{searched}"
        )

    return None


def load_dataset_from_path(path: Union[str, Path]) -> DataLoadResult:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(path)
        return DataLoadResult(df=df, path=path, file_type="csv")

    if suffix == ".parquet":
        df = pd.read_parquet(path)
        return DataLoadResult(df=df, path=path, file_type="parquet")

    raise ValueError(f"Unsupported file type: {suffix}")


def load_processed_dataset(
    filename_candidates: Optional[List[str]] = None,
    external_base_paths: Optional[List[Union[str, Path]]] = None,
) -> DataLoadResult:
    dataset_path = find_processed_dataset(
        filename_candidates=filename_candidates,
        external_base_paths=external_base_paths,
        must_exist=True,
    )
    return load_dataset_from_path(dataset_path)


def summarize_dataset(df: pd.DataFrame) -> dict:
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "null_counts": df.isnull().sum().to_dict(),
    }

    for col in ["date", "week", "region", "category", "sku_id", "demand", "weekly_demand", "units_ordered"]:
        if col in df.columns:
            if col in ["date", "week"]:
                try:
                    summary[f"{col}_min"] = str(pd.to_datetime(df[col]).min())
                    summary[f"{col}_max"] = str(pd.to_datetime(df[col]).max())
                except Exception:
                    summary[f"{col}_min"] = str(df[col].min())
                    summary[f"{col}_max"] = str(df[col].max())
            else:
                summary[f"{col}_unique"] = int(df[col].nunique())

    return summary
