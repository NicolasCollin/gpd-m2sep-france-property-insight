import gradio as gr
import pytest

from fpi.interface.prediction.form import get_form, reset_form, validate_inputs


@pytest.fixture
def valid_inputs() -> dict[str, str | float | int]:
    """
    Standard valid inputs for property prediction.

    Returns:
        dict: keys - postal, prop_type, area, rooms, land
    """
    return {
        "postal": "75001",
        "prop_type": "House",
        "area": 100.0,
        "rooms": 3,
        "land": 50.0,
    }


@pytest.fixture(
    params=[
        ("missing_postal", {"postal": "", "prop_type": "House", "area": 100.0, "rooms": 3, "land": 50.0}, "Postal code"),
        ("invalid_area", {"postal": "75001", "prop_type": "House", "area": 0.0, "rooms": 3, "land": 50.0}, "Living area"),
        ("invalid_rooms", {"postal": "75001", "prop_type": "House", "area": 100.0, "rooms": 0, "land": 50.0}, "Number of rooms"),
        ("invalid_land", {"postal": "75001", "prop_type": "House", "area": 100.0, "rooms": 3, "land": -1.0}, "Land area"),
        ("invalid_postal_format", {"postal": "7500", "prop_type": "House", "area": 100.0, "rooms": 3, "land": 50.0}, "postal code"),
    ]
)
def invalid_input_scenarios(request) -> tuple[str, dict[str, str | float | int], str]:
    """
    Parametrized fixture for invalid input scenarios.

    Returns:
        tuple: (scenario_name, input_dict, expected_error_substring)
    """
    return request.param


class TestValidateInputs:
    """
    Unit tests for `validate_inputs`.

    Scenarios tested:
        - All valid inputs produce an empty string (no error).
        - Missing required fields return an appropriate error.
        - Area, rooms, and land values must be positive and realistic.
        - Postal code must be exactly 5 digits.
    """

    def test_valid_inputs(self, valid_inputs: dict[str, str | float | int]) -> None:
        """Returns empty string when all inputs are valid."""
        result: str = validate_inputs(**valid_inputs)
        assert result == ""

    def test_invalid_inputs(self, invalid_input_scenarios: tuple[str, dict[str, str | float | int], str]) -> None:
        """Returns an error string for various invalid inputs."""
        _, inputs, expected_error = invalid_input_scenarios
        result: str = validate_inputs(**inputs)
        assert expected_error.lower() in result.lower()


class TestGetForm:
    """
    Unit tests for `get_form`.

    Scenarios tested:
        - Returns a tuple of input components list and a Dropdown.
        - Input list contains exactly the expected number of components.
        - Dropdown default value is 'House' with choices ['House', 'Apartment'].
    """

    def test_returns_components_and_dropdown(self) -> None:
        """Returns list of FormComponents and a Dropdown."""
        with gr.Blocks():
            inputs_list: list[gr.components.FormComponent]
            postal_input: gr.Dropdown
            prop_type_input: gr.Dropdown
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
    Unit tests for `reset_form`.

    Scenarios tested:
        - Returns a tuple of 6 elements corresponding to form fields and output string.
        - Default values are empty or initial state.
        - Last element is a markdown string containing '€'.
    """

    def test_returns_tuple_with_correct_length(self) -> None:
        """reset_form returns a tuple of 6 elements (postal, prop_type, area, rooms, land, output)."""
        result: tuple[str, str, float, int, float, str] = reset_form()
        assert isinstance(result, tuple)
        assert len(result) == 6

    def test_default_values(self) -> None:
        """Tuple values match expected initial state for the form."""
        postal: str
        prop_type: str
        area: float
        rooms: int
        land: float
        output: str

        postal, prop_type, area, rooms, land, output = reset_form()
        assert postal == ""
        assert prop_type == "Maison"
        assert area == 0.0
        assert rooms == 0
        assert land == 0.0
        assert output == "Estimation : **--- €**"

    def test_output_contains_euro(self) -> None:
        """Last element in tuple is a string containing '€' for markdown output."""
        output: str = reset_form()[-1]
        assert isinstance(output, str)
        assert "€" in output
