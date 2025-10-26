# src/analysis/app.py
from __future__ import annotations
import gradio as gr
from typing import Dict, Any

from src.analysis.predict import predict_from_inputs

# Helper to build default empty inputs (you can adapt choices)
DEFAULTS = {
    "Type_de_voie": "Rue",
    "Code_departement": "75",
    "Code_commune": "75056",
    "Code_type_local": "1",  # adapt to your meaning
    "Nombre_de_lots": 1,
    "Surface_reelle_bati": 50,
    "Nombre_pieces_principales": 2,
    "Surface_terrain": 0,
}


def predict_ui(
    type_de_voie: str,
    code_departement: str,
    code_commune: str,
    code_type_local: str,
    nombre_de_lots: float,
    surface_reelle_bati: float,
    nombre_pieces_principales: float,
    surface_terrain: float,
) -> str:
    inputs: Dict[str, Any] = {
        "Type_de_voie": type_de_voie,
        "Code_departement": str(code_departement),
        "Code_commune": str(code_commune),
        "Code_type_local": str(code_type_local),
        "Nombre_de_lots": nombre_de_lots,
        "Surface_reelle_bati": surface_reelle_bati,
        "Nombre_pieces_principales": nombre_pieces_principales,
        "Surface_terrain": surface_terrain,
    }
    try:
        pred = predict_from_inputs(inputs)
        return f"Predicted land value: €{pred:,.2f}"
    except Exception as e:
        return f"Error during prediction: {e}"


def launch_gradio():
    with gr.Blocks() as demo:
        gr.Markdown("## Real estate price predictor — land value (DVF-style)")
        with gr.Row():
            with gr.Column():
                type_de_voie = gr.Textbox(label="Type de voie (e.g. Rue, Avenue)", value=DEFAULTS["Type_de_voie"])
                code_departement = gr.Textbox(label="Code département", value=DEFAULTS["Code_departement"])
                code_commune = gr.Textbox(label="Code commune (INSEE)", value=DEFAULTS["Code_commune"])
                code_type_local = gr.Textbox(label="Code type local", value=DEFAULTS["Code_type_local"])
            with gr.Column():
                nombre_de_lots = gr.Number(label="Nombre de lots", value=DEFAULTS["Nombre_de_lots"])
                surface_reelle_bati = gr.Number(label="Surface réelle bâtie (m²)", value=DEFAULTS["Surface_reelle_bati"])
                nombre_pieces_principales = gr.Number(label="Nombre de pièces principales", value=DEFAULTS["Nombre_pieces_principales"])
                surface_terrain = gr.Number(label="Surface terrain (m²)", value=DEFAULTS["Surface_terrain"])
        predict_btn = gr.Button("Predict")
        output = gr.Textbox(label="Prediction result")

        predict_btn.click(
            fn=predict_ui,
            inputs=[
                type_de_voie,
                code_departement,
                code_commune,
                code_type_local,
                nombre_de_lots,
                surface_reelle_bati,
                nombre_pieces_principales,
                surface_terrain,
            ],
            outputs=output,
        )

    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    launch_gradio()
