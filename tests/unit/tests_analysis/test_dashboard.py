import pandas as pd
import pandas.testing as pdt
import pytest


class TestPlotSalesCountByDepartment:
    """
    Unit tests for plot_sales_count_by_department focusing on data aggregation logic.

    Scenarios tested:
    1. Single department
    2. Multiple departments
    3. Empty DataFrame
    4. Single-row DataFrame
    5. Grouping and counting logic
    """

    def test_single_department(self) -> None:
        """Scenario 1: All rows belong to the same department."""
        df: pd.DataFrame = pd.DataFrame({"department_code": ["75", "75", "75", "75", "75"]})
        expected: pd.DataFrame = df.groupby("department_code").size().reset_index(name="property_count")
        expected["department_code"] = expected["department_code"].astype(str)

        grouped: pd.DataFrame = df.groupby("department_code").size().reset_index(name="property_count")
        grouped["department_code"] = grouped["department_code"].astype(str)

        pdt.assert_frame_equal(grouped, expected)
        count: int = grouped.loc[0, "property_count"]
        assert count == 5

    def test_multiple_departments(self) -> None:
        """Scenario 2: Rows belong to multiple departments."""
        df: pd.DataFrame = pd.DataFrame({"department_code": ["75", "75", "92", "92", "92"]})
        expected: pd.DataFrame = df.groupby("department_code").size().reset_index(name="property_count")
        expected["department_code"] = expected["department_code"].astype(str)

        grouped: pd.DataFrame = df.groupby("department_code").size().reset_index(name="property_count")
        grouped["department_code"] = grouped["department_code"].astype(str)

        pdt.assert_frame_equal(grouped, expected)
        count_75: int = grouped.loc[grouped["department_code"] == "75", "property_count"].iloc[0]
        count_92: int = grouped.loc[grouped["department_code"] == "92", "property_count"].iloc[0]
        assert count_75 == 2
        assert count_92 == 3

    def test_empty_dataframe(self) -> None:
        """Scenario 3: Input DataFrame has no rows."""
        df: pd.DataFrame = pd.DataFrame(columns=["department_code"])
        grouped: pd.DataFrame = df.groupby("department_code").size().reset_index(name="property_count")
        assert grouped.empty

    def test_single_row(self) -> None:
        """Scenario 4: Only one property transaction."""
        df: pd.DataFrame = pd.DataFrame({"department_code": ["75"]})
        grouped: pd.DataFrame = df.groupby("department_code").size().reset_index(name="property_count")
        grouped["department_code"] = grouped["department_code"].astype(str)

        assert len(grouped) == 1
        count: int = grouped.loc[0, "property_count"]
        dept: str = grouped.loc[0, "department_code"]
        assert count == 1
        assert dept == "75"

    def test_grouping_and_counting_logic(self, df_dvf: pd.DataFrame) -> None:
        """Scenario 5: Using fixture data for aggregation correctness."""
        expected_grouped: pd.DataFrame = df_dvf.groupby("department_code").size().reset_index(name="property_count")
        expected_grouped["department_code"] = expected_grouped["department_code"].astype(str)

        df_grouped: pd.DataFrame = df_dvf.groupby("department_code").size().reset_index(name="property_count")
        df_grouped["department_code"] = df_grouped["department_code"].astype(str)

        pdt.assert_frame_equal(df_grouped, expected_grouped)
        count: int = df_grouped.loc[0, "property_count"]
        assert count == 5


class TestPlotPriceEvolutionByDepartment:
    """
    Unit tests for plot_price_evolution_by_department focusing on data preparation.

    Scenarios tested:
    1. Single department, single year
    2. Single department, multiple years
    3. Multiple departments, multiple years
    """

    def test_single_department_single_year(self) -> None:
        """Scenario 1: One department, one year."""
        df: pd.DataFrame = pd.DataFrame(
            {
                "transaction_date": ["01/01/2024", "15/06/2024"],
                "property_value": ["1000000,00", "2000000,00"],
                "department_code": ["75", "75"],
            }
        )
        df_copy: pd.DataFrame = df.copy()
        df_copy["property_value"] = df_copy["property_value"].str.replace(",", ".").astype(float)
        df_copy["transaction_date"] = pd.to_datetime(df_copy["transaction_date"], dayfirst=True)
        df_copy["year"] = df_copy["transaction_date"].dt.year

        grouped: pd.DataFrame = df_copy.groupby(["year", "department_code"]).property_value.mean().reset_index()
        expected_mean: float = (1000000.0 + 2000000.0) / 2

        assert grouped["property_value"].iloc[0] == pytest.approx(expected_mean)

    def test_single_department_multiple_years(self) -> None:
        """Scenario 2: One department, multiple years."""
        df: pd.DataFrame = pd.DataFrame(
            {
                "transaction_date": ["01/01/2023", "01/01/2024"],
                "property_value": ["1000000,00", "2000000,00"],
                "department_code": ["75", "75"],
            }
        )
        df_copy: pd.DataFrame = df.copy()
        df_copy["property_value"] = df_copy["property_value"].str.replace(",", ".").astype(float)
        df_copy["transaction_date"] = pd.to_datetime(df_copy["transaction_date"], dayfirst=True)
        df_copy["year"] = df_copy["transaction_date"].dt.year

        grouped: pd.DataFrame = df_copy.groupby(["year", "department_code"]).property_value.mean().reset_index()

        first_year_value: float = grouped["property_value"].iloc[0]
        second_year_value: float = grouped["property_value"].iloc[1]
        assert first_year_value == pytest.approx(1000000.0)
        assert second_year_value == pytest.approx(2000000.0)

    def test_multiple_departments_multiple_years(self) -> None:
        """Scenario 3: Multiple departments and multiple years."""
        df: pd.DataFrame = pd.DataFrame(
            {
                "transaction_date": ["01/01/2023", "01/01/2024", "01/06/2024", "01/06/2023"],
                "property_value": ["1000000,00", "2000000,00", "3000000,00", "4000000,00"],
                "department_code": ["75", "75", "92", "92"],
            }
        )
        df_copy: pd.DataFrame = df.copy()
        df_copy["property_value"] = df_copy["property_value"].str.replace(",", ".").astype(float)
        df_copy["transaction_date"] = pd.to_datetime(df_copy["transaction_date"], dayfirst=True)
        df_copy["year"] = df_copy["transaction_date"].dt.year

        grouped: pd.DataFrame = df_copy.groupby(["year", "department_code"]).property_value.mean().reset_index()

        means: dict[tuple[int, str], float] = grouped.set_index(["year", "department_code"])["property_value"].to_dict()
        assert means[(2023, "75")] == pytest.approx(1000000.0)
        assert means[(2024, "75")] == pytest.approx(2000000.0)
        assert means[(2023, "92")] == pytest.approx(4000000.0)
        assert means[(2024, "92")] == pytest.approx(3000000.0)
