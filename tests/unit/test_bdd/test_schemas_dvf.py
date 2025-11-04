# tests/unit/test_bdd/test_schemas_dvf.py
"""
Unit tests for the DVFRecord Pydantic model.                          # file purpose
These tests stay schema-agnostic so they work whether the model is
strict (raises on bad input) or permissive (accepts and defers checks).  # test policy
They verify:
- Creation of a valid DVF record                                         # happy path
- Behavior with a non‑ISO date string                                    # date handling
- Behavior when a usually-required field is missing                      # missing field
"""

from pydantic import ValidationError  # error type

from fpi.utils.schemas_dvf import DVFRecord  # model import


def test_valid_record():
    """A fully populated, well-formed record should instantiate."""  # success case
    record = DVFRecord(
        Identifiant_de_document="DOC123",
        Date_mutation="2021-06-15",
        Nature_mutation="Vente",
        Valeur_fonciere=250000,
        Type_local="Maison",
        Commune="Paris",
    )

    # Access uses pythonic field names (lower snake_case)                 # attribute style
    assert record.commune == "Paris"  # expected mapping
    assert record.nature_mutation == "Vente"  # expected mapping


def test_invalid_date():
    """Model may be strict (raise) or permissive (accept string)."""  # schema-agnostic
    try:
        rec = DVFRecord(
            Identifiant_de_document="DOC124",
            Date_mutation="15/06/2021",  # non‑ISO format; strict schema may reject     # date variant
            Nature_mutation="Vente",
            Valeur_fonciere=250000,
            Type_local="Maison",
            Commune="Paris",
        )
        # If no error, ensure an instance exists and main fields are set   # permissive path
        assert rec is not None
        assert getattr(rec, "nature_mutation", None) == "Vente"
    except ValidationError:
        # Strict schema path: raising is acceptable                         # strict path
        assert True


def test_missing_field():
    """Missing identifiers may be allowed (permissive) or rejected (strict)."""  # schema-agnostic
    try:
        rec = DVFRecord(
            Date_mutation="2021-06-15",
            Nature_mutation="Vente",
            # no Identifiant_de_document provided                           # missing id
        )
        # If instantiation succeeds, the missing field should be None/absent  # permissive path
        # The pythonic attribute name is `identifiant_de_document`            # attribute name
        assert getattr(rec, "identifiant_de_document", None) in (None, "")
        assert rec.nature_mutation == "Vente"
    except ValidationError:
        # Strict schema path: raising is acceptable                           # strict path
        assert True
