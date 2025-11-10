import re
from pathlib import Path

import pandas as pd


def process_data(cleaned_path: Path | str = "data/cleaned", processed_path: Path | str = "data/processed") -> None:
    """
    Process cleaned CSV files to extract useful columns and prepare data for analysis.

    Steps:
    1. Traverse all cleaned CSV files recursively under cleaned_path.
    2. Extract the year from 'transaction_date' (format DD/MM/YYYY) into a new column 'year'.
    3. Keep only rows where 'transaction_type' == 'Vente'.
    4. Drop columns: 'transaction_date', 'transaction_type', 'town_code', and 'property_type_code'.
    5. Save processed files under processed_path with a similar folder structure (e.g., processed2021/processed_data_2021.csv).

    Args:
        - cleaned_path (Path | str): Directory containing cleaned CSV files (default: "data/cleaned").
        - processed_path (Path | str): Directory where processed CSV files will be saved (default: "data/processed").
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
        print(f"Rows before filtering: {n_before}, after processing: {n_after}")

    print(f"\nAll files have been processed and saved to {processed_path_obj}")
