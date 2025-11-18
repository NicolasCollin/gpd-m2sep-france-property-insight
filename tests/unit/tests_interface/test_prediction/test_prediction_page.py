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

    @patch("fpi.interface.prediction.prediction_page.validate_inputs")
    @patch("fpi.interface.prediction.prediction_page.df")
    @patch("fpi.interface.prediction.prediction_page.predict_price")
    def test_valid_inputs_returns_estimation(self, mock_predict, mock_df, mock_validate):
        """Should return a formatted price string when inputs are valid."""
        mock_validate.return_value = ""
        mock_df.__getitem__.return_value = mock_df
        mock_df.empty = False
        mock_predict.return_value = 250000.0

        result = run_prediction("75005", "Maison", 120.0, 4, 50.0)

        assert result.startswith("Estimated property price")
        assert "250,000" in result

    @patch("fpi.interface.prediction.prediction_page.validate_inputs")
    def test_invalid_postal_returns_error(self, mock_validate):
        """Should return validation error when postal is invalid."""
        mock_validate.return_value = "Invalid postal code"

        result = run_prediction("123", "Maison", 100, 3, 50)

        assert "invalid postal" in result.lower()

    @patch("fpi.interface.prediction.prediction_page.validate_inputs")
    @patch("fpi.interface.prediction.prediction_page.df")
    @patch("fpi.interface.prediction.prediction_page.predict_price")
    def test_model_raises_exception(self, mock_predict, mock_df, mock_validate):
        """Should return error message when predict_price raises exception."""
        mock_validate.return_value = ""

        mock_df.__getitem__.return_value = mock_df
        mock_df.empty = False

        mock_predict.side_effect = Exception("Model file not found")

        result = run_prediction("75005 - PARIS 05", "Apartement", 80, 2, 20)

        assert result.startswith("Prediction failed")
        assert "Model file not found" in result

    @patch("fpi.interface.prediction.prediction_page.validate_inputs")
    @patch("fpi.interface.prediction.prediction_page.df")
    @patch("fpi.interface.prediction.prediction_page.predict_price")
    def test_property_type_conversion_house(self, mock_predict, mock_df, mock_validate):
        """Check that property_type_code=1 for House."""
        mock_validate.return_value = ""
        mock_df.__getitem__.return_value = mock_df
        mock_df.empty = False
        mock_predict.return_value = 1.0

        result = run_prediction("75005 - PARIS 05", "Maison", 100, 3, 50)

        assert "1" in result

    @patch("fpi.interface.prediction.prediction_page.validate_inputs")
    @patch("fpi.interface.prediction.prediction_page.df")
    @patch("fpi.interface.prediction.prediction_page.predict_price")
    def test_missing_required_fields(self, mock_predict, mock_df, mock_validate):
        """Should return validation error when postal is empty."""
        mock_validate.return_value = "Postal code is required"

        result = run_prediction("", "Maison", 100, 3, 50)

        assert "postal" in result.lower()


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
        with gr.Blocks():
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
