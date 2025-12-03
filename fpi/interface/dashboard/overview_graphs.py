import gradio as gr
import pandas as pd
import plotly.express as px

from fpi.data_pipeline.loader import load_all_csv


def plot_price_segments(df: pd.DataFrame) -> gr.Plot:
    """
    Build a bar chart showing the number of transactions per price segment.

    The segments are:
        - Entry (< 200k)
        - Mid (200–400k)
        - Upper (400–700k)
        - Luxury (> 700k)

    Args:
        df (pd.DataFrame): Loaded DVF-style DataFrame with column 'property_value'.

    Returns:
        gr.Plot: Gradio plot containing the bar chart.
    """
    df_valid: pd.DataFrame = df[df["property_value"].notna() & (df["property_value"] > 0)]

    max_val: float = float(df_valid["property_value"].max())

    bins: list[float] = [0, 200_000, 400_000, 700_000, max_val]
    labels: list[str] = ["Entry (<200k)", "Mid (200–400k)", "Upper (400–700k)", "Luxury (>700k)"]

    df_valid["price_segment"] = pd.cut(df_valid["property_value"], bins=bins, labels=labels, ordered=True)

    seg: pd.DataFrame = df_valid["price_segment"].value_counts(sort=False).reset_index()
    seg.columns = ["Segment", "Count"]

    fig = px.bar(
        seg, x="Segment", y="Count", title="Property Count by Price Segment", color="Segment", text_auto=True, category_orders={"Segment": labels}
    )
    fig.update_layout(height=420)

    return gr.Plot(value=fig)


def plot_property_type_pie(df: pd.DataFrame) -> gr.Plot:
    """
    Build a pie chart showing the distribution of property types across all transactions.

    Args:
        df (pd.DataFrame): Loaded DVF DataFrame with 'property_type'.

    Returns:
        gr.Plot: Gradio pie chart.
    """
    if "property_type" not in df.columns:
        raise ValueError("Column 'property_type' not found in DataFrame.")

    df_valid: pd.DataFrame = df[df["property_type"].notna()]

    table: pd.DataFrame = df_valid["property_type"].value_counts().reset_index()
    table.columns = ["property_type", "count"]

    fig = px.pie(table, names="property_type", values="count", title="Distribution of Property Types (Île-de-France)", hole=0.40)
    fig.update_traces(textinfo="percent+label")

    return gr.Plot(value=fig)


def get_overview_tab() -> gr.Blocks:
    """
    Build the Overview dashboard section for the Gradio interface.

    Returns:
        gr.Blocks: The overview tab.
    """
    df: pd.DataFrame = load_all_csv()
    df["property_value"] = pd.to_numeric(df["property_value"], errors="coerce")

    with gr.Blocks() as overview:
        gr.Markdown("## Market Overview — Île-de-France")

        gr.Markdown("### Price Segments")
        plot_price_segments(df)

        gr.Markdown("### Property Type Composition")
        plot_property_type_pie(df)

    return overview
