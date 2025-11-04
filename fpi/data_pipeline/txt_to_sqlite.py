import sqlite3
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd


def txt_to_sqlite(
    txt_path: Union[Path, str],
    db_path: Union[Path, str],
    table_name: str,
    delimiter: str = "|",
    chunksize: Optional[int] = None,
) -> None:
    """
    Convert a text file (CSV-like) into a SQLite .db file.

    Args:
        - txt_path: Path to the input text file.
        - db_path: Path where the .db file will be saved.
        - table_name: Name of the SQL table to create.
        - delimiter: Column separator (default: '|').
        - chunksize: Number of rows per chunk to process (for large files).

    Returns:
        - None

    Output:
        - Save SQLite .db file to db_path.
    """

    # Ensure paths are Path objects
    txt_path_obj: Path = Path(txt_path)
    db_path_obj: Path = Path(db_path)

    # Create parent folders if they do not exist
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Connect to SQLite database
    conn: sqlite3.Connection = sqlite3.connect(db_path_obj)

    # Helper function to clean column names
    def clean_columns(columns: List[str]) -> List[str]:
        return [col.strip().replace(" ", "_").replace("’", "_").replace("'", "_") for col in columns]

    # Load and insert data
    if chunksize:
        for idx, chunk_df in enumerate(
            pd.read_csv(txt_path_obj, delimiter=delimiter, chunksize=chunksize, low_memory=False)
        ):
            # chunk_df is a pd.DataFrame
            chunk_df.columns = clean_columns(list(chunk_df.columns))
            chunk_df.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"Chunk {idx+1} inserted ({len(chunk_df)} rows)")
    else:
        df: pd.DataFrame = pd.read_csv(txt_path_obj, delimiter=delimiter, low_memory=False)
        df.columns = clean_columns(list(df.columns))
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Inserted {len(df)} rows into table '{table_name}'")

    # Quick preview
    preview: pd.DataFrame = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 5", conn)
    print(preview)

    conn.close()
    print(f"Database saved at: {db_path_obj.resolve()}")


if __name__ == "__main__":
    txt_to_sqlite(
        txt_path="data/raw/sample2024.txt",
        db_path="data/raw/sample2024.db",
        table_name="sample_2024",
        delimiter="|",
    )
