from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional
import sqlite3
import pandas as pd

from fpi.utils.constants import VARS_TO_KEEP_SQL  # adjust the import path



class PropertyData(BaseModel):
    Valeur_fonciere: float = Field(..., gt=0, description="Valeur foncière en euros")
    Code_departement: str = Field(..., pattern=r"^\d{2}$", description="Code du département à 2 chiffres")
    Code_commune: int = Field(..., ge=0, description="Code de la commune")
    Nombre_de_lots: int = Field(..., ge=0, description="Nombre de lots")
    Code_type_local: int = Field(..., ge=0, description="Type de local (1=maison, 2=appartement, etc.)")
    Surface_reelle_bati: Optional[float] = Field(None, ge=0, description="Surface réelle bâtie en m²")
    Nombre_pieces_principales: Optional[int] = Field(None, ge=0, description="Nombre de pièces principales")
    Surface_terrain: Optional[float] = Field(None, ge=0, description="Surface du terrain en m²")

    # Clean the numeric values with commas if necessary
    @field_validator("Valeur_fonciere", mode="before")
    def clean_valeur_fonciere(cls, v):
        if isinstance(v, str):
            v = v.replace(",", ".")
        return float(v)




def load_from_db(db_path: str, table_name: str) -> pd.DataFrame:
    """Load a table from SQLite DB into a pandas DataFrame."""
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(f"SELECT {', '.join(VARS_TO_KEEP_SQL)} FROM {table_name}", conn)
    return df


def validate_rows(df: pd.DataFrame):
    """Validate each row using the Pydantic model."""
    valid_rows = []
    invalid_rows = []

    for idx, row in df.iterrows():
        try:
            item = PropertyData(**row.to_dict())
            valid_rows.append(item.model_dump())
        except ValidationError as e:
            invalid_rows.append((idx, e))

    print(f"✅ {len(valid_rows)} valid rows | ❌ {len(invalid_rows)} invalid rows")
    return pd.DataFrame(valid_rows), invalid_rows


def save_to_db(df: pd.DataFrame, output_db: str, table_name: str):
    """Save validated rows to a new SQLite DB."""
    with sqlite3.connect(output_db) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"💾 Saved {len(df)} validated rows to {output_db}")


if __name__ == "__main__":
    input_db = "data/cleaned/sample2024.db"
    output_db = "data/cleaned/validated2024.db"
    table_name = "sample_2024"

    df = load_from_db(input_db, table_name)
    valid_df, errors = validate_rows(df)
    save_to_db(valid_df, output_db, table_name)

