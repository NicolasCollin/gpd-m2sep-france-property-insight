import gradio as gr

def prediction_page():
    with gr.Blocks(css="""
        body {background-color: #f0f9f9;}
        h1 {color: #006b6b;}
    """) as prediction:
        gr.Markdown("# Estimation de propriété")
        gr.Markdown("Estimez la valeur actuelle ou future d’un bien immobilier à partir de ses caractéristiques.")
        back_home = gr.Button("Retour à l'accueil")
        return prediction, back_home
