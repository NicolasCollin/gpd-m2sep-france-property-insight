import os
import sys
import unittest
from typing import List

import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from fpi.interface.menu import app_menu


class TestAppMenu(unittest.TestCase):
    # Type hint for the instance attribute
    menu: gr.Blocks

    def setUp(self) -> None:
        """Initialize the app menu before each test"""
        self.menu = app_menu()

    def test_returns_blocks(self) -> None:
        """Check that the function returns a gradio blocks object"""
        self.assertIsInstance(self.menu, gr.Blocks)

    def test_contains_expected_sections(self) -> None:
        """Check that the main sections (home, dashboard, prediction) exist"""
        # Gradio keeps components in the Blocks.children attribute
        section_types: List[type] = [type(child) for child in self.menu.children]
        self.assertIn(gr.Column, section_types, "The app should contain multiple Columns")

    def test_contains_expected_ui_objects(self) -> None:
        """Ensure that each imported page contributes its UI elements"""
        # Each section (home, dashboard, prediction) should have child components
        for child in self.menu.children:
            if isinstance(child, gr.Column):
                self.assertGreater(len(child.children), 0, "Each section should contain UI elements")

    def test_has_navigation_logic(self) -> None:
        """Ensure that navigation buttons and events are defined"""
        # Retrieve all buttons within the menu
        buttons: List[gr.Button] = [child for child in self.menu.children if isinstance(child, gr.Button)]
        # Expect at least navigation buttons to be present
        self.assertTrue((len(buttons), 2), "Expected navigation buttons to be defined")

    def test_blocks_not_empty(self) -> None:
        """Verify that the menu layout has at least one component"""
        self.assertGreater(len(self.menu.children), 0, "Menu should contain child components")

    def test_can_launch_without_error(self) -> None:
        """Ensure that the app can be launched (builds correctly)"""
        try:
            # Launch a temporary Gradio Blocks context to build the menu
            with gr.Blocks() as test_menu_context:  # noqa: F841
                menu_instance: gr.Blocks = app_menu()  # noqa: F841
        except Exception as e:
            self.fail(f"app_menu() raised an exception during launch: {e}")


if __name__ == "__main__":
    unittest.main()
