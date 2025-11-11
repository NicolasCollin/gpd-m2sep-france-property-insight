"""
Integration tests for data pipeline components.

These tests verify that multiple data pipeline components work together correctly.
"""

import sqlite3

import pandas as pd

from fpi.data_pipeline.clean_data import clean_data
from fpi.data_pipeline.loader import load_all_csv
from fpi.data_pipeline.process_data import process_data
from fpi.data_pipeline.txt_to_sqlite import txt_to_sqlite


class TestDataPipelineIntegration:
    """Integration tests for the complete data pipeline."""

    def test_text_to_sqlite_pipeline(self, temp_data_dir, sample_text_file):
        """Test that text file can be converted to SQLite database."""
        # Arrange
        db_path = temp_data_dir / "test.db"
        table_name = "test_table"

        # Act
        txt_to_sqlite(
            txt_path=sample_text_file,
            db_path=db_path,
            table_name=table_name,
            delimiter="|",
            chunksize=10,
        )

        # Assert
        assert db_path.exists(), "Database file should be created"

        # Verify database contents
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        assert cursor.fetchone() is not None, "Table should exist"

        # Check data was inserted
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        assert len(df) == 2, "Should have 2 data rows"
        assert "Column_Name_1" in df.columns, "Column names should be cleaned"
        assert "Column_Name_2" in df.columns, "Column names should be cleaned"
        assert "Column_Name_3" in df.columns, "Column names should be cleaned"

        conn.close()

    def test_clean_data_pipeline(self, temp_data_dir, sample_raw_csv_file):
        """Test that raw data can be cleaned correctly."""
        # Arrange
        raw_path = temp_data_dir / "raw"
        cleaned_path = temp_data_dir / "cleaned"

        # Act
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)

        # Assert
        cleaned_file = cleaned_path / "cleaned2024" / "cleaned_75_2024.csv"
        assert cleaned_file.exists(), "Cleaned file should be created"

        # Verify cleaned data structure
        df = pd.read_csv(cleaned_file)
        assert "transaction_date" in df.columns, "Should have transaction_date column"
        assert "property_value" in df.columns, "Should have property_value column"
        assert "postal_code" in df.columns, "Should have postal_code column"
        assert len(df) > 0, "Should have data rows"

        # Verify no missing values in key columns
        assert df["property_value"].notna().all(), "Property values should not be null"
        assert df["postal_code"].notna().all(), "Postal codes should not be null"

    def test_process_data_pipeline(self, temp_data_dir, sample_cleaned_csv_file):
        """Test that cleaned data can be processed correctly."""
        # Arrange
        cleaned_path = temp_data_dir / "cleaned"
        processed_path = temp_data_dir / "processed"

        # Act
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        # Assert
        processed_file = processed_path / "processed2024" / "processed_75_2024.csv"
        assert processed_file.exists(), "Processed file should be created"

        # Verify processed data structure
        df = pd.read_csv(processed_file)
        assert "year" in df.columns, "Should have year column"
        assert "transaction_type" not in df.columns, "Should not have transaction_type column"
        assert "transaction_date" not in df.columns, "Should not have transaction_date column"

        # Verify only "Vente" transactions are kept
        # (This is handled in process_data, so all rows should be "Vente")
        assert len(df) > 0, "Should have processed data rows"
        assert df["year"].notna().all(), "Years should be extracted correctly"

    def test_complete_pipeline_raw_to_processed(self, temp_data_dir, sample_raw_csv_file):
        """Test complete pipeline: raw -> cleaned -> processed."""
        # Arrange
        raw_path = temp_data_dir / "raw"
        cleaned_path = temp_data_dir / "cleaned"
        processed_path = temp_data_dir / "processed"

        # Act - Step 1: Clean data
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)

        # Act - Step 2: Process data
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        # Assert - Verify cleaned file exists
        cleaned_file = cleaned_path / "cleaned2024" / "cleaned_75_2024.csv"
        assert cleaned_file.exists(), "Cleaned file should exist"

        # Assert - Verify processed file exists
        processed_file = processed_path / "processed2024" / "processed_75_2024.csv"
        assert processed_file.exists(), "Processed file should exist"

        # Assert - Verify data flow
        cleaned_df = pd.read_csv(cleaned_file)
        processed_df = pd.read_csv(processed_file)

        # Processed data should have year column
        assert "year" in processed_df.columns, "Processed data should have year column"

        # Processed data should have fewer or equal rows (filtered for "Vente")
        assert len(processed_df) <= len(cleaned_df), "Processed data should be filtered"

    def test_load_all_csv_integration(self, temp_data_dir, sample_cleaned_csv_file):
        """Test that load_all_csv correctly loads multiple cleaned files."""
        # Arrange - Create multiple cleaned files
        cleaned_dir = temp_data_dir / "cleaned"

        # Create another year folder
        cleaned_2023_dir = cleaned_dir / "cleaned2023"
        cleaned_2023_dir.mkdir(parents=True, exist_ok=True)

        # Create a file for 2023 using pandas (matches actual pipeline output)
        df_2023 = pd.DataFrame(
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
        cleaned_2023_file = cleaned_2023_dir / "cleaned_75_2023.csv"
        df_2023.to_csv(cleaned_2023_file, index=False)

        # Act
        df = load_all_csv(data_root=str(cleaned_dir))

        # Assert
        assert len(df) > 0, "Should load data from multiple files"
        assert "property_value" in df.columns, "Should have property_value column"
        assert "postal_code" in df.columns, "Should have postal_code column"

        # Verify data from both years is present
        assert len(df) >= 3, "Should have data from both 2023 and 2024 files"
