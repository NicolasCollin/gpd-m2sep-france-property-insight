from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine(db_path: str = "data/sql/app.db") -> Engine:
    """
    Create a SQLAlchemy engine for a SQLite database.

    Args:
        db_path (str | None):
            Path to the SQLite database file. If not provided, the default
            application database path is used.

    Returns (Engine): A SQLAlchemy Engine instance connected to the SQLite database.
    """
    db_file: pd.DataFrame = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    url: str = f"sqlite:///{db_file}"
    engine: Engine = create_engine(url)
    return engine


def migrate_csv(
    csv_path: str | Path,
    engine: Engine | None = None,
    table_name: str | None = None,
) -> None:
    """
    Load a CSV file into a SQLite database table.

    Args:
        csv_path (str | Path):
            Path to the CSV file to load.
        engine (Engine | None):
            Existing SQLAlchemy engine. If not provided, a new engine is created.
        table_name (str | None):
            Name of the SQL table. If omitted, the CSV filename (without extension)
            is used as the table name.

    Returns : None
    """
    path: Path = Path(csv_path)
    eng: Engine = engine or get_engine()
    name: str = table_name or path.stem
    df: pd.DataFrame = pd.read_csv(path, decimal=",")
    df.to_sql(name, con=eng, if_exists="replace", index=False)


def migrate_all_cleaned(
    engine: Engine | None = None,
    cleaned_root: str = "data/cleaned",
) -> None:
    """
    Load all cleaned CSV files into the SQLite database.

    This function scans the cleaned data directory recursively and loads each
    CSV file into the database. Each file is stored in a table named after
    the CSV filename (without extension).

    Args:
        engine (Engine | None):
            Existing SQLAlchemy engine. If not provided, a new engine is used.
        cleaned_root (str | None):
            Root directory containing cleaned CSV files.

    Returns: None

    Raises:
        FileNotFoundError
            If the cleaned data directory does not exist or contains no CSV files.
    """
    root: Path = Path(cleaned_root)
    if not root.exists():
        raise FileNotFoundError(f"Cleaned data directory not found: {root}")

    eng: Engine = engine or get_engine()
    csv_files: list[Path] = list(root.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under {root}")

    for csv_path in csv_files:
        migrate_csv(csv_path=csv_path, engine=eng)
