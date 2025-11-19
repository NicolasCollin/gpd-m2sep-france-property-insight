import gradio as gr
import pandas as pd

from fpi.interface.dashboard.market_explorer import (
    get_market_explorer_tab,
    update_market_analysis,
)


class TestUpdateMarketAnalysis:
    """
    Tests for update_market_analysis().

     Ensures:
     - Function runs without errors
     - Returns a list of 4 elements

    """

    def test_update_market_analysis_returns_list(self):
        """Should return a list of 4 elements with a DataFrame."""
        df = pd.DataFrame(
            {
                "postal_code": ["75001", "75002"],
                "town_name": ["PARIS 01", "PARIS 02"],
                "property_type": ["Maison", "Apartement"],
                "price": [300000, 450000],
                "area": [60, 45],
                "date": ["17/02/2021", "17/02/2022"],
            }
        )

        result = update_market_analysis(df, "75001 - PARIS 01")

        assert isinstance(result, list)
        assert len(result) == 4

    def test_update_market_analysis_empty_df(self):
        """Should not crash with an empty DataFrame."""
        df = pd.DataFrame(columns=["postal_code", "town_name", "property_type", "price", "area", "date"])

        result = update_market_analysis(df, "75001 - PARIS 01")
        assert isinstance(result, list)
        assert len(result) == 4


class TestGetMarketExplorerTab:
    """
    Tests for get_market_explorer_tab().

    Ensures:
    - Gradio components are created without error
    - Dropdown contains correct postal_code - town_name format
    """

    def test_get_market_explorer_tab_structure(self):
        """Check returned dictionary and component types."""
        df = pd.DataFrame({"postal_code": ["75001", "75002"], "town_name": ["PARIS 01", "PARIS 02"]})

        with gr.Blocks():
            components = get_market_explorer_tab(df)

        assert "location_dropdown" in components
        assert "total_transactions" in components
        assert "median_price_info" in components
        assert "sales_by_type_plot" in components
        assert "sales_by_date_plot" in components

        assert isinstance(components["location_dropdown"], gr.Dropdown)
        assert isinstance(components["total_transactions"], gr.Number)
        assert isinstance(components["median_price_info"], gr.Textbox)
        assert isinstance(components["sales_by_type_plot"], gr.Plot)
        assert isinstance(components["sales_by_date_plot"], gr.Plot)

    def test_empty_dataframe_dropdown(self):
        """Dropdown should handle empty DataFrame."""
        df = pd.DataFrame(columns=["postal_code", "town_name"])

        with gr.Blocks():
            components = get_market_explorer_tab(df)

        dropdown = components["location_dropdown"]
        assert isinstance(dropdown, gr.Dropdown)
        assert dropdown.choices == []
        assert dropdown.value is None
