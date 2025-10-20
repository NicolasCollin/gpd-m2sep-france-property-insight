import sqlite3
from pathlib import Path

import pandas as pd


def txt_to_sqlite(
    txt_path: Path | str,
    db_path: Path | str,
    table_name: str,
    delimiter: str = "|",
    chunksize: int | None = None,
) -> None:
    """
    Convert a text file (CSV-like) into a SQLite .db file.

    Args:
        txt_path (Path | str): Path to the input text file.
        db_path (Path | str): Path where the .db file will be saved.
        table_name (str): Name of the SQL table to create.
        delimiter (str): Column separator (default: '|').
        chunksize (int | None): Number of rows per chunk to process (for large files).
    """

    # Ensure paths are Path objects
    txt_path: Path = Path(txt_path)
    db_path: Path = Path(db_path)

    # Create parent folders if they do not exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to SQLite database
    conn: sqlite3.Connection = sqlite3.connect(db_path)

    # Helper function to clean column names
    def clean_columns(columns: list[str]) -> list[str]:
        cleaned: list[str] = [col.strip().replace(" ", "_").replace("’", "_").replace("'", "_") for col in columns]
        return cleaned

    # Load and insert data
    if chunksize:
        for i, chunk in enumerate(pd.read_csv(txt_path, delimiter=delimiter, chunksize=chunksize, low_memory=False)):
            chunk: pd.DataFrame
            chunk.columns = clean_columns(list(chunk.columns))
            chunk.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"Chunk {i+1} inserted ({len(chunk)} rows)")
    else:
        df: pd.DataFrame = pd.read_csv(txt_path, delimiter=delimiter, low_memory=False)
        df.columns = clean_columns(list(df.columns))
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Inserted {len(df)} rows into table '{table_name}'")

    # Quick preview
    preview: pd.DataFrame = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 5", conn)
    print(preview)

    conn.close()
    print(f"Database saved at: {db_path.resolve()}")


if __name__ == "__main__":
    txt_to_sqlite(
        txt_path="data/raw/raw_idf2023.csv", db_path="data/raw/raw_idf2023.db", table_name="raw_idf_2023", delimiter=","
    )
