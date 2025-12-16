import gradio as gr
import pandas as pd
import plotly.express as px

from fpi.utils.display_case import format_display_name


def plot_sales_count_by_department(df: pd.DataFrame) -> gr.Plot:
    """
    Create a bar chart showing the number of property transactions
    per department.

    Args:
        df (pd.DataFrame): DataFrame containing a 'department_code' column.

    Returns:
        gr.Plot: Gradio Plotly bar chart.
    """
    if "department_code" not in df.columns:
        return gr.Plot()

    df_grouped: pd.DataFrame = df.groupby("department_code").size().reset_index(name="property_count")

    df_grouped["department_code"] = df_grouped["department_code"].astype(str)

    fig = px.bar(
        df_grouped,
        x="department_code",
        y="property_count",
        labels={
            "department_code": format_display_name("department_code"),
            "property_count": format_display_name("property_count"),
        },
        title=format_display_name("number_of_properties_by_department"),
        text_auto=True,
    )

    fig.update_layout(height=420)

    return gr.Plot(value=fig)


def plot_price_evolution_by_department(df: pd.DataFrame) -> gr.Plot:
    """
    Create a line chart showing the yearly evolution of average
    property prices by department.

    Args:
        df (pd.DataFrame): DataFrame containing:
            - transaction_date
            - property_value
            - department_code

    Returns:
        gr.Plot: Gradio Plotly line chart.
    """
    required_columns = {"transaction_date", "property_value", "department_code"}
    if not required_columns.issubset(df.columns):
        return gr.Plot()

    df_copy: pd.DataFrame = df.copy()

    df_copy["property_value"] = df_copy["property_value"].astype(str).str.replace(",", ".", regex=False).astype(float)

    df_copy["transaction_date"] = pd.to_datetime(
        df_copy["transaction_date"],
        dayfirst=True,
        errors="coerce",
    )

    df_copy = df_copy[df_copy["transaction_date"].notna()]
    df_copy["year"] = df_copy["transaction_date"].dt.year.astype(str)

    df_grouped: pd.DataFrame = df_copy.groupby(["year", "department_code"])["property_value"].mean().reset_index()

    fig = px.line(
        df_grouped,
        x="year",
        y="property_value",
        color="department_code",
        markers=True,
        labels={
            "year": format_display_name("year"),
            "property_value": format_display_name("average_property_price"),
            "department_code": format_display_name("department"),
        },
        title=format_display_name("annual_evolution_of_property_prices_by_department"),
    )

    fig.update_layout(height=450)

    return gr.Plot(value=fig)
