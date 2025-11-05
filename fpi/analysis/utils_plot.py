import re
from pathlib import Path
<<<<<<< HEAD

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
=======
from typing import List, Optional, Union

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from fpi.utils.constants import DEPT_NAMES
>>>>>>> bp_analysis


def _clean_value_series(series: pd.Series) -> pd.Series:
    """
<<<<<<< HEAD
    Save histogram plots with better scaling and outlier handling.
    Automatically converts columns to numeric and skips non-numeric data.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for col in cols:
        if col not in df.columns:
            print(f" Column {col} not found.")
            continue

        # Clean and convert to numeric
        data = (
            df[col]
            .astype(str)
            .str.replace("€", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
        )
        data = pd.to_numeric(data, errors="coerce").dropna()

        if data.empty:
            print(f" No valid numeric data for {col}. Skipping.")
            continue

        # Remove outliers using IQR method
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        filtered_data = data[(data >= lower_bound) & (data <= upper_bound)]

        # Create subplots: original vs filtered
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 1: Original data
        counts_orig, bins_orig, _ = ax1.hist(data, bins=50, color="lightcoral", edgecolor="black", alpha=0.7)
        ax1.set_title(f"{col} - Original (with outliers)\nN={len(data):,}", fontweight="bold")
        ax1.set_xlabel(col)
        ax1.set_ylabel("Count")
        ax1.grid(True, alpha=0.3)
        ax1.ticklabel_format(style="plain")

        # Add value labels on bars (top 5 only)
        max_counts = sorted(set(counts_orig), reverse=True)[:5]
        for count, bin_val in zip(counts_orig, bins_orig[:-1]):
            if count in max_counts and count > 0:
                ax1.text(
                    bin_val + (bins_orig[1] - bins_orig[0]) / 2,
                    count,
                    f"{int(count):,}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        # Plot 2: Filtered data
        if len(filtered_data) > 0:
            counts_filt, bins_filt, _ = ax2.hist(filtered_data, bins=30, color="lightblue", edgecolor="black")
            ax2.set_title(f"{col} - Without Outliers\nN={len(filtered_data):,}", fontweight="bold")
            ax2.set_xlabel(col)
            ax2.set_ylabel("Count")
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, "No data after filtering", ha="center", va="center", transform=ax2.transAxes)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/{col}_hist_improved.png", dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Histogram for {col}: {len(filtered_data):,} records after filtering")


def save_lv(df: pd.DataFrame, col: str, output_dir: str) -> None:
    """
    Save a boxplot for a numeric variable. Cleans the column before plotting.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df_clean = df.copy()

    # Clean numeric data
    df_clean[col] = (
        df_clean[col]
        .astype(str)
        .str.replace("€", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    df_filtered = df_clean[df_clean[col].notna() & (df_clean[col] > 0)]
    if df_filtered.empty:
        print(f" No valid numeric data for {col}")
        return

    plt.figure(figsize=(8, 6))
    sns.boxplot(y=df_filtered[col], color="skyblue")
    plt.yscale("log")
    plt.ylabel(col)
    plt.title(f"Boxplot of {col}")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{col}_boxplot.png")
    plt.close()


def save_curv(cleaned_path: str | Path, var: str, output_dir: str | Path) -> None:
    """
    Plot and save density (KDE) curves for a numeric variable across all years and departments.
=======
    Clean and convert the `property_value` column to numeric.

    This function removes common formatting characters (€, spaces, commas)
    and coerces non-numeric values to NaN.
>>>>>>> bp_analysis

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


def _load_year_data(year_folder: Path, dept_filter: Optional[str] = None) -> List[pd.DataFrame]:
    """
    Load and clean all CSV files for a given year's folder.

<<<<<<< HEAD
    for year_folder in sorted(all_years):
        year = "".join(filter(str.isdigit, year_folder.name))
        csv_files = list(year_folder.glob("*.csv"))
=======
    Reads all CSV files named `cleaned_*.csv` inside the given folder,
    filters by department if specified, cleans the property values,
    and returns a list of processed DataFrames ready for aggregation.
>>>>>>> bp_analysis

    Args:
        year_folder (Path): Path to the folder corresponding to a given year.
        dept_filter (Optional[str]): Department code to include (e.g., "75" for Paris),
            or None to include all.

    Returns:
        List[pd.DataFrame]: A list of cleaned DataFrames containing
            columns: ["department_code", "department_name", "year", "property_value"].
    """
    year_str: str = "".join(filter(str.isdigit, year_folder.name))
    year: int = int(year_str) if year_str.isdigit() else 0
    dataframes: List[pd.DataFrame] = []

    for file in year_folder.glob("cleaned_*.csv"):
        dept_match: Optional[re.Match[str]] = re.search(r"_(\d{2,3})_", file.name)
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

<<<<<<< HEAD
    # ---- 2️. CURVES BY YEAR AND DEPARTMENT ----
    for year_folder in sorted(all_years):
        year = "".join(filter(str.isdigit, year_folder.name))
        csv_files = list(year_folder.glob("*.csv"))
=======
        except Exception as e:
            print(f" Error loading {file}: {e}")
>>>>>>> bp_analysis

    return dataframes


<<<<<<< HEAD
def property_trend(cleaned_path: str | Path, output_dir: str | Path, agg: str = "median") -> None:
=======
def display_trend(
    cleaned_path: Union[str, Path],
    dept_filter: Optional[str] = None,
    agg: str = "median",
    output_dir: Union[str, Path] = "docs/plots",
) -> None:
>>>>>>> bp_analysis
    """
    Display and save a trend plot of property values over time.

    Aggregates median or mean property values per year and department,
    then generates a line plot for all departments or a selected one.

    Args:
        cleaned_path (Union[str, Path]): Root path containing yearly folders with cleaned CSV files.
        dept_filter (Optional[str]): Department code (e.g., "75" for Paris) to focus on,
            or None to display all departments.
        agg (str): Aggregation method, either "median" or "mean". Defaults to "median".
        output_dir (Union[str, Path]): Directory where the generated plot is saved. Defaults to "docs/plots".

    Outputs:
        The function saves a `.png` plot file in the specified output directory and prints its path.
    """
    cleaned_root: Path = Path(cleaned_path)
    output_dir_path: Path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Load all yearly data
    all_data: List[pd.DataFrame] = [
        df
        for year_folder in sorted(cleaned_root.iterdir())
        if year_folder.is_dir()
        for df in _load_year_data(year_folder, dept_filter)
    ]

    if not all_data:
        print(" No data loaded.")
        return

    df_all: pd.DataFrame = pd.concat(all_data, ignore_index=True)

    # Aggregate by department and year
    agg_func: str = "mean" if agg == "mean" else "median"
    grouped: pd.core.groupby.GroupBy = df_all.groupby(["department_code", "department_name", "year"])
    trend_df: pd.DataFrame = grouped["property_value"].agg(agg_func).reset_index()

<<<<<<< HEAD
    # IMPROVEMENT 1: Calculate percentage change from first year
    trend_df = trend_df.sort_values(["department_code", "year"])
    trend_df["base_value"] = trend_df.groupby("department_code")["property_value"].transform("first")
    trend_df["pct_change"] = (trend_df["property_value"] / trend_df["base_value"] - 1) * 100

    # IMPROVEMENT 2: Distinct color palette
    unique_depts = trend_df["department_code"].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_depts)))

    # IMPROVEMENT 3: Department names (adapt based on your data)
    dept_names = {
        "76": "Seine-Maritime",
        "80": "Somme",
        "84": "Vaucluse",
        "88": "Vosges",
        "92": "Hauts-de-Seine",
        # Add other departments you have
    }

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # CHART 1: Percentage evolution (linear scale)
    for i, dept in enumerate(unique_depts):
        dept_data = trend_df[trend_df["department_code"] == dept]
        dept_name = dept_names.get(dept, f"Dept {dept}")

        ax1.plot(
            dept_data["year"],
            dept_data["pct_change"],
            marker="o",
            linewidth=2.5,
            markersize=6,
            color=colors[i],
            label=dept_name,
        )

    ax1.set_title("Property Price Evolution by Department (Base 100 in 2021)", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Evolution (%)")
    ax1.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax1.grid(True, alpha=0.3)

    # Add values on points
    for dept in unique_depts:
        dept_data = trend_df[trend_df["department_code"] == dept]
        for _, row in dept_data.iterrows():
            ax1.annotate(
                f"{row['pct_change']:.1f}%",
                (row["year"], row["pct_change"]),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=8,
            )

    # CHART 2: Median values in euros (log scale)
    for i, dept in enumerate(unique_depts):
        dept_data = trend_df[trend_df["department_code"] == dept]
        dept_name = dept_names.get(dept, f"Dept {dept}")

        ax2.plot(
            dept_data["year"],
            dept_data["property_value"],
            marker="s",
            linewidth=2,
            markersize=5,
            color=colors[i],
            label=dept_name,
        )

    ax2.set_title("Median Prices in Euros (Log Scale)", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Median Price (€)")
    ax2.set_yscale("log")  # Log scale
    ax2.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax2.grid(True, alpha=0.3)

    # Format y-axis in euros
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"€{x:,.0f}"))
=======
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
>>>>>>> bp_analysis

    # Formatting
    plt.xlabel("Année")
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: human_format(float(x))))
    plt.ylabel("Valeur médiane (€)")
    plt.legend(title="Département", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

<<<<<<< HEAD
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_dir) / f"propvalue_{agg}.png"
    plt.savefig(output_file, bbox_inches="tight", dpi=300)
    plt.close()

    print(f"Trend plot saved to {output_file}")
=======
    output_file: Path = output_dir_path / f"trend_{dept_filter or 'idf'}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f" Graph saved in {output_file}")


def human_format(num: float) -> str:
    """
    Convert a large number into a human-readable string with suffixes.

    Examples:
        >>> human_format(1200)
        '1.2 K'
        >>> human_format(2_500_000)
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
>>>>>>> bp_analysis
