from pathlib import Path

import pandas as pd

from fpi.data_pipeline.clean_data import clean_data


class TestCleanData:
    """
    Integration tests for the `clean_data` function.

    This class tests `clean_data()` end-to-end:
    - Discovery of raw_*.csv files in raw_path
    - Column normalization and renaming
    - Keeping only relevant columns
    - Dropping rows with NA and duplicates
    - Removing decimals (.0 or ,xx)
    - Saving cleaned CSVs under cleaned_path/cleanedYYYY/
    """

    def test_clean_data_creates_cleaned_file(self, tmp_path: Path) -> None:
        # Setup: create a raw CSV file in temporary directory
        raw_dir: Path = tmp_path / "data" / "raw"
        raw_dir.mkdir(parents=True)
        input_file: Path = raw_dir / "raw_75_2021.csv"

        # Sample raw data simulating minimal realistic input
        df: pd.DataFrame = pd.DataFrame(
            {
                "DATE_MUTATION": ["15/03/2021", "20/04/2021", None],
                "NATURE_MUTATION": ["Vente", "Echange", "Vente"],
                "VALEUR_FONCIERE": ["250000,00", "300000,50", "275000,00"],  # includes commas and decimals
                "CODE_POSTAL": [75001.0, 75002.0, 75003.0],  # decimals that should disappear
                "COMMUNE": ["Paris", "Paris", "Paris"],
                "CODE_DEPARTEMENT": ["75", "75", "75"],
                "CODE_COMMUNE": ["101", "102", "103"],
                "CODE_TYPE_LOCAL": [2.0, 2.0, 1.0],
                "TYPE_LOCAL": ["Appartement", "Appartement", "Maison"],
                "SURFACE_REELLE_BATI": [44.0, 52.0, 120.0],
                "NOMBRE_PIECES_PRINCIPALES": [2.0, 3.0, 5.0],
                "SURFACE_TERRAIN": [69.0, 0.0, 240.0],
                "EXTRA_COL": ["remove", "remove", "remove"],  # to be dropped
            }
        )
        df.to_csv(input_file, index=False)

        # Run cleaning
        clean_data(raw_path=tmp_path / "data/raw", cleaned_path=tmp_path / "data/cleaned")

        # Verify output directory structure
        cleaned_dir: Path = tmp_path / "data" / "cleaned" / "cleaned2021"
        assert cleaned_dir.exists(), "Cleaned folder was not created"

        # Check that a cleaned CSV exists
        cleaned_files: list[Path] = list(cleaned_dir.glob("cleaned_75_2021.csv"))
        assert cleaned_files, "Cleaned CSV file not found"
        output_file: Path = cleaned_files[0]

        # Load cleaned data
        cleaned_df: pd.DataFrame = pd.read_csv(output_file, dtype=str)

        # Extra columns should be removed
        assert "EXTRA_COL" not in cleaned_df.columns

        # Columns should be renamed to English equivalents
        expected_cols: list[str] = [
            "transaction_date",
            "transaction_type",
            "property_value",
            "postal_code",
            "town_name",
            "department_code",
            "town_code",
            "property_type_code",
            "property_type",
            "building_area",
            "main_rooms",
            "land_area",
        ]
        for col in expected_cols:
            assert col in cleaned_df.columns, f"Missing expected column: {col}"

        # The None date row should have been removed
        assert len(cleaned_df) == 2, "Rows with missing values were not dropped"

        # Check that decimals were removed correctly
        assert cleaned_df.loc[0, "property_value"] == "250000"
        assert cleaned_df.loc[1, "property_value"] == "300000"
        assert cleaned_df.loc[0, "postal_code"] == "75001"
        assert cleaned_df.loc[0, "building_area"] == "44"
        assert cleaned_df.loc[1, "main_rooms"] == "3"

        # Check that types are strings (consistent with CSV export)
        assert cleaned_df.dtypes.eq("object").all(), "All columns should be saved as strings"
