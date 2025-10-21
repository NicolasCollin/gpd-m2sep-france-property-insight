import os
import sys
import unittest
from typing import Tuple

import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from fpi.interface.home_page import home_page


class TestHomePage(unittest.TestCase):
    home: gr.Blocks
    go_dashboard: gr.Button
    go_prediction: gr.Button

    def setUp(self) -> None:
        """Initialize the page before each test"""
        self.home, self.go_dashboard, self.go_prediction = home_page()

    def test_returns_tuple(self) -> None:
        """Check that the function returns a tuple with the expected element types"""
        self.assertIsInstance(self.home, gr.Blocks)
        self.assertIsInstance(self.go_dashboard, gr.Button)
        self.assertIsInstance(self.go_prediction, gr.Button)

    def test_tuple_length(self) -> None:
        """Check that the tuple has exactly 3 elements"""
        result: Tuple[gr.Blocks, gr.Button, gr.Button] = home_page()
        self.assertEqual(len(result), 3)

    def test_button_labels(self) -> None:
        """Verify that the buttons have the correct labels"""
        self.assertEqual(self.go_dashboard.value, "Dashboard")
        self.assertEqual(self.go_prediction.value, "Prediction")

    def test_blocks_structure(self) -> None:
        """Ensure that the page contains Markdown components"""
        children_types: list[type] = [type(child) for child in self.home.children]
        self.assertIn(gr.Markdown, children_types, "The page should contain Markdown elements")

    def test_css_applied(self) -> None:
        """Check that custom CSS is defined"""
        self.assertIn("background-color", self.home.css)
        self.assertIn("#005b9e", self.home.css)


if __name__ == "__main__":
    unittest.main()
