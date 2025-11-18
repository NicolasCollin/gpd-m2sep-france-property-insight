import pandas as pd
from pydantic import BaseModel, Field, field_validator


class PredictionFormSchema(BaseModel):
    """
    Schema for storing user inputs from the property prediction form.

    Attributes:
        postal (str): Postal code (5-digit string).
        prop_type (str): Property type, default "House".
        area (float): Living area in m².
        rooms (int): Number of rooms.
        land (float): Land area in m².
        output (str): Prediction output, default empty string.
    """

    postal: str
    prop_type: str = "House"
    area: float
    rooms: int
    land: float
    output: str = ""


class PropertyData(BaseModel):
    """
    Structured representation of a single cleaned DVF row.

    Attributes:
        property_value (float): Sale price of the property (must be >0).
        postal_code (int): Postal code (1000–99999).
        department_code (int): Department code (1–976).
        town_code (int): Town code (>0).
        property_type_code (int): Numeric code for property type (1=House, 2=Apartment, 3=Other, 4=Land).
        building_area (float): Living area in m² (>=0).
        main_rooms (float): Number of main rooms (>=0).
        land_area (float): Land area in m² (>=0).

    Notes:
        - Numeric fields can be provided as floats, ints, or strings with European decimal commas.
        - Validators ensure type coercion before field constraints are applied.
    """

    property_value: float = Field(..., gt=0)
    postal_code: int = Field(..., ge=1000, le=99999)
    department_code: int = Field(..., ge=1, le=976)
    town_code: int = Field(..., gt=0)
    property_type_code: int = Field(..., ge=1, le=4)
    building_area: float = Field(..., ge=0)
    main_rooms: float = Field(..., ge=0)
    land_area: float = Field(..., ge=0)
    transaction_date: str = Field(default="")
    transaction_type: str = Field(default="")
    property_type: str = Field(default="")
    town_name: str = Field(default="")

    @staticmethod
    def _to_float_eu(v: float | int | str | None) -> float:
        """
        Parse numeric values that may come as floats, ints, or strings
        using a European decimal format (comma as decimal separator).

        Args:
            v (float | int | str | None): Input value to convert.

        Returns:
            v (float): Converted float value.

        Raises:
            ValueError:
            - If the value is None or cannot be parsed as a valid float.
        """

        if v is None or (isinstance(v, float) and pd.isna(v)):
            raise ValueError("Missing numeric value")
        if isinstance(v, str):
            v = v.replace(",", ".").strip()
        return float(v)

    @field_validator("property_value", "building_area", "main_rooms", "land_area", mode="before")
    def parse_float_fields(cls, v: float | int | str | None) -> float:
        """Coerce numeric fields to float before applying constraints."""
        return cls._to_float_eu(v)

    @field_validator("postal_code", "department_code", "town_code", "property_type_code", mode="before")
    def parse_int_fields(cls, v: float | int | str) -> int:
        """Coerce numeric codes to int before applying constraints."""
        if isinstance(v, float) and not pd.isna(v):
            return int(v)
        if isinstance(v, str):
            v = v.strip()
            if v.endswith(".0"):
                v = v[:-2]
        return int(v)

    @field_validator("property_type_code")
    def property_type_in_known_range(cls, v: int) -> int:
        """Ensure property_type_code is one of the known valid values (1–4)."""
        if v not in {1, 2, 3, 4}:
            raise ValueError("property_type_code must be one of {1,2,3,4}")
        return v
