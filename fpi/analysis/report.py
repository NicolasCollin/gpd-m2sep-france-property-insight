import pandas as pd

def count_missing_values(df: pd.DataFrame) -> dict:
    """
    Count missing values (NaN) per column.
    """
    return df.isna().sum().to_dict()


def count_type_local(df: pd.DataFrame) -> dict | None:
    """
    Count occurrences of each type_local value.
    Returns None if the column does not exist.
    """
    if "type_local" not in df.columns:
        return None
    return df["type_local"].value_counts(dropna=False).to_dict()


def detect_outliers(df: pd.DataFrame) -> dict:
    """
    Detect outliers in numeric columns using the IQR method.
    """
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

    return outliers


def analyze_dataset_quality(df: pd.DataFrame) -> dict:
    """
    Global qualitative analysis of a dataset.
    Combines missing values, type_local counts, and outliers.
    """
    return {
        "missing_values": count_missing_values(df),
        "type_local_counts": count_type_local(df),
        "outliers": detect_outliers(df),
    }