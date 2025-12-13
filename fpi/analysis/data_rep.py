import pandas as pd

from fpi.analysis.report import (
    analyze_dataset_quality,
    count_missing_values,
    count_type_local,
    detect_outliers,
)
from fpi.data_pipeline.loader import load_all_csv


def report_data() -> None:
    """
    Generate and print a diagnostic report about the raw dataset on its qualitative variables.

    This function loads all CSV files from the 'data/raw' directory, then
    prints several summaries to the console in order to help understand
    data quality issues and the distribution of key variables.

    The report includes:
        1. Missing values per column (top 20).
        2. Frequency counts of the 'Type_local' variable.
        3. Number of outliers detected per numerical column (top 20),
           using the detection logic defined in `detect_outliers`.
        4. A global data quality summary produced by `analyze_dataset_quality`.
    """
    df: pd.DataFrame = load_all_csv("data/raw")

    # Missing values
    print("\n=== NA per column ===")
    na_df: pd.DataFrame = pd.DataFrame(count_missing_values(df), columns=["Column", "NA_count"])
    print(na_df.sort_values("NA_count", ascending=False).head(20))

    # Type_local counts
    print("\n=== Type_local effectifs ===")
    type_df: pd.DataFrame = pd.DataFrame(count_type_local(df), columns=["Type_local", "Count"])
    print(type_df)

    # Outliers
    print("\n=== Outliers per numeric column ===")
    out_df: pd.DataFrame = pd.DataFrame(detect_outliers(df), columns=["Column", "Outlier_count"])
    print(out_df.sort_values("Outlier_count", ascending=False).head(20))

    # Global report (optional, but prettier)
    print("\n=== Global report ===")
    quality: dict[str, list[tuple[str, int]] | None] = analyze_dataset_quality(df)
    for key, values in quality.items():
        print(f"\n--- {key} ---")
        print(pd.DataFrame(values, columns=["Variable", "Value"]))
