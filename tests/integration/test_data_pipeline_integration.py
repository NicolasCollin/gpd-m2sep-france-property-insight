from pathlib import Path

import pandas as pd

from fpi.data_pipeline.clean_data import clean_data
from fpi.data_pipeline.load_all_csv import load_all_csv
from fpi.data_pipeline.process_data import process_data


class TestDataPipelineIntegration:
    """
    Minimal integration tests for the end-to-end data pipeline.

    Scenarios tested:
    1. Full pipeline execution from raw CSV to processed output.
       - Ensures the pipeline runs without crashing.
       - Checks that cleaned and processed output directories and files are created.
       - Validates that the processed DataFrame is non-empty and contains the 'year' column.
    2. Loading multiple cleaned CSV files using `load_all_csv`.
       - Ensures data from multiple year folders is loaded correctly.
       - Validates that the combined DataFrame is non-empty and contains key columns like 'property_value' and 'postal_code'.
    """

    def test_pipeline_runs_end_to_end(self, temp_data_dir: Path, sample_raw_csv_file: Path) -> None:
        """
        Test the full pipeline from raw CSV to processed output.

        Verifies:
        - Pipeline runs without crashing.
        - Output directories and processed file are created.
        - Processed DataFrame has at least some rows and key columns ('year').
        """
        raw_path: Path = temp_data_dir / "raw"
        cleaned_path: Path = temp_data_dir / "cleaned"
        processed_path: Path = temp_data_dir / "processed"

        # Run pipeline
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        # Check output directories exist
        cleaned_dir: Path = cleaned_path / "cleaned2024"
        processed_dir: Path = processed_path / "processed2024"

        assert cleaned_dir.exists(), "Cleaned directory should exist"
        assert processed_dir.exists(), "Processed directory should exist"

        # Load processed output
        processed_file: Path = processed_dir / "processed_75_2024.csv"
        df: pd.DataFrame = pd.read_csv(processed_file)

        # Basic sanity checks
        assert not df.empty, "Processed DataFrame should not be empty"
        assert "year" in df.columns, "Processed DataFrame should have 'year' column"

    def test_load_all_csv_integration(self, temp_data_dir: Path, sample_cleaned_csv_file: Path) -> None:
        """
        Test that load_all_csv can load multiple cleaned CSV files.

        Verifies:
        - Data from multiple files is loaded.
        - Output DataFrame is not empty.
        - Key columns ('property_value', 'postal_code') are present.
        """
        cleaned_dir: Path = temp_data_dir / "cleaned"

        # Create a second sample CSV to simulate multiple years
        cleaned_2023_dir: Path = cleaned_dir / "cleaned2023"
        cleaned_2023_dir.mkdir(parents=True, exist_ok=True)

        dest_file: Path = cleaned_2023_dir / "cleaned_75_2023.csv"
        sample_cleaned_csv_file.rename(dest_file)

        df: pd.DataFrame = load_all_csv(data_root=str(cleaned_dir))

        assert not df.empty, "Loaded DataFrame should not be empty"
        assert "property_value" in df.columns, "Expected column should exist"
        assert "postal_code" in df.columns, "Expected column should exist"
