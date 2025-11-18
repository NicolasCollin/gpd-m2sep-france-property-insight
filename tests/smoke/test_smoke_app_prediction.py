import gradio as gr

from fpi.interface.menu import app_menu
from fpi.interface.prediction.prediction_page import get_prediction_page, run_prediction


def test_app_smoke_full_flow() -> None:
    """
    Global smoke test for the app-to-prediction workflow.

    This test performs a quick end-to-end sanity check:
    1. Initializes the app.
    2. Creates the prediction page.
    3. Runs a prediction with valid inputs.
    4. Runs a prediction with invalid inputs.

    Purpose: Ensure the app and prediction page can run without crashing.
    """

    # 1. Initialize app
    app: gr.Blocks = app_menu()
    assert isinstance(app, gr.Blocks)

    # 2. Create prediction page
    with gr.Blocks():
        predict_btn: gr.components.Button
        reset_btn: gr.components.Button
        result_output: gr.components.Markdown
        inputs_list: list[gr.components.FormComponent]

        predict_btn, reset_btn, result_output, inputs_list = get_prediction_page()
        assert predict_btn is not None
        assert reset_btn is not None
        assert result_output is not None
        assert inputs_list is not None

    # 3. Run prediction with valid inputs
    result_valid: str = run_prediction("75002", "Apartment", 43.0, 2, 69.0)
    assert isinstance(result_valid, str)
    assert "Estimated property price" in result_valid or "Prediction failed" in result_valid

    # 4. Run prediction with invalid inputs
    result_invalid: str = run_prediction("123", "Apartment", 43.0, 2, 69.0)
    assert isinstance(result_invalid, str)
    assert result_invalid.startswith("Error :") or "failed" in result_invalid
