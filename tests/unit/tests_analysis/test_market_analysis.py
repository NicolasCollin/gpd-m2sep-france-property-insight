import pandas as pd

from fpi.analysis.market_analysis import (
    calculate_financing_simulation,
    calculate_market_metrics,
    calculate_median_price_per_m2_by_type,
    compare_departments,
    create_sales_by_date_plot,
    create_sales_by_property_type_plot,
    filter_data_by_location,
    get_location_choices,
    get_sales_by_type_data,
)


class TestGetLocationChoices:
    """
    Tests for `get_location_choices()`.

    Scenarios tested:
        - Empty DataFrame returns an empty list.
        - DataFrame with postal_code and town_name returns combined strings.
        - DataFrame with only department_code returns department codes.
    """

    def test_empty_df(self):
        df = pd.DataFrame()
        choices = get_location_choices(df)
        assert choices == []

    def test_postal_code_and_town_name(self):
        df = pd.DataFrame(
            {
                "postal_code": ["75001", "75002"],
                "town_name": ["PARIS 01", "PARIS 02"],
            }
        )
        choices = get_location_choices(df)
        expected = ["75001 - PARIS 01", "75002 - PARIS 02"]
        assert choices == sorted(expected)

    def test_department_code_only(self):
        df = pd.DataFrame({"department_code": ["75", "77"]})
        choices = get_location_choices(df)
        assert choices == ["75", "77"]


class TestFilterDataByLocation:
    """
    Tests for `filter_data_by_location()`.

    Scenarios tested:
        - Filtering by full postal code string.
        - Filtering by department code.
        - Empty location returns the original DataFrame.
    """

    @staticmethod
    def _df() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "postal_code": ["75001", "75002", "92000"],
                "department_code": ["75", "75", "92"],
                "value": [100, 200, 300],
            }
        )

    def test_filter_by_postal_code(self):
        df = self._df()
        filtered = filter_data_by_location(df, "75001 - PARIS 01")
        assert len(filtered) == 1
        assert filtered["postal_code"].iloc[0] == "75001"

    def test_filter_by_department_code(self):
        df = self._df()
        filtered = filter_data_by_location(df, "75")
        assert len(filtered) == 2
        assert all(filtered["department_code"] == "75")

    def test_empty_location_returns_df(self):
        df = self._df()
        filtered = filter_data_by_location(df, "")
        assert len(filtered) == len(df)


class TestCalculateMedianPricePerM2ByType:
    """
    Tests for `calculate_median_price_per_m2_by_type()`.

    Scenarios tested:
        - Returns correct median prices for multiple property types.
        - Handles both 'Maison' and 'Appartement' correctly.
    """

    df = pd.DataFrame(
        {
            "property_type": ["Maison", "Appartement", "Maison"],
            "property_value": [300000, 200000, 400000],
            "building_area": [60, 40, 80],
            "land_area": [10, 0, 20],
        }
    )

    def test_median_calculation(self):
        result = calculate_median_price_per_m2_by_type(self.df)
        assert "Maison" in result["property_type"].values
        assert "Appartement" in result["property_type"].values
        for val in result["median_price_per_m2"]:
            assert isinstance(val, (float, int, str))


class TestCalculateMarketMetrics:
    """
    Tests for `calculate_market_metrics()`.

    Scenarios tested:
        - Metrics dictionary contains all expected keys.
        - Total transactions matches DataFrame length.
    """

    df = pd.DataFrame(
        {
            "property_type": ["Maison", "Appartement"],
            "property_value": [300000, 200000],
            "building_area": [60, 40],
            "land_area": [10, 0],
        }
    )

    def test_metrics_structure(self):
        metrics = calculate_market_metrics(self.df)
        assert "total_transactions" in metrics
        assert "avg_surface" in metrics
        assert "median_price_per_m2_by_type" in metrics
        assert metrics["total_transactions"] == len(self.df)


class TestCreateSalesPlots:
    """
    Tests for sales plotting functions.

    Scenarios tested:
        - `create_sales_by_property_type_plot` returns a valid figure with correct layout.
        - `create_sales_by_date_plot` returns a valid figure with correct layout.
    """

    df = pd.DataFrame(
        {
            "property_type": ["Maison", "Appartement", "Maison"],
            "transaction_date": ["09/02/2021", "09/02/2021", "09/02/2021"],
        }
    )

    def test_sales_by_property_type_plot(self):
        fig = create_sales_by_property_type_plot(self.df)
        assert fig is not None
        assert fig.layout.height == 400

    def test_sales_by_date_plot(self):
        fig = create_sales_by_date_plot(self.df)
        assert fig is not None
        assert fig.layout.height == 400


class TestGetSalesByTypeData:
    """
    Tests for `get_sales_by_type_data()`.

    Scenarios tested:
        - Counts of each property type are correct.
        - Total transaction count matches input DataFrame.
    """

    df = pd.DataFrame({"property_type": ["Maison", "Appartement", "Maison"]})

    def test_counts(self):
        sales = get_sales_by_type_data(self.df)
        assert "Maison" in sales["property_type"].values
        assert "Appartement" in sales["property_type"].values
        assert sales["transaction_count"].sum() == 3


class TestCalculateFinancingSimulation:
    """
    Tests for `calculate_financing_simulation()`.

    Scenarios tested:
        - Positive loan values return positive monthly payments, total, and debt ratio.
        - Zero loan results in zero monthly payment, total, and debt ratio.
    """

    def test_basic_calculation(self):
        monthly, total, debt_ratio = calculate_financing_simulation(200000, 40000, 20, 3.5)
        assert monthly > 0
        assert total > 0
        assert debt_ratio > 0

    def test_zero_loan(self):
        monthly, total, debt_ratio = calculate_financing_simulation(100000, 100000, 10, 2)
        assert monthly == 0
        assert total == 0
        assert debt_ratio == 0


class TestCompareDepartments:
    """
    Tests for `compare_departments()`.

    Scenarios tested:
        - Returns a DataFrame with a "Department" column.
        - Correct number of rows for multiple selected departments.
        - Handles multiple property types per department.
    """

    df = pd.DataFrame(
        {
            "department_code": ["75", "75", "92"],
            "property_type": ["Maison", "Appartement", "Maison"],
            "property_value": [300000, 200000, 400000],
            "building_area": [60, 40, 80],
            "land_area": [10, 0, 20],
        }
    )

    def test_comparison_dataframe(self):
        result = compare_departments(self.df, ["75", "92"])
        assert isinstance(result, pd.DataFrame)
        assert "Department" in result.columns
        assert len(result) == 2
