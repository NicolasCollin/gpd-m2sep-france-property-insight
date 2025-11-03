import pandas as pd
from pathlib import Path

from fpi.analysis.utils_io import print_info
from fpi.analysis.utils_stats import statdes
from fpi.analysis.utils_plot import save_hist, save_lv, save_curv,property_trend
from fpi.utils.constants import NUMERIC_VARS, VARS_TO_KEEP


def load_data(cleaned_path: str = "data/cleaned") -> pd.DataFrame:
    """
    Automatically load the latest cleaned dataset from the given path.

    Args:
        cleaned_path (str): Folder containing cleaned CSV files.
    Returns:
        pd.DataFrame: The most recent cleaned dataset.
    """
    cleaned_dir = Path(cleaned_path)
    all_files = sorted(cleaned_dir.rglob("cleaned_*.csv"), reverse=True)
    if not all_files:
        raise FileNotFoundError("No cleaned CSV file found in data/cleaned/")

    latest_file = all_files[0]
    print(f"Loaded latest file: {latest_file.name}")
    return pd.read_csv(latest_file)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only relevant variables defined in constants.

    Args:
        df (pd.DataFrame): Raw DataFrame.
    Returns:
        pd.DataFrame: Filtered DataFrame with relevant columns.
    """
    df = df[[col for col in VARS_TO_KEEP if col in df.columns]]
    return df


def exp() -> None:
    """
    Full exploratory pipeline:
    1️ Load latest cleaned data
    2️ Display basic info
    3️ Compute descriptive stats
    4️ Generate plots (histograms, boxplots, curves)
    """
    # --- Step 1: Load latest data ---
    df = load_data()

    # --- Step 2: Inspect basic info ---
    print_info(df)

    # --- Step 3: Keep relevant columns ---
    df_clean = preprocess(df)
    statdes(df_clean)

    # --- Step 4: Plots ---
    output_dir = "docs/plots"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("\n Generating histograms...")
    save_hist(df_clean, NUMERIC_VARS, output_dir=output_dir)

    #print("\n Generating boxplot for property_value...")
    #save_lv(df_clean, "property_value", output_dir=output_dir)

    #print("\n Generating KDE curves (by year and department)...")
    #save_curv(cleaned_path="data/cleaned", var="property_value", output_dir=output_dir)

    print("\n Generating property value trend...")
    property_trend(cleaned_path="data/cleaned", output_dir="docs/plots", agg="median")

    print("\n All plots successfully saved in docs/plots/")


if __name__ == "__main__":
    exp()
