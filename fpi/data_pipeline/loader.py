import glob
import os

import pandas as pd


def load_all_csv(data_root: str = "data/cleaned") -> pd.DataFrame:
    """
    Load all department CSV files from data_root and concatenate them.

    Tries common patterns:
      - cleaned/* cleaned_*_*.csv
      - raw/*     raw_*_*.csv
      - direct CSVs (*.csv)
    """
    # Candidate patterns to try in order
    candidates = [
        os.path.join(data_root, "cleaned*", "cleaned_*_*.csv"),
        os.path.join(data_root, "raw*", "raw_*_*.csv"),
        os.path.join(data_root, "*.csv"),
    ]

    all_files: list[str] = []
    for pat in candidates:
        found = glob.glob(pat)
        if found:
            all_files = found
            break

    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {data_root}. " "Tried patterns: cleaned*/cleaned_*_*.csv, raw*/raw_*_*.csv, *.csv")

    df_list: list[pd.DataFrame] = []
    numeric_cols: list[str] = ["property_value", "building_area", "main_rooms", "land_area"]

    for file in all_files:
        try:
            df_file: pd.DataFrame = pd.read_csv(file, decimal=",", low_memory=False)
            for col in numeric_cols:
                if col in df_file.columns:
                    df_file[col] = pd.to_numeric(df_file[col], errors="coerce")
            df_list.append(df_file)
        except Exception as e:
            print(f"Failed to read {file}: {e}")

    if not df_list:
        raise ValueError("No CSV files could be loaded successfully.")

    df: pd.DataFrame = pd.concat(df_list, ignore_index=True)
    return df
