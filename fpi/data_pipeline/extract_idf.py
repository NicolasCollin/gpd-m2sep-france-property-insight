from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.sql.elements import TextClause


def extract_idf(
    db_path: Path | str,
    table_name: str,
    csv_path: Path | str,
) -> None:
    """
    Export rows from a SQLite table corresponding to Ile-de-France departments to a CSV file.

    Args:
        db_path (Path | str): Path to the SQLite database.
        table_name (str): Name of the table to query.
        csv_path (Path | str): Path where the CSV file will be saved.
    """
    db_path: Path = Path(db_path)
    csv_path: Path = Path(csv_path)

    # Ensure parent directories exist
    csv_parent: Path = csv_path.parent
    csv_parent.mkdir(parents=True, exist_ok=True)

    # Connect to SQLite
    engine: Engine = create_engine(f"sqlite:///{db_path}")

    # Ile-de-France department codes
    idf_departments: list[str] = ["75", "77", "78", "91", "92", "93", "94", "95"]

    # Prepare SQL query
    placeholders: str = ", ".join(f"'{code}'" for code in idf_departments)
    query: TextClause = text(f"""
        SELECT *
        FROM {table_name}
        WHERE Code_departement IN ({placeholders})
    """)

    # Execute query and load into DataFrame
    with engine.connect() as conn:
        conn_type: Connection = conn
        df: pd.DataFrame = pd.read_sql(query, conn_type)

    # Save to CSV
    df.to_csv(csv_path, index=False)
    row_count: int = len(df)
    print(f"Exported {row_count} rows to {csv_path.resolve()}")


if __name__ == "__main__":
    extract_idf(db_path="data/raw/raw2023.db", table_name="raw_2023", csv_path="data/raw/raw_idf2023.csv")
