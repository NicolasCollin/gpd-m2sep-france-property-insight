import gradio as gr
import pandas as pd

from fpi.analysis.dashboard import evolution_price_by_dept, nb_property_by_dept
from fpi.data_pipeline.data_prep import load_data


def table(df: pd.DataFrame) -> gr.Blocks:
    """
    Display key summary statistics and a preview of the dataset.

    Args:
        df: pd.DataFrame

    Returns:
        gr.Blocks: Gradio block containing summary statistics and data table.
    """
    with gr.Blocks() as table_block:
        with gr.Row():
            total_properties: int = len(df)
            avg_price: str = f"{df['property_value'].mean():,.0f} €"
            min_price: str = f"{df['property_value'].min():,.0f} €"
            max_price: str = f"{df['property_value'].max():,.0f} €"

            gr.Number(value=total_properties, label="Total properties in dataset", interactive=False)
            gr.Textbox(value=avg_price, label="Average property price", interactive=False)
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
    df: pd.DataFrame = load_data()
    with gr.Blocks() as dashboard:
        with gr.Tab("Overview"):
            _ = table(df)

        with gr.Tab("Data vizualisation"):
            _ = nb_property_by_dept(df)
            _ = evolution_price_by_dept(df)

    return dashboard


def dashboard_page() -> gr.Blocks:
    """
    Interactive dashboard for Ile-de-France real estate data.

    Returns:
        Dashboard (gr.Blocks)
    """

    gr.Markdown("# Ile-de-France Real Estate Dashboard", elem_classes="page-title")
    gr.Markdown("Explore property values interactively with filters for department and property type.")

    dashboard: gr.Blocks = display_dashboard()

    return dashboard
