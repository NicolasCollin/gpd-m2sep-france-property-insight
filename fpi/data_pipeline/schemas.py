import pandas as pd
from pydantic import BaseModel, Field, field_validator


class PredictionFormSchema(BaseModel):
    postal: str | None = None
    dept: str | None = None
    town: str | None = None
    prop_type: str = "House"
    area: float | None = None
    rooms: int | None = None
    land: float | None = None
    output: str = ""


class PropertyData(BaseModel):
    """
    Structured record for a *cleaned* DVF row.

    Each attribute maps 1-to-1 to a column name present in our **cleaned CSV**
    files. Constraints are intentionally light but meaningful for a university
    project: positivity/non-negativity, plausible code ranges, and robust
    parsing of European number formats.
    """

    property_value: float = Field(..., gt=0)
    postal_code: int = Field(..., ge=1000, le=99999)
    department_code: int = Field(..., ge=1, le=976)
    town_code: int = Field(..., gt=0)
    property_type_code: int = Field(..., ge=1, le=4)
    building_area: float = Field(..., ge=0)
    main_rooms: float = Field(..., ge=0)
    land_area: float = Field(..., ge=0)

    # helpers
    @staticmethod
    def _to_float_eu(v: float | int | str | None) -> float:
        """Parse floats that may use European comma decimals or come as numbers/strings."""
        if v is None or (isinstance(v, float) and pd.isna(v)):
            raise ValueError("Missing numeric value")
        if isinstance(v, str):
            v = v.replace(",", ".").strip()
        return float(v)

    @field_validator("property_value", "building_area", "main_rooms", "land_area", mode="before")
    def parse_float_fields(cls, v: float | int | str | None) -> float:
        """Accept '200000,00' or '15,5' and coerce to float before constraints apply."""
        return cls._to_float_eu(v)

    @field_validator("postal_code", "department_code", "town_code", "property_type_code", mode="before")
    def parse_int_fields(cls, v: float | int) -> int:
        """Coerce numeric codes that may arrive as floats or strings."""
        if isinstance(v, float) and not pd.isna(v):
            return int(v)
        if isinstance(v, str):
            v = v.strip()
            if v.endswith(".0"):
                v = v[:-2]
        return int(v)

    @field_validator("property_type_code")
    def property_type_in_known_range(cls, v: int) -> int:
        """Ensure property_type_code is within expected values."""
        if v not in {1, 2, 3, 4}:
            raise ValueError("property_type_code must be one of {1,2,3,4}")
        return v
