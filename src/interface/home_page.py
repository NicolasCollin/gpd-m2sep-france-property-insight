import gradio as gr


def home_page():
    with gr.Blocks(
        css="""
        body {background-color: #f8fafc;}
        h1 {color: #005b9e;}
        .button-row {display: flex; gap: 10px; margin-top: 20px;}
    """
    ) as home:
        gr.Markdown("# France Property Insight")
        gr.Markdown(
            "Bienvenue sur la plateforme d’analyse et de prévision immobilière en France. "
            "Explorez les données, visualisez les tendances et estimez la valeur des biens."
        )
        with gr.Row(elem_classes="button-row"):
            go_dashboard = gr.Button("Dashboard")
            go_prediction = gr.Button("Prediction")
        return home, go_dashboard, go_prediction
