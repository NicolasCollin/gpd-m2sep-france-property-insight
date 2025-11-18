import pandas as pd
import pytest

from fpi.analysis.price import compute_price_per_sqm


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """
    Provides a sample DataFrame for testing compute_price_per_sqm.

    Returns:
        pd.DataFrame: Contains columns 'property_value' and 'land_area'.
    """
    return pd.DataFrame(
        {
            "property_value": [100000.0, 200000.0, 300000.0, None],
            "land_area": [500.0, 1000.0, 1500.0, 600.0],
        }
    )


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """Provides an empty DataFrame to test edge cases."""
    return pd.DataFrame({"property_value": [], "land_area": []})


class TestComputePricePerSqm:
    """
    Unit tests for compute_price_per_sqm using land_area.
    """

    def test_median_computation(self, sample_df: pd.DataFrame) -> None:
        """Compute median price per square meter."""
        result = compute_price_per_sqm(sample_df, method="median")
        expected = pd.Series([100000 / 500, 200000 / 1000, 300000 / 1500]).median()
        assert result == expected

    def test_mean_computation(self, sample_df: pd.DataFrame) -> None:
        """Compute mean price per square meter."""
        result = compute_price_per_sqm(sample_df, method="mean")
        expected = pd.Series([100000 / 500, 200000 / 1000, 300000 / 1500]).mean()
        assert result == expected

    def test_ignore_nan_values(self) -> None:
        """Rows with NaN values should be ignored."""
        df = pd.DataFrame(
            {
                "property_value": [100000.0, None, 300000.0],
                "land_area": [500.0, 600.0, None],
            }
        )
        result = compute_price_per_sqm(df, method="median")
        expected = pd.Series([100000 / 500]).median()
        assert result == expected

    def test_empty_dataframe_raises(self, empty_df: pd.DataFrame) -> None:
        """Empty DataFrame should raise ValueError."""
        with pytest.raises(ValueError, match="No valid data"):
            compute_price_per_sqm(empty_df)

    def test_missing_columns_raise(self) -> None:
        """Missing required columns should raise ValueError."""
        df = pd.DataFrame({"property_value": [100000.0]})
        with pytest.raises(ValueError, match="must contain 'property_value' and 'land_area'"):
            compute_price_per_sqm(df)

        df = pd.DataFrame({"land_area": [500.0]})
        with pytest.raises(ValueError, match="must contain 'property_value' and 'land_area'"):
            compute_price_per_sqm(df)

    def test_ignore_zero_or_negative_land_area(self) -> None:
        """Rows with land_area <= 0 should be ignored."""
        df = pd.DataFrame(
            {
                "property_value": [100000.0, 200000.0],
                "land_area": [500.0, 0.0],
            }
        )
        result = compute_price_per_sqm(df, method="median")
        expected = pd.Series([100000 / 500]).median()
        assert result == expected
