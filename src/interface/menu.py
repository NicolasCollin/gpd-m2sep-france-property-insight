import gradio as gr  # Import Gradio library for building the interface

from src.interface.dashboard_page import dashboard_page
from src.interface.home_page import home_page
from src.interface.prediction_page import prediction_page


# --- Application Menu Layout ---
def app_menu():
    """
    Create and return the main menu interface for the application.

    This function defines the global layout of the app, organizing three main pages:
    - Home Page: Introduces the platform and provides navigation buttons.
    - Dashboard Page: Displays property data visualizations.
    - Prediction Page: Allows users to estimate property values.

    The function also handles navigation between these sections using Gradio event triggers.

    Returns:
        gr.Blocks: The complete Gradio layout for the app, including navigation logic.
    """
    # Define the global structure of the app with multiple pages (Home, Dashboard, Prediction)
    with gr.Blocks() as menu:
        # --- Section: Home Page ---
        with gr.Column(visible=True) as home:
            home_ui, go_dashboard, go_prediction = home_page()

        # --- Section: Dashboard Page ---
        with gr.Column(visible=False) as dashboard:
            dashboard_ui, back_home_1 = dashboard_page()

        # --- Section: Prediction Page ---
        with gr.Column(visible=False) as prediction:
            prediction_ui, back_home_2 = prediction_page()

        # --- Navigation Logic ---
        # Controls visibility between Home, Dashboard, and Prediction sections
        go_dashboard.click(
            lambda: (
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=False),
            ),
            None,
            [home, dashboard, prediction],
        )

        go_prediction.click(
            lambda: (
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
            ),
            None,
            [home, dashboard, prediction],
        )

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

    # Return the complete app structure
    return menu
