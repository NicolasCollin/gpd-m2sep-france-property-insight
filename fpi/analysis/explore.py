from pathlib import Path

from fpi.analysis.plots import display_trend
from fpi.analysis.stats import compute_descriptive_statistics, summary
from fpi.data_pipeline.data_prep import load_data


def explore() -> None:
    """
    Full exploratory pipeline:
    1️ Load every cleaned csv files from 2021 to 2024
    2️ Display summary statistics
    3️ Compute descriptive stats
    4️ Generate plots (histograms, boxplots, curves)
    """
    df = load_data()
    summary(df)
    compute_descriptive_statistics(df)

    output_dir = "docs/plots"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("\n Generating regional trends...")
    display_trend("data/cleaned", dept_filter=None, agg="median")
    for dept in ["75", "92", "93"]:
        display_trend("data/cleaned", dept_filter=dept, agg="median")
