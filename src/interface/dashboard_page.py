import gradio as gr  # Import Gradio

def dashboard_page():  # Define dashboard page
    with gr.Blocks(  # Main layout for dashboard
        css="""
        body {background-color: #eaf4ff;}
        h1 {color: #003f7f;}
    """
    ) as dashboard:
        gr.Markdown("# Tableau de bord")  # Page title
        gr.Markdown("Visualisez les tendances des valeurs foncières et explorez les données des propriétés françaises.")  # Description text
        back_home = gr.Button(" Retour à l'accueil")  # Button to go back home
        return dashboard, back_home  # Return layout and button
