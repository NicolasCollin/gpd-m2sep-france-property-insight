import gradio as gr
import pandas as pd
import plotly.express as px

from fpi.data_pipeline.loader import load_all_csv




def plot_price_segments(df: pd.DataFrame) -> gr.Plot:
    df_valid = df[df["property_value"].notna() & (df["property_value"] > 0)]

    bins = [0, 200_000, 400_000, 700_000, df_valid["property_value"].max()]
    labels = ["Entry (<200k)", "Mid (200–400k)", "Upper (400–700k)", "Luxury (>700k)"]
    df_valid["price_segment"] = pd.cut(df_valid["property_value"], bins=bins, labels=labels)

    seg = df_valid["price_segment"].value_counts().reset_index()
    seg.columns = ["Segment", "Count"]

    fig = px.bar(
        seg,
        x="Segment",
        y="Count",
        title="Property Count by Price Segment",
        color="Segment",
        text_auto=True,
    )
    fig.update_layout(height=420)

    return gr.Plot(value=fig)

def plot_property_type_proportions(df: pd.DataFrame) -> gr.Plot:
    df_valid = df[df["department_code"].notna() & df["property_type_code"].notna()]

    # Compute proportions with value_counts(normalize=True)
    table = (
        df_valid
        .value_counts(["department_code", "property_type_code"], normalize=True)
        .reset_index(name="proportion")
    )

    fig = px.bar(
        table,
        x="proportion",
        y="department_code",
        color="property_type_code",
        orientation="h",
        title="Proportion of Property Types per Department",
        labels={"department_code": "Department", "proportion": "Proportion"},
    )
    fig.update_layout(height=450)

    return gr.Plot(value=fig)



def plot_price_landscape(df: pd.DataFrame) -> gr.Plot:
    df_valid = df[
        df["property_value"].notna() &
        df["building_area"].notna() &
        (df["building_area"] > 10)
    ]

    fig = px.scatter(
        df_valid.sample(min(5000, len(df_valid))),
        x="building_area",
        y="property_value",
        color="property_value",
        opacity=0.45,
        title="Landscape of Price vs Surface (Sample)",
        labels={"building_area": "Living area (m²)", "property_value": "Price (€)"},
    )

    fig.update_layout(height=450)
    return gr.Plot(value=fig)


def get_overview_tab() -> gr.Blocks:
    df = load_all_csv()
    df["property_value"] = pd.to_numeric(df["property_value"], errors="coerce")

    with gr.Blocks() as overview:
        gr.Markdown("## Market Overview — Île-de-France")

        with gr.Row():
            gr.Number(value=len(df), label="Total transactions", interactive=False)
            gr.Number(value=df["property_value"].median(), label="Median price (€)", interactive=False)
            gr.Number(value=df["property_value"].max(), label="Maximum price (€)", interactive=False)

        gr.Markdown("### Price Segments")
        plot_price_segments(df)

        gr.Markdown("### Property Type Composition per Department")
        plot_property_type_proportions(df)

        gr.Markdown("### Price Landscape (Surface vs Price)")
        plot_price_landscape(df)

    return overview
