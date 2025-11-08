import gradio as gr
import pandas as pd
import pytest

from fpi.interface.dashboard.dashboard_page import (
    display_dashboard,
    get_dashboard_page,
    get_dashboard_table,
)


class TestGetDashboardTable:
    """
    Unit tests for the get_dashboard_table function.

    Each test ensures that:
        1. The function returns a Gradio Blocks object.
        2. The function handles a standard DVF-like DataFrame without errors.
    """

    def test_returns_gradio_blocks(self, df_dvf: pd.DataFrame) -> None:
        """
        Test that get_dashboard_table returns a Gradio Blocks container.
        """
        result: gr.Blocks = get_dashboard_table(df_dvf)
        assert isinstance(result, gr.Blocks)

    def test_handles_dataframe_input(self, df_dvf: pd.DataFrame) -> None:
        """
        Test that get_dashboard_table executes without raising exceptions
        when provided with a valid DataFrame.
        """
        result: gr.Blocks = get_dashboard_table(df_dvf)  # No exception expected
        assert isinstance(result, gr.Blocks)


class TestDisplayDashboard:
    """
    Unit tests for the display_dashboard function.

    Ensures that the function correctly builds the full dashboard container
    including table and plots, returning a Gradio Blocks object.
    """

    def test_returns_gradio_blocks(
        self,
        df_dvf: pd.DataFrame,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        Test that display_dashboard returns a Gradio Blocks object.

        Monkeypatches load_all_csv to return the sample DataFrame to
        avoid file I/O.
        """
        monkeypatch.setattr(
            "fpi.interface.dashboard.dashboard_page.load_all_csv",
            lambda: df_dvf,
        )
        result: gr.Blocks = display_dashboard()
        assert isinstance(result, gr.Blocks)


class TestGetDashboardPage:
    """
    Unit tests for the get_dashboard_page function.

    Ensures that the function builds the interactive dashboard page
    and returns a Gradio Blocks container without errors.
    """

    def test_returns_gradio_blocks(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        Test that get_dashboard_page returns a Gradio Blocks object.

        Monkeypatches display_dashboard to return a dummy Gradio Blocks object
        to isolate the test from the underlying data and plotting logic.
        """
        dummy: gr.Blocks = gr.Blocks()
        monkeypatch.setattr(
            "fpi.interface.dashboard.dashboard_page.display_dashboard",
            lambda: dummy,
        )
        result: gr.Blocks = get_dashboard_page()
        assert isinstance(result, gr.Blocks)
