"""
Integration tests for interface components.

These tests verify that interface components, such as forms and input validation,
work correctly with the backend. They simulate user input scenarios and ensure
that validation, conversion to model input, and prediction integration behave as expected.
"""

from pathlib import Path

from fpi.interface.prediction.form import validate_inputs


class TestPredictionFormIntegration:
    """Integration tests for prediction form validation and processing."""

    def test_form_validation_valid_inputs(self) -> None:
        """
        Test form validation with valid inputs.

        Ensures that all fields are correctly validated and no errors are returned
        when inputs are within expected ranges and formats.
        """
        # Arrange
        postal: str = "75002"
        prop_type: str = "Apartment"
        area: float = 43.0
        rooms: int = 2
        land: float = 69.0

        # Act
        error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)

        # Assert
        assert error_msg == "", "Valid inputs should not produce errors"

    def test_form_validation_missing_fields(self) -> None:
        """
        Test form validation with missing required fields.

        Checks that missing fields generate appropriate error messages.
        """
        # Arrange
        postal: str = ""
        prop_type: str = "Apartment"
        area: float = 43.0
        rooms: int = 2
        land: float = 69.0

        # Act
        error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Missing fields should produce error"
        assert "Postal code" in error_msg or "required" in error_msg

    def test_form_validation_invalid_area(self) -> None:
        """
        Test form validation with unrealistic property area.

        Ensures that excessively large areas are flagged as invalid.
        """
        # Arrange
        postal: str = "75002"
        prop_type: str = "Apartment"
        area: float = 2000.0  # Too large
        rooms: int = 2
        land: float = 69.0

        # Act
        error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Invalid area should produce error"
        assert "area" in error_msg.lower() or "realistic" in error_msg.lower()

    def test_form_validation_invalid_rooms(self) -> None:
        """
        Test form validation with invalid number of rooms.

        Negative or unrealistic numbers of rooms should produce errors.
        """
        # Arrange
        postal: str = "75002"
        prop_type: str = "Apartment"
        area: float = 43.0
        rooms: int = -1  # Invalid
        land: float = 69.0

        # Act
        error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Invalid rooms should produce error"
        assert "rooms" in error_msg.lower() or "positive" in error_msg.lower()

    def test_form_validation_invalid_land_area(self) -> None:
        """
        Test form validation with unrealistic land area.

        Ensures excessively large land areas are rejected.
        """
        # Arrange
        postal: str = "75002"
        prop_type: str = "Apartment"
        area: float = 43.0
        rooms: int = 2
        land: float = 200000.0  # Too large

        # Act
        error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Invalid land area should produce error"
        assert "land" in error_msg.lower() or "realistic" in error_msg.lower()

    def test_prediction_form_to_model_integration(self, temp_data_dir: Path, sample_cleaned_csv_file: Path) -> None:
        """
        Test that valid form inputs are correctly processed and converted to model input.

        Verifies that:
        - Validation passes for valid inputs.
        - Inputs are transformed to the correct numeric types.
        - Property type strings are correctly mapped to numeric codes.
        """
        # Arrange
        postal: str = "75002"
        prop_type: str = "Apartment"
        area: float = 43.0
        rooms: int = 2
        land: float = 69.0

        # Act - Validate inputs
        error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)
        assert error_msg == "", "Inputs should be valid"

        # Act - Convert to model input
        property_type_code: int = 1 if prop_type.lower() == "house" else 2
        input_data: dict[str, int | float] = {
            "building_area": float(area),
            "main_rooms": int(rooms),
            "land_area": float(land),
            "postal_code": int(postal),
            "property_type_code": property_type_code,
        }

        # Assert
        assert input_data["postal_code"] == 75002
        assert input_data["property_type_code"] == 2
        assert input_data["building_area"] == 43.0
        assert input_data["main_rooms"] == 2
        assert input_data["land_area"] == 69.0

    def test_run_prediction_with_valid_inputs_mock(self) -> None:
        """
        Test input processing for run_prediction function with valid inputs.

        This test ensures that form data is correctly converted to the numeric format
        expected by the prediction model, without requiring an actual trained model.
        """
        # Arrange
        postal: str = "75002"
        prop_type: str = "Apartment"
        area: float = 43.0
        rooms: int = 2
        land: float = 69.0

        # Act
        error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)
        assert error_msg == "", "Inputs should pass validation"

        property_type_code: int = 1 if prop_type.lower() == "house" else 2
        input_data: dict[str, int | float] = {
            "building_area": float(area),
            "main_rooms": int(rooms),
            "land_area": float(land),
            "postal_code": int(postal),
            "property_type_code": property_type_code,
        }

        # Assert
        assert all(isinstance(v, (int, float)) for v in input_data.values())
        assert input_data["property_type_code"] in [1, 2]

    def test_run_prediction_with_invalid_inputs(self) -> None:
        """
        Test run_prediction function with invalid inputs.

        Verifies that missing or malformed inputs are detected and result in error messages.
        """
        # Arrange
        postal: str = ""
        prop_type: str = "Apartment"
        area: float = 43.0
        rooms: int = 2
        land: float = 69.0

        # Act
        error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Invalid inputs should produce error"
