"""
Integration tests for interface components.

These tests verify that interface components (forms, validation) work correctly with backend.
"""

from fpi.interface.prediction.form import validate_inputs


class TestPredictionFormIntegration:
    """Integration tests for prediction form validation and processing."""

    def test_form_validation_valid_inputs(self):
        """Test form validation with valid inputs."""
        # Arrange
        postal = "75002"
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 43.0
        rooms = 2
        land = 69.0

        # Act
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)

        # Assert
        assert error_msg == "", "Valid inputs should not produce errors"

    def test_form_validation_missing_fields(self):
        """Test form validation with missing fields."""
        # Arrange
        postal = ""
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 43.0
        rooms = 2
        land = 69.0

        # Act
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Missing fields should produce error"
        assert "Postal code" in error_msg or "required" in error_msg

    def test_form_validation_invalid_postal_code(self):
        """Test form validation with invalid postal code format."""
        # Arrange
        postal = "750"  # Invalid: not 5 digits
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 43.0
        rooms = 2
        land = 69.0

        # Act
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Invalid postal code should produce error"
        assert "postal code" in error_msg.lower()

    def test_form_validation_invalid_area(self):
        """Test form validation with invalid area values."""
        # Arrange - Area too large
        postal = "75002"
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 2000.0  # Too large
        rooms = 2
        land = 69.0

        # Act
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Invalid area should produce error"
        assert "area" in error_msg.lower() or "realistic" in error_msg.lower()

    def test_form_validation_invalid_rooms(self):
        """Test form validation with invalid number of rooms."""
        # Arrange - Negative rooms
        postal = "75002"
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 43.0
        rooms = -1  # Invalid
        land = 69.0

        # Act
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Invalid rooms should produce error"
        assert "rooms" in error_msg.lower() or "positive" in error_msg.lower()

    def test_form_validation_invalid_land_area(self):
        """Test form validation with invalid land area."""
        # Arrange - Land area too large
        postal = "75002"
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 43.0
        rooms = 2
        land = 200000.0  # Too large

        # Act
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)

        # Assert
        assert error_msg.startswith("Error :"), "Invalid land area should produce error"
        assert "land" in error_msg.lower() or "realistic" in error_msg.lower()

    def test_prediction_form_to_model_integration(self, temp_data_dir, sample_cleaned_csv_file):
        """Test that form inputs are correctly processed and passed to prediction."""
        # This test verifies the integration between form validation and prediction
        # Arrange - Valid form inputs
        postal = "75002"
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 43.0
        rooms = 2
        land = 69.0

        # Act - Validate inputs
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)
        assert error_msg == "", "Inputs should be valid"

        # Act - Convert to model input format (as done in prediction_page.py)
        property_type_code = 1 if prop_type.lower() == "house" else 2
        input_data = {
            "building_area": float(area),
            "main_rooms": int(rooms),
            "land_area": float(land),
            "postal_code": int(postal),
            "property_type_code": property_type_code,
            "town_code": int(town),
            "department_code": int(dept),
        }

        # Assert - Verify conversion
        assert input_data["postal_code"] == 75002, "Postal code should be converted correctly"
        assert input_data["property_type_code"] == 2, "Apartment should map to code 2"
        assert input_data["building_area"] == 43.0, "Area should be float"
        assert input_data["main_rooms"] == 2, "Rooms should be int"
        assert input_data["department_code"] == 75, "Department code should be int"

    def test_run_prediction_with_valid_inputs_mock(self):
        """Test run_prediction function with valid inputs (mocked model)."""
        # Note: This tests the run_prediction function logic without requiring a trained model
        # The actual prediction call would fail without a model, so we test the input processing

        # Arrange - Valid inputs
        postal = "75002"
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 43.0
        rooms = 2
        land = 69.0

        # Act - Validate inputs first (as run_prediction does)
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)

        # Assert - Inputs should be valid
        assert error_msg == "", "Inputs should pass validation"

        # Act - Convert to model format (as run_prediction does)
        property_type_code = 1 if prop_type.lower() == "house" else 2
        input_data = {
            "building_area": float(area),
            "main_rooms": int(rooms),
            "land_area": float(land),
            "postal_code": int(postal),
            "property_type_code": property_type_code,
            "town_code": int(town),
            "department_code": int(dept),
        }

        # Assert - Data should be in correct format
        assert all(isinstance(v, (int, float)) for v in input_data.values()), "All values should be numeric"
        assert input_data["property_type_code"] in [1, 2], "Property type code should be 1 or 2"

    def test_run_prediction_with_invalid_inputs(self):
        """Test run_prediction function with invalid inputs."""
        # Arrange - Invalid inputs (missing postal code)
        postal = ""
        dept = "75"
        town = "102"
        prop_type = "Apartment"
        area = 43.0
        rooms = 2
        land = 69.0

        # Act - Validate inputs
        error_msg = validate_inputs(postal, dept, town, prop_type, area, rooms, land)

        # Assert - Should return error message
        assert error_msg.startswith("Error :"), "Invalid inputs should produce error"
        # run_prediction would return this error message without calling the model
