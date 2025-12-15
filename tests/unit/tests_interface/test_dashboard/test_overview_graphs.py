import gradio as gr
import pandas as pd
import pytest

from fpi.interface.dashboard.overview_graphs import (
    plot_price_segments,
    plot_property_type_pie,
)


class TestOverviewGraphs:
    """
    Tests for functions in overview_graphs.
    These tests ensure that plotting functions return Gradio Plot objects
    and handle invalid inputs correctly.
    """

    def test_plot_price_segments_returns_grplot(self):
        """
        Verify that plot_price_segments returns a Gradio Plot
        when given a DataFrame with valid property values.
        """

        df = pd.DataFrame({"property_value": [100000, 250000, 500000, 800000]})
        result = plot_price_segments(df)
        assert isinstance(result, gr.Plot)

    def test_plot_property_type_pie_returns_grplot(self):
        """
        Verify that plot_property_type_pie returns a Gradio Plot
        when given a DataFrame with a valid 'property_type' column.
        """

        df = pd.DataFrame({"property_type": ["Maison", "Appartement", "Maison"]})
        result = plot_property_type_pie(df)
        assert isinstance(result, gr.Plot)

    def test_plot_property_type_pie_raises_error_if_missing_column(self):
        """
        Verify that plot_property_type_pie raises a ValueError
        when the DataFrame does not contain the 'property_type' column.
        """
        df = pd.DataFrame({"property_value": [100000, 200000]})
        with pytest.raises(ValueError, match="Column 'property_type' not found"):
            plot_property_type_pie(df)
