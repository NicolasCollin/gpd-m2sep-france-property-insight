import re
from pathlib import Path

import pandas as pd

from fpi.data_pipeline.schemas import PropertyData


def clean_data(raw_path: Path | str = "data/raw", cleaned_path: Path | str = "data/cleaned") -> None:
    """
    Clean and standardize all CSV files found under a raw data directory.

    This function processes all CSV files whose filenames start with "raw_" under the given
    `raw_path` (recursively), cleans their content, and saves standardized versions under
    `cleaned_path`, preserving a year-based folder structure.

    Steps performed:
        1. Traverse all CSV files under `raw_path` recursively (including subfolders).
        2. Convert all column names to lowercase.
        3. Keep only a predefined set of relevant columns.
        4. Rename columns into English equivalents.
        5. Drop rows with missing values and duplicates.
        6. Remove decimals:
            * Round values in `property_value` by removing everything after the comma
              (e.g., "1350000,50" → "1350000").
            * Remove useless trailing ".0" in numeric columns (e.g., 75002.0 → 75002).
        7. Save cleaned files to `cleaned_path` under year-based folders (e.g., `cleaned2024/cleaned_2024.csv`).

    Args:
        raw_path (Path | str):
            Path to the root directory containing raw CSV files.
            Must include subfolders and files named like "raw_2024.csv".
            Default is "data/raw".

        cleaned_path (Path | str):
            Path to the output directory where cleaned files will be saved.
            Default is "data/cleaned".

    Output:
        - For each raw CSV file found, a cleaned version is created and saved under:
          `cleaned_path/cleanedYYYY/cleaned_<original_filename>.csv`

    Notes:
        - The function does not return a DataFrame; it writes cleaned CSVs directly to disk.

    Example:
        Suppose the raw CSV "raw_2024.csv" contains the following row:
        raw_line = "05/01/2024,Vente,\"1350000,50\",75020.0,PARIS 20,75,120,4.0,Appartement,44.0,2.0,69.0"

        After cleaning, the output line will look like:
        cleaned_line = "05/01/2024,Vente,1350000,75020,PARIS 20,75,120,4,Appartement,44,2,69"
    """

    rename_dict: dict[str, str] = {
        "date_mutation": "transaction_date",
        "nature_mutation": "transaction_type",
        "valeur_fonciere": "property_value",
        "code_postal": "postal_code",
        "commune": "town_name",
        "code_departement": "department_code",
        "code_commune": "town_code",
        "code_type_local": "property_type_code",
        "type_local": "property_type",
        "surface_reelle_bati": "building_area",
        "nombre_pieces_principales": "main_rooms",
        "surface_terrain": "land_area",
    }

    raw_path_obj = Path(raw_path)
    cleaned_path_obj = Path(cleaned_path)

    all_files = list(raw_path_obj.rglob("raw_*.csv"))
    if not all_files:
        print("No CSV files found in the raw folder.")
        return

    for file_path in all_files:
        print(f"\nProcessing file: {file_path}")

        df = pd.read_csv(file_path, sep=",", low_memory=False)
        n_before = df.shape[0]

        # Normalize and rename columns
        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=rename_dict)

        # Keep only relevant columns
        cols_to_keep = [v for v in rename_dict.values() if v in df.columns]
        df = df[cols_to_keep]

        # Drop NA and duplicates
        df = df.dropna().drop_duplicates()
        n_after = df.shape[0]

        # Clean up decimals
        for col in df.columns:
            if col == "property_value":
                # Remove all decimals (anything after a comma)
                df[col] = df[col].astype(str).str.replace(r",\d+", "", regex=True).str.strip()
            else:
                # Remove ".0" endings in numeric-like columns
                df[col] = df[col].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

        # Validate each row using Pydantic schema PropertyData
        def is_valid_row(row):
            try:
                PropertyData(**row.to_dict())
                return True
            except Exception:
                return False

        df = df[df.apply(is_valid_row, axis=1)].reset_index(drop=True)

        # Extract year from filename
        match = re.search(r"(\d{4})\.csv$", file_path.name)
        year = match.group(1) if match else "unknown_year"

        # Create output directory
        save_dir = cleaned_path_obj / f"cleaned{year}"
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save cleaned CSV
        output_file = save_dir / file_path.name.replace("raw_", "cleaned_")
        df.to_csv(output_file, index=False)

        print(f"Cleaned file saved: {output_file}")
        print(f"Rows before cleaning: {n_before}, after cleaning: {n_after}")

    print(f"\nAll files have been cleaned and saved to {cleaned_path_obj}")
