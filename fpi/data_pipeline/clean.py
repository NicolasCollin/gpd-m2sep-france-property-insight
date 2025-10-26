from typing import List

import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

from fpi.utils.constants import VARS_TO_KEEP_SQL


def drop_missing_rows(df: DataFrame, cols: List[str]) -> DataFrame:
    """
    Remove rows with missing values in the specified columns.

    Args:
        df (DataFrame): Input DataFrame.
        cols (List[str]): Columns to check for missing values.

    Returns:
        DataFrame: DataFrame without rows containing NA in the specified columns.
    """
    return df.dropna(subset=cols)


def filter_columns(input_db: str, output_db: str) -> None:
    """
    Create a new SQLite DB keeping only selected columns and removing rows with missing values.

    Args:
        input_db (str): Path to the input .db file (e.g. 'data/raw/sample2024.db')
        output_db (str): Path to the output .db file (e.g. 'data/cleaned/sample2024.db')
    """

    # Connect to databases
    engine_in: Engine = create_engine(f"sqlite:///{input_db}")
    engine_out: Engine = create_engine(f"sqlite:///{output_db}")

    inspector = inspect(engine_in)
    tables: List[str] = inspector.get_table_names()

    for table in tables:
        print(f"Processing table: {table}")

        df: DataFrame = pd.read_sql_table(table, engine_in)

        # Keep only requested columns that exist in the table
        existing_cols: List[str] = [col for col in VARS_TO_KEEP_SQL if col in df.columns]
        df_filtered: DataFrame = df[existing_cols]

        # Drop rows with missing values
        df_filtered = drop_missing_rows(df_filtered, existing_cols)

        # Write to the new database
        df_filtered.to_sql(table, engine_out, index=False, if_exists="replace")

    print(f"New database filtered by columns saved to: {output_db}")


if __name__ == "__main__":
    input_path: str = "data/raw/sample2024.db"
    output_path: str = "data/cleaned/sample2024.db"
    filter_columns(input_path, output_path)
