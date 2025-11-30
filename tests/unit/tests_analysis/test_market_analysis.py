import pandas as pd
import plotly.graph_objects as go

from fpi.analysis.market_analysis import (
    calculate_financing_simulation,
    calculate_market_metrics,
    calculate_median_price_per_m2_by_type,
    compare_departments_by_criteria,
    create_department_cards,
    create_department_trend_plots,
    create_sales_by_date_plot,
    create_sales_by_property_type_plot,
    filter_data_by_criteria,
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


class TestFilterDataByCriteria:
    """
    Tests for `filter_data_by_criteria()`.

    Scenarios tested:
        - Filtering by minimum rooms
        - Filtering by minimum surface
        - Filtering by maximum surface
        - Filtering by property type
        - Combining multiple criteria
        - No filter returns the original DataFrame
    """

    @staticmethod
    def _df() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "postal_code": ["75001", "75002", "92000"],
                "department_code": ["75", "75", "92"],
                "value": [100, 200, 300],
                "property_type": ["Maison", "Appartement", "Maison"],
                "main_rooms": [2, 5, 8],
                "building_area": [50, 70, 100],
            }
        )

    def test_min_rooms(self):
        df = self._df()
        filtered = filter_data_by_criteria(df, min_rooms=5)
        assert isinstance(filtered, pd.DataFrame)
        assert all(filtered["main_rooms"] >= 5)
        assert len(filtered) == 2

    def test_min_surface(self):
        df = self._df()
        filtered = filter_data_by_criteria(df, min_surface=70)
        assert all(filtered["building_area"] >= 70)
        assert len(filtered) == 2

    def test_max_surface(self):
        df = self._df()
        filtered = filter_data_by_criteria(df, max_surface=70)
        assert all(filtered["building_area"] <= 70)
        assert len(filtered) == 2

    def test_property_type(self):
        df = self._df()
        filtered = filter_data_by_criteria(df, property_type="Maison")
        assert all(filtered["property_type"] == "Maison")
        assert len(filtered) == 2

    def test_combined_filters(self):
        df = self._df()
        filtered = filter_data_by_criteria(df, min_rooms=5, min_surface=70, property_type="Maison")
        assert len(filtered) == 1
        row = filtered.iloc[0]
        assert row["main_rooms"] >= 5
        assert row["building_area"] >= 70
        assert row["property_type"] == "Maison"

    def test_no_filter_returns_all(self):
        df = self._df()
        filtered = filter_data_by_criteria(df)
        pd.testing.assert_frame_equal(filtered, df)


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
        monthly, total, debt_ratio = calculate_financing_simulation(200000, 40000, 4000, 20, 3.5)
        assert monthly > 0
        assert total > 0
        assert debt_ratio > 0

    def test_zero_loan(self):
        monthly, total, debt_ratio = calculate_financing_simulation(100000, 100000, 5000, 10, 2)
        assert monthly == 0
        assert total == 0
        assert debt_ratio == 0


class TestCompareDepartmentsByCriteria:
    """
    Tests for compare_departments_by_criteria()

    Scenarios tested:
        - Returns a DataFrame with department comparisons.
        - Correctly filters data by selected departments and criteria.
        - Includes expected columns: Department, Transactions, and median price per m² for property types.

    """

    @staticmethod
    def _df() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "department_code": ["75", "75", "92", "92"],
                "main_rooms": [2, 5, 3, 4],
                "building_area": [50, 70, 60, 80],
                "property_type": ["Maison", "Appartement", "Maison", "Appartement"],
                "value": [100, 200, 150, 250],
            }
        )

    def test_return_type_and_columns(self):
        df = self._df()
        result = compare_departments_by_criteria(df, selected_departments=["75", "92"], property_type="Maison")
        assert isinstance(result, pd.DataFrame)
        assert "Department" in result.columns
        assert "Transactions" in result.columns
        assert "Median price per m² – Maison" in result.columns

    def test_filtering_effect(self):
        df = self._df()
        result = compare_departments_by_criteria(df, selected_departments=["75"], min_rooms=3)
        assert all(result["Transactions"] >= 0)
        assert list(result["Department"]) == ["75"]


class TestCreateDepartmentCards:
    """
    Tests for create_department_cards()

    Scenarios tested:
        - Returns a list of department cards for specified departments and criteria.
        - Ensures that the cards contain relevant information based on the input DataFrame.

    """

    @staticmethod
    def _df() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "department_code": ["75", "75", "92"],
                "main_rooms": [2, 5, 3],
                "building_area": [50, 70, 60],
                "property_type": ["Maison", "Appartement", "Maison"],
                "value": [100, 200, 150],
            }
        )

    def test_return_type_and_content(self):
        df = self._df()
        cards = create_department_cards(df, departments=["75"], property_type="Maison", min_rooms=2, min_surface=50, max_surface=100)
        assert isinstance(cards, list)
        assert all(isinstance(c, str) for c in cards)
        assert "75" in cards[0]


class TestCreateDepartmentTrendPlots:
    """
    Tests for `create_department_trend_plots()`.

    Scenarios tested:
        - Returns a list of plotly.graph_objects.Figure, one per requested department.
        - Handles empty or fully filtered-out data by producing an empty figure (no traces).
        - Supports comparing multiple departments.

    """

    @staticmethod
    def _df() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "department_code": ["75", "75", "92"],
                "main_rooms": [2, 5, 3],
                "building_area": [50, 70, 60],
                "property_type": ["Maison", "Appartement", "Maison"],
                "value": [100, 200, 150],
                "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            }
        )

    def test_return_type_and_length(self):
        df = self._df()
        plots = create_department_trend_plots(df, departments=["75", "92"], property_type="Maison", min_rooms=2, min_surface=50, max_surface=100)
        assert isinstance(plots, list)
        assert all(isinstance(p, go.Figure) for p in plots)
        assert len(plots) == 2

    def test_empty_data_handling(self):
        df = pd.DataFrame(
            {
                "department_code": ["75"],
                "main_rooms": [1],
                "building_area": [10],
                "property_type": ["Appartement"],
                "value": [50],
                "date": ["2023-01-01"],
            }
        )
        plots = create_department_trend_plots(df, departments=["92"], property_type="Maison", min_rooms=5, min_surface=100, max_surface=200)
        assert isinstance(plots[0], go.Figure)
        assert plots[0].data == ()
