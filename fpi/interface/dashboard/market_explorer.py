import gradio as gr
import pandas as pd
import plotly.graph_objects as go

from fpi.analysis.market_analysis import (
    calculate_market_metrics,
    create_department_cards,
    create_department_trend_plots,
    create_sales_by_date_plot,
    create_sales_by_property_type_plot,
    filter_data_by_location,
    get_location_choices,
)
from fpi.interface.prediction.form import get_property_types


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
    metrics: dict[str, int | float | dict] = calculate_market_metrics(filtered_df)

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


MAX_DEPARTMENTS: int = 10


def update_compare_section(
    df: pd.DataFrame,
    selected_departments: list[str],
    property_type: str,
    min_rooms_val: int,
    min_surface_val: float,
    max_surface_val: float,
) -> list[str | go.Figure]:
    """
    Generate metric cards and trend plots to compare multiple departments
    based on specific criteria.

    Args:
        df: DataFrame containing real estate data.
        selected_departments: List of department codes to compare.
        property_type: Selected property type ('All', 'Maison', 'Appartement').
        min_rooms_val: Minimum number of rooms.
        min_surface_val: Minimum surface area in m².
        max_surface_val: Maximum surface area in m².

    Returns:
        A list where the first element is a Markdown string of comparison cards,
        followed by Plotly figures (up to MAX_DEPARTMENTS). Missing figures are
        replaced with empty Plotly figures.
    """
    if not selected_departments:
        return [""] * MAX_DEPARTMENTS + [go.Figure()] * MAX_DEPARTMENTS

    cards_list: list[str] = create_department_cards(df, selected_departments, property_type, min_rooms_val, min_surface_val, max_surface_val)

    plots: list[go.Figure] = create_department_trend_plots(
        df,
        selected_departments,
        property_type,
        min_rooms_val,
        min_surface_val,
        max_surface_val,
    )

    while len(cards_list) < MAX_DEPARTMENTS:
        cards_list.append("")
    while len(plots) < MAX_DEPARTMENTS:
        plots.append(go.Figure())

    return cards_list + plots


def get_market_explorer_tab(df: pd.DataFrame) -> dict[str, object]:
    """
    Create the market explorer tab.

    Args:
        df: fpi data

    Returns:
        Dictionary containing all UI components.
    """

    type_choices: list[str] = ["All"] + get_property_types(df)

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

    gr.Markdown("## Compare")

    with gr.Row():
        with gr.Column(scale=1):
            compare_dropdown: gr.Dropdown = gr.Dropdown(
                label="Select one or more departments to compare (Max 10)",
                choices=get_location_choices(df),
                multiselect=True,
                interactive=True,
            )

    with gr.Row():
        prop_type_input: gr.Dropdown = gr.Dropdown(
            label="Property type",
            choices=type_choices,
            value=type_choices[0] if type_choices else None,
            interactive=True,
        )
        min_rooms: gr.Slider = gr.Slider(0, 6, step=1, label="Minimum number of rooms", value=0)
        min_surface: gr.Number = gr.Number(label="Min surface (m²)", value=0)
        max_surface: gr.Number = gr.Number(label="Max surface (m²)", value=0)

    confirm_button: gr.Button = gr.Button("Confirm", variant="primary")

    department_cards: list[gr.Markdown] = []
    department_plots: list[gr.Plot] = []

    for i in range(MAX_DEPARTMENTS):
        with gr.Row(visible=True, elem_classes=["compare-row"], elem_id=f"compare-pair-{i}"):
            with gr.Column(scale=1):
                card: gr.Markdown = gr.Markdown(label=f"Department Metrics #{i+1}")
                department_cards.append(card)
            with gr.Column(scale=2):
                plot: gr.Plot = gr.Plot(visible=False, label=f"Sales trend #{i+1}")
                department_plots.append(plot)

    all_outputs: list = department_cards + department_plots

    compare_update = confirm_button.click(
        fn=lambda *args: update_compare_section(df, *args),
        inputs=[compare_dropdown, prop_type_input, min_rooms, min_surface, max_surface],
        outputs=all_outputs,
    )

    compare_update.then(
        fn=lambda: [gr.update(visible=True) for _ in department_plots],
        inputs=None,
        outputs=department_plots,
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
        "compare_dropdown": compare_dropdown,
        "department_cards": department_cards,
        "department_plots": department_plots,
        "prop_type_input": prop_type_input,
        "min_rooms": min_rooms,
        "min_surface": min_surface,
        "max_surface": max_surface,
        "confirm_button": confirm_button,
    }
