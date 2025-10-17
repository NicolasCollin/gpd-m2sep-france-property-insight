import gradio as gr  # Import Gradio

from src.interface.dashboard_page import dashboard_page  # Import dashboard page
from src.interface.home_page import home_page  # Import home page
from src.interface.prediction_page import prediction_page  # Import prediction page


def app_menu():  # Define app menu
    with gr.Blocks() as menu:  # Main app layout
        with gr.Column(visible=True) as home:  # Home page section
            home_ui, go_dashboard, go_prediction = home_page()

        with gr.Column(visible=False) as dashboard:  # Dashboard section
            dashboard_ui, back_home_1 = dashboard_page()

        with gr.Column(visible=False) as prediction:  # Prediction section
            prediction_ui, back_home_2 = prediction_page()

        # --- Navigation logic ---
        go_dashboard.click(  # Switch to dashboard
            lambda: (
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=False),
            ),
            None,
            [home, dashboard, prediction],
        )

        go_prediction.click(  # Switch to prediction page
            lambda: (
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
            ),
            None,
            [home, dashboard, prediction],
        )

        for back_btn in [back_home_1, back_home_2]:  # Return to home
            back_btn.click(
                lambda: (
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                ),
                None,
                [home, dashboard, prediction],
            )

    return menu  # Return complete menu
