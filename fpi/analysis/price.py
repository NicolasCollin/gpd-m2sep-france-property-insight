import pandas as pd


def compute_price_per_sqm(df: pd.DataFrame, method: str = "median") -> float:
    """
    Compute the median or mean price per square meter from a pre-filtered DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing at least 'property_value' and 'land_area' columns.
        method (str): Aggregation method, either 'median' or 'mean'. Defaults to 'median'.

    Returns:
        float: The aggregated price per square meter.
    """
    if "property_value" not in df.columns or "land_area" not in df.columns:
        raise ValueError("DataFrame must contain 'property_value' and 'land_area' columns.")

    df_valid = df[df["property_value"].notna() & df["land_area"].notna() & (df["land_area"] > 0)]
    if df_valid.empty:
        raise ValueError("No valid data to compute price per square meter.")

    price_per_sqm = df_valid["property_value"] / df_valid["land_area"]

    if method == "mean":
        return price_per_sqm.mean()
    return price_per_sqm.median()
