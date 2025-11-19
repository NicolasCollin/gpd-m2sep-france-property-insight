import gradio as gr

from fpi.interface.prediction.prediction_page import get_prediction_page


class TestGetPredictionPage:
    """
    Unit tests for the `get_prediction_page` function.

    Scenarios tested:
        1. Function returns the correct component types.
        2. Buttons have correct labels.
        3. Result Markdown has correct placeholder text.
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
