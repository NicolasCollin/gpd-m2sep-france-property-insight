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
        """
        df1 = pd.DataFrame(
            {
                "transaction_date": ["01/01/2024", "02/01/2024"],
                "property_value": ["1000000,00", "2000000,00"],
                "postal_code": [75001, 75001],
                "department_code": ["75", "75"],
                "town_code": [101, 102],
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

        df2 = pd.DataFrame(
            {
                "transaction_date": ["03/01/2024"],
                "property_value": ["1500000,00"],
                "postal_code": [75002],
                "department_code": ["75"],
                "town_code": [103],
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
        """
        df = load_all_csv(data_root=str(tmp_csv_dir))
        df = df.sort_values(by=["town_code"]).reset_index(drop=True)

        # Basic checks
        assert not df.empty
        assert df.shape[0] == 3  # 2 rows + 1 row
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
        assert list(df.columns) == expected_columns

    def test_numeric_columns_converted(self, tmp_csv_dir: Path) -> None:
        """
        Scenario: Numeric columns with French decimal format are converted to float.
        """
        df = load_all_csv(data_root=str(tmp_csv_dir))
        df = df.sort_values(by=["town_code"]).reset_index(drop=True)

        numeric_cols = ["property_value", "building_area", "main_rooms", "land_area"]
        for col in numeric_cols:
            assert pd.api.types.is_numeric_dtype(df[col])

        # Check converted values without relying on order
        expected_values = {1000000.0, 1500000.0, 2000000.0}
        assert set(df["property_value"].tolist()) == expected_values

    def test_department_codes_as_integers(self, tmp_csv_dir: Path) -> None:
        """
        Scenario: Department codes and other integer columns are correctly parsed.
        """
        df = load_all_csv(data_root=str(tmp_csv_dir))
        df = df.sort_values(by=["town_code"]).reset_index(drop=True)

        int_cols = ["department_code", "postal_code", "town_code", "property_type_code"]
        for col in int_cols:
            assert pd.api.types.is_integer_dtype(df[col])

        # Spot check that department codes are all '75'
        assert set(df["department_code"]) == {75}

        # Check that all expected town codes are present
        assert set(df["town_code"]) == {101, 102, 103}
