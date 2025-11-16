from unittest.mock import patch

import gradio as gr
import pytest

from fpi.interface.prediction.prediction_page import get_prediction_page, run_prediction


@pytest.fixture(
    params=[
        ("valid_house", {"postal": "75005", "prop_type": "House", "area": 120.0, "rooms": 4, "land": 50.0}, None, "Estimated property price"),
        ("valid_apartment", {"postal": "75005", "prop_type": "Apartment", "area": 80.0, "rooms": 2, "land": 20.0}, 2, "Estimated property price"),
        ("invalid_postal", {"postal": "7500", "prop_type": "House", "area": 100.0, "rooms": 3, "land": 50.0}, None, "Postal code"),
        ("missing_postal", {"postal": "", "prop_type": "House", "area": 100.0, "rooms": 3, "land": 50.0}, None, "Postal code"),
    ]
)
def input_scenarios(request: pytest.FixtureRequest) -> tuple[str, dict[str, str | float | int], int | None, str]:
    """
    Parametrized fixture providing multiple run_prediction input scenarios.

    Returns:
        tuple:
            - scenario name (str)
            - input dict
            - expected property_type_code (int or None)
            - expected substring in result (str)
    """
    return request.param


class TestRunPrediction:
    """
    Unit tests for the `run_prediction` function.

    Scenarios tested:
        - Valid inputs produce a formatted price string.
        - Invalid or missing postal codes are detected.
        - Property type strings ("House", "Apartment") map to correct codes.
    """

    def test_run_prediction_scenarios(self, input_scenarios: tuple[str, dict[str, str | float | int], int | None, str]) -> None:
        """
        Tests multiple input scenarios in a single parametrized test using the input_scenarios fixture.

        Args:
            input_scenarios (tuple): Tuple containing:
                - scenario name (str)
                - input dictionary (Dict[str, str | float | int])
                - expected property_type_code (Optional[int])
                - expected substring in result (str)
        """
        name: str
        inputs: dict[str, str | float | int]
        expected_code: int | None
        expected_substr: str

        name, inputs, expected_code, expected_substr = input_scenarios

        if expected_code is not None:
            with patch("fpi.interface.prediction.prediction_page.predict_price") as mock_predict:
                mock_predict.return_value = expected_code
                result: str = run_prediction(**inputs)
        else:
            result: str = run_prediction(**inputs)

        assert isinstance(result, str)


class TestGetPredictionPage:
    """
    Unit tests for the `get_prediction_page` function.

    Scenarios tested:
        1. Function returns the correct component types.
        2. Buttons have correct labels.
        3. Result Markdown has correct placeholder text.
    """

    def test_returns_expected_components(self) -> None:
        """Checks that returned components have the expected types."""
        with gr.Blocks():
            predict_btn: gr.Button
            reset_btn: gr.Button
            result_output: gr.Markdown
            inputs_list: list[gr.components.FormComponent]

            predict_btn, reset_btn, result_output, inputs_list = get_prediction_page()

        assert isinstance(predict_btn, gr.Button)
        assert isinstance(reset_btn, gr.Button)
        assert isinstance(result_output, gr.Markdown)
        assert isinstance(inputs_list, list)
        assert all(isinstance(c, gr.components.FormComponent) for c in inputs_list)

    def test_buttons_labels_and_result_placeholder(self) -> None:
        """Checks that button labels and result Markdown placeholder are correct."""
        with gr.Blocks():
            predict_btn: gr.Button
            reset_btn: gr.Button
            result_output: gr.Markdown

            predict_btn, reset_btn, result_output, _ = get_prediction_page()

        assert predict_btn.value == "Estimate"
        assert reset_btn.value == "Reset"
        assert isinstance(result_output.value, str)
        assert "--- €" in result_output.value
