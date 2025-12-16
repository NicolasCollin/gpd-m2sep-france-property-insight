import gradio as gr
import pandas as pd

from fpi.analysis.dashboard import plot_price_evolution_by_department, plot_sales_count_by_department
from fpi.data_pipeline.loader import load_all_csv
from fpi.interface.dashboard.market_explorer import get_market_explorer_tab
from fpi.interface.dashboard.overview_graphs import get_overview_tab


def get_dashboard_table(df: pd.DataFrame) -> gr.Blocks:
    """
    Display key summary statistics and a preview of the dataset.

    Args:
        df: Loaded DVF dataset.

    Returns:
        A Gradio Blocks section containing summary numbers and a sample table.
    """

    df["property_value"] = pd.to_numeric(df["property_value"].astype(str).str.replace(",", "."), errors="coerce")

    with gr.Blocks() as table_block:
        with gr.Row():
            total_properties = len(df)
            median_price = f"{df['property_value'].median():,.0f} €"
            min_price = f"{df['property_value'].min():,.0f} €"
            max_price = f"{df['property_value'].max():,.0f} €"

            gr.Number(value=total_properties, label="Total properties", interactive=False)
            gr.Textbox(value=median_price, label="Median price", interactive=False)
            gr.Textbox(value=min_price, label="Min price", interactive=False)
            gr.Textbox(value=max_price, label="Max price", interactive=False)

        gr.DataFrame(value=df.head(50), label="Sample of dataset")

    return table_block


def display_dashboard() -> gr.Blocks:
    """
    Display all dashboard components (tables, plots, maps) in a unified layout.

    Returns:
        The complete Gradio dashboard in a Blocks object.
    """
    df = load_all_csv()

    with gr.Blocks() as dashboard:
        with gr.Tab("Overview"):
            gr.Markdown("## Market & Area Insights")
            _ = get_dashboard_table(df)
            _ = plot_price_evolution_by_department(df)
            _ = plot_sales_count_by_department(df)
            _ = get_overview_tab()

        with gr.Tab("Explore the market"):
            gr.Markdown("## Explore the real estate market")
            _ = get_market_explorer_tab(df)

    return dashboard


def get_dashboard_page() -> gr.Blocks:
    """
    Render the full real-estate dashboard with overview, filters, and maps.

    Returns:
        Gradio Blocks page.
    """
    gr.Markdown(" Ile-de-France real estate dashboard", elem_classes="page-title")
    gr.Markdown("Interactive data exploration with filters, charts, and geospatial visualization.", elem_classes="page-subtitle")

    dashboard = display_dashboard()

    return dashboard
