import pandas as pd
from pathlib import Path

def statdes(df: pd.DataFrame, output_dir: str = "docs/stats") -> pd.DataFrame:
    """
    Compute and save descriptive statistics for a given dataset.

    :param df: Input DataFrame
    :param output_dir: Folder where results will be saved
    :return: Summary DataFrame with descriptive statistics
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

   
    desc = df.describe(include="all").transpose()
    corr = df.corr(numeric_only=True)

    # save results
    desc.to_csv(f"{output_dir}/descriptive_stats.csv", index=True)
    corr.to_csv(f"{output_dir}/correlation_matrix.csv", index=True)

    # quick review
    print(" Descriptive statistics ")
    print(desc[["count", "mean", "std", "min", "50%", "max"]].head())

    print("\nCorrelation matrix (numeric vars)")
    print(corr.head())

    print(f"\nStats saved in: {output_dir}/")
    return desc
