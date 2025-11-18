import pandas as pd
import pytest

from fpi.analysis.price import compute_price_per_sqm


def test_valid_median():
    df = pd.DataFrame({"property_value": [300000, 500000, 700000], "building_area": [60, 100, 140]})
    result = compute_price_per_sqm(df, method="median")
    assert round(result, 2) == 5000.00  # Median of [5000, 5000, 5000]


def test_valid_mean():
    df = pd.DataFrame({"property_value": [300000, 500000, 700000], "building_area": [60, 100, 140]})
    expected = (300000 / 60 + 500000 / 100 + 700000 / 140) / 3
    result = compute_price_per_sqm(df, method="mean")
    assert round(result, 2) == round(expected, 2)


def test_missing_columns():
    df = pd.DataFrame({"property_value": [300000, 500000]})
    with pytest.raises(ValueError, match="must contain 'property_value' and 'building_area'"):
        compute_price_per_sqm(df)
