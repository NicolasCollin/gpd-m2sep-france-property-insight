import gradio as gr
import pandas as pd
import plotly.express as px


def plot_sales_count_by_department(df: pd.DataFrame) -> gr.BarPlot:
    """
    Create a bar plot showing the number of property transactions by department.

    Args:
        df: pd.DataFrame

    Returns:
        gr.BarPlot: Gradio bar chart of transaction counts by department.
    """
    df_grouped: pd.DataFrame = df.groupby("department_code").size().reset_index(name="property_count")
    df_grouped["department_code"] = df_grouped["department_code"].astype(str)

    bar_plot: gr.BarPlot = gr.BarPlot(
        df_grouped,
        x="department_code",
        y="property_count",
        title="Number of property by department",
        yaxis_tickformat="~s",
    )

    return bar_plot


def plot_price_evolution_by_department(df: pd.DataFrame) -> gr.Plot:
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
    df_copy: pd.DataFrame = df.copy()

    df_copy["property_value"] = df_copy["property_value"].astype(str).str.replace(",", ".").astype(float)
    df_copy["transaction_date"] = pd.to_datetime(df_copy["transaction_date"], dayfirst=True)
    df_copy["year"] = df_copy["transaction_date"].dt.year
    df_copy["year"] = df_copy["year"].astype(str)

    df_grouped: pd.DataFrame = df_copy.groupby(["year", "department_code"]).property_value.mean().reset_index()

    fig: px.line = px.line(
        df_grouped,
        x="year",
        y="property_value",
        color="department_code",
        markers=True,
        labels={"year": "Year", "property_value": "Average Property Price (€)", "department_code": "Department"},
        title="Annual evolution of property prices by department",
    )

    return gr.Plot(value=fig)
