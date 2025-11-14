import pandas as pd

def analyze_variable_quality(df: pd.DataFrame, column: str) -> dict:
    """
    Perform a qualitative analysis of a given variable.

    This function reports:
    - Data type
    - Missing values count
    - Unique values count
    - Outliers count (for numeric columns)

    Example:
        >>> analyze_variable_quality(df, "property_value")

    Args:
        df (pd.DataFrame): Input dataset.
        column (str): Column name to analyze.

    Returns:
        dict: Summary of qualitative characteristics.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    series = df[column]
    total = len(series)
    missing = series.isna().sum()
    dtype = str(series.dtype)
    unique_vals = series.nunique(dropna=True)

    summary = {
        "display_name": format_display_name(column),
        "data_type": dtype,
        "total_count": total,
        "missing_count": missing,
        "unique_count": unique_vals,
    }

    # Detect outliers if numeric
    if pd.api.types.is_numeric_dtype(series):
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = ((series < lower) | (series > upper)).sum()
        summary["outliers_count"] = int(outliers)
    else:
        summary["outliers_count"] = None

    return summary
