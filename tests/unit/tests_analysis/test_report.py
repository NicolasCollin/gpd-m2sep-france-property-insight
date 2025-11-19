import pandas as pd
import pytest

from fpi.analysis.report import (
    analyze_dataset_quality,
    count_missing_values,
    count_type_local,
    detect_outliers,
)


@pytest.fixture
def sample_df():
    """Provide a sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "Type_local": ["Maison", "Appartement", "Maison", None, "Local"],
            "Valeur_fonciere": [100000, 200000, 150000, 3000000, None],
            "Surface": [50, 60, None, 200, 55],
            "Commune": ["Paris", "Lyon", None, "Marseille", "Lille"],
        }
    )


class TestDataQuality:
    """
    Unit tests for data quality analysis functions in `report.py`.

    Scenarios tested:
        - `count_missing_values`: correctly counts NaN values per column.
        - `count_type_local`: counts occurrences of each Type_local value, including handling None.
        - `detect_outliers`: identifies numeric columns and counts outliers.
        - `analyze_dataset_quality`: aggregates missing values, type_local counts, and outliers.
    """

    def test_count_missing_values(self, sample_df):
        """Verify missing values are correctly counted per column."""
        result = count_missing_values(sample_df)
        assert isinstance(result, list)
        assert ("Type_local", 1) in result
        assert ("Surface", 1) in result
        assert ("Commune", 1) in result

    def test_count_type_local(self, sample_df):
        """Check counts of each Type_local value, including handling None values."""
        result = count_type_local(sample_df)
        assert isinstance(result, list)
        values = dict(result)
        assert values.get("Maison") == 2
        assert values.get("Appartement") == 1
        assert values.get("Local") == 1
        assert values.get(None) is None

    def test_detect_outliers(self, sample_df):
        """Ensure numeric columns are checked and outlier counts are returned."""
        result = detect_outliers(sample_df)
        assert isinstance(result, list)
        values = dict(result)
        assert "Valeur_fonciere" in values
        assert "Surface" in values

    def test_analyze_dataset_quality(self, sample_df):
        """Verify that the global dataset quality report aggregates all metrics correctly."""
        report = analyze_dataset_quality(sample_df)
        assert "missing_values" in report
        assert "type_local_counts" in report
        assert "outliers" in report
        tl = dict(report["type_local_counts"])
        assert tl.get("Maison") == 2
