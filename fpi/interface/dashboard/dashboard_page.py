import gradio as gr

from analysis.utils_dashboard import display_dashboard

# -------------------------------------------------------------------
# DASHBOARD PAGE
# -------------------------------------------------------------------


def dashboard_page() -> gr.Blocks:
    """
    Interactive dashboard for Ile-de-France real estate data.

    Returns:
        Dashboard
    """

    gr.Markdown("# Ile-de-France Real Estate Dashboard", elem_classes="page-title")
    gr.Markdown("Explore property values interactively with filters for department and property type.")
    
    dashboard: gr.Blocks = display_dashboard()

    return dashboard
