import tempfile
from pathlib import Path

import numpy as np
import pandas as pd


def get_summary_data(df: pd.DataFrame) -> dict:
    """
    Return dataset summary for testing purposes.

    Args:
        df (pd.DataFrame)

    Returns:
        dict: {
            "head": first 5 rows as DataFrame,
            "shape": (rows, columns),
            "missing": Series of missing values per column
        }

    Example:
    >>> df = pd.DataFrame({"A": [1,2,None], "B": [4,5,6]})
    >>> result = get_summary_data(df)
    >>> result["shape"]
    (3, 2)
    >>> int(result["missing"]["A"])
    1
    >>> float(result["head"].iloc[0]["A"])
    1.0
    """
    missing = df.isnull().sum()
    missing = missing[missing > 0].astype(int)

    return {"head": df.head(), "shape": df.shape, "missing": missing}


def summary(df: pd.DataFrame) -> None:
    """Print basic dataset information using summary_data."""
    result = get_summary_data(df)
    print("\n===== HEAD =====")
    print(result["head"], "\n")
    print(f"Shape: {result['shape'][0]} rows × {result['shape'][1]} columns\n")
    if not result["missing"].empty:
        print("Missing values:\n", result["missing"], "\n")


def compute_descriptive_statistics(df: pd.DataFrame, output_dir: str | None = None) -> pd.DataFrame:
    """
    Compute descriptive statistics for numeric columns in a DataFrame.

    Saves descriptive stats and correlation matrix as CSVs. If `output_dir` is None,
    uses a temporary directory that is automatically cleaned up (good for doctests).

    Returns:
        pd.DataFrame: Formatted descriptive statistics for numeric columns.

    Example:
    >>> df = pd.DataFrame({"A": [1,2,3], "B": [4,5,6]})
    >>> result = compute_descriptive_statistics(df, output_dir=None)
    >>> isinstance(result, pd.DataFrame)
    True
    >>> "A" in result.index
    True
    >>> result.loc["A", "Count"]
    '3'
    """
    # Use a temporary directory if output_dir is None
    if output_dir is None:
        temp_dir = tempfile.TemporaryDirectory()
        output_path = Path(temp_dir.name)
    else:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

    numeric_df: pd.DataFrame = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return pd.DataFrame()

    summary_stats: pd.DataFrame = numeric_df.describe(percentiles=[0.25, 0.5, 0.75]).T
    summary_stats["count"] = summary_stats["count"].astype(int)
    summary_stats["missing"] = len(df) - summary_stats["count"]
    summary_stats["missing_pct"] = (summary_stats["missing"] / len(df) * 100).round(1)

    rename_map: dict[str, str] = {
        "count": "Count",
        "mean": "Mean",
        "std": "Std Dev",
        "min": "Minimum",
        "25%": "Q1 (25th%)",
        "50%": "Median",
        "75%": "Q3 (75th%)",
        "max": "Maximum",
        "missing": "Missing",
        "missing_pct": "Missing (%)",
    }
    summary_stats = summary_stats.rename(columns=rename_map)

    # Format numeric values as strings
    for col_name in ["Mean", "Std Dev", "Minimum", "Q1 (25th%)", "Median", "Q3 (75th%)", "Maximum"]:
        summary_stats[col_name] = summary_stats[col_name].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "NaN")
    summary_stats["Count"] = summary_stats["Count"].apply(lambda x: f"{x:,}")
    summary_stats["Missing"] = summary_stats["Missing"].apply(lambda x: f"{x:,}")
    summary_stats["Missing (%)"] = summary_stats["Missing (%)"].apply(lambda x: f"{x}%")

    # Save CSVs
    summary_stats.to_csv(output_path / "descriptive_stats.csv", index=True)
    numeric_df.corr().to_csv(output_path / "correlation_matrix.csv", index=True)

    return summary_stats
