from pathlib import Path

import pandas as pd

from fpi.data_pipeline.clean_data import clean_data


class TestCleanData:
    """
    Integration tests for the `clean_data` function.

    This class directly tests `clean_data()` end-to-end:
    - CSV discovery in raw_path
    - Column normalization and renaming
    - Keeping only relevant columns
    - Dropping rows with NA and duplicates
    - Saving cleaned CSVs in cleaned_path/cleanedYYYY with filenames like cleaned_75_2021.csv
    """

    def test_clean_data_creates_cleaned_file(self, tmp_path: Path) -> None:
        # Setup: create a raw CSV file
        raw_dir: Path = tmp_path / "data" / "raw"
        raw_dir.mkdir(parents=True)
        input_file: Path = raw_dir / "raw_75_2021.csv"

        df: pd.DataFrame = pd.DataFrame(
            {
                "DATE_MUTATION": ["15/03/2021", "20/04/2021", None],
                "NATURE_MUTATION": ["Vente", "Echange", "Vente"],
                "VALEUR_FONCIERE": [250000, 300000, 275000],
                "CODE_POSTAL": ["75001", "75002", "75003"],
                "COMMUNE": ["Paris", "Paris", "Paris"],
                "EXTRA_COL": ["remove", "remove", "remove"],
            }
        )
        df.to_csv(input_file, index=False)

        # Run clean_data directly
        clean_data(raw_path=tmp_path / "data/raw", cleaned_path=tmp_path / "data/cleaned")

        # Verify cleaned folder exists
        cleaned_dir: Path = tmp_path / "data" / "cleaned" / "cleaned2021"
        assert cleaned_dir.exists(), "Cleaned folder not created"

        # Verify cleaned CSV file exists
        cleaned_files: list[Path] = list(cleaned_dir.glob("cleaned_??_2021.csv"))
        assert cleaned_files, "No cleaned CSV was created"
        output_file: Path = cleaned_files[0]

        # Verify contents
        cleaned_df: pd.DataFrame = pd.read_csv(output_file)

        # Extra columns should be removed
        assert "EXTRA_COL" not in cleaned_df.columns

        # Columns should be renamed to English equivalents
        expected_cols: list[str] = ["transaction_date", "transaction_type", "property_value", "postal_code", "town_name"]
        for col in expected_cols:
            assert col in cleaned_df.columns

        # Rows with NA should be removed (the last row had None date)
        n_rows: int = cleaned_df.shape[0]
        assert n_rows == 2

        # Check values
        assert cleaned_df["property_value"].iloc[0] == 250000
        assert cleaned_df["transaction_type"].iloc[0] == "Vente"
