import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from fpi.utils.constants import DEPT_NAMES


def convert_value_for_display(value: float) -> str:
    """
    Format a numeric value into a human-readable string with suffixes and comma as decimal separator.

    Args:
        value (float): The numeric value to format.

    Returns:
        str: Formatted string with suffix (K, M, Md) and comma as decimal separator.
    """
    thresholds: list[tuple[int, str]] = [
        (1_000_000_000, " Md"),
        (1_000_000, " M"),
        (1_000, " K"),
    ]

    for threshold, suffix in thresholds:
        if abs(value) >= threshold:
            formatted = f"{value / threshold:.1f}".replace(".", ",")
            return f"{formatted}{suffix}"

    return f"{value:.1f}".replace(".", ",")


def _clean_value_series(series: pd.Series) -> pd.Series:
    """
    Clean and convert the `property_value` column to numeric.

    Args:
        series (pd.Series): Series of property values as strings.

    Returns:
        pd.Series: Cleaned numeric series with invalid values set to NaN.
    """
    series_str = series.astype(str)
    series_cleaned = (
        series_str
        .str.replace("€", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
    )
    return pd.to_numeric(series_cleaned, errors="coerce")


def _load_year_data(year_folder: Path | str, dept_filter: str | None) -> list[pd.DataFrame]:
    """
    Load and clean all CSV files for a given year.

    Args:
        year_folder (Path | str): Folder containing yearly CSV files.
        dept_filter (str | None): Department code to filter (e.g., "75"), or None for all.

    Returns:
        list[pd.DataFrame]: List of cleaned DataFrames with standardized columns.
    """
    year_folder = Path(year_folder)
    year_str = "".join(filter(str.isdigit, year_folder.name))
    year = int(year_str) if year_str.isdigit() else 0
    dataframes: list[pd.DataFrame] = []

    for file in year_folder.glob("cleaned_*.csv"):
        match = re.search(r"_(\d{2,3})_", file.name)
        dept_code = match.group(1) if match else "unknown"
        if dept_filter and dept_code != dept_filter:
            continue

        try:
            df = pd.read_csv(file)
            if "property_value" not in df.columns:
                continue

            df["property_value"] = _clean_value_series(df["property_value"])
            df = df[df["property_value"].notna() & (df["property_value"] > 0)]
            if df.empty:
                continue

            df["year"] = year
            df["department_code"] = dept_code
            df["department_name"] = DEPT_NAMES.get(dept_code, f"Department {dept_code}")
            dataframes.append(df[["department_code", "department_name", "year", "property_value"]])

        except Exception as e:
            print(f"Error loading {file}: {e}")

    return dataframes


def display_trend(
    cleaned_path: Path | str,
    dept_filter: str | None,
    agg: str = "median",
    output_dir: Path | str = "docs/plots",
) -> None:
    """
    Generate and save a trend line plot of property values over time.

    Args:
        cleaned_path (Path | str): Root folder containing yearly cleaned CSVs.
        dept_filter (str | None): Department code to filter, or None for all.
        agg (str): Aggregation method: "median" or "mean".
        output_dir (Path | str): Directory to save the plot.
    """
    cleaned_root = Path(cleaned_path)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    all_data = [
        df
        for year_folder in sorted(cleaned_root.iterdir())
        if year_folder.is_dir()
        for df in _load_year_data(year_folder, dept_filter)
    ]

    if not all_data:
        print("No data loaded.")
        return

    df_all = pd.concat(all_data, ignore_index=True)
    agg_func = "mean" if agg == "mean" else "median"
    grouped = df_all.groupby(["department_code", "department_name", "year"])
    trend_df = grouped["property_value"].agg(agg_func).reset_index()

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    if dept_filter:
        dept_df = trend_df[trend_df["department_code"] == dept_filter]
        if dept_df.empty:
            print(f"No data found for department {dept_filter}.")
            return

        sns.lineplot(
            data=dept_df,
            x="year",
            y="property_value",
            marker="o",
            linewidth=2.5,
            color="steelblue",
            label=f"{dept_df['department_name'].iloc[0]} ({dept_filter})",
        )
        plt.title(f"Real Estate Price Trend — {dept_df['department_name'].iloc[0]}")
    else:
        sns.lineplot(
            data=trend_df,
            x="year",
            y="property_value",
            hue="department_name",
            marker="o",
            linewidth=2.5,
        )
        plt.title("Real Estate Price Trends — Île-de-France")

    plt.xlabel("Year")
    plt.ylabel("Median Property Value (€)")
    plt.gca().yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: convert_value_for_display(x))
    )
    plt.legend(title="Department", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    output_file = output_dir_path / f"trend_{dept_filter or 'idf'}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Plot saved to {output_file}")
