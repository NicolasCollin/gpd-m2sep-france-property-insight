"""Schema definitions for DVF (Demande de Valeur Foncière) data ingestion and initial validation.

This module provides a Pydantic model for DVF records that is *permissive by default*
to unblock ingestion, but now adds a few minimal constraints on key fields so that
obviously bad rows are surfaced early (e.g., negative values, unknown categories).
Stricter validation remains in the transformation/validation steps.

Key ideas:
- Accept a wide range of input types (strings, numbers, blanks) to avoid rejecting rows up-front.
- Apply *soft* normalizations (blank→None, French numbers, lenient date parsing, city casing).
- Ignore unknown/extra columns coming from heterogeneous CSV exports.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator, AliasChoices
from pydantic import ConfigDict

__all__ = ["DVFRecord"]


# Mapping between canonical (French) field names and "cleaned" English headers
FRENCH_TO_CLEANED = {
    "valeur_fonciere": "property_value",
    "code_postal": "postal_code",
    "surface_reelle_bati": "building_area",
    "surface_terrain": "land_area",
    "nombre_pieces_principales": "main_rooms",
    "date_mutation": "mutation_date",
    "code_departement": "department_code",
    "code_commune": "town_code",
    "code_type_local": "property_type_code",
}
CLEANED_TO_FRENCH = {v: k for k, v in FRENCH_TO_CLEANED.items()}


# --- Canonical categories used for light normalization ----------------------
# Note: We keep the set small and conservative to avoid over-filtering.
ALLOWED_NATURE_MUTATION = {
    "Vente",
    "Echange",
    "Adjudication",
    "Vente en l'état futur d'achèvement",
    "Vente terrain à bâtir",
    "Vente de terrain à bâtir",
}

ALLOWED_TYPE_LOCAL = {
    "Maison",
    "Appartement",
    "Dépendance",
    "Dependance",
    "Local industriel. commercial ou assimilé",
}


# --- Main DVF model (permissive for initial ingestion) ------------------------
# Goal: NEVER block ingestion; we will clean and hard-validate in "transform".


# NOTE: This schema is tuned to work first-class with the **cleaned** dataset.
# Raw DVF (French headers) remain accepted through the KEY_TO_ATTR fallback, but
# we do not guarantee full coverage for all raw edge-cases.

class DVFRecord(BaseModel):
    """
    Permissive Pydantic model for DVF records.

    This model aims to never block data ingestion by accepting various data types
    and performing soft normalization. More rigorous validation and cleaning should
    be applied in later processing steps.
    """

    # Identifiers
    identifiant_de_document: Optional[Any] = Field(
        None,
        validation_alias=AliasChoices("Identifiant_de_document", "document_id", "doc_id", "identifiant_de_document"),
    )
    reference_document: Optional[Any] = Field(
        None,
        validation_alias=AliasChoices("Reference_document", "reference_document"),
    )

    # Mutation information
    date_mutation: Optional[Any] = Field(
        None,
        validation_alias=AliasChoices("Date_mutation", "mutation_date", "date_mutation"),
    )
    nature_mutation: Optional[Any] = Field(
        None,
        validation_alias=AliasChoices("Nature_mutation", "nature_mutation"),
    )
    valeur_fonciere: Optional[Any] = Field(
        None,
        validation_alias=AliasChoices("Valeur_fonciere", "property_value", "valeur_fonciere"),
    )

    # Address / location
    no_voie: Optional[Any] = Field(None, validation_alias=AliasChoices("No_voie", "no_voie"))
    btq: Optional[Any] = Field(None, validation_alias=AliasChoices("B/T/Q", "btq"))
    type_de_voie: Optional[Any] = Field(None, validation_alias=AliasChoices("Type_de_voie", "type_de_voie"))
    code_voie: Optional[Any] = Field(None, validation_alias=AliasChoices("Code_voie", "code_voie"))
    voie: Optional[Any] = Field(None, validation_alias=AliasChoices("Voie", "voie"))
    code_postal: Optional[Any] = Field(None, validation_alias=AliasChoices("Code_postal", "postal_code", "code_postal"))
    commune: Optional[Any] = Field(None, validation_alias=AliasChoices("Commune", "city", "commune"))
    code_departement: Optional[Any] = Field(None, validation_alias=AliasChoices("Code_departement", "department_code", "code_departement"))
    code_commune: Optional[Any] = Field(None, validation_alias=AliasChoices("Code_commune", "town_code", "code_commune"))

    # Parcel / lots
    prefixe_de_section: Optional[Any] = Field(None, validation_alias=AliasChoices("Prefixe_de_section", "prefixe_de_section"))
    section: Optional[Any] = Field(None, validation_alias=AliasChoices("Section", "section"))
    no_plan: Optional[Any] = Field(None, validation_alias=AliasChoices("No_plan", "no_plan"))
    no_volume: Optional[Any] = Field(None, validation_alias=AliasChoices("No_Volume", "no_volume"))

    lot1: Optional[Any] = Field(None, validation_alias=AliasChoices("1er_lot", "lot1"))
    surface_carrez_lot1: Optional[Any] = Field(None, validation_alias=AliasChoices("Surface_Carrez_du_1er_lot", "surface_carrez_lot1"))
    lot2: Optional[Any] = Field(None, validation_alias=AliasChoices("2eme_lot", "lot2"))
    surface_carrez_lot2: Optional[Any] = Field(None, validation_alias=AliasChoices("Surface_Carrez_du_2eme_lot", "surface_carrez_lot2"))
    lot3: Optional[Any] = Field(None, validation_alias=AliasChoices("3eme_lot", "lot3"))
    surface_carrez_lot3: Optional[Any] = Field(None, validation_alias=AliasChoices("Surface_Carrez_du_3eme_lot", "surface_carrez_lot3"))
    lot4: Optional[Any] = Field(None, validation_alias=AliasChoices("4eme_lot", "lot4"))
    surface_carrez_lot4: Optional[Any] = Field(None, validation_alias=AliasChoices("Surface_Carrez_du_4eme_lot", "surface_carrez_lot4"))
    lot5: Optional[Any] = Field(None, validation_alias=AliasChoices("5eme_lot", "lot5"))
    surface_carrez_lot5: Optional[Any] = Field(None, validation_alias=AliasChoices("Surface_Carrez_du_5eme_lot", "surface_carrez_lot5"))

    nombre_de_lots: Optional[Any] = Field(None, validation_alias=AliasChoices("Nombre_de_lots", "nombre_de_lots"))

    # Local information
    code_type_local: Optional[Any] = Field(None, validation_alias=AliasChoices("Code_type_local", "property_type_code", "code_type_local"))
    type_local: Optional[Any] = Field(None, validation_alias=AliasChoices("Type_local", "type_local"))
    identifiant_local: Optional[Any] = Field(None, validation_alias=AliasChoices("Identifiant_local", "identifiant_local"))
    surface_reelle_bati: Optional[Any] = Field(None, validation_alias=AliasChoices("Surface_reelle_bati", "building_area", "surface_reelle_bati"))
    nombre_pieces_principales: Optional[Any] = Field(None, validation_alias=AliasChoices("Nombre_pieces_principales", "main_rooms", "nombre_pieces_principales"))

    # Terrain / nature of cultivation
    nature_culture: Optional[Any] = Field(None, validation_alias=AliasChoices("Nature_culture", "nature_culture"))
    nature_culture_speciale: Optional[Any] = Field(None, validation_alias=AliasChoices("Nature_culture_speciale", "nature_culture_speciale"))
    surface_terrain: Optional[Any] = Field(None, validation_alias=AliasChoices("Surface_terrain", "land_area", "surface_terrain"))

    # --- Soft normalizations --------------------------------------------------
    @field_validator("*", mode="before")
    @classmethod
    def _blank_to_none(cls, v: Any) -> Any:
        """
        Convert blank or common 'null' string representations to None before validation.

        This helps unify missing or empty values across various fields.
        """
        if v is None:
            return None
        if isinstance(v, str) and v.strip().lower() in {"", "na", "nan", "none", "null"}:
            return None
        return v

    @field_validator(
        "valeur_fonciere",
        "surface_carrez_lot1",
        "surface_carrez_lot2",
        "surface_carrez_lot3",
        "surface_carrez_lot4",
        "surface_carrez_lot5",
        "surface_reelle_bati",
        "surface_terrain",
        "nombre_pieces_principales",
        "nombre_de_lots",
        mode="before",
    )
    @classmethod
    def _num_fr_soft(cls, v: Any) -> Optional[float]:
        """
        Softly parse French-style numeric values, returning float or None.

        Handles spaces, non‑breaking spaces, and commas as decimal separators.
        Returns None if parsing fails or the value is empty.
        """
        # Try parsing; on failure, return None (we do not block ingestion)
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).replace("\u202f", "").replace(" ", "").replace(",", ".")
        if s == "":
            return None
        try:
            return float(s)
        except ValueError:
            return None

    @field_validator("date_mutation", mode="before")
    @classmethod
    def _parse_date_soft(cls, v: Any) -> Any:
        """
        Attempt to parse date strings in multiple formats; return original value if all fail.

        Returns a date object if parsing succeeds, None if input is empty,
        or the original string if no format matches.
        """
        if v is None:
            return None
        if isinstance(v, date):
            return v
        s = str(v).strip()
        if not s:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        # Do not raise: keep the raw value for later cleaning
        return s

    @field_validator("nature_mutation", mode="after")
    @classmethod
    def _normalize_nature_mutation(cls, v: Any) -> Optional[str]:
        """Normalize and whitelist mutation nature.

        Accepts a variety of casings/spaces; returns the canonical label if known,
        otherwise `None` so downstream rules can decide what to do.
        """
        if v in (None, ""):
            return None
        s = str(v).strip()
        # Attempt to standardize a couple of common variants
        s = s.replace("Vente terrain a batir", "Vente terrain à bâtir")
        s = s.replace("Vente de terrain a batir", "Vente de terrain à bâtir")
        return s if s in ALLOWED_NATURE_MUTATION else None

    @field_validator("type_local", mode="after")
    @classmethod
    def _normalize_type_local(cls, v: Any) -> Optional[str]:
        """Normalize and whitelist local type (dwelling type)."""
        if v in (None, ""):
            return None
        s = str(v).strip().title()
        # Normalize common variants (accent-insensitive)
        if s == "Dependance":
            s = "Dépendance"
        return s if s in ALLOWED_TYPE_LOCAL else None

    @field_validator(
        "valeur_fonciere",
        "surface_reelle_bati",
        "surface_terrain",
        mode="after",
    )
    @classmethod
    def _non_negative(cls, v: Optional[float]) -> Optional[float]:
        """Reject negative numeric values by downgrading them to `None`.

        We do not raise errors here to keep ingestion robust; the downstream
        validator will count missing/invalid values.
        """
        if v is None:
            return None
        try:
            return v if float(v) >= 0 else None
        except Exception:
            return None

    @field_validator("commune", mode="after")
    @classmethod
    def _normalize_city(cls, v: Any) -> Optional[str]:
        """
        Normalize city names by stripping whitespace and applying title case.

        Returns None if the input is None or empty.
        """
        return None if v in (None, "") else str(v).strip().title()

    @field_validator("identifiant_de_document", mode="after")
    @classmethod
    def _normalize_doc_id(cls, v: Any) -> Optional[str]:
        """Trim the document identifier and drop it if empty."""
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    def to_serialized_row(self, prefer_cleaned: bool, original_columns: list[str] | None = None) -> dict:
        """
        Build a row dict suitable for CSV export.

        If `prefer_cleaned` is True, keys are exported using the cleaned English headers
        when a known mapping exists; otherwise canonical French field names are used.
        Any extra/unknown input columns are preserved (when available) so the output
        mirrors the incoming cleaned dataset.
        """
        data = self.model_dump(by_alias=False, exclude_none=True)
        # Include extras if any (only when extra="allow")
        extras = getattr(self, "model_extra", None) or {}
        # Rename keys if needed
        if prefer_cleaned:
            renamed = {FRENCH_TO_CLEANED.get(k, k): v for k, v in data.items()}
            # Merge extras as-is to keep original cleaned columns
            row = {**extras, **renamed}
        else:
            row = {**extras, **data}
        # If an original column order is provided, restrict to those keys first
        if original_columns:
            ordered = {k: row.get(k) for k in original_columns}
            # Append any new keys that were not in the original input
            for k, v in row.items():
                if k not in ordered:
                    ordered[k] = v
            return ordered
        return row

    # Pydantic v2 config (explicit for mypy)
    model_config = ConfigDict(
        populate_by_name=True,
        # Keep unknown/extra columns so we can preserve them when writing
        # validated CSVs for the *cleaned* dataset.
        extra="allow",
        str_strip_whitespace=True,
        validate_assignment=True,
    )
