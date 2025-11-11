from pathlib import Path

import pandas as pd

from fpi.analysis.plots import display_trend
from fpi.analysis.stats import compute_descriptive_statistics, summary
from fpi.data_pipeline.loader import load_all_csv


def explore() -> None:
    """
    Full exploratory pipeline:
    1. Load all cleaned CSV files (2021–2024)
    2. Display summary statistics
    3. Compute descriptive statistics
    4. Generate trend plots
    """
    df: pd.DataFrame = load_all_csv()
    summary(df)
    compute_descriptive_statistics(df)

    output_dir = Path("docs/plots")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nGenerating regional trend plots...")
    display_trend("data/cleaned", dept_filter=None, agg="median")

    for dept in ["75", "92", "93"]:
        display_trend("data/cleaned", dept_filter=dept, agg="median")
