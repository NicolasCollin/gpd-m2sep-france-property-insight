"""
Unit tests for fpi.models.predict
Uses a mock model to avoid loading real joblib files.

Checks:
1. predict_price returns expected value using a mocked model
2. Input dictionary is correctly converted to a DataFrame
3. Integer inputs are handled
4. Multiple calls produce independent predictions
5. Missing keys raise errors
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from fpi.models.predict import predict_price


@pytest.fixture
def example_input() -> dict[str, float]:
    """
    Provides a standard example input dictionary for property prediction.

    Returns:
        dict[str, float]: Dictionary with numeric property features.
    """
    return {
        "building_area": 13.0,
        "main_rooms": 1,
        "land_area": 20.0,
        "postal_code": 75020,
        "property_type_code": 2,
        "town_code": 120,
        "department_code": 75,
    }


class TestPredict:
    """
    Unit tests for the `predict_price` function from fpi.models.predict.

    Checks:
    1. Correct output using a mocked model
    2. DataFrame shape and column names
    3. Handling of integer input values
    4. Behavior when called multiple times
    5. Handling of missing keys in input data
    """

    def test_predict_price_mock(self, example_input: dict[str, float]) -> None:
        """
        Scenario: predict_price returns the expected float value using a mocked model.

        Steps:
        1. Create a MagicMock to simulate the model.
        2. Patch joblib.load to return the mock model.
        3. Call predict_price with example input.
        4. Assert the returned prediction matches the mock's output.
        """
        mock_model: MagicMock = MagicMock()
        mock_model.predict.return_value = [123456.0]

        with patch("fpi.models.predict.joblib.load", return_value=mock_model):
            predicted_price: float = predict_price("fake_path.joblib", example_input)

        assert predicted_price == 123456.0
        mock_model.predict.assert_called_once()

    def test_predict_price_input_shape(self, example_input: dict[str, float]) -> None:
        """
        Scenario: Input dictionary is converted to a DataFrame with correct shape and columns.

        Steps:
        1. Mock the model's predict method.
        2. Call predict_price.
        3. Check that the DataFrame passed to predict has 1 row and all required columns.
        """
        mock_model: MagicMock = MagicMock()
        mock_model.predict.return_value = [0.0]

        with patch("fpi.models.predict.joblib.load", return_value=mock_model):
            predict_price("fake_path.joblib", example_input)

        called_df: "pd.DataFrame" = mock_model.predict.call_args[0][0]
        assert called_df.shape[0] == 1
        assert set(called_df.columns) == set(example_input.keys())

    def test_predict_price_with_ints(self) -> None:
        """
        Scenario: Integer numeric values are accepted and correctly converted.

        Steps:
        1. Create an input dictionary with int values.
        2. Mock the model.
        3. Call predict_price and assert the returned value matches the mock.
        """
        example_input_int: dict[str, int] = {
            "building_area": 13,
            "main_rooms": 1,
            "land_area": 20,
            "postal_code": 75020,
            "property_type_code": 2,
            "town_code": 120,
            "department_code": 75,
        }
        mock_model: MagicMock = MagicMock()
        mock_model.predict.return_value = [50000.0]

        with patch("fpi.models.predict.joblib.load", return_value=mock_model):
            predicted_price: float = predict_price("fake_path.joblib", example_input_int)

        assert predicted_price == 50000.0

    def test_predict_price_multiple_calls(self, example_input: dict[str, float]) -> None:
        """
        Scenario: Multiple calls to predict_price produce independent results.

        Steps:
        1. Mock the model with different outputs for consecutive calls.
        2. Call predict_price twice.
        3. Assert returned values match expected outputs.
        4. Assert the predict method was called twice.
        """
        mock_model: MagicMock = MagicMock()
        mock_model.predict.side_effect = [[100000.0], [200000.0]]

        with patch("fpi.models.predict.joblib.load", return_value=mock_model):
            p1: float = predict_price("fake_path.joblib", example_input)
            p2: float = predict_price("fake_path.joblib", example_input)

        assert p1 == 100000.0
        assert p2 == 200000.0
        assert mock_model.predict.call_count == 2

    def test_predict_price_missing_key(self) -> None:
        """
        Scenario: Missing keys in input_data raise a KeyError inside the model's predict.

        Steps:
        1. Create an input dictionary missing required keys.
        2. Mock the model to raise KeyError.
        3. Call predict_price and assert KeyError is raised.
        """
        incomplete_input: dict[str, float] = {
            "building_area": 13.0,
            "land_area": 20.0,
            "postal_code": 75020,
            "property_type_code": 2,
            "town_code": 120,
            "department_code": 75,
        }
        mock_model: MagicMock = MagicMock()
        mock_model.predict.side_effect = KeyError("main_rooms")

        with patch("fpi.models.predict.joblib.load", return_value=mock_model):
            with pytest.raises(KeyError):
                predict_price("fake_path.joblib", incomplete_input)
