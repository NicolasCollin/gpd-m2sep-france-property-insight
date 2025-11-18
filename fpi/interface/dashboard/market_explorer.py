import gradio as gr
import pandas as pd
import plotly.graph_objects as go

from fpi.analysis.market_analysis import (
    calculate_financing_simulation,
    calculate_market_metrics,
    compare_departments,
    create_sales_by_property_type_plot,
    create_volume_evolution_plot,
    filter_data_by_location,
    get_location_choices,
)


def get_market_explorer_tab(df: pd.DataFrame) -> None:
    """
    Create the market explorer tab with real data analysis.

    Args:
        df: Complete property dataframe
    """
    # Location selection
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Select location")
            location_dropdown = gr.Dropdown(
                choices=get_location_choices(df),
                value=get_location_choices(df)[0] if get_location_choices(df) else None,
                label="Department",
                interactive=True,
                elem_id="location-dropdown",
            )

    # BLOCK 1 : Key market metrics
    gr.Markdown("## Market Indicators")

    with gr.Row():
        with gr.Column(scale=1):
            avg_price_m2 = gr.Number(label="Average price per m² (€)", interactive=False)
        with gr.Column(scale=1):
            total_transactions = gr.Number(label="Total transactions", interactive=False)
        with gr.Column(scale=1):
            median_price = gr.Number(label="Median price (€)", interactive=False)

    # BLOCK 2 : Two side-by-side charts
    gr.Markdown("## Price and volume analysis")

    with gr.Row():
        with gr.Column(scale=1):
            sales_by_type_plot = gr.Plot(label="Sales by property type")
        with gr.Column(scale=1):
            volume_evolution_plot = gr.Plot(label="Sales volume evolution")

    # BLOCK 3 : Compare multiple departments
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

    def update_comparison(selected_departments: list[str]) -> pd.DataFrame:
        if not selected_departments:
            return pd.DataFrame(columns=["Department", "Avg price/m² (€)", "Median price (€)", "Transactions"])
        return compare_departments(df, selected_departments)

    compare_button.click(fn=update_comparison, inputs=compare_dropdown, outputs=comparison_table)

    # BLOCK 4 : Financing simulation
    gr.Markdown("## Financing simulation")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Loan parameters")
            property_price = gr.Number(label="Property price (€)", interactive=True, minimum=0)
            personal_contribution = gr.Number(label="Personal contribution (€)", interactive=True, minimum=0)
            loan_duration = gr.Slider(label="Loan duration (years)", minimum=5, maximum=30, value=20, step=1)
            interest_rate = gr.Slider(label="Interest rate (%)", minimum=1.0, maximum=6.0, value=3.5, step=0.1)
            simulate_button = gr.Button("Calculate", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Simulation results")
            monthly_payment = gr.Number(label="Monthly payment (€)", interactive=False)
            total_loan_cost = gr.Number(label="Total loan cost (€)", interactive=False)
            debt_ratio = gr.Number(label="Debt ratio (%)", interactive=False)

    def update_market_analysis(location: str) -> list[float | int | go.Figure]:
        """
        Update all market analysis components when location changes.

        Args:
            location: Selected location string

        Returns:
            Dictionary with updated components
        """
        filtered_df: pd.DataFrame = filter_data_by_location(df, location)
        metrics: dict[str, float] = calculate_market_metrics(filtered_df)
        sales_by_type_plot: go.Figure = create_sales_by_property_type_plot(filtered_df)
        volume_evolution_plot: go.Figure = create_volume_evolution_plot(filtered_df)

        return [
            metrics["avg_price_per_m2"],
            metrics["total_transactions"],
            metrics["median_price"],
            sales_by_type_plot,
            volume_evolution_plot,
        ]

    # Update analysis when location changes
    location_dropdown.change(
        fn=update_market_analysis,
        inputs=location_dropdown,
        outputs=[avg_price_m2, total_transactions, median_price, sales_by_type_plot, volume_evolution_plot],
    )

    # Financing simulation
    simulate_button.click(
        fn=calculate_financing_simulation,
        inputs=[property_price, personal_contribution, loan_duration, interest_rate],
        outputs=[monthly_payment, total_loan_cost, debt_ratio],
    )
    # Initial update
    if get_location_choices(df):
        update_market_analysis(get_location_choices(df)[0])
