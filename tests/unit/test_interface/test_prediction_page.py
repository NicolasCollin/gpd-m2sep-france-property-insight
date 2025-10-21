import os
import sys
import unittest
from typing import Tuple

import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from fpi.interface.prediction_page import prediction_page


class TestPredictionPage(unittest.TestCase):
    # Type hints for instance attributes
    prediction: gr.Blocks
    back_home: gr.Button

    def setUp(self) -> None:
        """Initialise the page before each test"""
        self.prediction, self.back_home = prediction_page()

    def test_returns_tuple(self) -> None:
        """Check that the function returns a tuple with the expected element types"""
        self.assertIsInstance(self.prediction, gr.Blocks)
        self.assertIsInstance(self.back_home, gr.Button)

    def test_tuple_length(self) -> None:
        """Check that the tuple has exactly 2 elements"""
        result: Tuple[gr.Blocks, gr.Button] = prediction_page()
        self.assertEqual(len(result), 2)

    def test_button_labels(self) -> None:
        """Verify that the buttons have the correct labels"""
        self.assertEqual(self.back_home.value, "Retour à l'accueil")

    def test_blocks_structure(self) -> None:
        """Ensure that the page contains Markdown components"""
        children_types: list[type] = [type(child) for child in self.prediction.children]
        self.assertIn(gr.Markdown, children_types, "The page should contain Markdown elements")

    def test_css_applied(self) -> None:
        """Check that custom CSS is defined"""
        self.assertIn("background-color", self.prediction.css)
        self.assertIn("#006b6b", self.prediction.css)


if __name__ == "__main__":
    unittest.main()
