import re
from pathlib import Path
from typing import Dict, List

import pandas as pd


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

    # Convert to Path objects (type narrowing for mypy)
    raw_path_obj: Path = Path(raw_path)
    cleaned_path_obj: Path = Path(cleaned_path)

    # Find all raw CSV files
    all_files: List[Path] = list(raw_path_obj.rglob("raw_*.csv"))
    if not all_files:
        print("No CSV files found in the raw folder.")
        return

    for file_path in all_files:
        print(f"\nProcessing file: {file_path}")

        df: pd.DataFrame = pd.read_csv(file_path, sep=",", low_memory=False)
        n_before: int = df.shape[0]

        # Normalize and rename columns
        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=rename_dict)

        # Keep only relevant columns
        cols_to_keep: List[str] = [v for v in rename_dict.values() if v in df.columns]
        df = df[cols_to_keep]

        # Drop NA and duplicates
        df = df.dropna().drop_duplicates()
        n_after: int = df.shape[0]

        # Extract year from filename (e.g., raw_2023.csv)
        match: re.Match[str] | None = re.search(r"(\d{4})\.csv$", file_path.name)
        year: str = match.group(1) if match else "unknown_year"

        # Create output directory
        save_dir: Path = cleaned_path_obj / f"cleaned{year}"
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save cleaned CSV
        output_file: Path = save_dir / file_path.name.replace("raw_", "cleaned_")
        df.to_csv(output_file, index=False)

        print(f"Cleaned file saved: {output_file}")
        print(f"Rows before cleaning: {n_before}, after cleaning: {n_after}")

    print(f"\nAll files have been cleaned and saved to {cleaned_path_obj}")


if __name__ == "__main__":
    clean_data()
