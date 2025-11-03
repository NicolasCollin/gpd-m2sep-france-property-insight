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
    
    gr.Markdown("# Tableau de bord", elem_classes="page-title")
    gr.Markdown("Visualisez les tendances des valeurs foncières et explorez les données des propriétés françaises.")
    gr.Markdown("*(Le contenu du dashboard, comme les graphiques Plotly ou Matplotlib, ira ici...)*")
    