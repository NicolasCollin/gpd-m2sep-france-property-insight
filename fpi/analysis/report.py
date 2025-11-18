import pandas as pd


def analyze_dataset_quality(df: pd.DataFrame) -> dict:
    """
    Perform a global qualitative analysis of a raw dataset.

    The function computes three diagnostic elements:
        - missing_values: number of missing entries per column
        - type_local_counts: value distribution of the 'type_local' column, if present
        - outliers: count of IQR-based outliers for each numeric column

    Args:
        df (pd.DataFrame): Input DataFrame to analyze.

    Returns:
        dict: A dictionary with the keys:
            - 'missing_values' (dict[str, int]): Missing-value counts.
            - 'type_local_counts' (dict[str, object]): Distribution of 'type_local' values.
            - 'outliers' (dict[str, int]): IQR-based outlier counts for numeric columns.
    """
    report: dict = {}

    # 1. Missing values per column
    report["missing_values"] = df.isna().sum().to_dict()

    # 2. type_local distribution
    if "type_local" in df.columns:
        report["type_local_counts"] = df["type_local"].value_counts(dropna=False).to_dict()
    else:
        report["type_local_counts"] = {"None": "None"}

    # 3. Outliers on numeric columns
    numeric_cols: pd.Index[str] = df.select_dtypes(include=["number"]).columns
    outliers: dict[str, int] = {}

    for col in numeric_cols:
        series: pd.Series = df[col].dropna()

        if series.empty:
            outliers[col] = 0
            continue

        q1: float = float(series.quantile(0.25))
        q3: float = float(series.quantile(0.75))
        iqr: float = q3 - q1

        lower: float = q1 - 1.5 * iqr
        upper: float = q3 + 1.5 * iqr

        outliers[col] = int(((series < lower) | (series > upper)).sum())

    report["outliers"] = outliers

    return report
