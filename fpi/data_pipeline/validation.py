"""
This script validates cleaned DVF (Demande de Valeur Foncière) CSV files for structural and value correctness.

Usage:
------
- To validate all cleaned CSV files under the `data/cleaned/` directory, run:
      uv run validation
- To validate a specific cleaned CSV file, run:
      uv run validation --input path/to/your_cleaned_file.csv

Results:
--------
- Validation results are saved under `data/processed/`, mirroring the directory structure of `data/cleaned/`.
- For each dataset, two files are generated:
    - `<name>.valid.csv`   : All rows that pass validation.
    - `<name>.invalid.csv` : Rows that fail validation, with columns indicating the errors.
"""

import argparse
from collections.abc import Iterable
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from fpi.data_pipeline.schemas import PropertyData
from fpi.utils.constants import CLEANED_DATA, PROCESSED_DATA


def _compute_output_dir(csv_path: Path, cleaned_data: Path = CLEANED_DATA) -> Path:
    try:
        rel = csv_path.resolve().relative_to(CLEANED_DATA.resolve())
        return (PROCESSED_DATA / rel.parent).resolve()
    except Exception:
        return PROCESSED_DATA.resolve()


def _iter_csv_files(root: Path) -> Iterable[Path]:
    yield from root.rglob("*.csv")


def validate_csv(
    csv_path: str | Path,
    save_invalid: bool = True,
    cleaned_data: Path = CLEANED_DATA,
) -> tuple[list["PropertyData"], int, int]:
    csv_path_obj: Path = Path(csv_path)
    print(f"\nValidating file: {csv_path_obj.resolve()}")

    df: pd.DataFrame = pd.read_csv(csv_path_obj, sep=",", low_memory=False)
    PROCESSED_DATA.mkdir(parents=True, exist_ok=True)

    out_dir: Path = _compute_output_dir(Path(csv_path_obj), cleaned_data=CLEANED_DATA)
    out_dir.mkdir(parents=True, exist_ok=True)

    valid_rows: list["PropertyData"] = []
    valid_payloads: list[dict] = []
    invalid_entries: list[dict] = []

    for i, row in df.iterrows():
        row_dict: dict = row.to_dict()
        try:
            record: "PropertyData" = PropertyData(**row_dict)
            valid_rows.append(record)
            valid_payloads.append(row_dict)
        except ValidationError as e:
            error_columns: list[str] = [str(err["loc"][0]) for err in e.errors()]
            invalid_entries.append({**row_dict, "error_columns": error_columns})
            print(f"  • error at row {i}: {', '.join(error_columns)}")

    total_rows: int = len(df)
    valid_count: int = len(valid_rows)
    error_count: int = total_rows - valid_count
    base = csv_path_obj.stem
    print(f"⇒ {base}: {valid_count}/{total_rows} valid, {error_count} error(s)")

    if save_invalid:
        if valid_payloads:
            valid_out: Path = out_dir / f"{base}.valid.csv"
            pd.DataFrame(valid_payloads).to_csv(valid_out, index=False)
            print(f"   ✓ valid rows  → {valid_out.resolve()}")
        if invalid_entries:
            invalid_out: Path = out_dir / f"{base}.invalid.csv"
            pd.DataFrame(invalid_entries).to_csv(invalid_out, index=False)
            print(f"   ✗ invalid rows → {invalid_out.resolve()}")

    return valid_rows, total_rows, error_count


def validate_all_cleaned(
    root_dir: str | Path = "data/cleaned", save_invalid: bool = True
) -> list[tuple[Path, int, int]]:
    root = Path(root_dir)
    if not root.exists():
        print(f"[warn] Cleaned root does not exist: {root.resolve()}")
        return []

    summaries: list[tuple[Path, int, int]] = []
    for csv_file in _iter_csv_files(root):
        valid_rows, total_rows, error_count = validate_csv(csv_file, save_invalid=save_invalid, cleaned_data=root)
        summaries.append((csv_file, len(valid_rows), error_count))

    print("\nSummary:")
    for path, valid_count, error_count in summaries:
        total = valid_count + error_count
        print(f"  - {path}: {valid_count}/{total} valid, {error_count} error(s)")
    return summaries


def main() -> None:
    """
    CLI entry-point.

    Usage
    -----
    - Validate a single file:
        uv run validation --input data/cleaned/cleaned2024/cleaned_75_2024.csv

    - Validate *all* cleaned files under `data/cleaned/`:
        uv run validation
    """
    parser = argparse.ArgumentParser(description="Validate cleaned DVF CSV files.")
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Path to a specific cleaned CSV file. If omitted, validate all under data/cleaned/.",
    )
    parser.add_argument(
        "--no-save-invalid",
        action="store_true",
        help="Do not write `<name>.invalid.csv` files next to inputs.",
    )
    parser.add_argument(
        "--root",
        type=str,
        default="data/cleaned",
        help="Root directory for bulk validation (default: data/cleaned).",
    )
    args = parser.parse_args()

    if args.input:
        valid_rows, total_rows, error_count = validate_csv(
            Path(args.input),
            save_invalid=not args.no_save_invalid,
            cleaned_data=Path(args.root),
        )
        print(f"\nDone. File total: {total_rows}, valid: {len(valid_rows)}, errors: {error_count}")
    else:
        validate_all_cleaned(Path(args.root), save_invalid=not args.no_save_invalid)
