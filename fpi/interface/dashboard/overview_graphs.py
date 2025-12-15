import gradio as gr
import pandas as pd
import plotly.express as px

from fpi.data_pipeline.loader import load_all_csv
from fpi.utils.display_case import format_display_name


def plot_price_segments(df: pd.DataFrame) -> gr.Plot:
    """
    Plot a bar chart showing the distribution of properties
    across predefined price segments.

    Segments:
        - Entry: < 200k
        - Mid: 200–400k
        - Upper: 400–700k
        - Luxury: > 700k

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least `property_value`.

    Returns
    -------
    gr.Plot
        A Gradio plot containing the price segment bar chart.
    """
    # Filter valid rows
    df_valid = df[df["property_value"].notna() & (df["property_value"] > 0)]
    if df_valid.empty:
        return gr.Plot()

    # Price segment definition
    bins = [0, 200_000, 400_000, 700_000, df_valid["property_value"].max()]
    labels = ["Entry (<200k)", "Mid (200–400k)", "Upper (400–700k)", "Luxury (>700k)"]

    # Assign segments
    df_valid["price_segment"] = pd.cut(df_valid["property_value"], bins=bins, labels=labels, ordered=True)

    seg = df_valid["price_segment"].value_counts(sort=False).reset_index()
    seg.columns = ["Segment", "Count"]

    # Color gradient: blue → red (sequential)
    fig = px.bar(
        seg,
        x="Segment",
        y="Count",
        color="Segment",
        color_discrete_sequence=px.colors.sequential.Redor,
        title="Price Segment Distribution",
        text_auto=True,
        category_orders={"Segment": labels},
    )
    fig.update_layout(height=420)

    return gr.Plot(value=fig)


def plot_property_type_pie(df: pd.DataFrame) -> gr.Plot:
    """
    Plot a donut-style pie chart showing the distribution
    of property types.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing a `property_type` column.

    Returns
    -------
    gr.Plot
        A Gradio plot containing the pie chart.
    """
    if "property_type" not in df.columns:
        raise ValueError("Column 'property_type' not found.")

    # Filter valid rows
    df_valid = df[df["property_type"].notna()]
    if df_valid.empty:
        return gr.Plot()

    table = df_valid["property_type"].value_counts().reset_index()
    table.columns = ["property_type", "count"]

    # Format display names
    table["Property type"] = table["property_type"].apply(format_display_name)

    fig = px.pie(
        table,
        names="Property type",
        values="count",
        title="Property Types (Île-de-France)",
        hole=0.40,
    )
    fig.update_traces(textinfo="percent")

    return gr.Plot(value=fig)


def get_overview_tab() -> gr.Blocks:
    """
    Build the full Gradio 'Overview' tab combining statistical graphs:
        - Price segments bar chart
        - Property type pie chart


    Returns
    -------
    gr.Blocks
        A composed Gradio layout ready to be integrated into the main app.
    """
    df = load_all_csv()
    df["property_value"] = pd.to_numeric(df["property_value"], errors="coerce")
    df["land_area"] = pd.to_numeric(df.get("land_area"), errors="coerce")

    with gr.Blocks() as overview:
        gr.Markdown("##  Market Overview — Île-de-France")

        # --- PRICE SEGMENTS ---
        gr.Markdown("###  Price Segments")
        gr.Row(plot_price_segments(df))

        # --- PROPERTY TYPES ---
        gr.Markdown("###  Property Types")
        gr.Row(plot_property_type_pie(df))

    return overview
