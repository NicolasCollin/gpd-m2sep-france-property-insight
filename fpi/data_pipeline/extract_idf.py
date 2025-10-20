from pathlib import Path
from typing import List, Union

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def extract_idf(
    db_path: Union[Path, str],
    table_name: str,
    csv_path: Union[Path, str],
) -> None:
    """
    Export rows from a SQLite table corresponding to Ile-de-France departments to a CSV file.

    Args:
        db_path: Path to the SQLite database.
        table_name: Name of the table to query.
        csv_path: Path where the CSV file will be saved.
    """

    # Convert to Path objects
    db_path_obj: Path = Path(db_path)
    csv_path_obj: Path = Path(csv_path)

    # Ensure parent directories exist
    csv_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Connect to SQLite
    engine: Engine = create_engine(f"sqlite:///{db_path_obj}")

    # Ile-de-France department codes
    idf_departments: List[str] = ["75", "77", "78", "91", "92", "93", "94", "95"]

    # Prepare SQL query
    placeholders: str = ", ".join(f"'{code}'" for code in idf_departments)
    query = text(f"""
        SELECT *
        FROM {table_name}
        WHERE Code_departement IN ({placeholders})
    """)

    # Execute query and load into DataFrame
    with engine.connect() as conn:  # type: Connection
        df: pd.DataFrame = pd.read_sql(query, conn)

    # Save to CSV
    df.to_csv(csv_path_obj, index=False)
    print(f"Exported {len(df)} rows to {csv_path_obj.resolve()}")


if __name__ == "__main__":
    extract_idf(
        db_path="data/raw/raw2023.db",
        table_name="raw_2023",
        csv_path="data/raw/raw_idf2023.csv",
    )
