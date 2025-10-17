import gradio as gr  # Import Gradio for building the interface


# --- Prediction Page Layout ---
def prediction_page():
    """
    Create and return the layout for the Prediction Page.

    The Prediction Page includes:
    - A title and short description introducing the estimation tool
    - A navigation button to return to the home page

    Returns:
        tuple: A tuple containing:
            - gr.Blocks: The Gradio layout object representing the page
            - gr.Button: The navigation button to go back to the home page
    """
    # Define the overall layout and style for the prediction page
    with gr.Blocks(
        css="""
        body {background-color: #f0f9f9;}
        h1 {color: #006b6b;}
    """
    ) as prediction:
        # Section: Title and Description
        gr.Markdown("# Estimation de propriété")
        gr.Markdown("Estimez la valeur actuelle ou future d’un bien immobilier à partir de ses caractéristiques.")

        # Section: Navigation Button
        back_home = gr.Button("Retour à l'accueil")

        # Return the full layout and navigation control
        return prediction, back_home
