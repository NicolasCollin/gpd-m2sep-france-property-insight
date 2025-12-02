from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

DATA_DIR: Path = Path("data")
CLEANED_DIR: Path = DATA_DIR / "cleaned"
SQL_DIR: Path = DATA_DIR / "sql"
DB_PATH: Path = SQL_DIR / "app.db"


def get_engine(db_path: Path = DB_PATH) -> Engine:
    """
    Create a SQLAlchemy engine for a SQLite database.

    Parameters
    ----------
    db_path : Path, optional
        Path to the SQLite database file. If not provided, the default
        application database path is used.

    Returns
    -------
    Engine
        A SQLAlchemy Engine instance connected to the SQLite database.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_path}"
    engine: Engine = create_engine(url)
    return engine


def migrate_csv(
    csv_path: Path,
    engine: Optional[Engine] = None,
    table_name: Optional[str] = None,
) -> None:
    """
    Load a CSV file into a SQLite database table.

    Parameters
    ----------
    csv_path : Path
        Path to the CSV file to load.
    engine : Engine, optional
        Existing SQLAlchemy engine. If not provided, a new engine is created.
    table_name : str, optional
        Name of the SQL table. If omitted, the CSV filename (without extension)
        is used as the table name.

    Returns
    -------
    None
    """
    eng = engine or get_engine()
    name = table_name or csv_path.stem
    df = pd.read_csv(csv_path)
    df.to_sql(name, con=eng, if_exists="replace", index=False)


def migrate_all_cleaned(engine: Optional[Engine] = None) -> None:
    """
    Load all cleaned CSV files into the SQLite database.

    This function scans the cleaned data directory recursively and loads each
    CSV file into the database. Each file is stored in a table named after
    the CSV filename (without extension).

    Parameters
    ----------
    engine : Engine, optional
        Existing SQLAlchemy engine. If not provided, a new engine is used.

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        If the cleaned data directory does not exist or contains no CSV files.
    """
    if not CLEANED_DIR.exists():
        raise FileNotFoundError(f"Cleaned data directory not found: {CLEANED_DIR}")

    eng = engine or get_engine()
    csv_files = list(CLEANED_DIR.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under {CLEANED_DIR}")

    for csv_path in csv_files:
        migrate_csv(csv_path=csv_path, engine=eng)
