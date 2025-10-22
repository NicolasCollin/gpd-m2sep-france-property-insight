from pathlib import Path

# import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")  # backend non interactif, adapté aux tests/serveurs
import matplotlib.pyplot as plt
import pandas as pd


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
