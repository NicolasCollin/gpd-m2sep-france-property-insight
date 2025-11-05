from typing import List, Tuple

import gradio as gr

from fpi.interface.prediction.form import form, reset_form, validate_inputs
from fpi.models.build_linear_model import predict_price


# =====================================================================
# CALLBACK : run prediction
# =====================================================================
def run_prediction(postal: str, dept: str, town: str, prop_type: str, area: float, rooms: int, land: float) -> str:
    """
    Call backs for the "Estimate" button. It prepares the data and calls the model prediction function.
    Args:
        postal: Postal code (string).
        dept: Department code (string).
        town: Town code (string).
        prop_type: Property type ("House" / "Apartment").
        area: Living area in square
        rooms: Number of rooms (integer).
        land: Land area (float).
    Returns:
        A string with the predicted price or an error message.
    """

    error_msg: str = validate_inputs(postal, dept, town, prop_type, area, rooms, land)
    if error_msg:
        return error_msg

    property_type_code: int = 1 if prop_type.lower() == "house" else 2

    input_data: dict[str, float | int] = {
        "building_area": float(area),
        "main_rooms": int(rooms),
        "land_area": float(land),
        "postal_code": int(postal),
        "property_type_code": property_type_code,
        "town_code": int(town),
        "department_code": int(dept),
    }

    model_path: str = "fpi/models/linear_model.pkl"
    try:
        predicted_price: float = predict_price(model_path=model_path, input_data=input_data)
        return f"Estimated property price: €{predicted_price:,.0f}"
    except Exception as e:
        error_str: str = str(e)
        return f"Prediction failed: {error_str}"



# ==============================================================================
# PREDICTION PAGE LAYOUT
# ==============================================================================


def prediction_page() -> (
    Tuple[gr.components.Button, gr.components.Button, gr.components.Markdown, List[gr.components.Component]]
):
    """
    Creates and returns the layout for the Prediction Page

    Returns:
        tuple: A tuple containing:
            - predict_btn (gr.Button): Button to trigger the estimation.
            - reset_btn (gr.Button): Button to clear the form.
            - result_output (gr.Markdown): Component to display the result/error.
            - inputs_list (list[gr.Component]): Ordered list of all input fields.
    """

    with gr.Column():
        gr.Markdown("## Estimate the property value", elem_classes="page-title")
        gr.Markdown("Enter the characteristics of the property to get an estimated price.")

        with gr.Column(elem_classes="glass-box"):
            # --- FORM ---
            inputs_list: List[gr.components.Component]
            prop_type_input: gr.components.Component
            inputs_list, prop_type_input = form()

            # --- BUTTONS ---
            with gr.Row():
                predict_btn: gr.components.Button = gr.Button("Estimate", variant="primary")
                reset_btn: gr.components.Button = gr.Button("Reset")

            # --- RESULT ---
            result_output: gr.components.Markdown = gr.Markdown(
                value="Estimation : **--- €**", label="Price estimated", elem_classes="prediction-result"
            )

    # --- LINK CALLBACKS ---
    predict_btn.click(
        fn=run_prediction,
        inputs=inputs_list,
        outputs=result_output,
    )

    reset_btn.click(
        fn=reset_form,
        inputs=[],
        outputs=inputs_list + [result_output],
    )

    return predict_btn, reset_btn, result_output, inputs_list
