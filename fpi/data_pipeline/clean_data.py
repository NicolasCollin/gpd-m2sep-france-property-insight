import pandas as pd
from pathlib import Path
import re

def clean_data(raw_path: str = "data", cleaned_path: str = "data/cleaned") -> None:
    
    """
    Process all raw CSV files: clean and save them to the cleaned folder 
    while preserving the folder structure.

    Steps:
    1. Traverse all CSV files under raw_path (including subfolders).
    2. Convert all column names to lowercase.
    3. Keep only predefined relevant columns.
    4. Rename columns to English equivalents.
    5. Remove rows with missing values and duplicates.
    6. Save cleaned files to cleaned_path with the same structure as raw_path.

    Parameters
    ----------
    raw_path : str
        Folder containing raw CSV files.
    cleaned_path : str
        Folder where cleaned CSV files will be saved.

    
    Returns
    -------
    None
        Cleaned CSV files are saved to cleaned_path.
    """


    rename_dict = {
        "valeur_fonciere": "property_value",
        "code_postal": "postal_code",
        "code_departement": "department_code",
        "code_commune": "town_code",
        "code_type_local": "property_type_code",
        "surface_reelle_bati": "building_area",
        "nombre_pieces_principales": "main_rooms",
        "surface_terrain": "land_area"
    }

    keep_cols = list(rename_dict.keys())

    raw_path = Path(raw_path)
    cleaned_path = Path(cleaned_path)

    # Find all raw CSV files
    all_files = list(raw_path.rglob("raw_*.csv"))
    if not all_files:
        print("No CSV files found in the raw folder.")
        return
    
    for file_path in all_files:
        print(f"\nProcessing file: {file_path}")

        df = pd.read_csv(file_path, sep=",", low_memory=False)
        n_before = df.shape[0]

        # Rename columns to lowercase
        df.columns = df.columns.str.lower().str.strip()

        # Rename columns to english 
        df = df.rename(columns=rename_dict)

       # Keep only translated columns
        cols_to_keep = [rename_dict[c] for c in rename_dict if rename_dict[c] in df.columns]
        df = df[[col for col in cols_to_keep if col in df.columns]]

        # Drop NA and duplicates
        df = df.dropna()
        df = df.drop_duplicates()
        n_after = df.shape[0]

        # Extract year robustly
        match = re.search(r'(\d{4})\.csv$', file_path.name)
        year = match.group(1) if match else "unknown_year"

        save_dir = cleaned_path / f"cleaned{year}"
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save cleaned CSV
        output_file = save_dir / file_path.name.replace("raw_", "cleaned_")
        df.to_csv(output_file, index=False)

        print(f"Cleaned file saved: {output_file}")
        print(f"Rows before cleaning: {n_before}, after cleaning: {n_after}")

    print("\nAll files have been cleaned and saved to /data/cleaned/")


if __name__ == "__main__":
    clean_data()
