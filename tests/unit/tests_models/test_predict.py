from unittest.mock import MagicMock

import pandas as pd
import pytest

from fpi.models.predict import predict_price


class TestPredict:
    """
    Unit tests for the `predict_price` function.

    Scenarios tested:
        - Mocked model returns a fixed float and predict is called once.
        - Input dictionary is correctly converted to a DataFrame with expected shape and columns.
        - Integer inputs are accepted and correctly converted.
        - Multiple calls return independent results, respecting the model's side_effect.
        - Missing required keys in input raise a KeyError.
    """

    def test_predict_price_mock(self, example_input: dict[str, float], patched_model: MagicMock) -> None:
        """
        Scenario: predict_price returns the expected float value using a mocked model.

        Steps:
        1. Mock the model's predict method to return [123456.0].
        2. Call predict_price with the example_input fixture.
        3. Assert the returned value matches the mocked prediction.
        4. Assert the predict method was called exactly once.

        Args:
            example_input: Standard valid input dictionary for a property.
            patched_model: MagicMock patched to replace joblib.load.
        """
        patched_model.predict.return_value = [123456.0]

        result: float = predict_price("fake_path.joblib", example_input)

        assert result == 123456.0
        patched_model.predict.assert_called_once()

    def test_predict_price_input_shape(self, example_input: dict[str, float], patched_model: MagicMock) -> None:
        """
        Scenario: Input dictionary is correctly transformed to a DataFrame for prediction.

        Steps:
        1. Mock the model's predict method to return [0.0].
        2. Call predict_price with example_input.
        3. Retrieve the DataFrame passed to predict from call_args.
        4. Assert the DataFrame has one row and columns match the input keys.

        Args:
            example_input: Standard valid input dictionary.
            patched_model: MagicMock patched to replace joblib.load.
        """
        patched_model.predict.return_value = [0.0]

        _ = predict_price("fake_path.joblib", example_input)
        called_df: pd.DataFrame = patched_model.predict.call_args[0][0]

        assert called_df.shape == (1, len(example_input))
        assert set(called_df.columns) == set(example_input.keys())

    def test_predict_price_with_ints(self, example_input_int: dict[str, int], patched_model: MagicMock) -> None:
        """
        Scenario: Integer numeric values are accepted and correctly converted.

        Steps:
        1. Mock the model to return [50000.0].
        2. Call predict_price with integer input dictionary.
        3. Assert the returned prediction matches the mock output.

        Args:
            example_input_int: Input dictionary with integer values.
            patched_model: MagicMock patched to replace joblib.load.
        """
        patched_model.predict.return_value = [50000.0]

        result: float = predict_price("fake_path.joblib", example_input_int)

        assert result == 50000.0

    def test_predict_price_multiple_calls(self, example_input: dict[str, float], patched_model: MagicMock) -> None:
        """
        Scenario: Multiple calls to predict_price produce independent results.

        Steps:
        1. Mock the model with different outputs for consecutive calls using side_effect.
        2. Call predict_price twice with the same input.
        3. Assert each returned value matches the corresponding mock output.
        4. Assert the model's predict method was called twice.

        Args:
            example_input: Standard valid input dictionary.
            patched_model: MagicMock patched to replace joblib.load.
        """
        patched_model.predict.side_effect = [
            [100000.0],
            [200000.0],
        ]

        r1: float = predict_price("fake_path.joblib", example_input)
        r2: float = predict_price("fake_path.joblib", example_input)

        assert r1 == 100000.0
        assert r2 == 200000.0
        assert patched_model.predict.call_count == 2

    def test_predict_price_missing_key(self, incomplete_input: dict[str, float], patched_model: MagicMock) -> None:
        """
        Scenario: Missing keys in input_data raise a KeyError.

        Steps:
        1. Mock the model's predict method to raise KeyError for missing key.
        2. Call predict_price with incomplete_input fixture.
        3. Assert that a KeyError is raised.

        Args:
            incomplete_input: Input dictionary missing required keys.
            patched_model: MagicMock patched to replace joblib.load.
        """
        patched_model.predict.side_effect = KeyError("main_rooms")

        with pytest.raises(KeyError):
            _ = predict_price("fake_path.joblib", incomplete_input)
