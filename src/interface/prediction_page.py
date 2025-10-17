import gradio as gr  # Import Gradio library


def prediction_page():  # Define prediction page
    with gr.Blocks(  # Create a Gradio block layout
        css="""
        body {background-color: #f0f9f9;}
        h1 {color: #006b6b;}
    """
    ) as prediction:  # Assign layout to variable
        gr.Markdown("# Estimation de propriété")  # Page title
        gr.Markdown("Estimez la valeur actuelle ou future d’un bien immobilier à partir de ses caractéristiques.")  # Description text
        back_home = gr.Button("Retour à l'accueil")  # Button to go back home
        return prediction, back_home  # Return layout and button
