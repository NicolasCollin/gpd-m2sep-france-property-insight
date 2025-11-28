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

    if "property_type" not in df.columns:
        raise ValueError("La colonne 'property_type' est introuvable dans le dataframe.")

    df_valid = df[
        df["department_code"].notna() &
        df["property_type"].notna()
    ]

    table = (
        df_valid
        .groupby(["department_code", "property_type"])
        .size()
        .reset_index(name="count")
    )


    table["proportion"] = (
        table["count"] / table.groupby("department_code")["count"].transform("sum")
    )

    fig = px.bar(
        table,
        x="department_code",
        y="proportion",
        color="property_type",
        title="Répartition des types de biens par département",
        labels={
            "department_code": "Département",
            "proportion": "Proportion",
            "property_type": "Type de bien"
        },
        text="count"
    )

    fig.update_layout(
        height=450,
        barmode="stack",
        legend_title="Types de biens",
        xaxis=dict(type="category")
    )

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

    return overview
