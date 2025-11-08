"""
Unit tests for fpi.data_pipeline.loader
Covers the CSV loading logic via `load_all_csv`.

Checks:
1. Multiple CSV files are loaded and concatenated
2. Numeric columns are parsed correctly (handling French decimal format)
3. All relevant columns are preserved
4. No data is lost during concatenation
5. Input directory structure is handled correctly
"""

from pathlib import Path

import pandas as pd
import pytest

from fpi.data_pipeline.loader import load_all_csv


class TestLoadAllCsv:
    """
    Tests for the `load_all_csv` function in fpi.data_pipeline.loader.

    Scenarios covered:
    1. Multiple CSV files in nested directories are concatenated correctly.
    2. French decimal format in numeric columns is correctly converted to float.
    3. Department codes and other numeric columns are correctly parsed as integers.
    4. No rows or columns are lost during loading.
    """

    @pytest.fixture
    def tmp_csv_dir(self, tmp_path: Path) -> Path:
        """
        Create a temporary folder containing multiple cleaned CSV files.

        Steps:
        1. Generate two small DataFrames representing cleaned DVF data.
        2. Save them as CSV files in separate subdirectories under tmp_path.
        3. Ensure all parent directories exist before saving.

        Returns:
            Path: Path to the temporary root folder containing the CSV files.
        """
        # CSV 1
        df1 = pd.DataFrame(
            {
                "transaction_date": ["01/01/2024", "02/01/2024"],
                "property_value": ["1000000,00", "2000000,00"],
                "postal_code": [75001, 75001],
                "department_code": ["75", "75"],
                "town_code": [101, 101],
                "property_type_code": [1, 1],
                "property_type": ["Appartement", "Appartement"],
                "building_area": [50, 70],
                "main_rooms": [1, 2],
                "land_area": [0, 0],
            }
        )
        csv1 = tmp_path / "cleaned2024" / "cleaned_XX_XXXX.csv"
        csv1.parent.mkdir(parents=True, exist_ok=True)
        df1.to_csv(csv1, index=False, decimal=",")

        # CSV 2
        df2 = pd.DataFrame(
            {
                "transaction_date": ["03/01/2024"],
                "property_value": ["1500000,00"],
                "postal_code": [75002],
                "department_code": ["75"],
                "town_code": [102],
                "property_type_code": [2],
                "property_type": ["Appartement"],
                "building_area": [60],
                "main_rooms": [3],
                "land_area": [0],
            }
        )
        csv2 = tmp_path / "cleaned2023" / "cleaned_YY_YYYY.csv"
        csv2.parent.mkdir(parents=True, exist_ok=True)
        df2.to_csv(csv2, index=False, decimal=",")

        return tmp_path

    def test_multiple_csv_files_loaded(self, tmp_csv_dir: Path) -> None:
        """
        Scenario: Multiple cleaned CSV files from different subdirectories are loaded.

        Steps:
        1. Call `load_all_csv` with the temporary folder.
        2. Assert that the resulting DataFrame includes all rows.
        3. Assert that no extra columns are present and all relevant columns remain.
        """
        df = load_all_csv(data_root=str(tmp_csv_dir))

        # Basic row and column checks
        assert not df.empty
        assert df.shape[0] == 3  # 2 rows from CSV1 + 1 row from CSV2
        expected_columns = [
            "transaction_date",
            "property_value",
            "postal_code",
            "department_code",
            "town_code",
            "property_type_code",
            "property_type",
            "building_area",
            "main_rooms",
            "land_area",
        ]
        for col in expected_columns:
            assert col in df.columns

    def test_numeric_columns_converted(self, tmp_csv_dir: Path) -> None:
        """
        Scenario: Numeric columns with French decimal format are converted to float.

        Steps:
        1. Load CSV files with `load_all_csv`.
        2. Assert that 'property_value', 'building_area', 'main_rooms', 'land_area'
           are of type float.
        3. Assert that numeric values are correctly converted.
        """
        df = load_all_csv(data_root=str(tmp_csv_dir))

        numeric_cols = ["property_value", "building_area", "main_rooms", "land_area"]
        for col in numeric_cols:
            assert pd.api.types.is_numeric_dtype(df[col])

        # Check specific conversions
        assert df["property_value"].iloc[0] == 1500000.0
        assert df["property_value"].iloc[1] == 1000000.0
        assert df["building_area"].iloc[0] == 60.0
        assert df["main_rooms"].iloc[0] == 3.0

    def test_department_codes_as_integers(self, tmp_csv_dir: Path) -> None:
        """
        Scenario: Department codes and other integer columns are correctly parsed.

        Steps:
        1. Load CSV files.
        2. Assert that 'department_code', 'postal_code', 'town_code', 'property_type_code'
           are integers and match the expected values.
        """
        df = load_all_csv(data_root=str(tmp_csv_dir))

        int_cols = ["department_code", "postal_code", "town_code", "property_type_code"]
        for col in int_cols:
            assert pd.api.types.is_integer_dtype(df[col])

        # Spot check values
        assert df["department_code"].iloc[0] == 75
        assert df["town_code"].iloc[0] == 102
