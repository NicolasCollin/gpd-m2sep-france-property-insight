from unittest.mock import patch

import geopandas as gpd
import gradio as gr
import numpy as np
import pandas as pd
import pytest

from fpi.map_config.map import aggregate_properties, build_map_gdf, create_map_with_search, generate_map


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
        result: pd.DataFrame = aggregate_properties(df_dvf)

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
        result: pd.DataFrame = aggregate_properties(df_dvf)

        assert result["address"].dtype == object
        assert result["address"].str.endswith(", FRANCE").all()

    def test_aggregation_reduces_or_keeps_row_count(self, df_dvf: pd.DataFrame) -> None:
        """
        Aggregation should never increase the number of rows.

        """
        result: pd.DataFrame = aggregate_properties(df_dvf)
        assert len(result) <= len(df_dvf)

    def test_building_area_is_summed(self) -> None:
        """
        building_total should be the sum of building_area
        for identical group keys.

        """
        df: pd.DataFrame = pd.DataFrame(
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

        result: pd.DataFrame = aggregate_properties(df)

        assert len(result) == 1
        assert result.loc[0, "building_total"] == 80
        assert result.loc[0, "nb_lots"] == 2

    def test_price_m2_is_computed_correctly(self) -> None:
        """
        price_m2 should equal property_value / (building_total + land_area).

        """
        df: pd.DataFrame = pd.DataFrame(
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

        result: pd.DataFrame = aggregate_properties(df)
        expected_price_m2: float = 300000 / 150

        assert np.isclose(result.loc[0, "price_m2"], expected_price_m2)

    def test_price_m2_is_nan_when_area_is_zero(self) -> None:
        """
        price_m2 should be NaN if total area is zero.

        """
        df: pd.DataFrame = pd.DataFrame(
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

        result: pd.DataFrame = aggregate_properties(df)

        assert pd.isna(result.loc[0, "price_m2"])

    def test_numeric_columns_are_coerced(self, df_dvf: pd.DataFrame) -> None:
        """
        property_value, building_area and land_area
        should be numeric after aggregation.

        """
        result: pd.DataFrame = aggregate_properties(df_dvf)

        for col in ["property_value", "building_total", "land_area", "price_m2"]:
            assert pd.api.types.is_numeric_dtype(result[col])


class TestBuildMapGdf:
    """
    Unit tests for build_map_gdf using a dummy aggregated DataFrame.

    Each test ensures that:
        - The function returns a GeoDataFrame and a list of addresses.
        - Output types and structure
        - Column creation
        - Unique addresses in the returned list

    """

    @pytest.fixture(autouse=True)
    def patch_geocode(self, monkeypatch):
        """
        Patch geocode_address with a dummy returning fixed coordinates.

        """
        dummy_coords: tuple = (48.8566, 2.3522)
        monkeypatch.setattr("fpi.map_config.geocoding.geocode_address", lambda address: dummy_coords)

    @pytest.fixture
    def df_agg_sample(self):
        """
        A minimal aggregated DataFrame to test build_map_gdf logic.

        """
        return pd.DataFrame(
            {
                "street_number": ["1", "2"],
                "street_type": ["RUE", "RUE"],
                "street_name": ["TEST", "TEST"],
                "postal_code": [75000, 75000],
                "town_name": ["PARIS", "PARIS"],
                "address": ["1 RUE TEST, 75000 PARIS, FRANCE", "2 RUE TEST, 75000 PARIS, FRANCE"],
                "building_total": [50, 60],
                "nb_lots": [1, 1],
                "price_m2": [2000, 2500],
                "property_value": [100000, 150000],
                "transaction_date": ["2023-01-01", "2023-01-02"],
                "land_area": [0, 0],
                "property_type": ["Appartement", "Maison"],
                "building_area": [50, 60],
            }
        )

    def test_returns_correct_types(self, df_agg_sample):
        """
        Function should return a GeoDataFrame and a list of addresses.

        """
        gdf, addresses = build_map_gdf(df_agg_sample)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert isinstance(addresses, list)

    def test_contains_required_columns(self, df_agg_sample):
        """
        The GeoDataFrame should contain required columns.

        """
        gdf, _ = build_map_gdf(df_agg_sample)
        required_cols: list = ["lat", "lng", "address", "geometry"]
        for col in required_cols:
            assert col in gdf.columns

    def test_addresses_are_unique_in_list(self, df_agg_sample):
        """
        The returned list should contain unique addresses.

        """
        _, addresses = build_map_gdf(df_agg_sample)
        assert addresses == sorted(set(addresses))


class TestGenerateMap:
    """
    Tests for generate_map function.

    Ensures that:
        - The function returns an HTML string.
        - The HTML contains expected map elements.
        - The function handles empty GeoDataFrames gracefully.
    """

    def test_returns_html_string(self):
        """
        Function should return a string representing HTML.

        """
        df: pd.DataFrame = pd.DataFrame(
            {
                "address": ["1 RUE TEST, 75000 PARIS, FRANCE"],
                "lat": [48.8566],
                "lng": [2.3522],
                "property_value": [200000],
                "property_type": ["Appartement"],
                "main_rooms": [3],
                "transaction_date": ["2023-01-01"],
                "building_total": [50],
                "price_m2": [4000],
                "nb_lots": [1],
            }
        )
        gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat), crs="EPSG:4326")

        html: str = generate_map(gdf)
        assert isinstance(html, str)
        assert "<div" in html

    def test_handles_empty_gdf(self):
        """
        Should return a map even if GeoDataFrame is empty.

        """
        gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(columns=["lat", "lng", "address"], geometry=[], crs="EPSG:4326")
        html: str = generate_map(gdf)
        assert isinstance(html, str)


class TestCreateMapWithSearch:
    """
    Tests for create_map_with_search.

    Ensures that:
        - The function returns a Gradio Blocks object.
        - The function handles a standard DVF-like DataFrame without errors.

    """

    def test_returns_gradio_blocks(self):
        """
        Function should return a gr.Blocks object.

        """

        df: pd.DataFrame = pd.DataFrame(
            {
                "transaction_date": ["2023-01-01"],
                "street_number": [1],
                "street_type": ["RUE"],
                "street_name": ["TEST"],
                "postal_code": [75000],
                "town_name": ["PARIS"],
                "property_value": [200000],
                "building_area": [50],
                "land_area": [0],
                "property_type": ["Appartement"],
            }
        )

        with patch("fpi.map_config.map.build_map_gdf") as mock_build:
            gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(
                {
                    "address": ["1 RUE TEST, 75000 PARIS, FRANCE"],
                    "lat": [48.8566],
                    "lng": [2.3522],
                    "property_value": [200000],
                    "property_type": ["Appartement"],
                    "main_rooms": [3],
                    "transaction_date": ["2023-01-01"],
                    "building_total": [50],
                    "price_m2": [4000],
                    "nb_lots": [1],
                },
                geometry=gpd.points_from_xy([2.3522], [48.8566]),
                crs="EPSG:4326",
            )

            mock_build.return_value = (gdf, ["1 RUE TEST, 75000 PARIS, FRANCE"])
            interface: gr.Blocks = create_map_with_search(df)
            assert isinstance(interface, gr.Blocks)
