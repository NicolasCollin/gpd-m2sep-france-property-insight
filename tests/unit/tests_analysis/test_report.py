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
    def test_count_missing_values(self, sample_df):
        result = count_missing_values(sample_df)
        assert isinstance(result, list)
        assert ("Type_local", 1) in result
        assert ("Surface", 1) in result
        assert ("Commune", 1) in result

    def test_count_type_local(self, sample_df):
        result = count_type_local(sample_df)
        assert isinstance(result, list)
        values = dict(result)
        assert values.get("Maison") == 2
        assert values.get("Appartement") == 1
        assert values.get("Local") == 1
        assert values.get(None) == 1

    def test_detect_outliers(self, sample_df):
        result = detect_outliers(sample_df)
        assert isinstance(result, list)
        values = dict(result)
        assert "Valeur_fonciere" in values
        assert "Surface" in values

    def test_analyze_dataset_quality(self, sample_df):
        report = analyze_dataset_quality(sample_df)
        assert "missing_values" in report
        assert "type_local_counts" in report
        assert "outliers" in report
        tl = dict(report["type_local_counts"])
        assert tl.get("Maison") == 2
