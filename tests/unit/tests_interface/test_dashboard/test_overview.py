import gradio as gr
import pandas as pd
import pytest

from fpi.interface.dashboard.overview_graphs import (
    get_overview_tab,
    plot_price_segments,
    plot_property_type_pie,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """
    Provide a lightweight DataFrame simulating FPI cleaned data.

    Returns:
        pd.DataFrame: A mock DataFrame for testing.
    """
    return pd.DataFrame(
        {
            "property_value": [120000, 300000, 500000, 900000, None, 150000],
            "property_type": ["Apartment", "House", "House", "Apartment", "House", None],
            "department_code": ["75", "75", "92", "93", "93", "94"],
        }
    )


def test_plot_price_segments_returns_gr_plot(sample_df):
    """Ensure plot_price_segments returns a Gradio Plot object."""
    plot = plot_price_segments(sample_df)
    assert isinstance(plot, gr.Plot)


def test_price_segments_order(sample_df):
    """
    Ensure the segments are correctly ordered:
    Entry < Mid < Upper < Luxury.
    """
    plot = plot_price_segments(sample_df)
    fig = plot.value

    segments = [b["x"] for b in fig.to_dict()["data"]][0]
    expected = [
        "Entry (<200k)",
        "Mid (200–400k)",
        "Upper (400–700k)",
        "Luxury (>700k)",
    ]

    assert segments == expected


def test_property_type_pie_returns_plot(sample_df):
    """Ensure property type pie chart returns a Gradio Plot."""
    plot = plot_property_type_pie(sample_df)
    assert isinstance(plot, gr.Plot)


def test_property_type_pie_counts(sample_df):
    """Ensure pie chart uses correct value_counts."""
    plot = plot_property_type_pie(sample_df)
    fig = plot.value
    data_values = fig.to_dict()["data"][0]["values"]

    expected_counts = sample_df["property_type"].value_counts().tolist()

    assert sorted(data_values) == sorted(expected_counts)


def test_overview_tab_returns_blocks(monkeypatch, sample_df):
    """
    Test that get_overview_tab builds a Gradio Blocks layout.
    Mock load_all_csv to avoid loading real data.
    """

    def mock_loader():
        return sample_df

    monkeypatch.setattr("fpi.interface.dashboard.overview_graphs.load_all_csv", mock_loader)

    tab = get_overview_tab()
    assert isinstance(tab, gr.Blocks)
