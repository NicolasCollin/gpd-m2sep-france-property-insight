from pathlib import Path
from typing import Optional, Union

# from typing has to be removed in modern python
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

DB_PATH: str = "data/sql/app.db"

# if you only use DB_PATH once as a default value for a function just define it in its declaration
# dbpath: str = "data/sql/app.db"


def get_engine(db_path: str = DB_PATH) -> Engine:
    """
    Create a SQLAlchemy engine for a SQLite database.

    Parameters
    ----------
    db_path : str, optional
        Path to the SQLite database file. If not provided, the default
        application database path is used.

    Returns
    -------
    Engine
        A SQLAlchemy Engine instance connected to the SQLite database.
    """
    # missing type annotation
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_file}"
    # t'as fait le type annotation q'une seule fois mdr
    engine: Engine = create_engine(url)
    return engine


def migrate_csv(
    # use | instead of Union or Optional, good type hinting
    csv_path: Union[str, Path],
    engine: Optional[Engine] = None,
    table_name: Optional[str] = None,
) -> None:
    # our docstrings state Args instead of parameters, check how others are written for harmonization
    """
    Load a CSV file into a SQLite database table.

    Parameters
    ----------
    csv_path : Union[str, Path]
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
    path = Path(csv_path)
    eng = engine or get_engine()
    name = table_name or path.stem
    df = pd.read_csv(path, decimal=",")
    df.to_sql(name, con=eng, if_exists="replace", index=False)


def migrate_all_cleaned(
    engine: Optional[Engine] = None,
    cleaned_root: str = "data/cleaned",
) -> None:
    """
    Load all cleaned CSV files into the SQLite database.

    This function scans the cleaned data directory recursively and loads each
    CSV file into the database. Each file is stored in a table named after
    the CSV filename (without extension).

    Parameters
    ----------
    engine : Engine, optional
        Existing SQLAlchemy engine. If not provided, a new engine is used.
    cleaned_root : str, optional
        Root directory containing cleaned CSV files.

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        If the cleaned data directory does not exist or contains no CSV files.
    """
    root = Path(cleaned_root)
    if not root.exists():
        raise FileNotFoundError(f"Cleaned data directory not found: {root}")

    eng = engine or get_engine()
    csv_files = list(root.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under {root}")

    for csv_path in csv_files:
        migrate_csv(csv_path=csv_path, engine=eng)
