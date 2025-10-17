import gradio as gr

from src.interface.dashboard_page import dashboard_page
from src.interface.home_page import home_page
from src.interface.prediction_page import prediction_page


def app_menu():
    with gr.Blocks() as menu:
        with gr.Column(visible=True) as home:
            home_ui, go_dashboard, go_prediction = home_page()

        with gr.Column(visible=False) as dashboard:
            dashboard_ui, back_home_1 = dashboard_page()

        with gr.Column(visible=False) as prediction:
            prediction_ui, back_home_2 = prediction_page()

        # Dashboard
        go_dashboard.click(
            lambda: (
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=False),
            ),
            None,
            [home, dashboard, prediction],
        )

        # Prediction
        go_prediction.click(
            lambda: (
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
            ),
            None,
            [home, dashboard, prediction],
        )

        # Return
        for back_btn in [back_home_1, back_home_2]:
            back_btn.click(
                lambda: (
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=False),
                ),
                None,
                [home, dashboard, prediction],
            )

    return menu
