import unittest
import gradio as gr
from fpi.interface.dashboard.dashboard_page import dashboard_page


class TestDashboardPage(unittest.TestCase):
    def test_dashboard_page(self):
        result = dashboard_page()
        self.assertIsInstance(result, gr.Blocks)


if __name__ == "__main__":
    unittest.main()
