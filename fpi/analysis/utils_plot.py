from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def save_hist(df: pd.DataFrame, cols: list[str], output_dir: str) -> None:
    """
    Save histogram plots with log scale for numeric variables.

    :param df: DataFrame
    :param cols: List of numeric columns
    :param output_dir: Folder to save .png plots
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for col in cols:
        plt.figure(figsize=(8, 5))
        plt.hist(df[col].dropna(), bins=30, color="lightblue")
        plt.yscale("log")
        plt.title(f"Distribution of {col} (log scale)")
        plt.xlabel(col)
        plt.ylabel("Count (log)")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/{col}_hist.png")
        plt.close()
def save_lv(df: pd.DataFrame, col: str, output_dir: str) -> None: 
    """ 
    Save a boxplot for land value. Cleans the column to ensure numeric values.
     :param df: DataFrame containing the land value column 
     :param col: Name of the land value column 
     :param output_dir: Folder to save the boxplot .png 
     """ 
    Path(output_dir).mkdir(parents=True, exist_ok=True)
      # Work on a copy to avoid SettingWithCopyWarning 
    df_clean = df.copy() 
      # Clean the column: remove € symbol, spaces, commas, and convert to numeric
    df_clean[col] = ( df_clean[col] .astype(str) .str.replace("€", "", regex=False) .str.replace(",", "", regex=False) .str.replace(" ", "", regex=False) )
    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
      # Filter out missing or non-positive values 
    df_filtered = df_clean[df_clean[col].notna() & (df_clean[col] > 0)] 
      # Plot the boxplot
    plt.figure(figsize=(8, 6)) 
    sns.boxplot(y=df_filtered[col], color="skyblue") 
    plt.yscale("log")
    plt.ylabel(col) 
    plt.title(f"Boxplot of {col}") 
    plt.tight_layout() 
    plt.savefig(f"{output_dir}/{col}_boxplot.png") 
    plt.close()