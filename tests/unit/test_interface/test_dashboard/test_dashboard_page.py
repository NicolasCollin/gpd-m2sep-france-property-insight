import unittest

import gradio as gr

from fpi.interface.dashboard.dashboard_page import get_dashboard_page


class TestDashboardPage(unittest.TestCase):
    def test_dashboard_page(self):
        result: gr.Blocks = get_dashboard_page()
        self.assertIsInstance(result, gr.Blocks)


if __name__ == "__main__":
    unittest.main()
