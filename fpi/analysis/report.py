import pandas as pd


def count_missing_values(df: pd.DataFrame) -> list[tuple[str, int]]:
    """
    Count missing values (NaN) in each column of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to analyze.

    Returns:
        list[tuple[str, int]]: A list of tuples, each containing:
            - column_name (str): Name of the column.
            - NA_count (int): Number of missing values in that column.
    """

    missing_counts = df.isna().sum()
    return [(str(column_name), int(count)) for column_name, count in missing_counts.items()]


def count_type_local(df: pd.DataFrame) -> list[tuple[str, int]] | None:
    """
    Count occurrences of each value in the "Type_local" column.

    Args:
        df (pd.DataFrame): The DataFrame to analyze. Must contain a "Type_local" column.

    Returns:
        list[tuple[str, int]] | None:
            - A list of tuples with each unique value in "Type_local" and its count:
                (type_local_value, count)
            - Returns None if the "Type_local" column does not exist.
    """

    if "Type_local" not in df.columns:
        return None

    counts = df["Type_local"].value_counts(dropna=False)
    return [(str(type_local_value), int(count)) for type_local_value, count in counts.items()]


def detect_outliers(df: pd.DataFrame) -> list[tuple[str, int]]:
    """
    Detect outliers in numeric columns using the Interquartile Range (IQR) method.

    An outlier is defined as a value below Q1 - 1.5*IQR or above Q3 + 1.5*IQR.

    Args:
        df (pd.DataFrame): The DataFrame to analyze.

    Returns:
        list[tuple[str, int]]: A list of tuples, each containing:
            - column (str): Name of the numeric column.
            - outlier_count (int): Number of outlier values detected in the column.
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


def analyze_dataset_quality(df: pd.DataFrame) -> dict[str, list[tuple[str, int]] | None]:
    """
    Perform a global qualitative analysis of the dataset.

    Combines results from missing value counts, Type_local counts, and outlier detection
    into a single dictionary.

    Args:
        df (pd.DataFrame): The DataFrame to analyze.

    Returns:
        dict[str, list[tuple[str, int]] | None]: A dictionary with the following keys:
            - "missing_values": List of (column_name, NA_count) for all columns.
            - "type_local_counts": List of (Type_local value, count) or None if column missing.
            - "outliers": List of (column_name, outlier_count) for numeric columns.
    """

    return {
        "missing_values": count_missing_values(df),
        "type_local_counts": count_type_local(df),
        "outliers": detect_outliers(df),
    }
