import os
import sys
import unittest

import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fpi.interface.prediction.form import form, reset_form, validate_inputs


class TestFormModule(unittest.TestCase):
    # -----------------------------
    # Tests validate_inputs
    # -----------------------------
    def test_valid_inputs(self):
        msg = validate_inputs("75001", "75", "75101", "House", 100, 3, 50)
        self.assertEqual(msg, "")

    def test_missing_required_field(self):
        msg = validate_inputs("", "75", "75101", "House", 100, 3, 50)
        self.assertIn("Postal code", msg)

    def test_invalid_area(self):
        msg = validate_inputs("75001", "75", "75101", "House", 0, 3, 50)
        self.assertIn("Living area", msg)

    def test_invalid_rooms(self):
        msg = validate_inputs("75001", "75", "75101", "House", 100, 0, 50)
        self.assertIn("Number of rooms", msg)

    def test_invalid_land(self):
        msg = validate_inputs("75001", "75", "75101", "House", 100, 3, -10)
        self.assertIn("Land area", msg)

    def test_invalid_postal(self):
        msg = validate_inputs("7500", "75", "75101", "House", 100, 3, 50)
        self.assertIn("postal code", msg)

    # -----------------------------
    # Tests form()
    # -----------------------------
    def test_form_returns_components(self):
        with gr.Blocks():
            inputs_list, prop_type_input = form()
            self.assertIsInstance(inputs_list, list)
            self.assertTrue(all(isinstance(c, gr.components.Component) for c in inputs_list))
            self.assertIsInstance(prop_type_input, gr.Dropdown)
            self.assertEqual([c[0] for c in prop_type_input.choices], ["House", "Apartment"])
            self.assertEqual(prop_type_input.value, "House")

    # -----------------------------
    # Tests reset_form()
    # -----------------------------

    def test_reset_form_values(self):
        reset_values = reset_form()
        self.assertEqual(len(reset_values), 8)
        self.assertIsNone(reset_values[0])  # postal
        self.assertIsNone(reset_values[1])  # dept
        self.assertIsNone(reset_values[2])  # town
        self.assertEqual(reset_values[3], "House")  # prop_type
        self.assertIsNone(reset_values[4])  # area
        self.assertIsNone(reset_values[5])  # rooms
        self.assertIsNone(reset_values[6])  # land
        self.assertEqual(reset_values[7], "")  # result output


if __name__ == "__main__":
    unittest.main()
