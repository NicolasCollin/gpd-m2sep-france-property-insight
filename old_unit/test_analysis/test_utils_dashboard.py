import os
import sys
import unittest

import gradio as gr
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from fpi.analysis.utils_dashboard import plot_price_evolution_by_department, plot_sales_count_by_department, table


class TestUtilsDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Sample
        cls.df = pd.DataFrame(
            {
                "property_value": [100000, 200000, 150000, 300000],
                "department_code": [75, 75, 92, 92],
                "transaction_date": ["01/01/2022", "15/02/2022", "20/03/2021", "05/04/2021"],
            }
        )

    def test_table_returns_blocks(self):
        result = table(self.df)
        self.assertIsInstance(result, gr.Blocks)

    def test_plot_sales_count_by_department_returns_barplot(self):
        result = plot_sales_count_by_department(self.df)
        self.assertIsInstance(result, gr.BarPlot)
        # Verify department code
        df_grouped = self.df.groupby("department_code").size().reset_index(name="property_count")
        self.assertCountEqual(df_grouped["department_code"].astype(str).tolist(), ["75", "92"])

    def test_plot_price_evolution_by_department_type(self):
        result = plot_price_evolution_by_department(self.df)
        self.assertIsInstance(result, gr.Plot)


if __name__ == "__main__":
    unittest.main()
