import glob, os
import pandas as pd
from typing import List


def load_data() -> pd.DataFrame:
    """
    Load all cleaned department CSV files for all available years
    and concatenate them into a single DataFrame.

    Handles French decimal format (comma as decimal separator) and ensures numeric
    columns are correctly typed. Invalid entries are converted to NaN.

    Returns:
        pd.DataFrame: Combined data from all cleaned CSV files.
    """
    data_root = "data/cleaned/"
    all_files: List[str] = glob.glob(os.path.join(data_root, "cleaned*", "cleaned_*_*.csv"))
    
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {data_root}")

    df_list: List[pd.DataFrame] = []
    numeric_cols = ["property_value", "building_area", "main_rooms", "land_area",
                    "postal_code", "department_code", "town_code", "property_type_code"]

    for file in all_files:
        try:
            # Specify decimal="," to handle French decimal format
            df = pd.read_csv(file, decimal=",")
            
            # Ensure numeric columns are numeric
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            
            df_list.append(df)
        except Exception as e:
            print(f"Failed to read {file}: {e}")

    if not df_list:
        raise ValueError("No CSV files could be loaded successfully.")

    df: pd.DataFrame = pd.concat(df_list, ignore_index=True)
    return df