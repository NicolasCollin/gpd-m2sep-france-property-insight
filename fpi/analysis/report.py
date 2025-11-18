import pandas as pd

def count_missing_values(df: pd.DataFrame) -> list[tuple[str, int]]:
    """
    Count missing values (NaN) per column.
    Returns a list of (column, NA_count).
    """
    return list(df.isna().sum().items())


def count_type_local(df: pd.DataFrame) -> list[tuple[str, int]] | None:
    """
    Count occurrences of each Type_local value.
    Returns a list of (value, count) or None if the column does not exist.
    """
    if "Type_local" not in df.columns:
        return None
    return list(df["Type_local"].value_counts(dropna=False).items())


def detect_outliers(df: pd.DataFrame) -> list[tuple[str, int]]:
    """
    Detect outliers in numeric columns using the IQR method.
    Returns a list of (column, outlier_count).
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns
    outliers = []

    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            outliers.append((col, 0))
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_count = int(((series < lower) | (series > upper)).sum())
        outliers.append((col, outlier_count))

    return outliers


def analyze_dataset_quality(df: pd.DataFrame) -> dict:
    """
    Global qualitative analysis of a dataset.
    Combines missing values, type_local counts, and outliers.
    Each entry is a list instead of a dict.
    """
    return {
        "missing_values": count_missing_values(df),
        "type_local_counts": count_type_local(df),
        "outliers": detect_outliers(df),
    }