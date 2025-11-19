import gradio as gr
import requests

from fpi.interface.prediction.form import get_form, reset_form, validate_inputs


def run_prediction(postal: str, prop_type: str, area: float, rooms: int, land: float) -> str:
    """
    Call the FastAPI backend to compute a property price prediction.

    Parameters:
        postal (str): Postal code provided by the user.
        prop_type (str): Property type ("House", "Apartment", etc.).
        area (float): Living area in square meters.
        rooms (int): Number of main rooms.
        land (float): Land area in square meters.

    Returns:
        str: A formatted string containing the estimated price or an error message.
    """
    error_msg: str | None = validate_inputs(postal, prop_type, area, rooms, land)
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
        response: requests.Response = requests.post("http://localhost:7860/api/predict", json=data)
        response.raise_for_status()
        price: float = float(response.json()["predicted_price"])
        return f"Estimated property price: €{price:,.0f}"
    except Exception as e:
        return f"Prediction failed: {e}"


def get_prediction_page() -> (
    tuple[
        gr.components.Button,
        gr.components.Button,
        gr.components.Markdown,
        list[gr.components.FormComponent],
    ]
):
    """
    Build and return the complete layout for the prediction page.

    Returns:
        tuple:
            predict_btn (gr.Button): Button that triggers the prediction.
            reset_btn (gr.Button): Button that resets the form.
            result_output (gr.Markdown): Component where predictions or errors are displayed.
            inputs_list (list[gr.FormComponent]): Ordered list of all input UI components.
    """
    with gr.Column():
        gr.Markdown("## Estimate the property value", elem_classes="page-title")
        gr.Markdown(
            "Enter the characteristics of the property to get an estimated price.",
            elem_classes="page-subtitle",
        )

        with gr.Column(elem_classes="glass-box"):
            inputs_list: list[gr.components.FormComponent]
            prop_type_input: gr.components.Component
            inputs_list, prop_type_input = get_form()

            with gr.Row():
                predict_btn: gr.components.Button = gr.Button("Estimate", variant="primary")
                reset_btn: gr.components.Button = gr.Button("Reset")

            result_output: gr.components.Markdown = gr.Markdown(
                value="Estimation : **--- €**",
                label="Price estimated",
                elem_classes="prediction-result",
            )

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
