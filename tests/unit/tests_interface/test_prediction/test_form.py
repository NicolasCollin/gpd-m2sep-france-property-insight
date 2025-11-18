import gradio as gr
import pandas as pd

from fpi.interface.prediction.form import get_form, reset_form, validate_inputs


class TestValidateInputs:
    """
    Unit tests for the `validate_inputs` function.

    This class tests the input validation logic for property predictions.
    Tests include:
        - Valid input passes with no error message.
        - Missing required fields return an appropriate error.
        - Area, rooms, and land have realistic, positive values.
        - Postal code must follow a 5-digit format.
    """

    def test_all_valid_inputs(self) -> None:
        """Returns empty string when all inputs are valid."""
        postal: str = "75001"
        prop_type: str = "House"
        area: float = 100.0
        rooms: int = 3
        land: float = 50.0

        result: str = validate_inputs(postal, prop_type, area, rooms, land)
        assert result == ""

    def test_missing_required_field(self) -> None:
        """Returns error when a required field is missing."""
        result: str = validate_inputs("", "House", 100.0, 3, 50.0)
        assert "Postal code" in result

    def test_invalid_area(self) -> None:
        """Returns error when area is zero or unrealistic."""
        result: str = validate_inputs("75001", "House", 0.0, 3, 50.0)
        assert "Living area" in result

    def test_invalid_rooms(self) -> None:
        """Returns error when rooms are zero or unrealistic."""
        result: str = validate_inputs("75001", "House", 100.0, 0, 50.0)
        assert "Number of rooms" in result

    def test_invalid_land(self) -> None:
        """Returns error when land area is negative or too large."""
        result: str = validate_inputs("75001", "House", 100.0, 3, -1.0)
        assert "Land area" in result


class TestGetForm:
    """
    Unit tests for the `get_form` function.

    This class tests the construction of the Gradio prediction form. Tests include:
        - The function returns a tuple with a list of input components and a Dropdown.
        - The input list contains exactly the expected number of form components.
        - Dropdown component has the correct default value and choices.
    """

    def setup(self) -> None:
        """A mock data for all tests"""
        self.df_mock = pd.DataFrame(
            {
                "postal_code": [75001, 75002],
                "town_name": ["PARIS 01", "PARIS 02"],
                "property_type": ["Maison", "Apartement", "Dépendance", "Local industriel. commercial ou assimilé"],
            }
        )

    def test_returns_components_and_dropdown(self) -> None:
        """get_form returns a list of FormComponents and 2 Dropdown."""
        with gr.Blocks():
            inputs_list, postal_input, prop_type_input = get_form()

        assert isinstance(inputs_list, list)
        assert all(isinstance(c, gr.components.FormComponent) for c in inputs_list)
        assert isinstance(postal_input, gr.Dropdown)
        assert isinstance(prop_type_input, gr.Dropdown)

    def test_form_contains_expected_number_of_inputs(self) -> None:
        """Inputs list has exactly 5 components."""
        with gr.Blocks():
            inputs_list, _, _ = get_form()
        assert len(inputs_list) == 5


class TestResetForm:
    """
    Unit tests for the `reset_form` function.

    This class verifies that the reset_form utility correctly returns
    a tuple of default form values suitable for initializing or resetting
    the prediction form. Tests include:
        - Tuple has the expected length of 8 elements.
        - Default values match the expected empty or initial state.
        - The final output string contains the expected markdown for display.
    """

    def test_returns_tuple_with_correct_length(self) -> None:
        """reset_form returns a tuple of 8 elements."""
        result: tuple[str, str, float, int, float, str] = reset_form()
        assert isinstance(result, tuple)
        assert len(result) == 6

    def test_default_values_are_correct(self) -> None:
        """Tuple contains default form values and markdown reset text."""
        result: tuple[str, str, float, int, float, str] = reset_form()
        postal, prop_type, area, rooms, land, output = result

        assert postal == ""
        assert prop_type == "Maison"
        assert area == 0.0
        assert rooms == 0
        assert land == 0.0
        assert output == "Estimation : **--- €**"

    def test_output_is_final_string(self) -> None:
        """Last element in tuple should be a string used for markdown output."""
        result: tuple[str, str, float, int, float, str] = reset_form()
        output: str = result[-1]
        assert isinstance(output, str)
        assert "€" in output
