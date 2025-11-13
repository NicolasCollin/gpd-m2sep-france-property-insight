import gradio as gr
import pytest

from fpi.interface.menu import app_menu


class TestAppMenu:
    """
    Unit tests for the main app menu Gradio layout.

    This class tests that:
        - app_menu returns a valid Gradio Blocks object.
        - The menu contains at least one top-level Column.
        - All expected navigation buttons are present and have the correct elem_ids.
        - app_menu can be safely built inside a Gradio Blocks context without exceptions.
    """

    @pytest.fixture(autouse=True)
    def setup_menu(self) -> None:
        """
        Fixture to initialize the menu before each test.

        Sets:
            self.menu (gr.Blocks): the Gradio Blocks object returned by app_menu.
        """
        self.menu: gr.Blocks = app_menu()

    def test_returns_blocks(self) -> None:
        """The menu function returns a Gradio Blocks object."""
        assert isinstance(self.menu, gr.Blocks)

    def test_menu_contains_top_level_columns(self) -> None:
        """Menu should have at least one top-level Column."""
        top_columns: list[gr.Column] = [c for c in self.menu.children if isinstance(c, gr.Column)]
        assert len(top_columns) > 0

    def test_menu_contains_navigation_buttons(self) -> None:
        """Check that all expected navigation buttons exist and have correct labels."""

        def find_buttons(children: list) -> list[gr.Button]:
            """
            Recursively find all Button components in a nested Gradio layout.
            """
            buttons: list[gr.Button] = []
            for child in children:
                if isinstance(child, gr.Button):
                    buttons.append(child)
                elif hasattr(child, "children"):
                    buttons.extend(find_buttons(child.children))
            return buttons

        buttons: list[gr.Button] = find_buttons(self.menu.children)
        found_labels: list[str] = [b.value for b in buttons if b.value]

        expected_labels: list[str] = ["Home", "Dashboard", "Estimation", "API Docs", "GitLab"]

        for label in expected_labels:
            assert label in found_labels, f"Navigation button '{label}' not found in menu"

    def test_app_can_build_without_error(self) -> None:
        """Ensure app_menu can be created inside a Gradio Blocks context without raising exceptions."""
        try:
            with gr.Blocks():
                app_menu()
        except Exception as e:
            pytest.fail(f"app_menu() raised an exception: {e}")
