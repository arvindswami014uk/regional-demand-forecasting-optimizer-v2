from pathlib import Path
import pandas as pd


def load_features_data(
    project_root,
    filename="features.csv",
    parse_dates=("date",),
    extra_paths=None,
    verbose=True
):
    """
    Load the processed feature-engineered dataset.

    Search order:
    1. project_root/data/processed/filename
    2. any extra_paths passed in explicitly

    Parameters
    ----------
    project_root : str or Path
        Root directory of the project repo.
    filename : str
        Expected processed data filename.
    parse_dates : tuple
        Columns to parse as datetimes.
    extra_paths : list[str] or list[Path], optional
        Additional candidate file paths to check.
    verbose : bool
        Whether to print path search details.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.

    Raises
    ------
    FileNotFoundError
        If no candidate path exists.
    """
    project_root = Path(project_root)

    candidate_paths = [
        project_root / "data" / "processed" / filename,
    ]

    if extra_paths:
        candidate_paths.extend([Path(p) for p in extra_paths])

    if verbose:
        print("Looking for processed dataset...")
        for path in candidate_paths:
            print(f" - {path}")

    for path in candidate_paths:
        if path.exists():
            if verbose:
                print(f"\nLoaded data from: {path}")
            return pd.read_csv(path, parse_dates=list(parse_dates))

    raise FileNotFoundError(
        "Could not find processed dataset. Checked:\n" +
        "\n".join([str(p) for p in candidate_paths])
    )