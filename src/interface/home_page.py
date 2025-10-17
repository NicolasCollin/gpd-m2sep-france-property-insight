import gradio as gr  # Import Gradio for building the interface


# --- Home Page Layout ---
def home_page():
    """
    Create and return the layout for the Home Page.

    The Home Page includes:
    - A title and short description of the application
    - Two navigation buttons: one for accessing the Dashboard, another for the Prediction module

    Returns:
        tuple: A tuple containing:
            - gr.Blocks: The Gradio layout object representing the page
            - gr.Button: The Dashboard navigation button
            - gr.Button: The Prediction navigation button
    """
    # Define the layout and style for the home page
    with gr.Blocks(
        css="""
        body {background-color: #f8fafc;}
        h1 {color: #005b9e;}
        .button-row {display: flex; gap: 10px; margin-top: 20px;}
    """
    ) as home:
        # Section: Title and Introduction
        gr.Markdown("# France Property Insight")
        gr.Markdown(
            "Bienvenue sur la plateforme d’analyse et de prévision immobilière en France. "
            "Explorez les données, visualisez les tendances et estimez la valeur des biens."
        )

        # Section: Navigation Buttons
        with gr.Row(elem_classes="button-row"):
            go_dashboard = gr.Button("Dashboard")
            go_prediction = gr.Button("Prediction")

        # Return the layout and interactive buttons
        return home, go_dashboard, go_prediction
