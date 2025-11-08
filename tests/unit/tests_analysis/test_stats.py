import pandas as pd

from fpi.analysis.stats import summary


class TestSummaryFunction:
    """
    Unit tests for the summary() function.
    Scenarios:
    1. Basic DataFrame with no missing values
    2. DataFrame with missing values
    """

    def test_basic_dataframe(self, capsys) -> None:
        """Scenario 1: DataFrame without missing values."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})

        summary(df)

        captured = capsys.readouterr()
        # Check that head is printed
        assert "===== HEAD =====" in captured.out
        # Check that shape is printed
        assert "Shape: 3 rows × 2 columns" in captured.out
        # No missing values section
        assert "Missing values" not in captured.out

    def test_missing_values_dataframe(self, capsys) -> None:
        """Scenario 2: DataFrame with missing values."""
        df = pd.DataFrame({"A": [1, None, 3], "B": ["x", "y", None]})

        summary(df)

        captured = capsys.readouterr()
        # Check that missing values section is printed
        assert "Missing values" in captured.out
        assert "A    1" in captured.out
        assert "B    1" in captured.out
