import gradio as gr
import requests

from fpi.interface.prediction.form import get_form, reset_form, validate_inputs


def run_prediction(postal, prop_type, area, rooms, land) -> str:
    """
    Call backs for the "Estimate" button. It prepares the data and calls the model prediction function.

    Notes: Actually calls a FastAPI route which calls the backend function.

    Args:
        postal: Postal code (string).
        prop_type: Property type ("House" / "Apartment").
        area: Living area in square
        rooms: Number of rooms (integer).
        land: Land area (float).

    Returns:
        A string with the predicted price or an error message.
    """
    error_msg = validate_inputs(postal, prop_type, area, rooms, land)
    if error_msg:
        return error_msg

    data = {
        "postal": str(postal),
        "prop_type": str(prop_type),
        "area": float(area),
        "rooms": int(rooms),
        "land": float(land),
    }

    try:
        response = requests.post("http://localhost:7860/api/predict", json=data)
        response.raise_for_status()
        price = response.json()["predicted_price"]
        return f"Estimated property price: €{price:,.0f}"
    except Exception as e:
        return f"Prediction failed: {e}"


def get_prediction_page() -> tuple[gr.components.Button, gr.components.Button, gr.components.Markdown, list[gr.components.FormComponent]]:
    """
    Get the layout for the Prediction Page

    Returns:
        tuple:
            - predict_btn (gr.Button): Button to trigger the estimation.
            - reset_btn (gr.Button): Button to clear the form.
            - result_output (gr.Markdown): Component to display the result/error.
            - inputs_list (list(gr.Component)): Ordered list of all input fields.
    """

    with gr.Column():
        gr.Markdown("## Estimate the property value", elem_classes="page-title")
        gr.Markdown("Enter the characteristics of the property to get an estimated price.", elem_classes="page-subtitle")

        with gr.Column(elem_classes="glass-box"):
            # form inputs
            inputs_list: list[gr.components.FormComponent]
            prop_type_input: gr.components.Component
            inputs_list, prop_type_input = get_form()

            # buttons predict and reset
            with gr.Row():
                predict_btn: gr.components.Button = gr.Button("Estimate", variant="primary")
                reset_btn: gr.components.Button = gr.Button("Reset")

            # result
            result_output: gr.components.Markdown = gr.Markdown(
                value="Estimation : **--- €**", label="Price estimated", elem_classes="prediction-result"
            )

    # link callbacks
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
