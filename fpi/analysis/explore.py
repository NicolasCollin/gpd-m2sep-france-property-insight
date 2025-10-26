import pandas as pd

from fpi.analysis.utils_io import print_info
from fpi.analysis.utils_plot import save_hist
from fpi.utils.constants import NUMERIC_VARS, VARS_TO_KEEP_FR


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load the dataset from a raw text file.

    :param file_path: Path to the raw dataset
    :return: Pandas DataFrame
    """
    return pd.read_csv(file_path, sep="|", header=0)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select only the variables we want to keep and rename them in English.

    :param df: Raw DataFrame
    :return: Cleaned DataFrame with English column names
    """
    df = df[VARS_TO_KEEP_FR]
    df.columns = [
        "land_value",
        "postal_code",
        "building_surface",
        "mutation_date",
        "land_surface",
        "main_rooms",
    ]
    return df


def exp() -> None:
    """
    Main exploration pipeline:
    - Load
    - Inspect
    - Preprocess
    - Save visualizations
    """
    df = load_data("data/raw/sample2024.txt")
    print_info(df)

    df_clean = preprocess(df)
    save_hist(df_clean, NUMERIC_VARS, output_dir="docs/plots")

    print("Plots saved in docs/plots/")


if __name__ == "__main__":
    exp()
