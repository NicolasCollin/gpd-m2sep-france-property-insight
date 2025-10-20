import sqlite3
from pathlib import Path

import pandas as pd


def txt_to_sqlite(
    txt_path: str,
    db_path: str,
    table_name: str,
    delimiter: str = "|",
    chunksize: int | None = None,
) -> None:
    """
    Convert a text file (CSV-like) into a SQLite .db file.

    Args:
        txt_path (str): Path to the input text file.
        db_path (str): Path where the .db file will be saved.
        table_name (str): Name of the SQL table to create.
        delimiter (str): Column separator (default: '|').
        chunksize (int | None): Number of rows per chunk to process (for large files).
    """

    txt_path = Path(txt_path)
    db_path = Path(db_path)

    # Create parent folders if needed
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect (or create) database
    conn = sqlite3.connect(db_path)

    # Load the TXT file (all at once or in chunks)
    if chunksize:
        for i, chunk in enumerate(pd.read_csv(txt_path, delimiter=delimiter, chunksize=chunksize, low_memory=False)):
            chunk.columns = [col.strip().replace(" ", "_").replace("’", "_").replace("'", "_") for col in chunk.columns]
            chunk.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"Chunk {i+1} inserted ({len(chunk)} rows)")
    else:
        df = pd.read_csv(txt_path, delimiter=delimiter, low_memory=False)
        df.columns = [col.strip().replace(" ", "_").replace("’", "_").replace("'", "_") for col in df.columns]
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Inserted {len(df)} rows into table '{table_name}'")

    # Quick preview
    preview = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 5", conn)
    print(preview)

    conn.close()
    print(f"Database saved at: {db_path.resolve()}")


if __name__ == "__main__":
    txt_to_sqlite(
        txt_path="data/raw/raw2024.txt",
        db_path="data/raw/raw2024.db",
        table_name="raw_2024",
        delimiter="|",
    )
