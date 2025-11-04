from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, field_validator


class PropertyData(BaseModel):
    """
    Structured record for a *cleaned* DVF row.

    Each attribute maps 1‑to‑1 to a column name present in our **cleaned CSV**
    files. Constraints are intentionally light but meaningful for a university
    project: positivity/non‑negativity, plausible code ranges, and robust
    parsing of European number formats.

    Fields
    ------
    property_value : float
        Property sale price (must be strictly positive).
    postal_code : int
        French postal code (kept as 5‑digit range; overseas allowed).
    department_code : int
        Department numeric code in [1, 976].
    town_code : int
        Positive municipality code.
    property_type_code : int
        DVF property type code, expected in [1, 4].
    building_area : float
        Built area in m², non‑negative.
    main_rooms : float
        Number of main rooms, non‑negative.
    land_area : float
        Land area in m², non‑negative.
    """

    # --- Core schema (column names follow the *cleaned* dataset) ---
    property_value: float = Field(..., gt=0)
    postal_code: int = Field(..., ge=1000, le=99999)
    department_code: int = Field(..., ge=1, le=976)
    town_code: int = Field(..., gt=0)
    property_type_code: int = Field(..., ge=1, le=4)
    building_area: float = Field(..., ge=0)
    main_rooms: float = Field(..., ge=0)
    land_area: float = Field(..., ge=0)

    # ---------------------- Robust parsers (light “test” hardening) ----------------------
    @staticmethod
    def _to_float_eu(v: Any) -> float:
        """Parse floats that may use European comma decimals or come as numbers/strings."""
        if v is None or (isinstance(v, float) and pd.isna(v)):
            raise ValueError("Missing numeric value")
        if isinstance(v, str):
            v = v.replace(",", ".").strip()
        return float(v)

    @field_validator("property_value", "building_area", "main_rooms", "land_area", mode="before")
    def parse_float_fields(cls, v: Any) -> float:
        """Accept '200000,00' or '15,5' and coerce to float before constraints apply."""
        return cls._to_float_eu(v)

    @field_validator("postal_code", "department_code", "town_code", "property_type_code", mode="before")
    def parse_int_fields(cls, v: Any) -> int:
        """
        Coerce numeric codes that may arrive as floats (e.g., 75001.0) or strings.
        Keeps semantics strict: empty values still fail validation upstream.
        """
        if isinstance(v, float) and not pd.isna(v):
            return int(v)
        if isinstance(v, str):
            v = v.strip()
            if v.endswith(".0"):
                v = v[:-2]
        return int(v)

    @field_validator("property_type_code")
    def property_type_in_known_range(cls, v: int) -> int:
        """Tiny extra guard that also serves as a test target."""
        if v not in {1, 2, 3, 4}:
            raise ValueError("property_type_code must be one of {1,2,3,4}")
        return v


def _iter_csv_files(root: Path) -> Iterable[Path]:
    """Yield all `.csv` files under `root` recursively (depth‑first)."""
    yield from root.rglob("*.csv")


def validate_csv(csv_path: str | Path, save_invalid: bool = True) -> List[PropertyData]:
    """
    Validate all rows of a **single cleaned CSV** file using the PropertyData model.

    - Parses European decimals in numeric fields.
    - Coerces integer codes that may be stored as floats/strings.
    - Collects invalid rows with offending columns for quick triage.

    Parameters
    ----------
    csv_path : str | Path
        Path to the input CSV file to validate.
    save_invalid : bool, default True
        If True, write invalid rows next to the CSV as `<name>.invalid.csv`.

    Returns
    -------
    List[PropertyData]
        All valid rows converted to `PropertyData` instances.
    """
    csv_path_obj: Path = Path(csv_path)
    print(f"\nValidating file: {csv_path_obj.resolve()}")

    df: pd.DataFrame = pd.read_csv(csv_path_obj, sep=",", low_memory=False)
    valid_rows: List[PropertyData] = []
    invalid_entries: List[Dict[str, Any]] = []

    for i, row in df.iterrows():
        row_dict: Dict[str, Any] = row.to_dict()
        try:
            record: PropertyData = PropertyData(**row_dict)  # strict on *cleaned* column names
            valid_rows.append(record)
        except ValidationError as e:
            # Gather which columns failed (helps users fix the source file)
            error_columns: List[str] = [str(err["loc"][0]) for err in e.errors()]
            invalid_entries.append({**row_dict, "error_columns": error_columns})
            print(f"- Row {i} invalid: {', '.join(error_columns)}")

    total_rows: int = len(df)
    valid_count: int = len(valid_rows)
    print(f"→ {valid_count}/{total_rows} rows successfully validated.")

    if save_invalid and invalid_entries:
        out_path: Path = csv_path_obj.with_suffix(".invalid.csv")
        pd.DataFrame(invalid_entries).to_csv(out_path, index=False)
        print(f"✎ Invalid rows saved to: {out_path.resolve()}")

    return valid_rows


def validate_all_cleaned(
    root_dir: str | Path = "data/cleaned", save_invalid: bool = True
) -> List[Tuple[Path, int, int]]:
    """
    Validate **all CSV files** found recursively under `data/cleaned/`.

    Returns a compact summary per file to keep CI logs readable.

    Parameters
    ----------
    root_dir : str | Path
        Root directory that contains cleaned CSVs (defaults to `data/cleaned`).
    save_invalid : bool, default True
        Whether to write `<name>.invalid.csv` alongside each file with errors.

    Returns
    -------
    List[Tuple[Path, int, int]]
        A list of `(file_path, valid_count, total_count)` tuples.
    """
    root = Path(root_dir)
    if not root.exists():
        print(f"[warn] Cleaned root does not exist: {root.resolve()}")
        return []

    summaries: List[Tuple[Path, int, int]] = []
    for csv_file in _iter_csv_files(root):
        valid_rows = validate_csv(csv_file, save_invalid=save_invalid)
        summaries.append(
            (
                csv_file,
                len(valid_rows),
                sum(1 for _ in pd.read_csv(csv_file, chunksize=10_000)) * 10_000 if csv_file.exists() else 0,
            )
        )
    # Pretty print short recap
    print("\nSummary:")
    for path, valid_count, _ in summaries:
        print(f"  - {path}: {valid_count} valid rows")
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
        validate_csv(Path(args.input), save_invalid=not args.no_save_invalid)
    else:
        validate_all_cleaned(Path(args.root), save_invalid=not args.no_save_invalid)


if __name__ == "__main__":
    main()
