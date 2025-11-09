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
        assert len(result) == 5

    def test_returns_expected_tuple(self) -> None:
        """The function should return a tuple of 5 Gradio components with correct types."""
        department_dropdown: gr.Dropdown
        search_button: gr.Button
        dashboard_card: gr.Button
        estimation_card: gr.Button
        about_card: gr.Button

        department_dropdown, search_button, dashboard_card, estimation_card, about_card = get_home_page()

        assert isinstance(department_dropdown, gr.Dropdown)
        assert isinstance(search_button, gr.Button)
        assert isinstance(dashboard_card, gr.Button)
        assert isinstance(estimation_card, gr.Button)
        assert isinstance(about_card, gr.Button)

    def test_dropdown_properties(self) -> None:
        """Dropdown should be interactive, filterable, and have the correct choices."""
        department_dropdown: gr.Dropdown
        department_dropdown, *_ = get_home_page()

        expected_choices: list[str] = [
            "75 - Paris",
            "77 - Seine-et-Marne",
            "78 - Yvelines",
            "91 - Essonne",
            "92 - Hauts-de-Seine",
            "93 - Seine-Saint-Denis",
            "94 - Val-de-Marne",
            "95 - Val-d'Oise",
        ]

        # Gradio Dropdown stores choices as (value, label) tuples internally in tests
        actual_choices: list[str] = []
        for choice in department_dropdown.choices:
            if isinstance(choice, tuple):
                # tuple of (value, label)
                label: str = choice[1]
                actual_choices.append(label)
            else:
                actual_choices.append(str(choice))

        assert department_dropdown.interactive is True
        assert department_dropdown.filterable is True
        assert actual_choices == expected_choices
        assert "department-search" in department_dropdown.elem_id

    def test_buttons_have_expected_labels(self) -> None:
        """Check that buttons have non-empty labels."""
        search_button: gr.Button
        dashboard_card: gr.Button
        estimation_card: gr.Button
        about_card: gr.Button

        _, search_button, dashboard_card, estimation_card, about_card = get_home_page()

        buttons: list[gr.Button] = [search_button, dashboard_card, estimation_card, about_card]

        for button in buttons:
            label: str = getattr(button, "elem_id", "") or getattr(button, "label", "")
            assert label.strip() != "", f"Button {button} has empty label"
