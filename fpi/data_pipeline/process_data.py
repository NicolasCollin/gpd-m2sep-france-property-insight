import re
from pathlib import Path

import pandas as pd


def process_data(cleaned_path: Path | str = "data/cleaned", processed_path: Path | str = "data/processed") -> None:
    """
    Process all cleaned CSV files to prepare them for analysis.

    This function reads each cleaned CSV file, extracts useful information,
    and standardizes it into a consistent structure for downstream analysis.

    Steps performed:
        1. Recursively locate all files matching "cleaned_*.csv" under `cleaned_path`.
        2. Parse the year from 'transaction_date' (format DD/MM/YYYY) into a new 'year' column.
        3. Keep only rows where 'transaction_type' equals "Vente".
        4. Drop unnecessary columns: 'transaction_date', 'transaction_type', 'town_code', and 'property_type_code'.
        5. Save the processed data into `processed_path`, preserving the year-based folder structure
           (e.g., processed2021/processed_75_2021.csv).

    Args:
        cleaned_path (Path | str): Root directory containing cleaned CSV files.
        processed_path (Path | str): Output directory where processed CSV files will be stored.

    Output:
        - For each raw CSV file found, a cleaned version is created and saved under:
          `processed_path/processedYYYY/processed_<original_filename>.csv`

    Notes:
        - The function does not return a DataFrame; it writes processed CSVs directly to disk.

    Example:
        Suppose a cleaned CSV contains the following lines:

        transaction_date,transaction_type,property_value,postal_code,town_name,department_code,town_code,property_type_code,property_type,building_area,main_rooms,land_area
        12/01/2022,Vente,80000000,75008,PARIS 08,75,108,4,Local industriel. commercial ou assimilé,239,0,988
        12/01/2022,Vente,80000000,75008,PARIS 08,75,108,2,Appartement,172,4,988

        After running `process_data(cleaned_path, processed_path)`, the processed CSV will look like:

        property_value,postal_code,town_name,department_code,property_type,building_area,main_rooms,land_area,year
        80000000,75008,PARIS 08,75,Local industriel. commercial ou assimilé,239,0,988,2022
        80000000,75008,PARIS 08,75,Appartement,172,4,988,2022
    """

    cleaned_path_obj: Path = Path(cleaned_path)
    processed_path_obj: Path = Path(processed_path)

    # Find all cleaned CSV files recursively
    all_files: list[Path] = list(cleaned_path_obj.rglob("cleaned_*.csv"))
    if not all_files:
        print("No cleaned CSV files found to process.")
        return

    for file_path in all_files:
        print(f"\nProcessing file: {file_path}")

        df: pd.DataFrame = pd.read_csv(file_path, sep=",", low_memory=False)
        n_before: int = df.shape[0]

        # Ensure 'transaction_date' exists
        if "transaction_date" not in df.columns:
            print(f"Warning: 'transaction_date' column not found in {file_path.name}, skipping file.")
            continue

        # Extract year from 'transaction_date' (format DD/MM/YYYY)
        df["year"] = pd.to_datetime(df["transaction_date"], format="%d/%m/%Y", errors="coerce").dt.year

        # Keep only valid years and transactions of type 'Vente'
        df = df[df["transaction_type"].eq("Vente") & df["year"].notna()]

        # Drop unwanted columns if they exist
        cols_to_drop: list[str] = [
            "transaction_date",
            "transaction_type",
            "town_code",
            "property_type_code",
        ]
        df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

        n_after: int = df.shape[0]

        # Determine year from filename or from 'year' column
        match: re.Match[str] | None = re.search(r"(\d{4})\.csv$", file_path.name)
        year: str = match.group(1) if match else str(int(df["year"].mode()[0])) if not df.empty else "unknown_year"

        # Create output directory (e.g., processed2021)
        save_dir: Path = processed_path_obj / f"processed{year}"
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save processed CSV
        output_file: Path = save_dir / file_path.name.replace("cleaned_", "processed_")
        df.to_csv(output_file, index=False)

        print(f"Processed file saved: {output_file}")
        print(f"Rows before processing: {n_before}, after processing: {n_after}")

    print(f"\nAll files have been processed and saved to {processed_path_obj}")
