import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from fpi.utils.constants import DEPT_NAMES


# to be refactored in data_pipeline
def _clean_value_series(series: pd.Series) -> pd.Series:
    """
    Clean and convert the `property_value` column to numeric.

    This function removes common formatting characters (€, spaces, commas)
    and coerces non-numeric values to NaN.

    Args:
        series (pd.Series): A pandas Series containing property values as strings.

    Returns:
        pd.Series: A numeric pandas Series with invalid values converted to NaN.
    """
    series_str: pd.Series = series.astype(str)
    series_cleaned: pd.Series = (
        series_str.str.replace("€", "", regex=False).str.replace(",", "", regex=False).str.replace(" ", "", regex=False)
    )
    numeric_series: pd.Series = pd.to_numeric(series_cleaned, errors="coerce")
    return numeric_series


# to be refactored in data_pipeline
def _load_year_data(year_folder: Path | str, dept_filter: str | None) -> list[pd.DataFrame]:
    """
    Load and clean all CSV files for a given year's folder.

    Reads all CSV files named `cleaned_*.csv` inside the given folder,
    filters by department if specified, cleans the property values,
    and returns a list of processed DataFrames ready for aggregation.

    Args:
        year_folder (Path): Path to the folder corresponding to a given year.
        dept_filter (Str | None): Department code to include (e.g., "75" for Paris),
            or None to include all.

    Returns:
        list(pd.DataFrame): A list of cleaned DataFrames containing
            columns: ["department_code", "department_name", "year", "property_value"].
    """
    year_folder = Path(year_folder)
    year_str: str = "".join(filter(str.isdigit, year_folder.name))
    year: int = int(year_str) if year_str.isdigit() else 0
    dataframes: list[pd.DataFrame] = []

    for file in year_folder.glob("cleaned_*.csv"):
        dept_match: re.Match[str] | None = re.search(r"_(\d{2,3})_", file.name)
        dept_code: str = dept_match.group(1) if dept_match else "unknown"
        if dept_filter is not None and dept_code != dept_filter:
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
            df["department_name"] = DEPT_NAMES.get(dept_code, f"Département {dept_code}")
            subset_df: pd.DataFrame = df[["department_code", "department_name", "year", "property_value"]]
            dataframes.append(subset_df)

        except Exception as e:
            print(f" Error loading {file}: {e}")

    return dataframes


def display_trend(
    cleaned_path: Path | str,
    dept_filter: str | None,
    agg: str = "median",
    output_dir: Path | str = "docs/plots",
) -> None:
    """
    Display and save a trend plot of property values over time.

    Aggregates median or mean property values per year and department,
    then generates a line plot for all departments or a selected one.

    Args:
        cleaned_path (Path | str): Root path containing yearly folders with cleaned CSV files.
        dept_filter (str | None): Department code (e.g., "75" for Paris) to focus on,
            or None to display all departments.
        agg (str): Aggregation method, either "median" or "mean". Defaults to "median".
        output_dir (Path | str): Directory where the generated plot is saved. Defaults to "docs/plots".

    Outputs:
        The function saves a `.png` plot file in the specified output directory and prints its path.
    """
    cleaned_root: Path = Path(cleaned_path)
    output_dir_path: Path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Load data from every year
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

    # Aggregate by department and year
    agg_func: str = "mean" if agg == "mean" else "median"
    grouped: pd.core.groupby.GroupBy = df_all.groupby(["department_code", "department_name", "year"])
    trend_df: pd.DataFrame = grouped["property_value"].agg(agg_func).reset_index()

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    if dept_filter is not None:
        dept_df: pd.DataFrame = trend_df[trend_df["department_code"] == dept_filter]
        if not dept_df.empty:
            sns.lineplot(
                data=dept_df,
                x="year",
                y="property_value",
                marker="o",
                linewidth=2.5,
                color="steelblue",
                label=f"{dept_df['department_name'].iloc[0]} ({dept_filter})",
            )
            plt.title(f"Évolution des prix immobiliers — {dept_df['department_name'].iloc[0]}")
        else:
            print(f" No data found for department {dept_filter}.")
            return
    else:
        sns.lineplot(
            data=trend_df,
            x="year",
            y="property_value",
            hue="department_name",
            marker="o",
            linewidth=2.5,
        )
        plt.title("Évolution des prix immobiliers — Île-de-France")

    # Formatting
    plt.xlabel("Année")
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: convert_number_for_display(float(x))))
    plt.ylabel("Valeur médiane (€)")
    plt.legend(title="Département", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    output_file: Path = output_dir_path / f"trend_{dept_filter or 'idf'}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f" Graph saved in {output_file}")


def convert_number_for_display(num: float) -> str:
    """
    Convert a large number into a human-readable string with suffixes.

    Examples:
        >>> convert_number_for_display(1200)
        '1.2 K'
        >>> convert_number_for_display(2_500_000)
        '2.5 M'

    Args:
        num (float): The numeric value to format.

    Returns:
        str: Formatted string with a scale suffix (K, M, Md).
    """
    num_float: float = float(num)
    for unit in ["", " K", " M", " Md"]:
        if abs(num_float) < 1000:
            return f"{num_float:.1f}{unit}"
        num_float /= 1000.0
    return f"{num_float:.1f} Md"
