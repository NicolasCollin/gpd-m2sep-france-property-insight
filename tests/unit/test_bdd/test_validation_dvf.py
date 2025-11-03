# tests/unit/test_bdd/test_validation_dvf.py
"""
Unit tests for the validation_dvf module.                               # file purpose
These tests ensure that:
- CSV files are read correctly with different encodings/separators
- The validation functions return the expected structure and statistics
- Error reporting and summaries work as intended
"""

import pandas as pd
import pytest
from pathlib import Path

from fpi.utils.validation_dvf import (
    read_csv_any,
    validate_records,
    summarize,
)


@pytest.fixture
def sample_data(tmp_path: Path):
    """Create a small temporary CSV file for testing."""                # test fixture
    csv_path = tmp_path / "test.csv"
    data = pd.DataFrame({
        "Identifiant_de_document": ["A1", "A2"],
        "Date_mutation": ["2021-01-01", "2021-02-02"],
        "Nature_mutation": ["Vente", "Echange"],
        "Valeur_fonciere": [250000, 300000],
        "Type_local": ["Maison", "Appartement"],
        "Commune": ["Paris", "Lyon"],
    })
    data.to_csv(csv_path, index=False)
    return csv_path


def test_read_csv_any(sample_data):
    """Ensure read_csv_any correctly loads a valid CSV file."""         # read function test
    df = read_csv_any(sample_data)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Identifiant_de_document" in df.columns


def test_validate_records_with_valid_data():
    """Check that valid data passes validation with no errors."""       # basic validation test
    records = [
        {
            "Identifiant_de_document": "A1",
            "Date_mutation": "2021-01-01",
            "Nature_mutation": "Vente",
            "Valeur_fonciere": 250000,
            "Type_local": "Maison",
            "Commune": "Paris",
        }
    ]
    valid, errors = validate_records(records)
    assert len(valid) == 1
    assert errors.empty


def test_validate_records_with_invalid_data():
    """Check that invalid data triggers validation errors."""           # invalid input test
    records = [
        {
            "Identifiant_de_document": "A2",
            "Date_mutation": "invalid-date",  # bad format
            "Nature_mutation": "Vente",
            "Valeur_fonciere": -100,          # negative value
            "Type_local": "Unknown",          # invalid type
            "Commune": "Marseille",
        }
    ]
    valid, errors = validate_records(records)
    assert len(valid) == 0
    assert not errors.empty
    assert "Date_mutation" in errors["column"].values or "Valeur_fonciere" in errors["column"].values


def test_summarize_function():
    """Ensure summarize returns correct counts."""                     # summary logic test
    fake_models = [object(), object()]
    fake_errors = pd.DataFrame([{"msg": "error1"}, {"msg": "error2"}])
    stats = summarize(fake_models, fake_errors)
    assert stats["valid"] == 2
    assert stats["errors"] == 2
    assert stats["total"] == 4