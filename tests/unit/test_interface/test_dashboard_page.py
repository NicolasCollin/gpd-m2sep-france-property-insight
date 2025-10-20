import os
import sys
import unittest
from typing import List, Tuple

import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from fpi.interface.dashboard_page import dashboard_page


class TestDashboardPage(unittest.TestCase):
    dashboard: gr.Blocks
    back_home: gr.Button

    def setUp(self) -> None:
        """Initialize the dashboard page before each test"""
        self.dashboard, self.back_home = dashboard_page()

    def test_returns_tuple(self) -> None:
        """Check that the function returns a tuple with the expected element types"""
        self.assertIsInstance(self.dashboard, gr.Blocks)
        self.assertIsInstance(self.back_home, gr.Button)

    def test_tuple_length(self) -> None:
        """Check that the tuple has exactly 2 elements"""
        result: Tuple[gr.Blocks, gr.Button] = dashboard_page()
        self.assertEqual(len(result), 2)

    def test_button_labels(self) -> None:
        """Verify that the back button has the correct label"""
        self.assertEqual(self.back_home.value, "Retour à l'accueil")

    def test_blocks_structure(self) -> None:
        """Ensure that the page contains Markdown components"""
        children_types: List[type] = [type(child) for child in self.dashboard.children]
        self.assertIn(gr.Markdown, children_types, "The page should contain Markdown elements")

    def test_css_applied(self) -> None:
        """Check that custom CSS is defined"""
        self.assertIn("background-color", self.dashboard.css)
        self.assertIn("#003f7f", self.dashboard.css)


if __name__ == "__main__":
    unittest.main()
