import unittest

from fpi.utils.mapper import suggest_postal_code, suggest_town


class TestMapperFunctions(unittest.TestCase):
    def setUp(self):
        # Simulated mapping for testing
        self.mapping = {
            "75001": "Paris",
            "75002": "Paris",
            "93100": "Montreuil",
            "93200": "Saint-Denis",
            "93300": "Aubervilliers",
        }

    def test_suggest_postal_code_by_code(self):
        result = suggest_postal_code("750", self.mapping)
        expected = ["75001 - Paris", "75002 - Paris"]
        self.assertTrue(all(item in result for item in expected))

    def test_suggest_postal_code_by_name(self):
        result = suggest_postal_code("par", self.mapping)
        expected = ["75001 - Paris", "75002 - Paris"]
        self.assertTrue(all(item in result for item in expected))

    def test_suggest_town_match(self):
        result = suggest_town("93100", "montr", self.mapping)
        self.assertEqual(result, ["Montreuil"])

    def test_suggest_town_no_match(self):
        result = suggest_town("93100", "aubervilliers", self.mapping)
        self.assertEqual(result, [])

    def test_suggest_town_invalid_code(self):
        result = suggest_town("99999", "paris", self.mapping)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
