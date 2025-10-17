import gradio as gr  # Import Gradio for building the interface


# --- Dashboard Page Layout ---
def dashboard_page():
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
        back_home = gr.Button(" Retour à l'accueil")

        # Return the layout and navigation control
        return dashboard, back_home
