from typing import Tuple

import gradio as gr  # Import Gradio for building the interface


# --- Dashboard Page Layout ---
def dashboard_page() -> Tuple[gr.Blocks, gr.Button]:
    """
    Create and return the layout for the Dashboard Page.

    The Dashboard Page includes:
    - A title and short description of its purpose
    - A navigation button to return to the home page

    Returns:
        tuple: A tuple containing:
            - dashboard_page (gr.Blocks): The Gradio layout object representing the dashboard
            - return_home_button (gr.Button): The navigation button to go back to the home page
    """
    # Define the overall structure and style of the dashboard page
    with gr.Blocks(
        css="""
        body {background-color: #eaf4ff;}
        h1 {color: #003f7f;}
    """
    ) as dashboard:
        # Section: Title and Description
        gr.Markdown("# Tableau de bord")
        gr.Markdown("Visualisez les tendances des valeurs foncières et explorez les données des propriétés françaises.")

        # Section: Navigation Button
        back_home = gr.Button("Retour à l'accueil")

        # Return the layout and navigation control
        return dashboard, back_home
