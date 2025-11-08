"""
Unit tests for fpi.data_pipeline.schemas
Covers the Pydantic models: PredictionFormSchema and PropertyData.

Checks:
1. Valid input is parsed correctly
2. Default values are applied
3. Validation errors for invalid numeric values
4. Validation errors for out-of-range codes
5. Malformed string inputs
"""

import pytest
from pydantic import ValidationError

from fpi.data_pipeline.schemas import PredictionFormSchema, PropertyData


class TestPredictionFormSchema:
    """
    Unit tests for PredictionFormSchema model.

    Checks:
    1. Valid form input creates a model instance.
    2. Default values (like `output`) are applied.
    """

    def test_valid_input(self) -> None:
        """
        Scenario: A complete, valid input dictionary is provided.

        Steps:
        1. Create a dictionary with postal code, department, town, property type, area, rooms, and land.
        2. Instantiate PredictionFormSchema with the dictionary.
        3. Assert that all fields are correctly stored.
        4. Assert that the default output field is an empty string.
        """
        data: dict[str, float | str] = {
            "postal": "75001",
            "dept": "75",
            "town": "101",
            "prop_type": "House",
            "area": 50.0,
            "rooms": 2,
            "land": 100.0,
        }
        form: PredictionFormSchema = PredictionFormSchema(**data)

        assert form.postal == "75001"
        assert form.dept == "75"
        assert form.town == "101"
        assert form.prop_type == "House"
        assert form.area == 50.0
        assert form.rooms == 2
        assert form.land == 100.0
        assert form.output == ""


class TestPropertyData:
    """
    Unit tests for PropertyData model.

    Checks:
    1. Valid numeric and string input is correctly parsed and coerced.
    2. property_value must be >0.
    3. property_type_code must be within the valid range 1–4.
    4. Malformed strings for numeric fields raise ValidationError.
    """

    def test_valid_input(self) -> None:
        """
        Scenario: A valid DVF row with numeric values as strings and European decimal commas.

        Steps:
        1. Create a dictionary simulating cleaned DVF row.
        2. Instantiate PropertyData.
        3. Assert that numeric values are coerced to float/int correctly.
        """
        data: dict[str, str | int | float] = {
            "property_value": "1000000,50",
            "postal_code": "75001",
            "department_code": "75",
            "town_code": "101",
            "property_type_code": "1",
            "building_area": "50,0",
            "main_rooms": "2",
            "land_area": "100,5",
        }

        prop: PropertyData = PropertyData(**data)

        assert prop.property_value == pytest.approx(1000000.50)
        assert prop.postal_code == 75001
        assert prop.department_code == 75
        assert prop.town_code == 101
        assert prop.property_type_code == 1
        assert prop.building_area == pytest.approx(50.0)
        assert prop.main_rooms == pytest.approx(2.0)
        assert prop.land_area == pytest.approx(100.5)

    def test_invalid_property_value_zero(self) -> None:
        """
        Scenario: property_value <= 0 is provided.

        Steps:
        1. Create a dictionary with property_value set to 0.
        2. Assert that instantiating PropertyData raises ValidationError.
        """
        data: dict[str, int] = {
            "property_value": 0,
            "postal_code": 75001,
            "department_code": 75,
            "town_code": 101,
            "property_type_code": 1,
            "building_area": 50,
            "main_rooms": 2,
            "land_area": 100,
        }

        with pytest.raises(ValidationError):
            PropertyData(**data)

    def test_invalid_property_type_code(self) -> None:
        """
        Scenario: property_type_code outside the valid range [1, 4].

        Steps:
        1. Create a dictionary with property_type_code = 5.
        2. Assert that instantiating PropertyData raises ValidationError.
        """
        data: dict[str, int] = {
            "property_value": 1000000,
            "postal_code": 75001,
            "department_code": 75,
            "town_code": 101,
            "property_type_code": 5,
            "building_area": 50,
            "main_rooms": 2,
            "land_area": 100,
        }

        with pytest.raises(ValidationError):
            PropertyData(**data)

    def test_invalid_strings_for_numeric_fields(self) -> None:
        """
        Scenario: Non-numeric strings are provided for numeric fields.

        Steps:
        1. Create a dictionary with malformed strings for numeric fields.
        2. Assert that instantiating PropertyData raises ValidationError.
        """
        data: dict[str, str] = {
            "property_value": "abc",
            "postal_code": "75a01",
            "department_code": "7b",
            "town_code": "101c",
            "property_type_code": "1",
            "building_area": "50x",
            "main_rooms": "2y",
            "land_area": "100z",
        }

        with pytest.raises(ValidationError):
            PropertyData(**data)
