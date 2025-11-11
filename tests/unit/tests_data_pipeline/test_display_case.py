import unittest
from fpi.utils.display_case import format_display_name  

class TestFormatDisplayName(unittest.TestCase):

    def test_snake_case(self):
        self.assertEqual(format_display_name("property_value"), "Property value")

    def test_camel_case(self):
        self.assertEqual(format_display_name("yearBuilt"), "Year built")

    def test_empty_string(self):
        self.assertEqual(format_display_name(""), "")

    def test_single_word(self):
        self.assertEqual(format_display_name("price"), "Price")

    def test_mixed_case_and_underscore(self):
        self.assertEqual(format_display_name("totalPrice_value"), "Total price value")

if __name__ == "__main__":
    unittest.main()
