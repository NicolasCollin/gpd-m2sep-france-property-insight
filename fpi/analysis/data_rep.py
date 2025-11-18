import pandas as pd

from fpi.analysis.report import analyze_dataset_quality
from fpi.analysis.stats import summary
from fpi.data_pipeline.loader import load_all_csv


def report_data() -> None:
    """
    Full exploratory pipeline:
    1. Load all raw CSV files available in the data directory
    2. Display summary statistics
    3. Compute qualitative statistics (missing values, types, outliers)
    """

    # Step 1 — Load raw dataset
    df: pd.DataFrame = load_all_csv("data/raw")

    # Step 2 — Summary (general)
    summary(df)

    # Step 3 — Qualitative analysis
    print("\n=== QUALITATIVE REPORT ===")
    quality = analyze_dataset_quality(df)
    print(quality)
