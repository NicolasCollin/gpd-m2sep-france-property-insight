"""Schema definitions for DVF (Demande de Valeur Foncière) data ingestion and initial validation.

This module provides a permissive Pydantic model for DVF records to facilitate
initial data ingestion without blocking on validation errors. Data cleaning and
stricter validation are intended to be performed in subsequent transformation steps.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

# --- Modèle principal DVF (version permissive pour ingestion initiale) ---
# Objectif: ne JAMAIS bloquer l'ingestion; on nettoiera en étape "transform".


class DVFRecord(BaseModel):
    """
    Permissive Pydantic model for DVF records.

    This model aims to never block data ingestion by accepting various data types
    and performing soft normalization. More rigorous validation and cleaning should
    be applied in later processing steps.
    """

    # Identifiers
    identifiant_de_document: Optional[Any] = Field(None, alias="Identifiant_de_document")
    reference_document: Optional[Any] = Field(None, alias="Reference_document")

    # Mutation information
    date_mutation: Optional[Any] = Field(None, alias="Date_mutation")
    nature_mutation: Optional[Any] = Field(None, alias="Nature_mutation")
    valeur_fonciere: Optional[Any] = Field(None, alias="Valeur_fonciere")

    # Address / location
    no_voie: Optional[Any] = Field(None, alias="No_voie")
    btq: Optional[Any] = Field(None, alias="B/T/Q")
    type_de_voie: Optional[Any] = Field(None, alias="Type_de_voie")
    code_voie: Optional[Any] = Field(None, alias="Code_voie")
    voie: Optional[Any] = Field(None, alias="Voie")
    code_postal: Optional[Any] = Field(None, alias="Code_postal")
    commune: Optional[Any] = Field(None, alias="Commune")
    code_departement: Optional[Any] = Field(None, alias="Code_departement")
    code_commune: Optional[Any] = Field(None, alias="Code_commune")

    # Parcel / lots
    prefixe_de_section: Optional[Any] = Field(None, alias="Prefixe_de_section")
    section: Optional[Any] = Field(None, alias="Section")
    no_plan: Optional[Any] = Field(None, alias="No_plan")
    no_volume: Optional[Any] = Field(None, alias="No_Volume")

    lot1: Optional[Any] = Field(None, alias="1er_lot")
    surface_carrez_lot1: Optional[Any] = Field(None, alias="Surface_Carrez_du_1er_lot")
    lot2: Optional[Any] = Field(None, alias="2eme_lot")
    surface_carrez_lot2: Optional[Any] = Field(None, alias="Surface_Carrez_du_2eme_lot")
    lot3: Optional[Any] = Field(None, alias="3eme_lot")
    surface_carrez_lot3: Optional[Any] = Field(None, alias="Surface_Carrez_du_3eme_lot")
    lot4: Optional[Any] = Field(None, alias="4eme_lot")
    surface_carrez_lot4: Optional[Any] = Field(None, alias="Surface_Carrez_du_4eme_lot")
    lot5: Optional[Any] = Field(None, alias="5eme_lot")
    surface_carrez_lot5: Optional[Any] = Field(None, alias="Surface_Carrez_du_5eme_lot")

    nombre_de_lots: Optional[Any] = Field(None, alias="Nombre_de_lots")

    # Local information
    code_type_local: Optional[Any] = Field(None, alias="Code_type_local")
    type_local: Optional[Any] = Field(None, alias="Type_local")
    identifiant_local: Optional[Any] = Field(None, alias="Identifiant_local")
    surface_reelle_bati: Optional[Any] = Field(None, alias="Surface_reelle_bati")
    nombre_pieces_principales: Optional[Any] = Field(None, alias="Nombre_pieces_principales")

    # Terrain / nature of cultivation
    nature_culture: Optional[Any] = Field(None, alias="Nature_culture")
    nature_culture_speciale: Optional[Any] = Field(None, alias="Nature_culture_speciale")
    surface_terrain: Optional[Any] = Field(None, alias="Surface_terrain")

    # --- Soft normalizations / DO NOT BLOCK -----------------------------
    @field_validator("*", mode="before")
    @classmethod
    def _blank_to_none(cls, v):
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
    def _num_fr_soft(cls, v):
        """
        Softly parse French-style numeric values, returning float or None.

        Handles spaces, non-breaking spaces, and commas as decimal separators.
        Returns None if parsing fails or value is empty.
        """
        # Tente de parser, sinon renvoie None (on ne bloque pas)
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return v
        s = str(v).replace("\u202f", "").replace(" ", "").replace(",", ".")
        if s == "":
            return None
        try:
            # gardons float pour uniformiser
            return float(s)
        except ValueError:
            return None

    @field_validator("date_mutation", mode="before")
    @classmethod
    def _parse_date_soft(cls, v):
        """
        Attempt to parse date strings in multiple formats; return original value if all fail.

        Returns a date object if parsing succeeds, None if input is empty,
        or the original string if no format matches.
        """
        # Essaie plusieurs formats; en cas d'échec, renvoie tel quel (ou None si vide)
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
        # ne pas lever d'erreur : on laisse la valeur brute (ingestion d'abord)
        return s

    @field_validator("commune", mode="after")
    @classmethod
    def _normalize_city(cls, v):
        """
        Normalize city names by stripping whitespace and applying title case.

        Returns None if the input is None or empty string.
        """
        return None if v in (None, "") else str(v).strip().title()

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",  # colonnes inconnues ignorées
        "str_strip_whitespace": True,
    }
