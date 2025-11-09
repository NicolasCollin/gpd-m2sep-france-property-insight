from pathlib import Path

import numpy as np
import pandas as pd
from tabulate import tabulate  # type: ignore[import-untyped]


def summary(df: pd.DataFrame) -> None:
    """Print basic dataset information.

    Args:
        - df (pd.DataFrame): any pandas dataframe

    Outputs:
        - Prints the first 5 rows of the DataFrame
        - Prints DataFrame info (column types and non-null counts)
        - Prints the shape of the DataFrame (rows × columns)
        - Prints columns with missing values and their counts (if any)
    """

    print("\n===== HEAD =====")
    print(df.head(), "\n")

    print("===== INFO =====")
    df.info()

    print(f"\nShape: {df.shape[0]} rows × {df.shape[1]} columns\n")

    # Per-column missing values
    missing: pd.Series = df.isnull().sum()
    missing = missing[missing > 0]

    if not missing.empty:
        print("Missing values:\n", missing, "\n")


def compute_descriptive_statistics(df: pd.DataFrame, output_dir: str = "docs/stats") -> pd.DataFrame:
    """
    Compute and display comprehensive descriptive statistics for a given DataFrame,
    including summary statistics, missing values, coefficient of variation, and correlations.
    Results are printed to the console and saved as CSV files.

    Args:
        df (pd.DataFrame): Input DataFrame to analyze.
        output_dir (str, optional): Directory where CSV outputs are saved. Defaults to "docs/stats".

    Returns:
        pd.DataFrame: Formatted DataFrame with descriptive statistics for numeric columns.

    Outputs:
        - descriptive_stats.csv
        - correlation_matrix.csv
    """
    output_path: Path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 80)
    print("COMPREHENSIVE DESCRIPTIVE STATISTICS")
    print("=" * 80)

    # Dataset overview
    n_rows: int = df.shape[0]
    n_cols: int = df.shape[1]
    print(f" Dataset Shape: {n_rows:,} rows × {n_cols:,} columns")

    print(" Data Types:")
    for col_dtype, count in df.dtypes.value_counts().items():
        print(f"   • {col_dtype}: {count} columns")

    # Missing values
    total_missing: int = int(df.isnull().sum().sum())
    missing_percentage: float = total_missing / (n_rows * n_cols) * 100
    print(f" Missing Values: {total_missing:,} ({missing_percentage:.1f}% of total data)")

    # Numeric columns
    numeric_df: pd.DataFrame = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        print("No numeric columns found for detailed analysis.")
        return pd.DataFrame()

    # Descriptive stats
    summary_stats: pd.DataFrame = numeric_df.describe(percentiles=[0.25, 0.5, 0.75]).T
    summary_stats["count"] = summary_stats["count"].astype(int)
    summary_stats["missing"] = len(df) - summary_stats["count"]
    summary_stats["missing_pct"] = (summary_stats["missing"] / len(df) * 100).round(1)

    # Rename columns
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

    # Format numeric values
    for col_name in ["Mean", "Std Dev", "Minimum", "Q1 (25th%)", "Median", "Q3 (75th%)", "Maximum"]:
        summary_stats[col_name] = summary_stats[col_name].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "NaN")
    summary_stats["Count"] = summary_stats["Count"].apply(lambda x: f"{x:,}")
    summary_stats["Missing"] = summary_stats["Missing"].apply(lambda x: f"{x:,}")
    summary_stats["Missing (%)"] = summary_stats["Missing (%)"].apply(lambda x: f"{x}%")

    print("\n" + "─" * 80)
    print(" NUMERIC VARIABLES SUMMARY")
    print("─" * 80)
    print(tabulate(summary_stats, headers="keys", tablefmt="grid", stralign="right"))

    # Key insights
    print("\n KEY INSIGHTS:")
    print("─" * 50)
    for col_name in numeric_df.columns:
        col_data: pd.Series = numeric_df[col_name].dropna()
        if len(col_data) == 0:
            continue
        coefficient_variation: float = (col_data.std() / col_data.mean() * 100) if col_data.mean() != 0 else 0.0
        min_val: float = float(pd.to_numeric(col_data.min(), errors="coerce"))
        max_val: float = float(pd.to_numeric(col_data.max(), errors="coerce"))
        print(
            f"• {col_name:20}: {len(col_data):>6,} values | " f"CV: {coefficient_variation:>6.1f}% | " f"Range: {min_val:>10,.1f} - {max_val:>10,.1f}"
        )

    # Correlation matrix
    print("\n" + "─" * 80)
    print(" CORRELATION MATRIX")
    print("─" * 80)
    corr_matrix: pd.DataFrame = numeric_df.corr(method="pearson")
    formatted_corr: pd.DataFrame = corr_matrix.copy()
    for col_name in formatted_corr.columns:
        formatted_corr[col_name] = formatted_corr[col_name].apply(
            lambda x: ("1.000" if x == 1 else "—" if pd.isna(x) else f"{x:.3f}" if abs(x) >= 0.01 else f"{x:.1e}" if x != 0 else "0.000")
        )
    print(tabulate(formatted_corr, headers="keys", tablefmt="grid", stralign="center"))

    # Strong correlations
    print("\n STRONG CORRELATIONS (|r| > 0.5):")
    print("─" * 50)
    strong_correlations: list[tuple[str, str, float]] = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            raw_value = corr_matrix.iloc[i, j]
            corr_val: float = float(pd.to_numeric(raw_value, errors="coerce"))
            if not pd.isna(corr_val) and abs(corr_val) > 0.5:
                strong_correlations.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))

    if strong_correlations:
        for var1, var2, corr in sorted(strong_correlations, key=lambda x: abs(x[2]), reverse=True):
            direction: str = "positive" if corr > 0 else "negative"
            strength: str = "strong" if abs(corr) > 0.7 else "moderate"
            print(f"• {var1} ↔ {var2}: {corr:.3f} ({strength} {direction})")
    else:
        print("No strong correlations found (|r| > 0.5)")

    # Save CSVs
    summary_csv_path: Path = output_path / "descriptive_stats.csv"
    corr_csv_path: Path = output_path / "correlation_matrix.csv"
    summary_stats.to_csv(summary_csv_path, index=True)
    corr_matrix.to_csv(corr_csv_path, index=True)
    print(f"\n Statistics saved in: {output_path.resolve()}/")

    return summary_stats
