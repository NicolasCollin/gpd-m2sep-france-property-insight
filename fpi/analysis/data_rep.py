import pandas as pd
from fpi.analysis.report import (
    count_missing_values,
    count_type_local,
    detect_outliers,
    analyze_dataset_quality,
)
from fpi.data_pipeline.loader import load_all_csv

def report_data() -> None:
    df = load_all_csv("data/raw")

    # Missing values
    print("\n=== NA per column ===")
    na_df = pd.DataFrame(count_missing_values(df), columns=["Column", "NA_count"])
    print(na_df.sort_values("NA_count", ascending=False).head(20))

    # Type_local counts
    print("\n=== Type_local effectifs ===")
    type_df = pd.DataFrame(count_type_local(df), columns=["Type_local", "Count"])
    print(type_df)

    # Outliers
    print("\n=== Outliers per numeric column ===")
    out_df = pd.DataFrame(detect_outliers(df), columns=["Column", "Outlier_count"])
    print(out_df.sort_values("Outlier_count", ascending=False).head(20))

    # Global report (optional, but prettier)
    print("\n=== Global report ===")
    quality = analyze_dataset_quality(df)
    for key, values in quality.items():
        print(f"\n--- {key} ---")
        print(pd.DataFrame(values, columns=["Variable", "Value"]))