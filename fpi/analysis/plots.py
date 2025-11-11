import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from fpi.utils.constants import DEPT_NAMES


def convert_number_for_display(number: float | int) -> str:
    """
    Format a numeric value into a human-readable string with suffixes (K, M, Md)
    and comma as the decimal separator.

    Args:
        number (float): The numeric value to format.

    Returns:
        str: Formatted string with suffix (K, M, Md) and comma as decimal separator.
    """
    thresholds: list[tuple[int, str]] = [
        (1_000_000_000, " Md"),
        (1_000_000, " M"),
        (1_000, " K"),
    ]

    for threshold, suffix in thresholds:
        if abs(number) >= threshold:
            formatted: str = f"{number / threshold:.1f}".replace(".", ",")
            return f"{formatted}{suffix}"

    formatted: str = f"{number:.1f}".replace(".", ",")
    return formatted


def _clean_value_series(series: pd.Series) -> pd.Series:
    """
    Clean and convert a series of property values to numeric.

    Args:
        series (pd.Series): Series containing property values as strings (e.g. "450 000 €").

    Returns:
        pd.Series: Series of cleaned numeric values, with invalid entries replaced by NaN.
    """
    series_str: pd.Series[str] = series.astype(str)
    series_cleaned: pd.Series[str] = (
        series_str.str.replace("€", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
    )
    series_numeric: pd.Series[float] = pd.to_numeric(series_cleaned, errors="coerce")
    return series_numeric


def _load_year_data(year_folder: Path | str, dept_filter: str | None) -> list[pd.DataFrame]:
    """
    Load and clean all CSV files for a given year.

    Args:
        year_folder (Path | str): Path to the folder containing cleaned CSV files for that year.
        dept_filter (str | None): Department code to filter (e.g., "75") or None for all.

    Returns:
        list[pd.DataFrame]: A list of cleaned DataFrames, each containing standardized columns.
    """
    year_folder_path: Path = Path(year_folder)
    year_str: str = "".join(filter(str.isdigit, year_folder_path.name))
    year: int = int(year_str) if year_str.isdigit() else 0
    dataframes: list[pd.DataFrame] = []

    for file in year_folder_path.glob("cleaned_*.csv"):
        match: re.Match[str] | None = re.search(r"_(\d{2,3})_", file.name)
        dept_code: str = match.group(1) if match else "unknown"

        if dept_filter and dept_code != dept_filter:
            continue

        try:
            df: pd.DataFrame = pd.read_csv(file)

            if "property_value" not in df.columns:
                continue

            df["property_value"] = _clean_value_series(df["property_value"])
            df = df[df["property_value"].notna() & (df["property_value"] > 0)]
            if df.empty:
                continue

            df["year"] = year
            df["department_code"] = dept_code
            df["department_name"] = DEPT_NAMES.get(dept_code, f"Department {dept_code}")
            df_clean: pd.DataFrame = df[["department_code", "department_name", "year", "property_value"]]
            dataframes.append(df_clean)

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
        cleaned_path (Path | str): Root folder containing yearly cleaned CSV files.
        dept_filter (str | None): Department code to filter (e.g., "75"), or None for all departments.
        agg (str): Aggregation method, either "median" or "mean". Defaults to "median".
        output_dir (Path | str): Directory where the resulting plot will be saved. Defaults to "docs/plots".

    Outputs:
        - Saves a PNG file named `trend_<dept_filter>.png` (or `trend_idf.png` if no filter) in the output directory.
        - The plot shows the temporal evolution of real estate prices by department.
    """
    cleaned_root: Path = Path(cleaned_path)
    output_dir_path: Path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    all_data: list[pd.DataFrame] = [
        df
        for year_folder in sorted(cleaned_root.iterdir())
        if year_folder.is_dir()
        for df in _load_year_data(year_folder, dept_filter)
    ]

    if not all_data:
        print("No data loaded.")
        return

    df_all: pd.DataFrame = pd.concat(all_data, ignore_index=True)
    agg_func: str = "mean" if agg == "mean" else "median"

    grouped = df_all.groupby(["department_code", "department_name", "year"])
    trend_df: pd.DataFrame = grouped["property_value"].agg(agg_func).reset_index()

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    if dept_filter:
        dept_df: pd.DataFrame = trend_df[trend_df["department_code"] == dept_filter]
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
        title: str = f"Real Estate Price Trend — {dept_df['department_name'].iloc[0]}"
        plt.title(title)
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
    formatter = mticker.FuncFormatter(lambda x, _: convert_number_for_display(x))
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.legend(title="Department", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    output_file: Path = output_dir_path / f"trend_{dept_filter or 'idf'}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Plot saved to {output_file}")
