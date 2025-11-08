import pytest
from pydantic import ValidationError

from fpi.data_pipeline.schemas import PredictionFormSchema, PropertyData


class TestPredictionFormSchema:
    def test_valid_input(self) -> None:
        """Valid data should create a PredictionFormSchema instance."""
        data = {
            "postal": "75001",
            "dept": "75",
            "town": "101",
            "prop_type": "House",
            "area": 50.0,
            "rooms": 2,
            "land": 100.0,
        }
        form = PredictionFormSchema(**data)

        assert form.postal == "75001"
        assert form.dept == "75"
        assert form.town == "101"
        assert form.prop_type == "House"
        assert form.area == 50.0
        assert form.rooms == 2
        assert form.land == 100.0
        assert form.output == ""  # default value


class TestPropertyData:
    def test_valid_input(self) -> None:
        """Valid property row is parsed correctly with coercion."""
        data = {
            "property_value": "1000000,50",
            "postal_code": "75001",
            "department_code": "75",
            "town_code": "101",
            "property_type_code": "1",
            "building_area": "50,0",
            "main_rooms": "2",
            "land_area": "100,5",
        }

        prop = PropertyData(**data)

        assert prop.property_value == pytest.approx(1000000.50)
        assert prop.postal_code == 75001
        assert prop.department_code == 75
        assert prop.town_code == 101
        assert prop.property_type_code == 1
        assert prop.building_area == pytest.approx(50.0)
        assert prop.main_rooms == pytest.approx(2.0)
        assert prop.land_area == pytest.approx(100.5)

    def test_invalid_property_value_zero(self) -> None:
        """property_value <= 0 should raise ValidationError."""
        data = {
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
        """property_type_code outside 1–4 should raise ValidationError."""
        data = {
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
        """Malformed numeric strings should raise ValidationError."""
        data = {
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
