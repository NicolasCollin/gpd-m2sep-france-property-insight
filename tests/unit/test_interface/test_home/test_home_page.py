import os
import sys
import unittest
from typing import Tuple

import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from fpi.interface.home.home_page import home_page


class TestHomePage(unittest.TestCase):
    card_dashboard: gr.Button
    card_estimate: gr.Button

    def setUp(self) -> None:
        """Initialize the page before each test"""
        self.card_dashboard, self.card_estimate = home_page()

    def test_returns_tuple(self) -> None:
        """Check that the function returns a tuple with the expected element types"""
        self.assertIsInstance(self.card_dashboard, gr.Button)
        self.assertIsInstance(self.card_estimate, gr.Button)

    def test_tuple_length(self) -> None:
        """Check that the tuple has exactly 2 elements"""
        result: Tuple[gr.Button, gr.Button] = home_page()
        self.assertEqual(len(result), 2)

    def test_button_labels(self) -> None:
        """Verify that the buttons have the correct labels"""
        self.assertEqual(self.card_dashboard.value, "Dashboard")
        self.assertEqual(self.card_estimate.value, "Estimate your property")


if __name__ == "__main__":
    unittest.main()
