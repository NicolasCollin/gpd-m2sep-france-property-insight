import gradio as gr  # Import Gradio

def home_page():  # Define home page
    with gr.Blocks(  # Main page layout
        css="""
        body {background-color: #f8fafc;}
        h1 {color: #005b9e;}
        .button-row {display: flex; gap: 10px; margin-top: 20px;}
    """
    ) as home:
        gr.Markdown("# France Property Insight")  # Page title
        gr.Markdown(  # Description section
            "Bienvenue sur la plateforme d’analyse et de prévision immobilière en France. "
            "Explorez les données, visualisez les tendances et estimez la valeur des biens."
        )
        with gr.Row(elem_classes="button-row"):  # Button row
            go_dashboard = gr.Button("Dashboard")  # Button for dashboard
            go_prediction = gr.Button("Prediction")  # Button for prediction
        return home, go_dashboard, go_prediction  # Return layout and buttons
