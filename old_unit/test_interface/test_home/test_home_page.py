import unittest

import gradio as gr

from fpi.interface.home.home_page import home_page


class TestHomePage(unittest.TestCase):
    department_dropdown: gr.Dropdown
    search_button: gr.Button
    dashboard_card: gr.Button
    estimation_card: gr.Button
    about_card: gr.Button

    def setUp(self) -> None:
        """Initialize the page before each test"""
        with gr.Blocks():
            with gr.Blocks():
                (
                    self.department_dropdown,
                    self.search_button,
                    self.dashboard_card,
                    self.estimation_card,
                    self.about_card,
                ) = home_page()

    def test_returns_tuple(self) -> None:
        """Check that the function returns a tuple with the expected element types"""
        self.assertIsInstance(self.department_dropdown, gr.Dropdown)
        self.assertIsInstance(self.search_button, gr.Button)
        self.assertIsInstance(self.dashboard_card, gr.Button)
        self.assertIsInstance(self.estimation_card, gr.Button)
        self.assertIsInstance(self.about_card, gr.Button)

    def test_tuple_length(self) -> None:
        """Check that the tuple has exactly 5 elements"""
        with gr.Blocks():
            result = home_page()
            self.assertEqual(len(result), 5)

    def test_dropdown_properties(self):
        """Verify the department dropdown settings"""
        self.assertEqual(self.department_dropdown.elem_id, "department-search")
        self.assertTrue(self.department_dropdown.interactive)
        choices_labels = [choice[0] if isinstance(choice, tuple) else choice for choice in self.department_dropdown.choices]
        self.assertIn("75 - Paris", choices_labels)

    def test_search_button_label(self):
        """Verify the search button label"""
        self.assertEqual(self.search_button.value, "Analyze →")
        self.assertEqual(self.search_button.elem_id, "search-button")

    def test_dashboard_card_label(self):
        """Verify the label of the Dashboard button"""
        expected_label = "📊 DASHBOARD\nVisualize market trends, price per m², time evolution and detailed analysis by area"
        self.assertEqual(self.dashboard_card.value, expected_label)

    def test_estimation_card_label(self):
        """Verify the label of the Estimation button"""
        expected_label = "🏠 ESTIMATION\nGet accurate property valuation thanks to our artificial intelligence models"
        self.assertEqual(self.estimation_card.value, expected_label)

    def test_about_card_label(self):
        """Verify the label of the About Us button"""
        expected_label = "ABOUT US\nDiscover our mission and expertise in French real estate market analysis"
        self.assertEqual(self.about_card.value, expected_label)

    def test_feature_cards_ids(self):
        """Verify the elem_id of each button"""
        self.assertEqual(self.dashboard_card.elem_id, "feature-dashboard")
        self.assertEqual(self.estimation_card.elem_id, "feature-estimation")
        self.assertEqual(self.about_card.elem_id, "feature-about")

    def test_feature_cards_class(self):
        """Verify that all buttons have the correct CSS class"""
        for card in [self.dashboard_card, self.estimation_card, self.about_card]:
            self.assertIn("feature-card", card.elem_classes)


if __name__ == "__main__":
    unittest.main()
