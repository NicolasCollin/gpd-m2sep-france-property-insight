import numpy as np
import pandas as pd

from fpi.map_config.map import aggregate_properties


class TestAggregateProperties:
    """
    Unit tests for the aggregate_properties function.

    Each test ensures that:
        - The function returns a Data Frame object.
        - Output type and structure
        - Column creation
        - Aggregation logic
        - Numeric coercion and NaN handling
        - Price per square meter computation
    """

    def test_returns_data_frame(self, df_dvf: pd.DataFrame) -> None:
        """
        Test that aggregate_properties returns a data frame.

        """
        result: pd.DataFrame = aggregate_properties(df_dvf)
        assert isinstance(result, pd.DataFrame)

    def test_creates_expected_columns(self, df_dvf: pd.DataFrame) -> None:
        """
        The aggregated DataFrame should contain expected computed columns.

        """
        result = aggregate_properties(df_dvf)

        expected_columns = {
            "address",
            "building_total",
            "nb_lots",
            "price_m2",
            "property_value",
            "transaction_date",
            "land_area",
        }

        assert expected_columns.issubset(result.columns)

    def test_address_is_built_correctly(self, df_dvf: pd.DataFrame) -> None:
        """
        Address column should be a non-empty string ending with ', FRANCE'.

        """
        result = aggregate_properties(df_dvf)

        assert result["address"].dtype == object
        assert result["address"].str.endswith(", FRANCE").all()

    def test_aggregation_reduces_or_keeps_row_count(self, df_dvf: pd.DataFrame) -> None:
        """
        Aggregation should never increase the number of rows.

        """
        result = aggregate_properties(df_dvf)
        assert len(result) <= len(df_dvf)

    def test_building_area_is_summed(self) -> None:
        """
        building_total should be the sum of building_area
        for identical group keys.

        """
        df = pd.DataFrame(
            {
                "transaction_date": ["2023-01-01", "2023-01-01"],
                "street_number": [10, 10],
                "street_type": ["RUE", "RUE"],
                "street_name": ["TEST", "TEST"],
                "postal_code": [75000, 75000],
                "town_name": ["PARIS", "PARIS"],
                "property_value": [200000, 200000],
                "building_area": [50, 30],
                "land_area": [0, 0],
                "property_type": ["Appartement", "Appartement"],
            }
        )

        result = aggregate_properties(df)

        assert len(result) == 1
        assert result.loc[0, "building_total"] == 80
        assert result.loc[0, "nb_lots"] == 2

    def test_price_m2_is_computed_correctly(self) -> None:
        """
        price_m2 should equal property_value / (building_total + land_area).

        """
        df = pd.DataFrame(
            {
                "transaction_date": ["2023-01-01"],
                "street_number": [1],
                "street_type": ["RUE"],
                "street_name": ["TEST"],
                "postal_code": [75000],
                "town_name": ["PARIS"],
                "property_value": [300000],
                "building_area": [100],
                "land_area": [50],
                "property_type": ["Maison"],
            }
        )

        result = aggregate_properties(df)
        expected_price_m2 = 300000 / 150

        assert np.isclose(result.loc[0, "price_m2"], expected_price_m2)

    def test_price_m2_is_nan_when_area_is_zero(self) -> None:
        """
        price_m2 should be NaN if total area is zero.

        """
        df = pd.DataFrame(
            {
                "transaction_date": ["2023-01-01"],
                "street_number": [1],
                "street_type": ["RUE"],
                "street_name": ["TEST"],
                "postal_code": [75000],
                "town_name": ["PARIS"],
                "property_value": [200000],
                "building_area": [0],
                "land_area": [0],
                "property_type": ["Appartement"],
            }
        )

        result = aggregate_properties(df)

        assert pd.isna(result.loc[0, "price_m2"])

    def test_numeric_columns_are_coerced(self, df_dvf: pd.DataFrame) -> None:
        """
        property_value, building_area and land_area
        should be numeric after aggregation.

        """
        result = aggregate_properties(df_dvf)

        for col in ["property_value", "building_total", "land_area", "price_m2"]:
            assert pd.api.types.is_numeric_dtype(result[col])
