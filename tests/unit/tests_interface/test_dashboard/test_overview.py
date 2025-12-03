import gradio as gr
import pandas as pd
import pytest

from fpi.interface.dashboard.overview_graphs import (
    get_overview_tab,
    plot_price_segments,
    plot_property_type_pie,
)


# ---------------------------------------------------------------------
# Helper: Extract Plotly Figure regardless of Gradio's internal format
# ---------------------------------------------------------------------
def extract_plotly_data(plot: gr.Plot) -> dict:
    """
    Standardize extraction of Plotly dict from a Gradio Plot object.

    Handles all cases:
    - plot.value is a plotly.graph_objs.Figure
    - plot.value is a dict containing "data"
    - plot.value nested like {"plot": {...}}, {"figure": {...}}
    """
    fig = plot.value

    # Case 1: Direct Plotly Figure
    if hasattr(fig, "to_dict"):
        return fig.to_dict()

    # Case 2: Direct figure dict
    if isinstance(fig, dict) and "data" in fig:
        return fig

    # Case 3: Nested dicts { "plot": {...} } or { "figure": {...} }
    if isinstance(fig, dict):
        for key in ("plot", "figure", "fig"):
            if key in fig:
                inner = fig[key]
                if hasattr(inner, "to_dict"):
                    return inner.to_dict()
                if isinstance(inner, dict) and "data" in inner:
                    return inner

    raise KeyError("Could not extract Plotly figure → missing 'data'")


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def sample_df():
    """Provide a lightweight DataFrame simulating FPI cleaned data."""
    return pd.DataFrame(
        {
            "property_value": [120000, 300000, 500000, 900000, None, 150000],
            "property_type": ["Apartment", "House", "House", "Apartment", "House", None],
            "department_code": ["75", "75", "92", "93", "93", "94"],
        }
    )


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
def test_plot_price_segments_returns_gr_plot(sample_df):
    """Ensure plot_price_segments returns a Gradio Plot."""
    plot = plot_price_segments(sample_df)
    assert isinstance(plot, gr.Plot)


def test_price_segments_order(sample_df):
    """Ensure segments appear in the correct order."""
    plot = plot_price_segments(sample_df)
    fig = extract_plotly_data(plot)

    data = fig["data"]
    segments = data[0]["x"]

    assert segments == ["Entry", "Mid", "Upper", "Luxury"]


def test_property_type_pie_counts(sample_df):
    """Ensure pie chart uses correct value_counts."""
    plot = plot_property_type_pie(sample_df)
    fig = extract_plotly_data(plot)

    values = fig["data"][0]["values"]

    expected_counts = (
        sample_df["property_type"]
        .dropna()
        .value_counts()
        .sort_index()
        .tolist()
    )

    assert sorted(values) == sorted(expected_counts)


def test_overview_tab_returns_blocks(monkeypatch, sample_df):
    """Ensure overview tab builds a Gradio Blocks layout."""

    def mock_loader():
        return sample_df

    monkeypatch.setattr(
        "fpi.interface.dashboard.overview_graphs.load_all_csv",
        mock_loader
    )

    tab = get_overview_tab()
    assert isinstance(tab, gr.Blocks)
