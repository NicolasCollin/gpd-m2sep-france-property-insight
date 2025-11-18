import gradio as gr

from fpi.analysis.market_analysis import calculate_financing_simulation
from fpi.data_pipeline.loader import load_all_csv
from fpi.interface.prediction.form import get_form, reset_form, validate_inputs
from fpi.models.predict import predict_price

df = load_all_csv()
PROPERTY_TYPE_MAP = {"Maison": 1, "Apartement": 2, "Dépendance": 3, "Local industriel. commercial ou assimilé": 4}


def run_prediction(postal: str, prop_type: str, area: float, rooms: int, land: float) -> str:
    """
    Call backs for the "Estimate" button. It prepares the data and calls the model prediction function.
    Args:
        postal: Postal code (string).
        prop_type: Property type ("House" / "Apartment").
        area: Living area in square
        rooms: Number of rooms (integer).
        land: Land area (float).
    Returns:
        A string with the predicted price or an error message.
    """

    error_msg: str = validate_inputs(postal, prop_type, area, rooms, land)
    if error_msg:
        return error_msg

    postal_code = int(postal.split(" - ")[0])
    filtered_df = df[(df["postal_code"] == postal_code) & (df["property_type"].str.lower() == prop_type.lower())]

    if filtered_df.empty:
        return "No data available for this postal code and property type."

    property_type_code = PROPERTY_TYPE_MAP.get(prop_type, 0)

    input_data: dict[str, float | int] = {
        "building_area": float(area),
        "main_rooms": int(rooms),
        "land_area": float(land),
        "postal_code": int(postal_code),
        "property_type_code": property_type_code,
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
        gr.Markdown("Enter the characteristics of the property to get an estimated price.", elem_classes="page-subtitle")

        with gr.Column(elem_classes="glass-box"):
            inputs_list: list[gr.components.FormComponent]
            postal_input: gr.components.Component
            prop_type_input: gr.components.Component
            inputs_list, postal_input, prop_type_input = get_form()

            with gr.Row():
                predict_btn: gr.components.Button = gr.Button("Estimate", variant="primary")
                reset_btn: gr.components.Button = gr.Button("Reset")

            result_output: gr.components.Markdown = gr.Markdown(
                value="Estimation : **--- €**", label="Price estimated", elem_classes="prediction-result"
            )

    gr.Markdown("## Financing simulation")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Loan parameters")
            property_price = gr.Number(label="Property price (€)", interactive=True, value=200000, minimum=0)
            personal_contribution = gr.Number(label="Personal contribution (€)", interactive=True, value=40000, minimum=0)
            loan_duration = gr.Slider(label="Loan duration (years)", minimum=5, maximum=30, value=20, step=1)
            interest_rate = gr.Slider(label="Interest rate (%)", minimum=1.0, maximum=6.0, value=3.5, step=0.1)
            simulate_button = gr.Button("Calculate", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Simulation results")
            monthly_payment = gr.Number(label="Monthly payment (€)", interactive=False)
            total_loan_cost = gr.Number(label="Total loan cost (€)", interactive=False)
            debt_ratio = gr.Number(label="Debt ratio (%)", interactive=False)

    def run_financing_simulation(price, contribution, duration, rate):
        return calculate_financing_simulation(price, contribution, duration, rate)

    simulate_button.click(
        fn=run_financing_simulation,
        inputs=[property_price, personal_contribution, loan_duration, interest_rate],
        outputs=[monthly_payment, total_loan_cost, debt_ratio],
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
