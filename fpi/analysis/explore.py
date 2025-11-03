import pandas as pd
from pathlib import Path

from fpi.analysis.utils_io import print_info
from fpi.analysis.utils_stats import statdes
from fpi.analysis.utils_plot import save_hist, save_lv
from fpi.utils.constants import NUMERIC_VARS, VARS_TO_KEEP


def load_data(cleaned_path: str = "data/cleaned") -> pd.DataFrame:
    """
    load automatically latest cleaned data.
    """
    cleaned_dir = Path(cleaned_path)
    all_files = sorted(cleaned_dir.rglob("cleaned_*.csv"), reverse=True)
    if not all_files:
        raise FileNotFoundError("No file found in data/cleaned/")
    
    latest_file = all_files[0]
    print(f"Load succeeded: {latest_file.name}")
    return pd.read_csv(latest_file)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Only keeps important variables.
    """
    df = df[[col for col in VARS_TO_KEEP if col in df.columns]]
    return df


def exp() -> None:
    """
    Exploratory pipeline :
    1️.Loading
    2️. Cleaning columns
    3️. Descriptive stats
    4️. Graphs
    """
    df = load_latest_data()
    print_info(df)

    df_clean = preprocess(df)
    statdes(df_clean)

    # Histogramm
    save_hist(df_clean, NUMERIC_VARS, output_dir="docs/plots")

    # Boxplots per key variable
    save_lv(df_clean, "property_value", output_dir="docs/plots")

    print("\n Graphs saved in docs/plots/.")


if __name__ == "__main__":
    exp()
