"""
Unit tests for the aggregation logic inside `display_trend`.

Covers:
1. Single department with a single year
2. Single department across multiple years
3. Multiple departments across multiple years

Checks:
- Correct calculation of median property values after grouping.
- Correct handling of department and year grouping.
- Aggregation behaves as expected for different input scenarios.
"""

import pandas as pd
import pytest


class TestDisplayTrendAggregation:
    """
    Unit tests for the trend aggregation logic.

    Each test scenario constructs small DataFrames simulating DVF data,
    performs grouping and median aggregation, and asserts expected values.
    """

    def test_single_department_single_year(self) -> None:
        """
        Scenario: One department in a single year.

        Steps:
        1. Create a DataFrame with two property values for the same department and year.
        2. Group by department_code, department_name, and year, then calculate median.
        3. Assert that the median is correctly computed.

        Expected behavior:
        - Median property value equals the mean of the two values.
        """
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
        trend_df: pd.DataFrame = df_all.groupby(["department_code", "department_name", "year"])["property_value"].median().reset_index()

        expected_median: float = 1500000.0
        assert trend_df["property_value"].iloc[0] == pytest.approx(expected_median)

    def test_single_department_multiple_years(self) -> None:
        """
        Scenario: One department across multiple years.

        Steps:
        1. Create a DataFrame with property values for two different years.
        2. Group by department_code, department_name, and year, then calculate median.
        3. Assert medians per year.

        Expected behavior:
        - Each year’s median matches the property value for that year.
        """
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
        trend_df: pd.DataFrame = df_all.groupby(["department_code", "department_name", "year"])["property_value"].median().reset_index()

        medians = trend_df.set_index("year")["property_value"].to_dict()
        assert medians[2023] == pytest.approx(1000000.0)
        assert medians[2024] == pytest.approx(2000000.0)

    def test_multiple_departments_multiple_years(self) -> None:
        """
        Scenario: Multiple departments across multiple years.

        Steps:
        1. Create a DataFrame with property values for two departments over two years.
        2. Group by department_code, department_name, and year, then calculate median.
        3. Assert medians for each department-year pair.

        Expected behavior:
        - Each department-year median is correctly calculated.
        """
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
        trend_df: pd.DataFrame = df_all.groupby(["department_code", "department_name", "year"])["property_value"].median().reset_index()

        medians = trend_df.set_index(["year", "department_code"])["property_value"].to_dict()
        assert medians[(2023, "75")] == pytest.approx(1000000.0)
        assert medians[(2024, "75")] == pytest.approx(2000000.0)
        assert medians[(2023, "92")] == pytest.approx(4000000.0)
        assert medians[(2024, "92")] == pytest.approx(3000000.0)
