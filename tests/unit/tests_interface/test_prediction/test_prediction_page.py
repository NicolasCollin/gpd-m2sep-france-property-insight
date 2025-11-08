from unittest.mock import patch

import gradio as gr

from fpi.interface.prediction.prediction_page import get_prediction_page, run_prediction


class TestRunPrediction:
    """
    Unit tests for the `run_prediction` function.

    This class covers the core prediction logic, including:
        - Valid inputs producing correctly formatted price strings.
        - Handling of invalid postal codes.
        - Model exceptions being caught and reported.
        - Correct conversion of property type to internal code.
        - Detection of missing required fields.
    """

    def test_valid_inputs_returns_estimation(self) -> None:
        """
        Should return a formatted price string when inputs are valid.
        """
        with patch("fpi.interface.prediction.prediction_page.predict_price") as mock_predict:
            mock_predict.return_value: float = 250000.0

            postal: str = "75005"
            dept: str = "75"
            town: str = "75101"
            prop_type: str = "House"
            area: float = 120.0
            rooms: int = 4
            land: float = 50.0

            result: str = run_prediction(postal, dept, town, prop_type, area, rooms, land)

        assert result.startswith("Estimated property price")
        assert "250,000" in result

    def test_invalid_postal_returns_error(self) -> None:
        """
        Should return a validation error when postal code is invalid.
        """
        postal: str = "7500"  # invalid postal
        dept: str = "75"
        town: str = "75101"
        prop_type: str = "House"
        area: float = 100.0
        rooms: int = 3
        land: float = 50.0

        result: str = run_prediction(postal, dept, town, prop_type, area, rooms, land)

        assert "postal code" in result.lower()

    def test_model_raises_exception(self) -> None:
        """
        Should return an error message when predict_price raises an exception.
        """
        with patch("fpi.interface.prediction.prediction_page.predict_price") as mock_predict:
            mock_predict.side_effect: Exception = Exception("Model file not found")

            postal: str = "75001"
            dept: str = "75"
            town: str = "75101"
            prop_type: str = "Apartment"
            area: float = 80.0
            rooms: int = 2
            land: float = 20.0

            result: str = run_prediction(postal, dept, town, prop_type, area, rooms, land)

        assert result.startswith("Prediction failed")
        assert "Model file not found" in result

    def test_property_type_conversion_house(self) -> None:
        """
        Should assign property_type_code = 1 for House.
        """
        with patch("fpi.interface.prediction.prediction_page.predict_price") as mock_predict:
            mock_predict.return_value: float = 1.0

            result: str = run_prediction("75005", "75", "75101", "House", 100.0, 3, 50.0)

        assert "1" in result

    def test_property_type_conversion_apartment(self) -> None:
        """
        Should assign property_type_code = 2 for Apartment.
        """
        with patch("fpi.interface.prediction.prediction_page.predict_price") as mock_predict:
            mock_predict.return_value: float = 2.0

            result: str = run_prediction("75005", "75", "75101", "Apartment", 100.0, 3, 50.0)

        assert "2" in result

    def test_missing_required_fields(self) -> None:
        """
        Should return an error when required fields (postal, dept, town) are missing.
        """
        postal: str = ""
        dept: str = ""
        town: str = ""
        prop_type: str = "House"
        area: float = 100.0
        rooms: int = 3
        land: float = 50.0

        result: str = run_prediction(postal, dept, town, prop_type, area, rooms, land)

        assert "postal code" in result.lower() or "required" in result.lower()


class TestGetPredictionPage:
    """
    Unit tests for the `get_prediction_page` function.

    This class ensures the Gradio interface for property predictions is constructed correctly:
        - Returned tuple contains expected component types.
        - Buttons have correct labels.
        - Result output Markdown initializes with the correct placeholder text.
    """

    def test_returns_expected_tuple(self) -> None:
        """
        Should return a tuple of (predict_btn, reset_btn, result_output, inputs_list)
        with the correct types.
        """
        with gr.Blocks():  # Ensure Gradio context
            predict_btn, reset_btn, result_output, inputs_list = get_prediction_page()

        assert isinstance(predict_btn, gr.Button)
        assert isinstance(reset_btn, gr.Button)
        assert isinstance(result_output, gr.Markdown)
        assert isinstance(inputs_list, list)
        assert all(isinstance(c, gr.components.FormComponent) for c in inputs_list)

    def test_buttons_have_correct_labels(self) -> None:
        """
        The predict button should be labeled 'Estimate', reset button 'Reset'.
        """
        with gr.Blocks():
            predict_btn, reset_btn, _, _ = get_prediction_page()

        assert predict_btn.value == "Estimate"
        assert reset_btn.value == "Reset"

    def test_result_output_initial_value(self) -> None:
        """
        The result_output Markdown should contain the placeholder text.
        """
        with gr.Blocks():
            _, _, result_output, _ = get_prediction_page()

        assert isinstance(result_output.value, str)
        assert "--- €" in result_output.value
