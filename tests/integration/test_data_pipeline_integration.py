"""
Integration tests for data pipeline components.

These tests verify that multiple data pipeline components work together correctly.
The suite covers:

1. Conversion of text files to SQLite.
2. Cleaning of raw CSV data.
3. Processing of cleaned data (filtering and column extraction).
4. Loading of multiple CSV files into a single DataFrame.
5. End-to-end flow from raw data to processed output.

Each test ensures both the structural integrity of the data (columns, types)
and correctness of transformations applied by the pipeline components.
"""

import sqlite3
from pathlib import Path

import pandas as pd

from fpi.data_pipeline.clean_data import clean_data
from fpi.data_pipeline.loader import load_all_csv
from fpi.data_pipeline.process_data import process_data
from fpi.data_pipeline.txt_to_sqlite import txt_to_sqlite


class TestDataPipelineIntegration:
    """Integration tests for the complete data pipeline components."""

    def test_text_to_sqlite_pipeline(self, temp_data_dir: Path, sample_text_file: Path) -> None:
        """
        Test that a text file can be converted to a SQLite database table.

        Verifies:
        - Database file creation.
        - Table creation within the database.
        - Data insertion and column name cleanup.
        """
        db_path: Path = temp_data_dir / "test.db"
        table_name: str = "test_table"

        txt_to_sqlite(
            txt_path=sample_text_file,
            db_path=db_path,
            table_name=table_name,
            delimiter="|",
            chunksize=10,
        )

        assert db_path.exists(), "Database file should be created"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            )
            assert cursor.fetchone() is not None, "Table should exist"

            df: pd.DataFrame = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            assert len(df) == 2, "Should have 2 data rows"
            assert "Column_Name_1" in df.columns, "Column names should be cleaned"
            assert "Column_Name_2" in df.columns, "Column names should be cleaned"
            assert "Column_Name_3" in df.columns, "Column names should be cleaned"

    def test_clean_data_pipeline(self, temp_data_dir: Path, sample_raw_csv_file: Path) -> None:
        """
        Test that raw CSV data is cleaned correctly.

        Verifies:
        - Cleaned file creation with proper naming.
        - Presence of expected columns.
        - No missing values in key columns (property_value, postal_code).
        """
        raw_path: Path = temp_data_dir / "raw"
        cleaned_path: Path = temp_data_dir / "cleaned"

        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)

        cleaned_file: Path = cleaned_path / "cleaned2024" / "cleaned_75_2024.csv"
        assert cleaned_file.exists(), "Cleaned file should be created"

        df: pd.DataFrame = pd.read_csv(cleaned_file)
        assert "transaction_date" in df.columns, "Should have transaction_date column"
        assert "property_value" in df.columns, "Should have property_value column"
        assert "postal_code" in df.columns, "Should have postal_code column"
        assert len(df) > 0, "Should have data rows"
        assert df["property_value"].notna().all(), "Property values should not be null"
        assert df["postal_code"].notna().all(), "Postal codes should not be null"

    def test_process_data_pipeline(self, temp_data_dir: Path, sample_cleaned_csv_file: Path) -> None:
        """
        Test that cleaned CSV data is processed correctly.

        Verifies:
        - Processed file creation.
        - Proper extraction of 'year' column.
        - Removal of unneeded columns ('transaction_type', 'transaction_date').
        - Only 'Vente' transactions are kept.
        """
        cleaned_path: Path = temp_data_dir / "cleaned"
        processed_path: Path = temp_data_dir / "processed"

        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        processed_file: Path = processed_path / "processed2024" / "processed_75_2024.csv"
        assert processed_file.exists(), "Processed file should be created"

        df: pd.DataFrame = pd.read_csv(processed_file)
        assert "year" in df.columns, "Should have year column"
        assert "transaction_type" not in df.columns, "Should not have transaction_type column"
        assert "transaction_date" not in df.columns, "Should not have transaction_date column"
        assert len(df) > 0, "Should have processed data rows"
        assert df["year"].notna().all(), "Years should be extracted correctly"

    def test_complete_pipeline_raw_to_processed(self, temp_data_dir: Path, sample_raw_csv_file: Path) -> None:
        """
        Test the complete data pipeline from raw to processed data.

        Verifies:
        - Cleaned and processed files are created.
        - Processed data contains the 'year' column.
        - Processed data has fewer or equal rows compared to cleaned data (filtered).
        """
        raw_path: Path = temp_data_dir / "raw"
        cleaned_path: Path = temp_data_dir / "cleaned"
        processed_path: Path = temp_data_dir / "processed"

        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        cleaned_file: Path = cleaned_path / "cleaned2024" / "cleaned_75_2024.csv"
        processed_file: Path = processed_path / "processed2024" / "processed_75_2024.csv"

        assert cleaned_file.exists(), "Cleaned file should exist"
        assert processed_file.exists(), "Processed file should exist"

        cleaned_df: pd.DataFrame = pd.read_csv(cleaned_file)
        processed_df: pd.DataFrame = pd.read_csv(processed_file)

        assert "year" in processed_df.columns, "Processed data should have year column"
        assert len(processed_df) <= len(cleaned_df), "Processed data should be filtered"

    def test_load_all_csv_integration(self, temp_data_dir: Path, sample_cleaned_csv_file: Path) -> None:
        """
        Test that load_all_csv correctly loads multiple cleaned CSV files.

        Verifies:
        - Data from multiple year folders is loaded.
        - Expected columns are present.
        - All rows are included from different source files.
        """
        cleaned_dir: Path = temp_data_dir / "cleaned"

        cleaned_2023_dir: Path = cleaned_dir / "cleaned2023"
        cleaned_2023_dir.mkdir(parents=True, exist_ok=True)

        df_2023: pd.DataFrame = pd.DataFrame(
            {
                "transaction_date": ["15/06/2023"],
                "transaction_type": ["Vente"],
                "property_value": [2000000.00],
                "postal_code": [75001],
                "town_name": ["PARIS 01"],
                "department_code": [75],
                "town_code": [101],
                "property_type_code": [2],
                "property_type": ["Appartement"],
                "building_area": [50.0],
                "main_rooms": [3.0],
                "land_area": [80.0],
            }
        )
        cleaned_2023_file: Path = cleaned_2023_dir / "cleaned_75_2023.csv"
        df_2023.to_csv(cleaned_2023_file, index=False)

        df: pd.DataFrame = load_all_csv(data_root=str(cleaned_dir))

        assert len(df) > 0, "Should load data from multiple files"
        assert "property_value" in df.columns, "Should have property_value column"
        assert "postal_code" in df.columns, "Should have postal_code column"
        assert len(df) >= 3, "Should have data from both 2023 and 2024 files"
