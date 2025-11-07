from collections.abc import Callable
from typing import Any

import gradio as gr

from fpi.interface.dashboard.dashboard_page import get_dashboard_page
from fpi.interface.home.home_page import get_home_page
from fpi.interface.prediction.prediction_page import get_prediction_page

# Correct type for Gradio update function
update_fn: Callable = gr.update

global_css = """
/* --- Global --- */


.gradio-container {
    background: radial-gradient(#004f99 5%, #ffffff 100%); !important;
    max-width: 100% !important; /* Full width */
    padding: 0 !important;
    position: relative;
    min-height: 100vh;
}


/* --- HEADER --- */

#navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    border-radius: 15px;
    gap: 0 !important;
    margin: 0 !important;
    width: 100%;
}


#logo {
    font-size: 1.8rem;
    font-weight: bold;
    color: #004f99;
}


#nav-links {
    display: flex;
    gap: 1.5rem;
}


/* Buttons*/
#nav-links .gradio-button {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    color: #555 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.5rem !important;
    min-width: auto !important;
}
#nav-links .gradio-button:hover {
    color: #007bff !important;
    background: #f0f0f0 !important;
}


/* --- PAGE CONTENT --- */

.page-content {
    background: none;
    max-width: 1280px;
    margin: 0 auto !important;
    padding: 2rem !important;
}
h2.page-title {
    font-size: 2.5rem;
    color: #333;
    margin-bottom: 0.5rem;
}


/* --- OPTION CARDS --- */

/* Electric glitch animation */
@keyframes neon-glitch {
    0%   { box-shadow: 0 0 5px #fff, 0 0 10px #007bff; border-color: #007bff; }
    25%  { box-shadow: 0 0 8px #fff, 0 0 15px #004f99; border-color: #004f99; }
    50%  { box-shadow: 0 0 10px #fff, 0 0 20px #007bff; border-color: #007bff; }
    75%  { box-shadow: 0 0 8px #fff, 0 0 15px #004f99; border-color: #004f99; }
    100% { box-shadow: 0 0 5px #fff, 0 0 10px #007bff; border-color: #007bff; }
}

/* Glassmorphism */
.home-card {
    min-height: 350px !important;
    width: 100% !important;
    border-radius: 15px !important;
    transition: all 0.3s ease !important;

    /* Base Glassmorphism */
    background: rgba(255, 255, 255, 0.2) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* Text */
    color: #ffffff !important;
    font-size: 2.2rem !important;
    font-weight: bold !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;

    display: flex !important;
    justify-content: center !important;
    align-items: center !important;

    /* Effect */
    box-shadow: 0 0 5px #fff, 0 0 10px #007bff;

}

/* Touch effect */
.home-card:hover {
    transform: translateY(-3px) !important; /* movement */

   /* Activate animation */
    animation: neon-glitch 0.8s infinite alternate !important;
    cursor: pointer !important;
}

#card-dashboard, #card-prediction {
    background: rgba(255, 255, 255, 0.2) !important;
}

/* ---PREDICTION PAGE --- */
.glass-box {
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.8);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    padding: 30px;
    margin-top: 1rem;
}
.glass-box label {
    color: #003366 !important;
    font-weight: 600 !important;
}
"""


def show_page(page_id: str) -> list[Any]:
    """
    Updates the visibility of the main content columns to show only the selected page.
    """
    is_home = page_id == "home"
    is_dashboard = page_id == "dashboard"
    is_prediction = page_id == "prediction"

    return [
        gr.update(visible=is_home),
        gr.update(visible=is_dashboard),
        gr.update(visible=is_prediction),
    ]


def app_menu() -> gr.Blocks:
    """
    Create and return the main menu interface for the application.

    This function defines the global layout of the app, organizing three main pages:
    - Home page: introduces the platform and provides navigation buttons and menu.
    - Dashboard page: displays property data visualizations.
    - Prediction page: allows users to estimate property values.

    The function also handles navigation between these sections using Gradio event triggers.

    Returns:
        menu (gr.Blocks): The complete Gradio layout for the app, including navigation logic.
    """

    with gr.Blocks(css=global_css, title="France Property Insight", fill_width=True) as menu:
        # Header / Navbar (applied for all pages)
        with gr.Row(elem_id="navbar"):
            gr.HTML('<div id="logo">FRANCE PROPERTY INSIGHT</div>')
            with gr.Row(elem_id="nav-links"):
                nav_home: gr.Button = gr.Button("Home")
                nav_dashboard: gr.Button = gr.Button("Dashboard")
                nav_estimate: gr.Button = gr.Button("Estimate your property")

        # Home page
        with gr.Column(visible=True, elem_classes="page-content") as home:
            gr.Markdown("## Bienvenue sur FPI Platform", elem_classes="page-title")
            gr.Markdown("Explorez, analysez et prédisez les valeurs immobilières grâce à nos outils interactifs.")
            card_dashboard: gr.Button
            card_estimate: gr.Button
            card_dashboard, card_estimate = get_home_page()

        # Dashboard page
        with gr.Column(visible=False, elem_classes="page-content") as dashboard:
            get_dashboard_page()

        # Prediction page
        with gr.Column(visible=False, elem_classes="page-content") as prediction:
            predict_btn: gr.Button
            reset_btn: gr.Button
            result_output: gr.Markdown
            inputs_list: list[Any]
            predict_btn, reset_btn, result_output, inputs_list = get_prediction_page()

        # Navigation logic
        all_pages: list[gr.Component] = [home, dashboard, prediction]

        # Navigation button clicks
        nav_home.click(fn=show_page, inputs=gr.State("home"), outputs=all_pages)
        nav_dashboard.click(fn=show_page, inputs=gr.State("dashboard"), outputs=all_pages)
        nav_estimate.click(fn=show_page, inputs=gr.State("prediction"), outputs=all_pages)

        # Card clicks on Home page
        card_dashboard.click(fn=show_page, inputs=gr.State("dashboard"), outputs=all_pages)
        card_estimate.click(fn=show_page, inputs=gr.State("prediction"), outputs=all_pages)

    return menu
