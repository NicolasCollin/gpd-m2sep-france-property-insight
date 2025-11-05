import unittest
from unittest.mock import patch
import gradio as gr

from fpi.interface.prediction.form import reset_form, validate_inputs
from fpi.interface.prediction.prediction_page import prediction_page, run_prediction


class TestPredictionPage(unittest.TestCase):
    # -----------------------------
    # Tests run_prediction()
    # -----------------------------
    def test_run_prediction_valid_inputs(self):
        with patch("fpi.interface.prediction.prediction_page.predict_price") as mock_predict:
            mock_predict.return_value: float = 500000
            result = run_prediction(
                postal="75005", dept="75", town="75101", prop_type="House", area=100, rooms=3, land=50
            )
            self.assertIn("Estimated property price", result)
            self.assertIn("500,000", result)

    def test_run_prediction_invalid_inputs(self):
        # Postal code invalid
        result = run_prediction(postal="7500", dept="75", town="75101", prop_type="House", area=100, rooms=3, land=50)
        self.assertIn("postal code", result)

    def test_run_prediction_model_exception(self):
        with patch("fpi.interface.prediction.prediction_page.predict_price") as mock_predict:
            mock_predict.side_effect = Exception("Model file not found")
            result = run_prediction(
                postal="75001", dept="75", town="75101", prop_type="Apartment", area=80, rooms=2, land=20
            )
            self.assertIn("Prediction failed", result)
            self.assertIn("Model file not found", result)

    # -----------------------------
    # Tests prediction_page()
    # -----------------------------
    def test_prediction_page_components(self):
        with gr.Blocks():
            predict_btn, reset_btn,  result_output, inputs_list = prediction_page()
            self.assertIsInstance(predict_btn, gr.Button)
            self.assertIsInstance(reset_btn, gr.Button)
            self.assertIsInstance(result_output, gr.Markdown)
            self.assertIsInstance(inputs_list, list)
            self.assertTrue(all(isinstance(c, gr.components.Component) for c in inputs_list))

    # -----------------------------
    # Tests reset_form()
    # -----------------------------
    def test_reset_form_returns_list(self):
        reset_values = reset_form()
        self.assertIsInstance(reset_values, list)
        self.assertEqual(len(reset_values), 8)
        self.assertEqual(reset_values[3], "House")  # Dropdown default
        self.assertEqual(reset_values[7], "")  # Result output

    # -----------------------------
    # Tests validate_inputs()
    # -----------------------------
    def test_validate_inputs_required_field(self):
        error_msg = validate_inputs("", "75", "75101", "House", 100, 3, 50)
        self.assertIn("Postal code", error_msg)


if __name__ == "__main__":
    unittest.main()
