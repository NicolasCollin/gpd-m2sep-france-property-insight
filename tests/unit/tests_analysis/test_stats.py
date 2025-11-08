"""
Unit tests for fpi.analysis.stats.summary function.

Covers:
1. Printing of DataFrame head and shape.
2. Handling of DataFrames with missing values.
3. Correct display of missing value counts.
"""

import pandas as pd

from fpi.analysis.stats import summary


class TestSummaryFunction:
    """
    Unit tests for the `summary()` function.

    Checks:
    1. Basic DataFrame without missing values prints head and shape.
    2. DataFrame with missing values prints missing value counts.
    """

    def test_basic_dataframe(self, capsys) -> None:
        """
        Scenario: DataFrame without missing values.

        Steps:
        1. Create a simple DataFrame with numeric and string columns.
        2. Call summary(df).
        3. Capture printed output.

        Expected behavior:
        - Head of DataFrame is printed.
        - Shape of DataFrame is printed.
        - Missing values section is NOT printed.
        """
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})

        summary(df)

        captured = capsys.readouterr()
        # Check that head is printed
        assert "===== HEAD =====" in captured.out
        # Check that shape is printed
        assert "Shape: 3 rows × 2 columns" in captured.out
        # Missing values section should not appear
        assert "Missing values" not in captured.out

    def test_missing_values_dataframe(self, capsys) -> None:
        """
        Scenario: DataFrame containing missing values.

        Steps:
        1. Create a DataFrame with some NaNs.
        2. Call summary(df).
        3. Capture printed output.

        Expected behavior:
        - Missing values section is printed.
        - Counts of missing values per column are displayed.
        """
        df = pd.DataFrame({"A": [1, None, 3], "B": ["x", "y", None]})

        summary(df)

        captured = capsys.readouterr()
        # Check that missing values section is printed
        assert "Missing values" in captured.out
        assert "A    1" in captured.out
        assert "B    1" in captured.out
