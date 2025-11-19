import pytest
from pydantic import ValidationError

from fpi.data_pipeline.schemas import PredictionFormSchema, PropertyData


class TestPredictionFormSchema:
    """
    Unit tests for PredictionFormSchema model.

    Checks:
    1. Valid form input creates a model instance.
    2. Default values (like `output`) are applied.
    3. Invalid numeric fields raise ValidationError.
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
            "prop_type": "House",
            "area": 50.0,
            "rooms": 2,
            "land": 100.0,
        }
        form: PredictionFormSchema = PredictionFormSchema(**data)

        assert form.postal == "75001"
        assert form.prop_type == "House"
        assert form.area == 50.0
        assert form.rooms == 2
        assert form.land == 100.0
        assert form.output == ""

    def test_invalid_numeric_field(self) -> None:
        """
        Scenario: Non-numeric field is passed for a numeric parameter.

        Expectation:
        - Should raise ValidationError.
        """
        with pytest.raises(ValidationError):
            PredictionFormSchema(
                postal="75001",
                prop_type="House",
                area="abc",
                rooms=2,
                land=50,
            )


class TestPropertyData:
    """
    Unit tests for PropertyData model.

    Checks:
    1. Valid numeric and string input is correctly parsed and coerced.
    2. property_value must be >0.
    3. property_type_code must be within the valid range 1–4.
    4. Malformed strings for numeric fields raise ValidationError.
    5. Internal coercion helpers (_to_float_eu, parse_float_fields, parse_int_fields) behave correctly.
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

    def test_to_float_eu_valid(self) -> None:
        """_to_float_eu correctly parses various numeric formats."""
        assert PropertyData._to_float_eu("10,5") == 10.5
        assert PropertyData._to_float_eu("20.75") == 20.75
        assert PropertyData._to_float_eu(15) == 15.0

    def test_to_float_eu_invalid(self) -> None:
        """_to_float_eu should raise ValueError for invalid data."""
        with pytest.raises(ValueError):
            PropertyData._to_float_eu("abc")
        with pytest.raises(ValueError):
            PropertyData._to_float_eu(None)

    def test_parse_float_fields_valid(self) -> None:
        """parse_float_fields converts strings with commas to floats."""
        assert PropertyData.parse_float_fields("30,2") == 30.2

    def test_parse_float_fields_invalid(self) -> None:
        """parse_float_fields must raise ValueError for malformed numbers."""
        with pytest.raises(ValueError):
            PropertyData.parse_float_fields("xx,yy")

    def test_parse_int_fields_valid(self) -> None:
        """parse_int_fields converts strings and floats to ints."""
        assert PropertyData.parse_int_fields("75") == 75
        assert PropertyData.parse_int_fields("75.0") == 75

    def test_parse_int_fields_invalid(self) -> None:
        """parse_int_fields raises ValueError for invalid integers."""
        with pytest.raises(ValueError):
            PropertyData.parse_int_fields("7a")

    def test_property_type_in_known_range_valid(self) -> None:
        """Allowed values for property_type_code should pass."""
        assert PropertyData.property_type_in_known_range(1) == 1
        assert PropertyData.property_type_in_known_range(4) == 4

    def test_property_type_in_known_range_invalid(self) -> None:
        """Out-of-range property_type_code values must raise ValueError."""
        with pytest.raises(ValueError):
            PropertyData.property_type_in_known_range(0)
        with pytest.raises(ValueError):
            PropertyData.property_type_in_known_range(5)
