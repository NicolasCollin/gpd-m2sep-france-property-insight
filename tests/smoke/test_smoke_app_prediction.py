from unittest.mock import MagicMock, patch

import gradio as gr

from fpi.interface.menu import app_menu
from fpi.interface.prediction.prediction_page import get_prediction_page, run_prediction


class TestAppPredictionSmoke:
    """
    Smoke tests for the app-to-prediction workflow.

    Methods:
    1. test_app_runs
       - Verifies the app can be initialized as a Gradio Blocks object.

    2. test_prediction_page_runs
       - Verifies that the prediction page can be created within a Blocks context.

    3. test_prediction_flow_runs
       - Checks that a user can submit typical inputs and receive a result.

    4. test_prediction_flow_validation_error
       - Checks that invalid inputs return an error string.
    """

    def test_app_runs(self) -> None:
        """App can be initialized without crashing."""
        app: gr.Blocks = app_menu()
        assert isinstance(app, gr.Blocks)

    def test_prediction_page_runs(self) -> None:
        """Prediction page can be created without crashing, within a Blocks context."""
        with gr.Blocks():
            predict_btn, reset_btn, result_output, inputs_list = get_prediction_page()

        assert predict_btn is not None
        assert reset_btn is not None
        assert result_output is not None
        assert inputs_list is not None

    @patch("fpi.interface.prediction.prediction_page.predict_price")
    def test_prediction_flow_runs(self, mock_predict: MagicMock) -> None:
        """Prediction flow runs with valid inputs (mocked model)."""
        mock_predict.return_value = 1.0  # Minimal dummy prediction
        result: str = run_prediction("75002", "Apartment", 43.0, 2, 69.0)
        assert isinstance(result, str)
        assert mock_predict.called

    def test_prediction_flow_validation_error(self) -> None:
        """Prediction flow handles invalid inputs without crashing."""
        result: str = run_prediction("123", "Apartment", 43.0, 2, 69.0)
        assert isinstance(result, str)
        assert result.startswith("Error :")
