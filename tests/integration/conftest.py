"""Shared fixtures for integration tests."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_raw_csv_data():
    """Sample raw CSV data in French format."""
    return """date_mutation,nature_mutation,valeur_fonciere,code_postal,commune,code_departement,\
        code_commune,code_type_local,type_local,surface_reelle_bati,nombre_pieces_principales,surface_terrain
05/01/2024,Vente,1350000,00,75020,PARIS 20,75,120,4,Local industriel. commercial ou assimilé,135,0,124
19/01/2024,Vente,2865000,00,75002,PARIS 02,75,102,2,Appartement,43,2,69
19/01/2024,Vente,2865000,00,75002,PARIS 02,75,102,2,Appartement,44,2,69"""


@pytest.fixture
def sample_raw_csv_file(temp_data_dir, sample_raw_csv_data):
    """Create a sample raw CSV file for testing."""
    raw_dir = temp_data_dir / "raw" / "raw2024"
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_file = raw_dir / "raw_75_2024.csv"
    raw_file.write_text(sample_raw_csv_data, encoding="utf-8")

    return raw_file


@pytest.fixture
def sample_cleaned_csv_file(temp_data_dir):
    """Create a sample cleaned CSV file for testing using pandas (matches actual pipeline output)."""
    cleaned_dir = temp_data_dir / "cleaned" / "cleaned2024"
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    # Create DataFrame matching cleaned data structure
    df = pd.DataFrame(
        {
            "transaction_date": ["05/01/2024", "19/01/2024", "19/01/2024"],
            "transaction_type": ["Vente", "Vente", "Vente"],
            "property_value": [1350000.00, 2865000.00, 2865000.00],
            "postal_code": [75020, 75002, 75002],
            "town_name": ["PARIS 20", "PARIS 02", "PARIS 02"],
            "department_code": [75, 75, 75],
            "town_code": [120, 102, 102],
            "property_type_code": [4, 2, 2],
            "property_type": ["Local industriel. commercial ou assimilé", "Appartement", "Appartement"],
            "building_area": [135.0, 43.0, 44.0],
            "main_rooms": [0.0, 2.0, 2.0],
            "land_area": [124.0, 69.0, 69.0],
        }
    )

    cleaned_file = cleaned_dir / "cleaned_75_2024.csv"
    # Write using default format (dot decimals, comma column separator)
    # This matches what clean_data.py produces with df.to_csv()
    df.to_csv(cleaned_file, index=False)

    return cleaned_file


@pytest.fixture
def sample_text_file(temp_data_dir):
    """Create a sample pipe-delimited text file for testing."""
    text_data = """Column Name 1|Column Name 2|Column Name 3
Value 1|Value 2|Value 3
Value 4|Value 5|Value 6"""

    text_file = temp_data_dir / "sample.txt"
    text_file.write_text(text_data, encoding="utf-8")

    return text_file


@pytest.fixture
def sample_prediction_input():
    """Sample input data for prediction."""
    return {
        "building_area": 43.0,
        "main_rooms": 2,
        "land_area": 69.0,
        "postal_code": 75002,
        "property_type_code": 2,
        "town_code": 102,
        "department_code": 75,
    }
