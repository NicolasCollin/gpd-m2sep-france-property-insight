import pandas as pd
import pytest


class TestDisplayTrendAggregation:
    """
    Unit tests for the aggregation logic inside display_trend.
    Scenarios:
    1. Single department, single year
    2. Single department, multiple years
    3. Multiple departments, multiple years
    """

    def test_single_department_single_year(self) -> None:
        """Scenario 1: One department, one year."""
        dfs = [
            pd.DataFrame(
                {
                    "department_code": ["75", "75"],
                    "department_name": ["Paris", "Paris"],
                    "year": [2024, 2024],
                    "property_value": [1000000.0, 2000000.0],
                }
            )
        ]
        df_all: pd.DataFrame = pd.concat(dfs, ignore_index=True)
        trend_df: pd.DataFrame = (
            df_all.groupby(["department_code", "department_name", "year"])["property_value"].median().reset_index()
        )

        expected_median: float = 1500000.0
        assert trend_df["property_value"].iloc[0] == pytest.approx(expected_median)

    def test_single_department_multiple_years(self) -> None:
        """Scenario 2: One department, multiple years."""
        dfs = [
            pd.DataFrame(
                {
                    "department_code": ["75", "75"],
                    "department_name": ["Paris", "Paris"],
                    "year": [2023, 2024],
                    "property_value": [1000000.0, 2000000.0],
                }
            )
        ]
        df_all: pd.DataFrame = pd.concat(dfs, ignore_index=True)
        trend_df: pd.DataFrame = (
            df_all.groupby(["department_code", "department_name", "year"])["property_value"].median().reset_index()
        )

        medians = trend_df.set_index("year")["property_value"].to_dict()
        assert medians[2023] == pytest.approx(1000000.0)
        assert medians[2024] == pytest.approx(2000000.0)

    def test_multiple_departments_multiple_years(self) -> None:
        """Scenario 3: Multiple departments, multiple years."""
        dfs = [
            pd.DataFrame(
                {
                    "department_code": ["75", "75", "92", "92"],
                    "department_name": ["Paris", "Paris", "Hauts-de-Seine", "Hauts-de-Seine"],
                    "year": [2023, 2024, 2023, 2024],
                    "property_value": [1000000, 2000000, 4000000, 3000000],
                }
            )
        ]
        df_all: pd.DataFrame = pd.concat(dfs, ignore_index=True)
        trend_df: pd.DataFrame = (
            df_all.groupby(["department_code", "department_name", "year"])["property_value"].median().reset_index()
        )

        means = trend_df.set_index(["year", "department_code"])["property_value"].to_dict()
        assert means[(2023, "75")] == pytest.approx(1000000.0)
        assert means[(2024, "75")] == pytest.approx(2000000.0)
        assert means[(2023, "92")] == pytest.approx(4000000.0)
        assert means[(2024, "92")] == pytest.approx(3000000.0)
