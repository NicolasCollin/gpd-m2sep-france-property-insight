import gradio as gr
import pytest

from fpi.interface.home.home_page import get_home_page


class TestGetHomePage:
    """
    Unit tests for the get_home_page function in home_page.py.

    Tests:
        1. The function runs without raising exceptions.
        2. The returned tuple contains the expected Gradio component types.
        3. The Dropdown has the expected choices (normalized to strings).
        4. Buttons have non-empty labels.
    """

    def test_function_runs_without_error(self) -> None:
        """get_home_page should run without raising any exception."""
        result: tuple = ()
        try:
            result = get_home_page()
        except Exception as e:
            pytest.fail(f"get_home_page raised an exception: {e}")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_returns_expected_tuple(self) -> None:
        """The function should return a tuple of 3 Gradio components with correct types."""
        dashboard_card: gr.Button
        estimation_card: gr.Button
        about_card: gr.Button

        dashboard_card, estimation_card, about_card = get_home_page()

        assert isinstance(dashboard_card, gr.Button)
        assert isinstance(estimation_card, gr.Button)
        assert isinstance(about_card, gr.Button)

    def test_buttons_have_expected_labels(self) -> None:
        """Check that buttons have non-empty labels."""
        dashboard_card: gr.Button
        estimation_card: gr.Button
        about_card: gr.Button

        dashboard_card, estimation_card, about_card = get_home_page()

        buttons: list[gr.Button] = [dashboard_card, estimation_card, about_card]

        for button in buttons:
            label: str = getattr(button, "elem_id", "") or getattr(button, "label", "")
            assert label.strip() != "", f"Button {button} has empty label"
