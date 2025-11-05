import os
import sys
import unittest

import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from fpi.interface.dashboard.dashboard_page import dashboard_page


class TestDashboardPage(unittest.TestCase):
    def test_dashboard_page(self):
        result = dashboard_page()
        self.assertIsInstance(result, gr.Blocks)


if __name__ == "__main__":
    unittest.main()
