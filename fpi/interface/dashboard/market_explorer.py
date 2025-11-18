from typing import Any, Dict, List

import gradio as gr
import pandas as pd

from fpi.analysis.market_analysis import (
    calculate_market_metrics,
    compare_departments,
    create_sales_by_date_plot,
    create_sales_by_property_type_plot,
    filter_data_by_location,
    get_location_choices,
)


def update_market_analysis(df: pd.DataFrame, location: str) -> List[Any]:
    """
    Update all market analysis components when location changes.

    Arg:
        str: location

    Return:
        A list of indicators and graphs

    """
    filtered_df = filter_data_by_location(df, location)
    metrics = calculate_market_metrics(filtered_df)

    median_prices = metrics.get("median_price_per_m2_by_type", {})
    median_prices_text = ""
    if isinstance(median_prices, dict):
        for prop_type, price in median_prices.items():
            median_prices_text += f"{prop_type}: {price} €/m²\n"
    else:
        median_prices_text = "No available"
    sales_by_type_fig = create_sales_by_property_type_plot(filtered_df)
    sales_by_date_fig = create_sales_by_date_plot(filtered_df)

    return [
        metrics["total_transactions"],
        median_prices_text.strip(),
        sales_by_type_fig,
        sales_by_date_fig,
    ]


def get_market_explorer_tab(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create the market explorer tab.

    Args :
        pd.DataFrame : fpi data

    Returns:
        Dict : location_dropdown, total_transactions, median_price_info, sales_by_type_plot, sales_by_date_plot

    """
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Select a location")
            location_dropdown = gr.Dropdown(
                choices=get_location_choices(df),
                value=get_location_choices(df)[0] if get_location_choices(df) else None,
                label="Department",
                interactive=True,
                elem_id="location-dropdown",
            )

    gr.Markdown("## Market indicators")

    with gr.Row():
        with gr.Column(scale=1):
            total_transactions = gr.Number(label="Total transactions", interactive=False)
        with gr.Column(scale=1):
            median_price_info = gr.Textbox(label="Median price per m² by type", interactive=False, lines=3)

    gr.Markdown("## Sales analysis")

    with gr.Row():
        with gr.Column(scale=1):
            sales_by_type_plot = gr.Plot(label="Sales by property type")
        with gr.Column(scale=1):
            sales_by_date_plot = gr.Plot(label="Sales by date")

    gr.Markdown("## Compare multiple departments")

    with gr.Row():
        with gr.Column(scale=1):
            compare_dropdown = gr.Dropdown(
                label="Select one or more departments to compare",
                choices=get_location_choices(df),
                multiselect=True,
                value=[get_location_choices(df)[0]] if get_location_choices(df) else [],
                interactive=True,
            )
            compare_button = gr.Button("Compare", variant="primary")
        with gr.Column(scale=2):
            comparison_table = gr.DataFrame(label="Comparison of market indicators", interactive=False)

    def update_comparison(selected_departments: List[str]) -> pd.DataFrame:
        if not selected_departments:
            return pd.DataFrame(columns=["Department", "Median price per m² (€)", "Transactions"])
        return compare_departments(df, selected_departments)

    compare_button.click(fn=update_comparison, inputs=compare_dropdown, outputs=comparison_table)

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
