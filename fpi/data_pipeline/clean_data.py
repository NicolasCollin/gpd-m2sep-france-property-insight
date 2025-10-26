import pandas as pd
from pathlib import Path
import re
from typing import Dict, List


def clean_data(raw_path: str | Path = "data", cleaned_path: str | Path = "data/cleaned") -> None:
    """
    Clean and standardize all CSV files found under a raw data directory.

    This function traverses the given `raw_path` recursively (=including all subfolders), finds all CSV files
    whose names start with "raw_", applies a series of cleaning operations, and saves
    the results in `cleaned_path`, preserving a year-based folder structure.

    Steps:
    1. Traverse all CSV files under raw_path recursively (=including subfolders).
    2. Convert all column names to lowercase.
    3. Keep only predefined relevant columns.
    4. Rename columns to English equivalents.
    5. Remove rows with missing values and duplicates.
    6. Save cleaned files to cleaned_path with the same structure as raw_path.

    Args:
        - raw_path (str | Path): 
            Path to the directory containing raw CSV files (default: `"data"`).
        - cleaned_path (str | Path): 
            Path to the directory where cleaned CSV files will be saved (default: `"data/cleaned"`).
    
    Returns:
        - None

    Output:
        - Cleaned CSV files saved under `cleaned_path` in subfolders (e.g., `cleaned2021/cleaned_data_2021.csv`).
    """

    rename_dict: Dict[str, str] = {
        "valeur_fonciere": "property_value",
        "code_postal": "postal_code",
        "code_departement": "department_code",
        "code_commune": "town_code",
        "code_type_local": "property_type_code",
        "surface_reelle_bati": "building_area",
        "nombre_pieces_principales": "main_rooms",
        "surface_terrain": "land_area",
    }

    keep_cols: List[str] = list(rename_dict.keys())

    raw_path: Path = Path(raw_path)
    cleaned_path: Path = Path(cleaned_path)

    # Find all raw CSV files
    all_files: List[Path] = list(raw_path.rglob("raw_*.csv"))
    if not all_files:
        print("No CSV files found in the raw folder.")
        return
    
    for file_path in all_files:
        print(f"\nProcessing file: {file_path}")

        df: pd.DataFrame = pd.read_csv(file_path, sep=",", low_memory=False)
        # Count number of rows in each file before cleaning
        n_before: int = df.shape[0]

        # Rename columns to lowercase
        df.columns = df.columns.str.lower().str.strip()

        # Rename columns to English 
        df = df.rename(columns=rename_dict)

        # Keep only translated columns
        cols_to_keep: List[str] = [v for v in rename_dict.values() if v in df.columns]
        df = df[[col for col in cols_to_keep if col in df.columns]]

        # Drop NA and duplicates
        df = df.dropna()
        df = df.drop_duplicates()
        # Count how many rows are kept after cleaning
        n_after: int = df.shape[0]

        # Extract year robustly
        match: re.Match[str] | None = re.search(r'(\d{4})\.csv$', file_path.name)
        year: str = match.group(1) if match else "unknown_year"

        save_dir: Path = cleaned_path / f"cleaned{year}"
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save cleaned CSV
        output_file: Path = save_dir / file_path.name.replace("raw_", "cleaned_")
        df.to_csv(output_file, index=False)

        print(f"Cleaned file saved: {output_file}")
        print(f"Rows before cleaning: {n_before}, after cleaning: {n_after}")

    print(f"\nAll files have been cleaned and saved to {cleaned_path}")


if __name__ == "__main__":
    clean_data()
