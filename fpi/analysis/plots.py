from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from fpi.data_pipeline.loader import load_all_csv
from fpi.utils.constants import DEPT_NAMES


def convert_value_for_display(value: float) -> str:
    """
    Convert a numeric value into a readable format using French decimal style
    and compact suffixes (K, M, Md).
    """
    thresholds = [
        (1_000_000_000, " Md"),
        (1_000_000, " M"),
        (1_000, " K"),
    ]
    for threshold, suffix in thresholds:
        if abs(value) >= threshold:
            formatted = f"{value / threshold:.1f}".replace(".", ",")
            return f"{formatted}{suffix}"
    return f"{value:.1f}".replace(".", ",")


def display_trend(
    cleaned_path: Path | str,
    dept_filter: str | None,
    agg: str = "median",
    output_dir: Path | str = "docs/plots",
) -> None:
    """
    Load all cleaned real estate data, compute yearly aggregated values
    (median or mean), and generate a trend line plot.

    Parameters
    ----------
    cleaned_path : Path or str
        Root directory containing cleaned CSV files.
    dept_filter : str or None
        Department code to plot exclusively. If None, all departments are shown.
    agg : str
        Aggregation method: "median" (default) or "mean".
    output_dir : Path or str
        Folder where the resulting plot is saved.
    """
    df_all: pd.DataFrame = load_all_csv(str(cleaned_path))

    if "property_value" not in df_all.columns:
        raise KeyError("Missing required column: 'property_value'")

    # Derive year if necessary
    if "year" not in df_all.columns:
        if "transaction_date" in df_all.columns:
            df_all["year"] = pd.to_datetime(
                df_all["transaction_date"],
                dayfirst=True,
                errors="coerce",
            ).dt.year
        else:
            raise KeyError("Missing required column: 'year' (and no 'transaction_date' to derive it).")

    # Derive department_code if necessary
    if "department_code" not in df_all.columns:
        if "postal_code" in df_all.columns:
            df_all["department_code"] = df_all["postal_code"].astype(str).str[:2]
        else:
            raise KeyError("Missing required column: 'department_code' (and no 'postal_code' to derive it).")

    df_all = df_all[df_all["property_value"].notna() & (df_all["property_value"] > 0)]
    if df_all.empty:
        print("No usable property values after filtering.")
        return

    if "department_name" not in df_all.columns:
        df_all["department_code"] = df_all["department_code"].astype(str)
        df_all["department_name"] = df_all["department_code"].map(lambda code: DEPT_NAMES.get(code, f"Department {code}"))

    if dept_filter:
        df_all = df_all[df_all["department_code"].astype(str) == str(dept_filter)]
        if df_all.empty:
            print(f"No data found for department {dept_filter}.")
            return

    agg_func = "mean" if agg == "mean" else "median"
    label_metric = "Mean" if agg_func == "mean" else "Median"

    trend_df = df_all.groupby(["department_code", "department_name", "year"], as_index=False)["property_value"].agg(agg_func)
    if trend_df.empty:
        print("Aggregation produced no data.")
        return

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    if dept_filter:
        dept_name = trend_df["department_name"].iloc[0]
        sns.lineplot(
            data=trend_df,
            x="year",
            y="property_value",
            marker="o",
            linewidth=2.5,
            color="steelblue",
            label=f"{dept_name} ({dept_filter})",
        )
        plt.title(f"{label_metric} Real Estate Price Trend — {dept_name}")
    else:
        sns.lineplot(
            data=trend_df,
            x="year",
            y="property_value",
            hue="department_name",
            marker="o",
            linewidth=2.5,
        )
        plt.title(f"{label_metric} Real Estate Price Trends — Île-de-France")

    plt.xlabel("Year")
    plt.ylabel(f"{label_metric} Property Value (€)")

    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: convert_value_for_display(x)))

    plt.legend(title="Department", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    output_file = output_dir_path / f"trend_{dept_filter or 'idf'}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Plot saved to {output_file}")
