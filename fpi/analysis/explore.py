from pathlib import Path
import pandas as pd

from fpi.analysis.plots import display_trend
from fpi.analysis.stats import compute_descriptive_statistics, summary
from fpi.data_pipeline.loader import load_all_csv


def explore() -> None:
    """
    Full exploratory pipeline:
    1. Load all cleaned CSV files available in the data directory
    2. Display summary statistics
    3. Compute descriptive statistics
    4. Generate trend plots (regional + department-level)
    """
    # Step 1 — Load data
    df: pd.DataFrame = load_all_csv()

    # Step 2 — Summary
    summary(df)

    # Step 3 — Descriptive statistics
    compute_descriptive_statistics(df)

    # Step 4 — Plots
    output_dir = Path("docs/plots")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n Generating regional and department trend plots...")

    # Global trend
    display_trend("data/cleaned", dept_filter=None, agg="median")

    # Department trends
    for dept in ["75", "92", "93"]:
        display_trend("data/cleaned", dept_filter=dept, agg="median")

    print("\n Trend plots successfully generated.")


if __name__ == "__main__":
    exp()
