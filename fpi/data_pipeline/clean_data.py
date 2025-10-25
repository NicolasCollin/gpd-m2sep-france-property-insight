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
    3. Keep only predefined columns.
    4. Remove rows with missing values and duplicates.
    5. Save cleaned files to cleaned_path with the same folder structure as raw_path.

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

    # --- Columns to keep ---
    keep_cols = [ "valeur_fonciere",
                 "code_postal", 
                 "code_departement",
                 "code_commune",
                 "code_type_local",
                 "surface_reelle_bati",
                 "nombre_pieces_principales",
                 "surface_terrain"
                 #  "nature_mutation",
                 #  "type_local",
                 #  "nombre_de_lots",
                 #  "no_voie",
                 #  "b/t/q",
                 #  "type_de_voie",
    ]

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

        # Keep only selected columns
        cols_to_keep = [col for col in keep_cols if col in df.columns]
        df = df[cols_to_keep]

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
