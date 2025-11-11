from collections.abc import Callable
from typing import Any

import gradio as gr

from fpi.interface.dashboard.dashboard_page import get_dashboard_page
from fpi.interface.home.home_page import get_home_page
from fpi.interface.prediction.prediction_page import get_prediction_page

update_fn: Callable = gr.update

global_css = """
/* --- Global --- */
.gradio-container {
    background: #ffffff !important;
    max-width: 100% !important;
    padding: 0 !important;
    position: relative;
    min-height: 100vh;
    color-scheme: light only !important;
}

=/* ----- Dark / Light mode adaptation ----- */

.page-title,
.page-subtitle,
.search-title,
.feature-title,
.prediction-result {
    color: inherit !important; 
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
    vertical-align: middle;
}

#logo-title {
    font-size: 20px;
    font-weight: bold;
    color: #0170bc;
    display: flex;
    align-items: center;  
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
#nav-links .nav-links-button {
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


#nav-links .nav-links-button:hover {
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

.page-title {
    font-size: 2.5rem;
    font-family: 'Inter', system-ui, sans-serif;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #000;
}

.page-subtitle {
    font-size: 1.25rem;
    font-family: 'Inter', system-ui, sans-serif;
    font-weight: 400; 
    margin-bottom: 1rem;
    color: #555; 
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
    background: linear-gradient(0deg, #ffe047 0%, #ffffff 100%);
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
    color: white !important;
}

.stat-label {
    font-size: 1rem;
    opacity: 0.8;
    font-weight: 300;
    color: white !important;
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
    color: #000;
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

/* ==== Feature cards ==== */
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
    line-height: 1.4;
    font-size: 15px;       
    font-weight: 500;       
}

.feature-title {
    font-size: 2rem;
    color: #000;
    margin-bottom: 2rem;
    font-weight: 600;
}


.feature-card:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 15px 40px rgba(0,0,0,0.15) !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
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

/*=========== PREDICTION PAGE ===========*/
.prediction-result {
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    margin-top: 1rem;
    color: #333;
}

/* === PAGE DASHBOARD === */
footer { display: none !important; }

/* === TABS === */
.tab-nav button { color: black !important; }
.tab-nav button.selected { 
    color: black !important; 
    border-bottom: 2px solid blue !important;
}

.page-title *, 
.page-subtitle *, 
.search-title *, 
.feature-title *, 
.prediction-result * {
    color: inherit !important;
}


"""


def show_page(page_id: str) -> list[Any]:
    """
    Control which main page is visible based on a page identifier.

    Args:
        page_id (str):
            String identifier for the page to show.
            Accepted values are:
                - "home" → displays the homepage
                - "dashboard" → displays the dashboard
                - "prediction" → displays the property estimation page

    Returns:
        list[gr.Update]:
            A list of `gr.update()` objects controlling the visibility
            of each of the three main app sections, in the following order:
            [home, dashboard, prediction].
    """
    is_home: bool = page_id == "home"
    is_dashboard: bool = page_id == "dashboard"
    is_prediction: bool = page_id == "prediction"

    return [
        gr.update(visible=is_home),
        gr.update(visible=is_dashboard),
        gr.update(visible=is_prediction),
    ]


def app_menu() -> gr.Blocks:
    """
    Build and return the full Gradio interface for the application.

    This function defines:
    - A fixed navigation bar with buttons (Home, Dashboard, Estimation, API Docs, GitLab)
    - Three distinct pages:
        1. Home page (overview, cards, department search)
        2. Dashboard page (visual data analysis)
        3. Prediction page (property price estimation form)
    - Navigation logic between these pages through Gradio event triggers.

    Returns:
        gr.Blocks:
            The complete Gradio Blocks interface representing the full application.
    """

    with gr.Blocks(css=global_css, title="France Property Insight", fill_width=True) as menu:

        # Header / Navigation bar
        with gr.Row(elem_id="navbar"):
            # Left section: logo
            with gr.Column(scale=1):
                gr.Image(
                    format="png",
                    value="docs/fpi-logo.png",
                    type="pil",
                    show_label=False,
                    elem_id="logo-image",
                    container=False,
                    interactive=False,
                    show_download_button=False,
                    show_fullscreen_button=False,
                    show_share_button=False,
                    height=90,
                )

            # Right section: navigation links
            with gr.Column(scale=9):
                with gr.Row(elem_id="nav-links"):
                    nav_home: gr.Button = gr.Button("Home", elem_classes="nav-links-button")
                    nav_dashboard: gr.Button = gr.Button("Dashboard", elem_classes="nav-links-button")
                    nav_estimate: gr.Button = gr.Button("Estimation", elem_classes="nav-links-button")
                    nav_api_docs: gr.Button = gr.Button(
                        "API Docs", link="https://france-property-insight-docs.onrender.com/fpi.html", elem_classes="nav-links-button"
                    )
                    nav_gitlab: gr.Button = gr.Button(
                        "GitLab", link="https://gitlab-mi.univ-reims.fr/phan0005/gpd-m2sep-france-property-insight", elem_classes="nav-links-button"
                    )

        # Home page
        with gr.Column(visible=True, elem_classes="page-content") as home:
            department_dropdown, search_button, dashboard_card, estimation_card, about_card = get_home_page()

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

        # Main menu buttons
        nav_home.click(fn=show_page, inputs=gr.State("home"), outputs=all_pages)
        nav_dashboard.click(fn=show_page, inputs=gr.State("dashboard"), outputs=all_pages)
        nav_estimate.click(fn=show_page, inputs=gr.State("prediction"), outputs=all_pages)

        # External links
        nav_api_docs.click(lambda: gr.HTML("<script>window.open('https://france-property-insight-docs.onrender.com/fpi.html', '_blank')</script>"))
        nav_gitlab.click(
            lambda: gr.HTML("<script>window.open('https://gitlab-mi.univ-reims.fr/phan0005/gpd-m2sep-france-property-insight', '_blank')</script>")
        )

        # Homepage cards navigation
        dashboard_card.click(fn=show_page, inputs=gr.State("dashboard"), outputs=all_pages)
        estimation_card.click(fn=show_page, inputs=gr.State("prediction"), outputs=all_pages)
        about_card.click(fn=lambda: gr.Info("Coming soon"), inputs=None, outputs=None)

        # Search + Dashboard logic
        def navigate_to_dashboard(department: str | None) -> list[Any]:
            """
            Redirect the user to the dashboard page after selecting a department.

            Args:
                department (str | None): The selected department name or code.

            Returns:
                list[gr.Update]: Visibility updates for each page (home, dashboard, prediction).
            """
            if department:
                print(f"Navigating to dashboard with: {department}")
                return [
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(visible=False),
                ]
            return [
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
            ]

        search_button.click(fn=navigate_to_dashboard, inputs=department_dropdown, outputs=all_pages)

    return menu
