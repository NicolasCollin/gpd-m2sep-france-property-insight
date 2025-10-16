import gradio as gr

def dashboard_page():
    with gr.Blocks(css="""
        body {background-color: #eaf4ff;}
        h1 {color: #003f7f;}
    """) as dashboard:
        gr.Markdown("# Tableau de bord")
        gr.Markdown("Visualisez les tendances des valeurs foncières et explorez les données des propriétés françaises.")
        back_home = gr.Button(" Retour à l'accueil")
        return dashboard, back_home
