from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine, Result


def count_rows_per_department(
    db_path: Path | str,
    table_name: str,
) -> None:
    """
    Count the number of rows per department in a given SQLite table.

    Args:
        db_path (Path | str): Path to the SQLite database.
        table_name (str): Name of the table to query.
    """
    db_path: Path = Path(db_path)

    # Connect to SQLite
    engine: Engine = create_engine(f"sqlite:///{db_path}")

    # Prepare SQL query
    query_str: str = f"""
        SELECT Code_departement, COUNT(*) AS nb_lignes
        FROM {table_name}
        GROUP BY Code_departement
        ORDER BY nb_lignes DESC;
    """
    query: text = text(query_str)

    # Execute query
    with engine.connect() as conn:
        conn_type: Connection = conn
        result: Result = conn_type.execute(query)

        # Print counts per department
        for row in result:
            code: str = row.Code_departement
            nb: int = row.nb_lignes
            print(f"Département {code}: {nb} lignes")
