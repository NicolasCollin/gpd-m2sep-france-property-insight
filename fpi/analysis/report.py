import glob
import os

import pandas as pd


def load_raw(data_root: str = "data/raw") -> pd.DataFrame:
    """
    Load all raw department CSV files for all available years
    and concatenate them into a single DataFrame.

    Handles French decimal format (comma as decimal separator) and ensures numeric
    columns are correctly typed. Invalid entries are converted to NaN.

    Returns:
        pd.DataFrame: Combined data from all raw CSV files.
    """

    all_files: list[str] = glob.glob(os.path.join(data_root, "raw*", "raw_*_*.csv"))
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
            df_file: pd.DataFrame = pd.read_csv(file, decimal=",", low_memory=False)
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


def analyze_dataset_quality(df: pd.DataFrame) -> dict:
    """
    Global qualitative analysis of a raw dataset.

    Output dict contains:
      - missing_values: NA count per column
      - outliers: outlier count per numeric column (IQR)
      - type_local_counts: distribution of type_local only (if exists)
    """

    report = {}

    # --- 1. Missing values per column ---
    report["missing_values"] = df.isna().sum().to_dict()

    # --- 2. type_local distribution (ONLY if the column exists) ---
    if "type_local" in df.columns:
        report["type_local_counts"] = df["type_local"].value_counts(dropna=False).to_dict()
    else:
        report["type_local_counts"] = None

    # --- 3. Outliers on numeric columns ---
    numeric_cols = df.select_dtypes(include=["number"]).columns
    outliers = {}

    for col in numeric_cols:
        series = df[col].dropna()

        if series.empty:
            outliers[col] = 0
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers[col] = int(((series < lower) | (series > upper)).sum())

    report["outliers"] = outliers

    return report
