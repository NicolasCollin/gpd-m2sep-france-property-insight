import os
import sys

import gradio as gr
import pandas as pd
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fpi.data_pipeline.data_prep import load_data

# Load dataset once to optimize performance


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
            gr.Number(value=len(df), label="Total properties in dataset", interactive=False)
            gr.Textbox(value=f"{df['property_value'].mean():,.0f} €", label="Average property price", interactive=False)
            gr.Textbox(value=f"{df['property_value'].min():,.0f} €", label="Minimum property price", interactive=False)
            gr.Textbox(value=f"{df['property_value'].max():,.0f} €", label="Maximum property price", interactive=False)

        gr.DataFrame(value=df.head(50), label="Sample of dataset")

    return table_block


def nb_property_by_dept(df: pd.DataFrame) -> gr.BarPlot:
    """
    Create a bar plot showing the number of property transactions by department.

    Args:
        df: pd.DataFrame

    Returns:
        gr.BarPlot: Gradio bar chart of transaction counts by department.
    """

    df_grouped = df.groupby("department_code").size().reset_index(name="property_count")

    df_grouped["department_code"] = df_grouped["department_code"].astype(str)

    bar_plot = gr.BarPlot(
        df_grouped,
        x="department_code",
        y="property_count",
        title="Number of property by department",
        yaxis_tickformat="~s",
    )

    return bar_plot


def evolution_price_by_dept(df: pd.DataFrame) -> gr.Plot:
    """
    Creates an interactive line plot showing the evolution of average property prices
    per department on a yearly basis.

    Args:
        df (pd.DataFrame): DataFrame containing at least the following columns:
            - 'transaction_date' (str): date of the transaction (format: dd/mm/yyyy)
            - 'property_value' (str or float): property price, e.g., "63600000,00"
            - 'department_code' (int or str): department identifier

    Returns:
        gr.Plot: Gradio plot component with the yearly average property prices per department
    """

    # --- Data preprocessing ---
    df = df.copy()

    # Convert property_value to float
    df["property_value"] = df["property_value"].astype(str).str.replace(",", ".").astype(float)

    # Convert transaction_date to datetime
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], dayfirst=True)

    # Extract year
    df["year"] = df["transaction_date"].dt.year

    # --- Group by year and department ---
    df_grouped = df.groupby(["year", "department_code"]).property_value.mean().reset_index()

    # --- Plot ---
    fig = px.line(
        df_grouped,
        x="year",
        y="property_value",
        color="department_code",
        markers=True,
        labels={"year": "Year", "property_value": "Average Property Price (€)", "department_code": "Department"},
        title="Annual evolution of property prices by department",
    )

    return gr.Plot(value=fig)


# -------------------------------------------------------------------
# DISPLAY FUNCTION
# -------------------------------------------------------------------

df = load_data()


def display_dashboard() -> gr.Blocks:
    """
    Display all dashboard components (tables + graphs) in a single container.

    Returns:
        gr.Blocks: Complete Gradio dashboard layout ready to be rendered.
    """
    with gr.Blocks() as dashboard:
        with gr.Tab("Overview"):
            table(df)

        with gr.Tab("Data vizualisation"):
            nb_property_by_dept(df)
            evolution_price_by_dept(df)

    return dashboard
