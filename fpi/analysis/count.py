from pathlib import Path
from typing import Union

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Result


def count_rows_per_department(
    db_path: Union[Path, str],
    table_name: str,
) -> None:
    """
    Count the number of rows per department in a given SQLite table.

    Args:
        db_path: Path to the SQLite database.
        table_name: Name of the table to query.
    """

    # Convert to Path object
    db_path_obj: Path = Path(db_path)

    # Connect to SQLite
    engine: Engine = create_engine(f"sqlite:///{db_path_obj}")

    # Prepare SQL query (text() is a function, do not type it)
    query_str: str = f"""
        SELECT Code_departement, COUNT(*) AS nb_lignes
        FROM {table_name}
        GROUP BY Code_departement
        ORDER BY nb_lignes DESC;
    """
    query = text(query_str)  # no type hint here

    # Execute query
    with engine.connect() as conn:
        result: Result = conn.execute(query)

        # Print counts per department
        for row in result:
            code: str = row.Code_departement
            nb: int = row.nb_lignes
            print(f"Département {code}: {nb} lignes")


if __name__ == "__main__":
    count_rows_per_department("data/raw/raw_idf2023.db", "raw_idf_2023")
