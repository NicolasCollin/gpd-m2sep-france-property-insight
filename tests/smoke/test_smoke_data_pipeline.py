from pathlib import Path

import pandas as pd

from fpi.data_pipeline.clean_data import clean_data
from fpi.data_pipeline.process_data import process_data


# issue: using the fixture in conftest somehow messes up with the temporary saved csv
# between clean_data and process_data calls
def sample_raw_csv_data() -> str:
    """Sample raw CSV data in French DVF format."""
    return """date_mutation,nature_mutation,valeur_fonciere,code_postal,commune,code_departement,\
code_commune,code_type_local,type_local,surface_reelle_bati,nombre_pieces_principales,surface_terrain
05/01/2024,Vente,1350000,75020,PARIS 20,75,120,4,Local industriel. commercial ou assimilé,135,0,124
19/01/2024,Vente,2865000,75002,PARIS 02,75,102,2,Appartement,43,2,69
19/01/2024,Vente,2865000,75002,PARIS 02,75,102,2,Appartement,44,2,69"""


def test_data_pipeline_smoke_single_file(tmp_path: Path) -> None:
    """
    Global smoke test for the data pipeline (single CSV).

    Steps:
    1. Write a sample raw CSV into tmp_path/raw
    2. Run clean_data → writes to tmp_path/cleaned
    3. Check cleaned CSV exists and has rows
    4. Run process_data → writes to tmp_path/processed
    5. Check processed CSV exists and has rows
    """

    # 1. Create raw folder and write sample CSV
    raw_dir: Path = tmp_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_file: Path = raw_dir / "raw_2024.csv"
    raw_file.write_text(sample_raw_csv_data(), encoding="utf-8")

    # 2. Run clean_data
    cleaned_dir: Path = tmp_path / "cleaned"
    clean_data(raw_path=raw_dir, cleaned_path=cleaned_dir)

    # 3. Check cleaned CSV
    cleaned_file = next(cleaned_dir.rglob("cleaned_*.csv"))
    assert cleaned_file.exists(), "Cleaned file should exist"
    df_cleaned = pd.read_csv(cleaned_file)
    assert not df_cleaned.empty, "Cleaned DataFrame should have rows"

    # 4. Run process_data
    processed_dir: Path = tmp_path / "processed"
    process_data(cleaned_path=cleaned_dir, processed_path=processed_dir)

    # 5. Check processed CSV
    processed_file = next(processed_dir.rglob("processed_*.csv"))
    assert processed_file.exists(), "Processed file should exist"
    df_processed = pd.read_csv(processed_file)
    assert not df_processed.empty, "Processed DataFrame should have rows"
    # Optional: check 'year' column
    assert "year" in df_processed.columns, "Processed DataFrame should contain 'year'"
