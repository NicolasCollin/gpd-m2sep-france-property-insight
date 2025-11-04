from typing import List, Any
import gradio as gr
import os,sys
os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
from fpi.interface.prediction.form import form 


# ==============================================================================
# PREDICTION PAGE LAYOUT
# ==============================================================================

def prediction_page() -> tuple[gr.components.Button, gr.components.Button, gr.components.Markdown, list[gr.components.Component]]:
    """
    Creates and returns the layout for the Prediction Page

    Returns:
        tuple: A tuple containing:
            - predict_btn (gr.Button): Button to trigger the estimation.
            - reset_btn (gr.Button): Button to clear the form.
            - result_output (gr.Markdown): Component to display the result/error.
            - inputs_list (list[gr.Component]): Ordered list of all input fields.
    """
    
    with gr.Column():
        gr.Markdown("## Estimate the property value", elem_classes="page-title")
        gr.Markdown("Enter the characteristics of the property to get an estimated price.")
        
        with gr.Column(elem_classes="glass-box"):
            
            # --- FORM ---
            inputs_list: List[gr.components.Component] = form()
            
            # --- BUTTONS ---
            with gr.Row():
                predict_btn = gr.Button("Estimate", variant="primary")
                reset_btn = gr.Button("Reset")

            # --- RESULT ---
            result_output = gr.Markdown(
                value="Estimation : **--- €**", 
                label="Price estimated", 
                elem_classes="prediction-result"
            )

    return predict_btn, reset_btn, result_output, inputs_list