# tests/unit/test_bdd/test_schemas_dvf.py
"""
Unit tests for the DVFRecord Pydantic model.                            # file purpose
These tests check:
- Creation of valid DVF records
- Handling of invalid data (e.g., wrong date format)
- Missing required fields
"""

import pytest

from fpi.utils.schemas_dvf import DVFRecord  # import the Pydantic model


def test_valid_record():
    """Test that a valid DVF record can be created successfully."""  # simple creation test
    record = DVFRecord(
        Identifiant_de_document="DOC123",
        Date_mutation="2021-06-15",
        Nature_mutation="Vente",
        Valeur_fonciere=250000,
        Type_local="Maison",
        Commune="Paris",
    )

    # Check if key fields are properly stored
    assert record.Commune == "Paris"
    assert record.Nature_mutation == "Vente"


def test_invalid_date():
    """Test that an invalid date format raises a validation error."""  # invalid date test
    with pytest.raises(ValueError):
        DVFRecord(
            Identifiant_de_document="DOC124",
            Date_mutation="15/06/2021",  # wrong format
            Nature_mutation="Vente",
            Valeur_fonciere=250000,
            Type_local="Maison",
            Commune="Paris",
        )


def test_missing_field():
    """Test that missing a required field raises a validation error."""  # missing key field test
    with pytest.raises(ValueError):
        DVFRecord(
            Date_mutation="2021-06-15",
            Nature_mutation="Vente",
        )
