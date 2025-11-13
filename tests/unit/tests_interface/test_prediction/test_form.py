import gradio as gr

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
        dept: str = "75"
        town: str = "75101"
        prop_type: str = "House"
        area: float = 100.0
        rooms: int = 3
        land: float = 50.0

        result: str = validate_inputs(postal, dept, town, prop_type, area, rooms, land)
        assert result == ""

    def test_missing_required_field(self) -> None:
        """Returns error when a required field is missing."""
        result: str = validate_inputs("", "75", "75101", "House", 100.0, 3, 50.0)
        assert "Postal code" in result

    def test_invalid_area(self) -> None:
        """Returns error when area is zero or unrealistic."""
        result: str = validate_inputs("75001", "75", "75101", "House", 0.0, 3, 50.0)
        assert "Living area" in result

    def test_invalid_rooms(self) -> None:
        """Returns error when rooms are zero or unrealistic."""
        result: str = validate_inputs("75001", "75", "75101", "House", 100.0, 0, 50.0)
        assert "Number of rooms" in result

    def test_invalid_land(self) -> None:
        """Returns error when land area is negative or too large."""
        result: str = validate_inputs("75001", "75", "75101", "House", 100.0, 3, -1.0)
        assert "Land area" in result

    def test_invalid_postal_code_format(self) -> None:
        """Returns error when postal code is not 5 digits."""
        result: str = validate_inputs("7500", "75", "75101", "House", 100.0, 3, 50.0)
        assert "postal code" in result.lower()


class TestGetForm:
    """
    Unit tests for the `get_form` function.

    This class tests the construction of the Gradio prediction form. Tests include:
        - The function returns a tuple with a list of input components and a Dropdown.
        - The input list contains exactly the expected number of form components.
        - Dropdown component has the correct default value and choices.
    """

    def test_returns_components_and_dropdown(self) -> None:
        """get_form returns a list of FormComponents and a Dropdown."""
        with gr.Blocks():
            inputs_list, prop_type_input = get_form()

        assert isinstance(inputs_list, list)
        assert all(isinstance(c, gr.components.FormComponent) for c in inputs_list)
        assert isinstance(prop_type_input, gr.Dropdown)

    def test_form_contains_expected_number_of_inputs(self) -> None:
        """Inputs list has exactly 7 components."""
        with gr.Blocks():
            inputs_list, _ = get_form()
        assert len(inputs_list) == 7

    def test_dropdown_default_value_and_choices(self) -> None:
        """Dropdown has default value 'House' and expected choices."""
        with gr.Blocks():
            _, prop_type_input = get_form()
        assert prop_type_input.value == "House"

        # handle tuple choices (label, value)
        choices_labels: list[str] = [choice[0] if isinstance(choice, tuple) else choice for choice in prop_type_input.choices]
        assert choices_labels == ["House", "Apartment"]


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
        result: tuple[str, str, str, str, float, int, float, str] = reset_form()
        assert isinstance(result, tuple)
        assert len(result) == 8

    def test_default_values_are_correct(self) -> None:
        """Tuple contains default form values and markdown reset text."""
        result: tuple[str, str, str, str, float, int, float, str] = reset_form()
        postal, dept, town, prop_type, area, rooms, land, output = result

        assert postal == ""
        assert dept == ""
        assert town == ""
        assert prop_type == "House"
        assert area == 0.0
        assert rooms == 0
        assert land == 0.0
        assert output == "Estimation : **--- €**"

    def test_output_is_final_string(self) -> None:
        """Last element in tuple should be a string used for markdown output."""
        result: tuple[str, str, str, str, float, int, float, str] = reset_form()
        output: str = result[-1]
        assert isinstance(output, str)
        assert "€" in output
