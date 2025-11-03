from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re


def save_hist(df: pd.DataFrame, cols: list[str], output_dir: str) -> None:
    """
    Save histogram plots with better scaling and outlier handling.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for col in cols:
        if col not in df.columns:
            print(f" Column {col} not found.")
            continue

        # Clean and filter data
        data = df[col].dropna()
        
        # Remove outliers using IQR method
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        filtered_data = data[(data >= lower_bound) & (data <= upper_bound)]
        
        # Create subplots: original vs filtered
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Original data (with outliers)
        counts_orig, bins_orig, _ = ax1.hist(data, bins=50, color='lightcoral', 
                                           edgecolor='black', alpha=0.7)
        ax1.set_title(f'{col} - Original (with outliers)\nN={len(data):,}', 
                     fontweight='bold')
        ax1.set_xlabel(col)
        ax1.set_ylabel('Count')
        ax1.grid(True, alpha=0.3)
        ax1.ticklabel_format(style='plain')
        
        # Add value labels on bars (top 5 only)
        max_counts = sorted(set(counts_orig), reverse=True)[:5]
        for count, bin_val in zip(counts_orig, bins_orig[:-1]):
            if count in max_counts and count > 0:
                ax1.text(bin_val + (bins_orig[1]-bins_orig[0])/2, count, 
                        f'{int(count):,}', ha='center', va='bottom', fontsize=8)
        
        # Plot 2: Filtered data (without outliers)
        if len(filtered_data) > 0:
            counts_filt, bins_filt, _ = ax2.hist(filtered_data, bins=30, 
                                               color='lightblue', edgecolor='black')
            ax2.set_title(f'{col} - Without Outliers\nN={len(filtered_data):,}', 
                         fontweight='bold')
            ax2.set_xlabel(col)
            ax2.set_ylabel('Count')
            ax2.grid(True, alpha=0.3)
            
            # Add value labels on bars (top 5 only)
            max_counts_filt = sorted(set(counts_filt), reverse=True)[:5]
            for count, bin_val in zip(counts_filt, bins_filt[:-1]):
                if count in max_counts_filt and count > 0:
                    ax2.text(bin_val + (bins_filt[1]-bins_filt[0])/2, count, 
                            f'{int(count):,}', ha='center', va='bottom', fontsize=8)
        else:
            ax2.text(0.5, 0.5, 'No data after filtering', 
                    ha='center', va='center', transform=ax2.transAxes)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/{col}_hist_improved.png", dpi=300, bbox_inches='tight')
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

    Args:
        cleaned_path (str | Path): Path to the folder containing year subfolders.
        var (str): The numeric variable to plot (e.g., "property_value").
        output_dir (str | Path): Directory where the plot will be saved.
    """
    cleaned_root = Path(cleaned_path)
    all_years = [f for f in cleaned_root.iterdir() if f.is_dir()]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    sns.set_style("whitegrid")

    # ---- 1️. CURVES ACROSS YEARS ----
    plt.figure(figsize=(10, 6))
    data_loaded = False

    for year_folder in sorted(all_years):
        year = ''.join(filter(str.isdigit, year_folder.name))
        csv_files = list(year_folder.glob("*.csv"))

        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if var not in df.columns:
                    continue

                # Clean numeric variable
                df[var] = (
                    df[var]
                    .astype(str)
                    .str.replace("€", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.replace(" ", "", regex=False)
                )
                df[var] = pd.to_numeric(df[var], errors="coerce")
                dfs.append(df[[var]])
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")

        if not dfs:
            continue

        df_year = pd.concat(dfs, ignore_index=True)
        df_year = df_year[df_year[var].notna() & (df_year[var] > 0)]
        if df_year.empty:
            continue

        sns.kdeplot(df_year[var], label=year, linewidth=2)
        data_loaded = True

    if data_loaded:
        plt.title(f"Density Curves of {var} Across Years")
        plt.xlabel(var)
        plt.ylabel("Density")
        plt.legend(title="Year")
        plt.tight_layout()
        plt.savefig(Path(output_dir) / f"{var}_curves_by_year.png")
        plt.close()
        print(f" Saved global curves by year to {output_dir}")
    else:
        print(" No valid data for any year.")

    # ---- 2️. CURVES BY YEAR AND DEPARTMENT ----
    for year_folder in sorted(all_years):
        year = ''.join(filter(str.isdigit, year_folder.name))
        csv_files = list(year_folder.glob("*.csv"))

        plt.figure(figsize=(10, 6))
        has_data = False

        for csv_file in csv_files:
            dept_match = re.search(r"_(\d{2,3})_", csv_file.name)
            dept_code = dept_match.group(1) if dept_match else "unknown"

            try:
                df = pd.read_csv(csv_file)
                if var not in df.columns:
                    continue

                df[var] = (
                    df[var]
                    .astype(str)
                    .str.replace("€", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.replace(" ", "", regex=False)
                )
                df[var] = pd.to_numeric(df[var], errors="coerce")
                df = df[df[var].notna() & (df[var] > 0)]

                if not df.empty:
                    sns.kdeplot(df[var], label=f"Dept {dept_code}", linewidth=1.8)
                    has_data = True

            except Exception as e:
                print(f" Error loading {csv_file}: {e}")

        if has_data:
            plt.title(f"{var} — Density by Department ({year})")
            plt.xlabel(var)
            plt.ylabel("Density")
            plt.legend(title="Department")
            plt.tight_layout()
            plt.savefig(Path(output_dir) / f"{var}_curves_{year}_by_dept.png")
            plt.close()
            print(f"Saved curves by department for {year}")
        else:
            print(f"No valid data for {year}")


def property_trend(
    cleaned_path: str | Path,
    output_dir: str | Path,
    agg: str = "median"
) -> None:
    """
    Plot trend of property values by department over multiple years.

    Args:
        cleaned_path (str | Path): Path to the main folder containing yearly cleaned data (e.g., data/cleaned).
        output_dir (str | Path): Directory where the plot will be saved.
        agg (str): Aggregation method, either "mean" or "median". Default is "median".
    """

    cleaned_dir = Path(cleaned_path)
    all_files = sorted(cleaned_dir.rglob("cleaned_*.csv"))

    if not all_files:
        print("No cleaned CSV files found.")
        return

    data_frames = []
    for file in all_files:
        # Extract year from file name
        year_part = file.stem.split("_")[-1]
        try:
            year = int(year_part)
        except ValueError:
            print(f"Skipping {file.name} (no valid year)")
            continue

        df = pd.read_csv(file)

        # Ensure expected columns exist
        if "property_value" not in df.columns or "department_code" not in df.columns:
            print(f"Missing columns in {file.name}")
            continue

        # Clean property_value
        df["property_value"] = (
            df["property_value"]
            .astype(str)
            .str.replace("€", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
        )
        df["property_value"] = pd.to_numeric(df["property_value"], errors="coerce")

        df = df[df["property_value"].notna() & (df["property_value"] > 0)]
        df["year"] = year

        data_frames.append(df)

    if not data_frames:
        print("No valid data available for plotting.")
        return

    df_all = pd.concat(data_frames, ignore_index=True)

    # Aggregate by department and year
    if agg == "mean":
        trend_df = df_all.groupby(["department_code", "year"])["property_value"].mean().reset_index()
    else:  # median by default
        trend_df = df_all.groupby(["department_code", "year"])["property_value"].median().reset_index()

    # IMPROVEMENT 1: Calculate percentage change from first year
    trend_df = trend_df.sort_values(['department_code', 'year'])
    trend_df['base_value'] = trend_df.groupby('department_code')['property_value'].transform('first')
    trend_df['pct_change'] = (trend_df['property_value'] / trend_df['base_value'] - 1) * 100

    # IMPROVEMENT 2: Distinct color palette
    unique_depts = trend_df['department_code'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_depts)))
    
    # IMPROVEMENT 3: Department names (adapt based on your data)
    dept_names = {
        '76': 'Seine-Maritime',
        '80': 'Somme', 
        '84': 'Vaucluse',
        '88': 'Vosges',
        '92': 'Hauts-de-Seine'
        # Add other departments you have
    }

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # CHART 1: Percentage evolution (linear scale)
    for i, dept in enumerate(unique_depts):
        dept_data = trend_df[trend_df['department_code'] == dept]
        dept_name = dept_names.get(dept, f"Dept {dept}")
        
        ax1.plot(dept_data['year'], dept_data['pct_change'], 
                marker='o', linewidth=2.5, markersize=6, 
                color=colors[i], label=dept_name)
    
    ax1.set_title('Property Price Evolution by Department (Base 100 in 2021)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Evolution (%)')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Add values on points
    for dept in unique_depts:
        dept_data = trend_df[trend_df['department_code'] == dept]
        for _, row in dept_data.iterrows():
            ax1.annotate(f"{row['pct_change']:.1f}%", 
                        (row['year'], row['pct_change']),
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center', 
                        fontsize=8)

    # CHART 2: Median values in euros (log scale)
    for i, dept in enumerate(unique_depts):
        dept_data = trend_df[trend_df['department_code'] == dept]
        dept_name = dept_names.get(dept, f"Dept {dept}")
        
        ax2.plot(dept_data['year'], dept_data['property_value'], 
                marker='s', linewidth=2, markersize=5, 
                color=colors[i], label=dept_name)
    
    ax2.set_title('Median Prices in Euros (Log Scale)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Median Price (€)')
    ax2.set_yscale('log')  # Log scale
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Format y-axis in euros
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))

    plt.tight_layout()

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_dir) / f"propvalue_{agg}.png"
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    plt.close()

    print(f"Trend plot saved to {output_file}")