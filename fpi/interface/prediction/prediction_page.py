import gradio as gr
import requests

from fpi.analysis.market_analysis import calculate_financing_simulation
from fpi.data_pipeline.loader import load_all_csv
from fpi.interface.prediction.form import get_form, reset_form, validate_inputs

df = load_all_csv()


def run_prediction(postal: str, prop_type: str, area: float, rooms: int, land: float) -> str:
    """
    Call the FastAPI backend to compute a property price prediction.

    Args:
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

    postal = str(postal.split(" - ")[0])
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

        with gr.Column():
            inputs_list: list[gr.components.FormComponent]
            postal_input: gr.components.Component
            prop_type_input: gr.components.Component
            inputs_list, postal_input, prop_type_input = get_form()

            with gr.Row():
                predict_btn: gr.components.Button = gr.Button("Estimate", variant="primary")
                reset_btn: gr.components.Button = gr.Button("Reset")

            result_output: gr.components.Markdown = gr.Markdown(
                value="Estimation : **--- €**",
                label="Price estimated",
                elem_classes="prediction-result",
            )

    gr.Markdown("## Financing simulation")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Loan parameters")
            property_price: gr.Number = gr.Number(label="Property price (€)", interactive=True, minimum=0)
            personal_contribution: gr.Number = gr.Number(label="Personal contribution (€)", interactive=True, minimum=0)
            income: gr.Number = gr.Number(label="Income per month (€)", interactive=True, minimum=0)
            loan_duration: gr.Slider = gr.Slider(label="Loan duration (years)", minimum=5, maximum=30, value=20, step=1)
            interest_rate: gr.Slider = gr.Slider(label="Interest rate (%)", minimum=1.0, maximum=6.0, value=3.5, step=0.1)
            simulate_button: gr.Button = gr.Button("Calculate", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Simulation results")
            monthly_payment: gr.Number = gr.Number(label="Monthly payment (€)", interactive=False)
            total_loan_cost: gr.Number = gr.Number(label="Total loan cost (€)", interactive=False)
            debt_ratio: gr.Number = gr.Number(label="Debt ratio (%)", interactive=False)

    def run_financing_simulation(
        price: float, contribution: float, income: float, loan_duration: int, interest_rate: float
    ) -> tuple[float, float, float]:
        """
        Runs calculate_financing_simulation and extract its results.

        Args:
            property_price (float): Total property cost in euros.
            personal_contribution (float): Amount contributed upfront.
            loan_duration (int): Duration of the loan in years.
            interest_rate (float): Annual interest rate (%).

        Returns:
            tuple containing:
                monthly payment, total cost, debt ratio
        """
        return calculate_financing_simulation(price, contribution, income, loan_duration, interest_rate)

    simulate_button.click(
        fn=run_financing_simulation,
        inputs=[property_price, personal_contribution, income, loan_duration, interest_rate],
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
