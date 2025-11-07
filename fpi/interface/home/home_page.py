import gradio as gr  # Import Gradio for building the interface


def home_page() -> tuple[gr.Button, gr.Button]:
    """
    Create and return the layout for the Home Page.

    The Home Page includes:
    - A title and short description of the application
    - Two navigation buttons: one for accessing the Dashboard, another for the Prediction module

    Returns:
        tuple:
            - dashboard_button (gr.Button): The Dashboard navigation button
            - prediction_button (gr.Button): The Prediction navigation button
    """

    with gr.Row(elem_id="home-cards-container"):
        card_dashboard: gr.Button = gr.Button("Dashboard", elem_id="card-dashboard", elem_classes="home-card")
        card_estimate: gr.Button = gr.Button(
            "Estimate your property", elem_id="card-prediction", elem_classes="home-card"
        )

    return card_dashboard, card_estimate
