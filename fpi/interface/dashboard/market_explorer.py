import gradio as gr
import pandas as pd
import plotly.graph_objects as go

from fpi.analysis.market_analysis import (
    calculate_market_metrics,
    create_sales_by_date_plot,
    create_sales_by_property_type_plot,
    filter_data_by_location,
    get_location_choices,
)


def update_market_analysis(df: pd.DataFrame, location: str) -> list[object]:
    """
    Update all market analysis components when location changes.

    Args:
        df: DataFrame with real-estate data
        location: Location string (department or town)

    Returns:
        A list of indicators and graphs:
        [total_transactions, median_prices_text, plot1, plot2]
    """

    filtered_df: pd.DataFrame = filter_data_by_location(df, location)
    metrics = calculate_market_metrics(filtered_df)

    median_prices: object = metrics.get("median_price_per_m2_by_type", {})
    median_prices_text: str = ""

    if isinstance(median_prices, dict):
        for prop_type, price in median_prices.items():
            median_prices_text += f"{prop_type}: {price} €/m²\n"
    else:
        median_prices_text = "No available"

    sales_by_type_fig: go.Figure = create_sales_by_property_type_plot(filtered_df)
    sales_by_date_fig: go.Figure = create_sales_by_date_plot(filtered_df)

    return [
        metrics["total_transactions"],
        median_prices_text.strip(),
        sales_by_type_fig,
        sales_by_date_fig,
    ]


def get_market_explorer_tab(df: pd.DataFrame) -> dict[str, object]:
    """
    Create the market explorer tab.

    Args:
        df: fpi data

    Returns:
        Dictionary containing all UI components.
    """

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Select a location")
            location_choices: list[str] = get_location_choices(df)
            default_location: str | None = location_choices[0] if location_choices else None

            location_dropdown: gr.Dropdown = gr.Dropdown(
                choices=location_choices,
                value=default_location,
                label="Department",
                interactive=True,
                elem_id="location-dropdown",
            )

    gr.Markdown("## Market indicators")

    with gr.Row():
        with gr.Column(scale=1):
            total_transactions: gr.Number = gr.Number(
                label="Total transactions",
                interactive=False,
            )
        with gr.Column(scale=1):
            median_price_info: gr.Textbox = gr.Textbox(
                label="Median price per m² by type",
                interactive=False,
                lines=3,
            )

    gr.Markdown("## Sales analysis")

    with gr.Row():
        with gr.Column(scale=1):
            sales_by_type_plot: gr.Plot = gr.Plot(label="Sales by property type")
        with gr.Column(scale=1):
            sales_by_date_plot: gr.Plot = gr.Plot(label="Sales by date")

    gr.Markdown("## Compare multiple departments")

    with gr.Row():
        with gr.Column(scale=1):
            compare_dropdown: gr.Dropdown = gr.Dropdown(
                label="Select one or more departments to compare",
                choices=location_choices,
                multiselect=True,
                value=[default_location] if default_location else [],
                interactive=True,
            )

            compare_button: gr.Button = gr.Button("Compare", variant="primary")

        with gr.Column(scale=2):
            comparison_table: gr.DataFrame = gr.DataFrame(
                label="Comparison of market indicators",
                interactive=False,
            )

    def update_comparison(selected_departments: list[str]) -> pd.DataFrame:
        if not selected_departments:
            return pd.DataFrame(columns=["Department", "Median price per m² (€)", "Transactions"])
        return compare_departments(df, selected_departments)

    compare_button.click(
        fn=update_comparison,
        inputs=compare_dropdown,
        outputs=comparison_table,
    )

    location_dropdown.change(
        fn=lambda loc: update_market_analysis(df, loc),
        inputs=location_dropdown,
        outputs=[total_transactions, median_price_info, sales_by_type_plot, sales_by_date_plot],
    )

    return {
        "location_dropdown": location_dropdown,
        "total_transactions": total_transactions,
        "median_price_info": median_price_info,
        "sales_by_type_plot": sales_by_type_plot,
        "sales_by_date_plot": sales_by_date_plot,
    }
