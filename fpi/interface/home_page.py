from typing import Tuple
import os

import gradio as gr  # Import Gradio for building the interface


# --- Home Page Layout ---
def home_page() -> Tuple[gr.HTML, gr.Button, gr.Button]:
    """
    Create and return the layout for the Home Page.

    The Home Page includes:
    - A title and short description of the application
    - Two navigation buttons: one for accessing the Dashboard, another for the Prediction module

    Returns:
        tuple: A tuple containing:
            - home_page (gr.HTML): The Gradio layout object representing the page
            - dashboard_button (gr.Button): The Dashboard navigation button
            - prediction_button (gr.Button): The Prediction navigation button
    """

    # Custom CSS for styling buttons and layout
    gr.HTML("""
    <style>

    .button-home-page {
        background-color: #c7e6ff !important;
        border-radius: 100px !important;
        box-shadow:
            rgba(3, 102, 214, .18) 0 -25px 18px -14px inset,
            rgba(3, 102, 214, .12) 0 1px 2px,
            rgba(3, 102, 214, .12) 0 2px 4px,
            rgba(3, 102, 214, .12) 0 4px 8px,
            rgba(3, 102, 214, .12) 0 8px 16px,
            rgba(3, 102, 214, .12) 0 16px 32px !important;
        color: #004f99 !important;              
        cursor: pointer;
        font-family: "Segoe UI", -apple-system, system-ui, Roboto, sans-serif;
        padding: 8px 20px !important;
        transition: all 250ms;
        border: 0 !important;
        font-size: 16px;
        user-select: none;
    }

    .button-home-page:hover {
        box-shadow:
            rgba(3,102,214,.32) 0 -25px 18px -14px inset,
            rgba(3,102,214,.22) 0 1px 2px,
            rgba(3,102,214,.22) 0 2px 4px,
            rgba(3,102,214,.22) 0 4px 8px,
            rgba(3,102,214,.22) 0 8px 16px,
            rgba(3,102,214,.22) 0 16px 32px !important;
        transform: scale(1.05) rotate(-1deg);
    }

    .home-wrapper { padding: 24px 36px; }
    .page-title {
      text-align: center;
      font-size: 3rem;
      color: #004f99;
      font-weight: bold;
      margin: 1rem 0;
    }
    .slogan-box {
      background: linear-gradient(0deg,#d28eb2 0%,#ffffff 100%);
      border-radius: 20px;
      padding: 16px 18px;
      font-size: 16px;
      text-align: center;
      font-weight: 700;
      color: #333;
      margin-bottom: 16px;
    }

    @media (max-width: 900px) {
      .home-wrapper { padding: 16px; }
      .page-title { font-size: 1.8rem; text-align: center; }
    }
    </style>
    """)

    # Wrapper HTML
    gr.HTML('<div class="home-wrapper">')

    # Title
    gr.HTML('<h1 class="page-title">FRANCE PROPERTY INSIGHT</h1>')

    # Slogan box
    gr.HTML('''
      <div class="slogan-box">
        Bienvenue sur FPI platform
        <br><br>
        Explorez, analysez et prédisez les valeurs immobilières grâce à nos outils interactifs basés sur la data.
      </div>
    ''')

    with gr.Row():
        go_dashboard = gr.Button("Dashboard", elem_classes="button-home-page")
        go_prediction = gr.Button("Estimate your property", elem_classes="button-home-page")

    # Close the divs
    gr.HTML('</div>')


        # Return the layout and interactive buttons
    return gr.HTML(''), go_dashboard, go_prediction
    

    


