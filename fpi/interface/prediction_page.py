from typing import Tuple

import gradio as gr  # Import Gradio for building the interface


# --- Prediction Page Layout ---
def prediction_page() -> Tuple[gr.Blocks, gr.Button, gr.Button]:
    """
    Create and return the layout for the Prediction Page.

    The Prediction Page includes:
    - A title and short description introducing the estimation tool
    - A button to estimate property value based on user inputs
    - A navigation button to return to the home page

    Returns:
        tuple: A tuple containing:
            - prediction_page (gr.Blocks): The Gradio layout object representing the page
            - predict_btn (gr.Button): The button to trigger the property value estimation
            - return_home_button (gr.Button): The navigation button to go back to the home page
    """
    # Define the overall layout and style for the prediction page
    with gr.Blocks() as prediction:
        gr.Markdown("## Estimate your property")
        gr.Markdown("Please provide the property details to get an approximate valuation.")

        with gr.Row():
            with gr.Column(scale=1):
                postal_code = gr.Textbox(label="Postal code", placeholder="ex : 75015")
                department_code = gr.Textbox(label="Department code", placeholder="ex : 75")
                town_code = gr.Textbox(label="Town code", placeholder="ex : 123")
                property_type_code = gr.Dropdown(
                    ["House", "Apartment", "Dependency", "Industrial premises"],
                    label="Property type",
                    value="House"
                )
            with gr.Column(scale=1):
                building_area = gr.Number(label="Building area (m²)", precision=0)
                main_rooms = gr.Number(label="Main rooms", precision=0)
                land_area = gr.Number(label="Land area (m²)", precision=0)

        # --- Predict button ---
        predict_btn = gr.Button("Estimate", variant="primary")

        # --- Result ---
        result = gr.Textbox(label="Result", interactive=False)

        # --- predict button ---
        #predict_btn.click(
            #fn=predict_value,
            #inputs=[
                #postal_code, department_code, town_code, property_type_code,
                #building_area, main_rooms, land_area
            #],
            #outputs=result
        #)

        back_home = gr.Button("Back to home")


        return prediction, predict_btn, back_home
