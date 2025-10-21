import pandas as pd


def print_info(df: pd.DataFrame) -> None:
    """Print basic dataset information."""
    print("\n===== HEAD =====")
    print(df.head(), "\n")

    print("===== INFO =====")
    # print(df.info(), "\n")\
    df.info()

    print(f"\nShape: {df.shape[0]} rows × {df.shape[1]} columns\n")

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        print("Missing values:\n", missing, "\n")
