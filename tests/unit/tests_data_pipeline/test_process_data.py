from pathlib import Path

import pandas as pd

from fpi.data_pipeline.process_data import process_data


class TestProcessData:
    """
    Integration tests for the `process_data` function.

    Directly tests `process_data()` end-to-end with the correct folder structure:
    - CSV discovery in cleaned/cleanedYYYY
    - Year extraction
    - Filtering for transaction_type "Vente"
    - Dropping unwanted columns
    - Saving output in processed/processedYYYY with filenames like processed_75_2021.csv
    """

    def test_process_data_creates_processed_file(self, tmp_path: Path) -> None:
        # Setup: create a cleaned CSV file in the correct structure
        cleaned_dir: Path = tmp_path / "data" / "cleaned" / "cleaned2021"
        cleaned_dir.mkdir(parents=True)
        input_file: Path = cleaned_dir / "cleaned_75_2021.csv"  # matches your naming convention

        df: pd.DataFrame = pd.DataFrame(
            {
                "transaction_date": ["15/03/2021", "20/04/2021", None],
                "transaction_type": ["Vente", "Echange", "Vente"],
                "property_value": [250000, 300000, 275000],
                "town_code": ["12345", "12345", "99999"],
                "property_type_code": ["1", "2", "1"],
            }
        )
        df.to_csv(input_file, index=False)

        # Run process_data directly
        process_data(cleaned_path=tmp_path / "data/cleaned", processed_path=tmp_path / "data/processed")

        # Verify processed folder exists
        processed_dir: Path = tmp_path / "data" / "processed" / "processed2021"
        assert processed_dir.exists(), "Processed folder not created"

        # Verify processed CSV file exists with exact naming pattern
        processed_files: list[Path] = list(processed_dir.glob("processed_??_2021.csv"))
        assert processed_files, "No processed CSV was created"
        output_file: Path = processed_files[0]

        # Verify contents
        processed_df: pd.DataFrame = pd.read_csv(output_file)

        # Only rows with transaction_type 'Vente' and valid dates remain
        n_rows: int = processed_df.shape[0]
        assert n_rows == 1
        value: int = processed_df["property_value"].iloc[0]
        year: int = processed_df["year"].iloc[0]
        assert value == 250000
        assert year == 2021

        # Dropped columns are removed
        dropped_cols: list[str] = ["transaction_date", "transaction_type", "town_code", "property_type_code"]
        for col in dropped_cols:
            assert col not in processed_df.columns
