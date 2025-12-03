import gradio as gr
import pandas as pd
import plotly.graph_objects as go

from fpi.interface.dashboard.market_explorer import MAX_DEPARTMENTS, get_market_explorer_tab, update_compare_section, update_market_analysis


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
        df = pd.DataFrame({"postal_code": ["75001", "75002"], "town_name": ["PARIS 01", "PARIS 02"], "property_type": ["Maison", "Appartement"]})

        with gr.Blocks():
            components = get_market_explorer_tab(df)

        assert "location_dropdown" in components
        assert "total_transactions" in components
        assert "median_price_info" in components
        assert "sales_by_type_plot" in components
        assert "sales_by_date_plot" in components
        assert "compare_dropdown" in components
        assert "department_cards" in components
        assert "department_plots" in components
        assert "prop_type_input" in components
        assert "min_rooms" in components
        assert "min_surface" in components
        assert "max_surface" in components
        assert "confirm_button" in components

        assert isinstance(components["location_dropdown"], gr.Dropdown)
        assert isinstance(components["total_transactions"], gr.Number)
        assert isinstance(components["median_price_info"], gr.Textbox)
        assert isinstance(components["sales_by_type_plot"], gr.Plot)
        assert isinstance(components["sales_by_date_plot"], gr.Plot)
        assert isinstance(components["compare_dropdown"], gr.Dropdown)
        assert all(isinstance(card, gr.Markdown) for card in components["department_cards"])
        assert isinstance(components["department_plots"], list)
        assert all(isinstance(plot, gr.Plot) for plot in components["department_plots"])
        assert isinstance(components["prop_type_input"], gr.Dropdown)
        assert isinstance(components["min_rooms"], gr.Slider)
        assert isinstance(components["min_surface"], gr.Number)
        assert isinstance(components["max_surface"], gr.Number)
        assert isinstance(components["confirm_button"], gr.Button)

    def test_empty_dataframe_dropdown(self):
        """Dropdown should handle empty DataFrame."""
        df = pd.DataFrame(columns=["postal_code", "town_name", "property_type"])

        with gr.Blocks():
            components = get_market_explorer_tab(df)

        dropdown = components["location_dropdown"]
        assert isinstance(dropdown, gr.Dropdown)
        assert dropdown.choices == []
        assert dropdown.value is None


class TestUpdateCompareSection:
    """
    Tests for update_compare_section().

    Ensures:
    - Function runs without errors
    - Returns a list of length 2 * MAX_DEPARTMENTS
    - Returns empty strings and empty figures when no department is selected
    """

    def test_update_compare_section_returns_list(self):
        """Should return a list of cards and figures with correct length."""
        df = pd.DataFrame(
            {
                "postal_code": ["75001", "75002"],
                "town_name": ["PARIS 01", "PARIS 02"],
                "property_type": ["Maison", "Appartement"],
                "property_value": [300000, 450000],
                "building_area": [60, 45],
                "main_rooms": [3, 2],
                "transaction_date": ["17/02/2021", "17/02/2022"],
            }
        )

        selected_departments = ["75"]
        result = update_compare_section(df, selected_departments, "All", 2, 40, 70)

        assert isinstance(result, list)
        assert len(result) == 2 * MAX_DEPARTMENTS
        assert all(isinstance(x, str) for x in result[:MAX_DEPARTMENTS])
        assert all(isinstance(x, go.Figure) for x in result[MAX_DEPARTMENTS:])

    def test_update_compare_section_empty_selection(self):
        """Should return empty cards and empty figures if no department is selected."""
        df = pd.DataFrame(
            {
                "postal_code": ["75001", "75002"],
                "town_name": ["PARIS 01", "PARIS 02"],
                "property_type": ["Maison", "Appartement"],
                "property_value": [300000, 450000],
                "building_area": [60, 45],
                "main_rooms": [3, 2],
                "transaction_date": ["17/02/2021", "17/02/2022"],
            }
        )

        result = update_compare_section(df, [], "All", 2, 40, 70)

        assert isinstance(result, list)
        assert len(result) == 2 * MAX_DEPARTMENTS
        assert all(x == "" for x in result[:MAX_DEPARTMENTS])
        assert all(isinstance(x, go.Figure) for x in result[MAX_DEPARTMENTS:])
