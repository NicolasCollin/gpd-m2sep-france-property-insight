import gradio as gr
import pandas as pd

from fpi.analysis.dashboard import plot_price_evolution_by_department, plot_sales_count_by_department
from fpi.data_pipeline.loader import load_all_csv
from fpi.interface.dashboard.market_explorer import get_market_explorer_tab


def get_dashboard_table(df: pd.DataFrame) -> gr.Blocks:
    """
    Display key summary statistics and a preview of the dataset.
    """
    # Ensure property_value is numeric even if loaded as string
    df["property_value"] = pd.to_numeric(df["property_value"].astype(str).str.replace(",", "."), errors="coerce")

    with gr.Blocks() as table_block:
        with gr.Row():
            total_properties: int = len(df)
            median_price: str = f"{df['property_value'].median():,.0f} €"
            min_price: str = f"{df['property_value'].min():,.0f} €"
            max_price: str = f"{df['property_value'].max():,.0f} €"

            gr.Number(value=total_properties, label="Total properties in dataset", interactive=False)
            gr.Textbox(value=median_price, label="Median property price", interactive=False)
            gr.Textbox(value=min_price, label="Minimum property price", interactive=False)
            gr.Textbox(value=max_price, label="Maximum property price", interactive=False)

        gr.DataFrame(value=df.head(50), label="Sample of dataset")

    return table_block


def display_dashboard() -> gr.Blocks:
    """
    Display all dashboard components (tables + graphs) in a single container.

    Returns:
        gr.Blocks: Complete Gradio dashboard layout ready to be rendered.
    """
    df: pd.DataFrame = load_all_csv()
    with gr.Blocks() as dashboard:
        with gr.Tab("Overview"):
            _ = get_dashboard_table(df)
            _ = plot_sales_count_by_department(df)
            _ = plot_price_evolution_by_department(df)

        with gr.Tab("Explore the market"):
            gr.Markdown("## Explore the real estate market in Ile-de-France")
            get_market_explorer_tab(df)

    return dashboard


def get_dashboard_page() -> gr.Blocks:
    """
    Interactive dashboard for Ile-de-France real estate data.

    Returns:
        Dashboard (gr.Blocks)
    """

    gr.Markdown("# Ile-de-France real estate dashboard", elem_classes="page-title")
    gr.Markdown("Explore property values interactively with filters for department and property type.", elem_classes="page-subtitle")

    dashboard: gr.Blocks = display_dashboard()

    return dashboard
