from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# --- Enums DVF courants (souples : on laisse None pour inconnus) ---


class NatureMutation(str, Enum):
    VENTE = "Vente"
    ECHANGE = "Echange"
    EXPROPRIATION = "Expropriation"
    ADJUDICATION = "Adjudication"
    AUTRE = "Autre"


class TypeLocal(str, Enum):
    MAISON = "Maison"
    APPARTEMENT = "Appartement"
    DEPENDANCE = "Dépendance"
    LOCAL_INDUSTRIEL = "Local industriel. commercial ou assimilé"
    AUTRE = "Autre"


# --- Modèle principal ligne DVF (avec alias = noms de colonnes) ---


class DVFRecord(BaseModel):
    # Identifiants
    identifiant_de_document: Optional[str] = Field(None, alias="Identifiant_de_document")
    reference_document: Optional[str] = Field(None, alias="Reference_document")

    # Infos mutation
    date_mutation: date = Field(..., alias="Date_mutation")
    nature_mutation: Optional[NatureMutation] = Field(None, alias="Nature_mutation")
    valeur_fonciere: Optional[int] = Field(None, alias="Valeur_fonciere", ge=1, le=50_000_000)

    # Adresse / localisation
    no_voie: Optional[str] = Field(None, alias="No_voie")
    btq: Optional[str] = Field(None, alias="B/T/Q")
    type_de_voie: Optional[str] = Field(None, alias="Type_de_voie")
    code_voie: Optional[str] = Field(None, alias="Code_voie")
    voie: Optional[str] = Field(None, alias="Voie")
    code_postal: Optional[str] = Field(None, alias="Code_postal", pattern=r"^\d{5}$")
    commune: Optional[str] = Field(None, alias="Commune")
    code_departement: Optional[str] = Field(None, alias="Code_departement", pattern=r"^\d{2,3}$")
    code_commune: Optional[str] = Field(None, alias="Code_commune")

    # Parcelle / lots
    prefixe_de_section: Optional[str] = Field(None, alias="Prefixe_de_section")
    section: Optional[str] = Field(None, alias="Section")
    no_plan: Optional[str] = Field(None, alias="No_plan")
    no_volume: Optional[str] = Field(None, alias="No_Volume")

    lot1: Optional[str] = Field(None, alias="1er_lot")
    surface_carrez_lot1: Optional[float] = Field(None, alias="Surface_Carrez_du_1er_lot", ge=0)
    lot2: Optional[str] = Field(None, alias="2eme_lot")
    surface_carrez_lot2: Optional[float] = Field(None, alias="Surface_Carrez_du_2eme_lot", ge=0)
    lot3: Optional[str] = Field(None, alias="3eme_lot")
    surface_carrez_lot3: Optional[float] = Field(None, alias="Surface_Carrez_du_3eme_lot", ge=0)
    lot4: Optional[str] = Field(None, alias="4eme_lot")
    surface_carrez_lot4: Optional[float] = Field(None, alias="Surface_Carrez_du_4eme_lot", ge=0)
    lot5: Optional[str] = Field(None, alias="5eme_lot")
    surface_carrez_lot5: Optional[float] = Field(None, alias="Surface_Carrez_du_5eme_lot", ge=0)

    nombre_de_lots: Optional[int] = Field(None, alias="Nombre_de_lots", ge=0, le=100)

    # Local
    code_type_local: Optional[int] = Field(None, alias="Code_type_local", ge=1, le=99)
    type_local: Optional[TypeLocal] = Field(None, alias="Type_local")
    identifiant_local: Optional[str] = Field(None, alias="Identifiant_local")
    surface_reelle_bati: Optional[float] = Field(None, alias="Surface_reelle_bati", ge=0, le=5_000)
    nombre_pieces_principales: Optional[int] = Field(None, alias="Nombre_pieces_principales", ge=0, le=30)

    # Terrain / nature de culture
    nature_culture: Optional[str] = Field(None, alias="Nature_culture")
    nature_culture_speciale: Optional[str] = Field(None, alias="Nature_culture_speciale")
    surface_terrain: Optional[float] = Field(None, alias="Surface_terrain", ge=0, le=100_000_000)

    # --- Normalisations / coercitions -------------------------------------------------

    @field_validator("date_mutation", mode="before")
    @classmethod
    def _parse_date(cls, v):
        if isinstance(v, date):
            return v
        if v in (None, "", "NA"):
            raise ValueError("Date_mutation manquante")
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(str(v), fmt).date()
            except ValueError:
                pass
        raise ValueError("Format de date invalide")

    @field_validator(
        "valeur_fonciere",
        "surface_carrez_lot1",
        "surface_carrez_lot2",
        "surface_carrez_lot3",
        "surface_carrez_lot4",
        "surface_carrez_lot5",
        "surface_reelle_bati",
        "surface_terrain",
        mode="before",
    )
    @classmethod
    def _num_fr(cls, v):
        # accepte "123 456,78" / "123456.78" / "" -> None
        if v in (None, "", "NA"):
            return None
        if isinstance(v, (int, float)):
            return v
        s = str(v).replace(" ", "").replace("\u202f", "")  # espaces insécables
        s = s.replace(",", ".")
        try:
            return float(s) if (("." in s) or ("e" in s.lower())) else int(s)
        except ValueError:
            raise ValueError("Nombre invalide")

    @field_validator("commune", mode="after")
    @classmethod
    def _normalize_city(cls, v):
        return None if v in (None, "") else v.strip().title()

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",  # colonnes inconnues ignorées
        "str_strip_whitespace": True,
    }
