import gradio as gr

from fpi.interface.prediction.form import get_form, reset_form, validate_inputs
from fpi.models.predict import predict_price


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

    # house or apartment
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

    model_path: str = "fpi/models/random_forest.joblib"

    try:
        predicted_price: float = predict_price(model_path=model_path, input_data=input_data)
        return f"Estimated property price: €{predicted_price:,.0f}"
    except Exception as e:
        error_str: str = str(e)
        return f"Prediction failed: {error_str}"


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
        gr.Markdown("Enter the characteristics of the property to get an estimated price.")

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
