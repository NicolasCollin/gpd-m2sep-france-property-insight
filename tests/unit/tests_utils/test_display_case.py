import pytest

from fpi.utils.display_case import format_display_name


class TestFormatDisplayName:
    """
    Unit tests for the `format_display_name` function.

    Scenarios tested:
        1. Standard snake_case variable names are converted to human-readable format.
        2. camelCase variable names are split and capitalized.
        3. Mixed snake_case and camelCase are handled correctly.
        4. Empty string input returns an empty string.
        5. Leading/trailing underscores are removed in the display format.
    """

    @pytest.mark.parametrize(
        "input_name, expected_output",
        [
            ("property_value", "Property value"),
            ("yearBuilt", "Year built"),
            ("totalRooms", "Total rooms"),
            ("land_area", "Land area"),
            ("numberOfBathrooms", "Number of bathrooms"),
            ("_private_var", "Private var"),
            ("", ""),
            ("alreadyFormatted", "Already formatted"),
            ("mixed_case_VarName", "Mixed case var name"),
        ],
    )
    def test_format_display_name_various_cases(self, input_name: str, expected_output: str) -> None:
        """
        Parametrized test for various input formats.

        Args:
            input_name (str): Variable name to format.
            expected_output (str): Expected human-readable output.
        """
        result: str = format_display_name(input_name)
        assert result == expected_output

    def test_leading_trailing_spaces_removed(self) -> None:
        """
        Ensure that leading/trailing spaces in the input are removed in the output.
        """
        input_name: str = "  property_value  "
        result: str = format_display_name(input_name)
        assert result == "Property value"

    def test_empty_string_returns_empty(self) -> None:
        """
        Ensure that passing an empty string returns an empty string.
        """
        input_name: str = ""
        result: str = format_display_name(input_name)
        assert result == ""

    def test_camel_and_snake_combined(self) -> None:
        """
        Test a variable name that mixes camelCase and underscores.
        """
        input_name: str = "myVariable_name"
        result: str = format_display_name(input_name)
        assert result == "My variable name"
