
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import matplotlib.ticker as mticker


DEPT_NAMES = {
    "75": "Paris",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d’Oise"
}

def display_trend(cleaned_path: str | Path, 
                  dept_filter: str | None = None,
                  agg: str = "median",
                  output_dir: str | Path = "docs/plots") -> None:
    """
    Display a trend of property values over time for all or a specific department.
    """
    cleaned_root = Path(cleaned_path)
    all_years = [f for f in cleaned_root.iterdir() if f.is_dir()]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    all_data = []

    for year_folder in sorted(all_years):
        year = ''.join(filter(str.isdigit, year_folder.name))
        csv_files = list(year_folder.glob("cleaned_*.csv"))

        for file in csv_files:
            dept_match = re.search(r"_(\d{2,3})_", file.name)
            dept_code = dept_match.group(1) if dept_match else "unknown"

            # department filter
            if dept_filter and dept_code != dept_filter:
                continue

            try:
                df = pd.read_csv(file)

                if "property_value" not in df.columns:
                    continue

                # cleaning
                df["property_value"] = (
                    df["property_value"]
                    .astype(str)
                    .str.replace("€", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.replace(" ", "", regex=False)
                )
                df["property_value"] = pd.to_numeric(df["property_value"], errors="coerce")
                df = df[df["property_value"].notna() & (df["property_value"] > 0)]

                if not df.empty:
                    df["year"] = int(year)
                    df["department_code"] = dept_code
                    df["department_name"] = DEPT_NAMES.get(dept_code, f"Département {dept_code}")
                    all_data.append(df[["department_code", "department_name", "year", "property_value"]])

            except Exception as e:
                print(f" Error loading {file}: {e}")

    if not all_data:
        print(" No data loaded.")
        return

    df_all = pd.concat(all_data, ignore_index=True)

    # Agreggation
    if agg == "mean":
        trend_df = df_all.groupby(["department_code", "department_name", "year"])["property_value"].mean().reset_index()
    else:
        trend_df = df_all.groupby(["department_code", "department_name", "year"])["property_value"].median().reset_index()

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    if dept_filter:
        dept_df = trend_df[trend_df["department_code"] == dept_filter]
        sns.lineplot(
            data=dept_df,
            x="year", y="property_value",
            marker="o", linewidth=2.5,
            color="steelblue",
            label=f"{dept_df['department_name'].iloc[0]} ({dept_filter})"
        )
        plt.title(f"Évolution des prix immobiliers — {dept_df['department_name'].iloc[0]}")
    else:
        sns.lineplot(
            data=trend_df,
            x="year", y="property_value",
            hue="department_name",
            marker="o", linewidth=2.5
        )
        plt.title("Évolution des prix immobiliers — Île-de-France")

    plt.xlabel("Année")

    
    def human_format(num):
        for unit in ["", " K", " M", " Md"]:
            if abs(num) < 1000:
                return f"{num:.1f}{unit}"
            num /= 1000
        return f"{num:.1f} Md"

    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: human_format(x)))
    plt.ylabel("Valeur médiane (€)")
    plt.legend(title="Département", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    output_file = Path(output_dir) / f"trend_{dept_filter or 'idf'}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f" Graph saved in {output_file}")

