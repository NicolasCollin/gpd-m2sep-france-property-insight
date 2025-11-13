import glob
import os

import pandas as pd


def load_all_csv(data_root: str = "data/cleaned") -> pd.DataFrame:
    """
    Load all cleaned department CSV files for all available years
    and concatenate them into a single DataFrame.

    Handles French decimal format (comma as decimal separator) and ensures numeric
    columns are correctly typed. Invalid entries are converted to NaN.

    Returns:
        pd.DataFrame: Combined data from all cleaned CSV files.
    """

    all_files: list[str] = glob.glob(os.path.join(data_root, "cleaned*", "cleaned_*_*.csv"))
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {data_root}")

    df_list: list[pd.DataFrame] = []
    numeric_cols: list[str] = [
        "property_value",
        "building_area",
        "main_rooms",
        "land_area",
    ]

    for file in all_files:
        try:
            df_file: pd.DataFrame = pd.read_csv(file, decimal=",")
            for col in numeric_cols:
                if col in df_file.columns:
                    df_file[col] = pd.to_numeric(df_file[col], errors="coerce")
            df_list.append(df_file)
        except Exception as e:
            error_msg: str = f"Failed to read {file}: {e}"
            print(error_msg)

    if not df_list:
        raise ValueError("No CSV files could be loaded successfully.")

    df: pd.DataFrame = pd.concat(df_list, ignore_index=True)

    return df
