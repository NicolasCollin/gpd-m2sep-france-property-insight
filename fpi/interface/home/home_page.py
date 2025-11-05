from typing import Tuple

import gradio as gr  # Import Gradio for building the interface


# --- Home Page Layout ---
def home_page() -> Tuple[gr.Button, gr.Button]:
    """
    Create and return the layout for the Home Page.

    The Home Page includes:
    - A title and short description of the application
    - Two navigation buttons: one for accessing the Dashboard, another for the Prediction module

    Returns:
        tuple: A tuple containing:
            - home_page (gr.HTML): The Gradio layout object representing the page
            - dashboard_button (gr.Button): The Dashboard navigation button
            - prediction_button (gr.Button): The Prediction navigation button
    """

    with gr.Row(elem_id="home-cards-container"):
        # Ces boutons sont stylisés par le CSS dans menu.py
        card_dashboard = gr.Button("Dashboard", elem_id="card-dashboard", elem_classes="home-card")
        card_estimate = gr.Button("Estimate your property", elem_id="card-prediction", elem_classes="home-card")

    return card_dashboard, card_estimate
