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
    background: #ffffff !important;
    max-width: 100% !important;
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
    background: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-bottom: 1px solid #e0e0e0;
    width: 100%;
    margin: 0 !important;
}

#logo-image {
    height: 40px;
    margin-right: 10px;
    border: none;
    box-shadow: none;
}

#logo-title {
    font-size: 20px;
    font-weight: bold;
    color: #0170bc;
}

/* Navigation links */
#nav-links {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-left: auto;
    align-items: center;
    flex-wrap: nowrap;
}

/* ---- NAVBAR BUTTONS ---- */
#nav-links button {
    padding: 12px 25px !important;
    font-size: 14px !important;
    color: #000 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 500 !important;
    background: transparent !important;
    border: 2px solid var(--text-accent) !important;
    border-radius: 80px !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
    cursor: pointer;
    outline: none;
}


#nav-links button:hover {
    background: linear-gradient(292deg, rgba(2, 0, 36, 1) 0%, rgba(9, 9, 121, 1) 35%, rgba(0, 212, 255, 1) 100%) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: 0px 8px 20px rgba(0, 212, 255, 0.3) !important;
    transform: translateY(-3px) !important;
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

/* ============ HOME PAGE STYLES ============ */
#home-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Hero Section */
#hero-section {
    background: #020024;
    background: linear-gradient(292deg,rgba(2, 0, 36, 1) 0%, rgba(9, 9, 121, 1) 35%, rgba(0, 212, 255, 1) 100%);
    border-radius: 20px;
    padding: 4rem 2rem;
    margin: 2rem 0;
    color: white;
    text-align: center;
}


/* Hero text animation */
.hero-text-container {
    text-align: center;
    margin-bottom: 3rem;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    font-family: 'Inter', system-ui, sans-serif;
    margin-bottom: 1rem;
    color: #ffffff;
    line-height: 1.1;
}

.text-fixed {
    color: #ffffff;
    font-weight: 800;
}

.hero-subtitle {
    font-size: 1.8rem;
    font-weight: 500;
    font-family: 'Inter', system-ui, sans-serif;
    color: #7f8c8d;
    margin-bottom: 1rem;
    text-align: center;
    height: 2.5rem;
    position: relative;
}

.text-rotating {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 2.5rem;
    text-align: center;
}

.text-rotating .word {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: rotateWords 12s infinite;
    white-space: nowrap;
}

/* Animation timing */
.text-rotating .word:nth-child(2) { animation-delay: 2s; }
.text-rotating .word:nth-child(3) { animation-delay: 4s; }
.text-rotating .word:nth-child(4) { animation-delay: 6s; }
.text-rotating .word:nth-child(5) { animation-delay: 8s; }
.text-rotating .word:nth-child(6) { animation-delay: 10s; }

@keyframes rotateWords {
    0%, 12% {
        opacity: 0;
        transform: translateX(-50%) translateY(20px);
    }
    2%, 10% {
        opacity: 1;
        transform: translateX(-50%) translateY(0px);
    }
    15%, 100% {
        opacity: 0;
        transform: translateX(-50%) translateY(-20px);
    }
}


.hero-stats {
    display: flex;
    justify-content: center;
    gap: 4rem;
    margin-top: 2rem;
}

.stat-item {
    text-align: center;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 1rem;
    opacity: 0.8;
    font-weight: 300;
}

/* ----- Search section ----- */
#search-section {
    background: white;
    border-radius: 15px;
    padding: 3rem 2rem;
    margin: 2rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    border: 1px solid #e0e0e0;
}

#search-container {
    width: 100%;
    text-align: center;
}

.search-title {
    font-size: 2rem;
    color: #2c3e50;
    margin-bottom: 2rem;
    font-weight: 600;
}

#search-input-row {
    justify-content: center;
    align-items: stretch;
    gap: 1rem;
}

#department-search {
    min-width: 400px;
}

#department-search .gr-dropdown {
    border-radius: 12px !important;
    border: 2px solid #e8e8e8 !important;
    padding: 1rem 1.5rem !important;
    font-size: 1.1rem !important;
    height: auto !important;
    background: #f8f9fa !important;
}

#department-search .gr-dropdown:focus {
    border-color: #667eea !important;
    background: white !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

#search-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 1rem 2rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    height: auto !important;
    transition: all 0.3s ease !important;
}

#search-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
}

/* Features section */
#features-section {
    margin: 4rem 0;
    text-align: center;
    items-align: center;
    justify-content: center;
    font-family: 'Inter', system-ui, sans-serif;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    width: 100%;
}

/* Feature cards */
.feature-card {
    background: white;
    padding: 2.5rem 2rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    border: 1px solid #f0f0f0;
    transition: all 0.3s ease;
    cursor: pointer;
    height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin: 0.5rem;
    font-family: 'Inter', system-ui, sans-serif;
    color: #2c3e50;
    white-space: pre-line;
    line-height: 1.8;
    font-size: 1rem;
    font-weight: 400;
}

.feature-card:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 15px 40px rgba(0,0,0,0.15) !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
}

/* Title and icon */
.feature-card::first-line {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    margin-bottom: 1rem !important;
    line-height: 1.2 !important;
    /* Forcer l'affichage */
    display: block !important;
}

/* Responsive design */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }

    .hero-stats {
        gap: 2rem;
        flex-direction: column;
    }

    #department-search {
        min-width: 200px;
    }

    .features-grid {
        grid-template-columns: 1fr;
    }
}

@media (prefers-color-scheme: light) {
  h {
    color: black !important;
    background-color: white !important;
  }
}

@media (prefers-color-scheme: dark) {
  h2, page-title {
    color: black !important;
    background-color: white !important;
  }
}
"""


def show_page(page_id: str) -> list[Any]:
    """
    Updates the visibility of the main content columns to show only the selected page.

    Args:
        page_id (str): A string identifier for the page to show ("home", "dashboard", or "prediction").

    Returns:
        A list of gr.update objects controlling the visibility for each of the
        three main pages in order: [home, dashboard, prediction].
        page_id: A string identifier for the page to show ("home", "dashboard", or "prediction").

    Returns:
        List[Any]: A list of Gradio update objects to set visibility for each page.

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
        # Header / Navbar
        with gr.Row(elem_id="navbar"):
            # Logo + title on the left
            with gr.Column(scale=1, min_width=200):
                gr.HTML("""
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <img src="/file=docs/fpi-logo.png" alt="Logo" style="height: 40px;">
                        <div style="font-size: 20px; font-weight: bold; color: #0170bc;">France Property Insight</div>
                    </div>
                """)

            # Navigation links on the right
            with gr.Column(scale=2):
                with gr.Row(elem_id="nav-links"):
                    nav_home: gr.components.Button = gr.Button("Home", elem_id="nav-home")
                    nav_dashboard: gr.components.Button = gr.Button("Dashboard", elem_id="nav-dashboard")
                    nav_estimate: gr.components.Button = gr.Button("Estimation", elem_id="nav-estimate")
                    nav_api_docs: gr.components.Button = gr.Button("API Docs", elem_id="nav-api-docs")
                    nav_gitlab: gr.components.Button = gr.Button("GitLab", elem_id="nav-gitlab")

        # ---------------------------- Home page -----------------------------
        with gr.Column(visible=True, elem_classes="page-content") as home:
            # Appeler la nouvelle homepage qui retourne department_dropdown et search_button
            department_dropdown, search_button, dashboard_card, estimation_card, about_card = get_home_page()

        # ---------------------------- Dashboard page -----------------------------
        with gr.Column(visible=False, elem_classes="page-content") as dashboard:
            get_dashboard_page()

        # --------------------------- Prediction page ---------------------------
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

        # Navigation for API Docs and GitLab
        nav_api_docs.click(lambda: gr.HTML("<script>window.open('https://france-property-insight-docs.onrender.com/fpi.html', '_blank')</script>"))
        nav_gitlab.click(
            lambda: gr.HTML("<script>window.open('https://gitlab-mi.univ-reims.fr/phan0005/gpd-m2sep-france-property-insight', '_blank')</script>")
        )

        # Navigation depuis les cartes
        dashboard_card.click(fn=show_page, inputs=gr.State("dashboard"), outputs=all_pages)
        estimation_card.click(fn=show_page, inputs=gr.State("prediction"), outputs=all_pages)
        about_card.click(fn=lambda: gr.Info("Page À propos - En développement"), inputs=None, outputs=None)

        def navigate_to_dashboard(department):
            if department:
                # Ici vous pouvez traiter le département sélectionné
                print(f"Navigation vers dashboard avec: {department}")
                return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

        # Connecter la recherche au dashboard
        search_button.click(fn=navigate_to_dashboard, inputs=department_dropdown, outputs=all_pages)

    return menu
