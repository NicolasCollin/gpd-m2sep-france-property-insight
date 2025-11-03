"""
DVF Validation Utility

This module provides a simplified validation script for DVF (Demande de Valeur Foncière) data using Pydantic.
It can validate a single CSV *or* recursively validate **all** CSV files under a root directory (default: `data/`),
while **excluding** any file located under the output folder (default: `data/processed/`).

Outputs mirror the input tree under `data/processed/`: for an input `data/raw/2021/x.csv`, you get:
- `data/processed/raw/2021/x.validated.parquet`
- `data/processed/raw/2021/x.validation_errors.csv`

Main functionalities:
- Robust CSV reading with fallback encodings and separators.
- Row-wise validation with detailed error capturing.
- Output of validated data and error reports (per file).
- Command-line interface for single-file and batch modes.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd
from pydantic import ValidationError

try:
    from fpi.models.schemas_dvf import DVFRecord  # type: ignore[import-untyped]
except Exception:
    from fpi.utils.schemas_dvf import DVFRecord  # type: ignore[import-untyped]


# --- Read CSV robustly --------------------------------------------------------
def read_csv_any(path: str | Path) -> pd.DataFrame:
    """
    Attempt to read a CSV file using multiple common encodings and separators until one succeeds.

    This function tries various combinations of separators (';' and ',') and encodings ('utf-8' and 'latin-1')
    to robustly read CSV files that may come from different sources or locales.

    Parameters:
        path (str | Path): Path to the CSV file to read.

    Returns:
        pd.DataFrame: DataFrame containing the CSV data.

    Raises:
        RuntimeError: If the file cannot be read using any of the attempted combinations.
    """
    path = Path(path)
    attempts = [(";", "utf-8"), (",", "utf-8"), (";", "latin-1"), (",", "latin-1")]
    # Try each encoding and separator combination until one works
    for sep, enc in attempts:
        try:
            return pd.read_csv(path, sep=sep, encoding=enc, low_memory=False)
        except Exception:
            # Ignore and try next combination
            continue
    # If all attempts fail, raise an error indicating the file could not be read
    raise RuntimeError(f"Impossible de lire le fichier CSV : {path}")


"""
# Backward-compatibility shim for legacy imports
"""


def read_any_csv(path: str | Path) -> pd.DataFrame:
    """Legacy alias: forwards to read_csv_any for older callers."""
    return read_csv_any(path)


def validate_records(records: Iterable[dict]) -> Tuple[List[DVFRecord], pd.DataFrame]:
    """Validate an iterable of dict-like rows into DVFRecord models.
    Returns a tuple (valid_models, errors_df) with columns [row, column, message]."""
    valids: List[DVFRecord] = []
    errors: List[Dict[str, Any]] = []
    for i, rec in enumerate(records):
        try:
            valids.append(DVFRecord.model_validate(rec))
        except ValidationError as e:
            for err in e.errors():
                errors.append(
                    {
                        "row": i,
                        "column": ".".join(map(str, err.get("loc", []))),
                        "message": err.get("msg", ""),
                    }
                )
    return valids, pd.DataFrame(errors)


def validate_dataframe(df: pd.DataFrame) -> Tuple[List[DVFRecord], pd.DataFrame]:
    """Legacy convenience wrapper: DataFrame -> records -> validate_records."""
    return validate_records(df.to_dict(orient="records"))


# --- Core single-file validation ---------------------------------------------
def validate_csv(
    path: str | Path, out_valid_path: Path | None = None, out_errors_path: Path | None = None
) -> Tuple[int, int, int]:
    """
    Validate a single CSV file against the DVFRecord schema and output validated data and errors.

    This function reads the CSV file robustly, validates each row with the Pydantic model DVFRecord,
    collects validation errors with detailed information, and writes the validated data to a parquet file
    and the errors to a CSV file. Output paths default to 'data/processed' if not provided.

    Parameters:
        path (str | Path): Path to the input CSV file to validate.
        out_valid_path (Path | None): Optional path to write the validated parquet file.
        out_errors_path (Path | None): Optional path to write the validation errors CSV.

    Returns:
        Tuple[int, int, int]: A tuple containing:
            - Number of valid rows
            - Number of validation errors
            - Total number of rows processed
    """
    logger = logging.getLogger(__name__)
    start = time.perf_counter()

    # Read the CSV file robustly using multiple encoding and separator options
    df = read_csv_any(path)
    records = df.to_dict(orient="records")

    valids, errors_df = validate_records(records)

    dur = time.perf_counter() - start
    logger.info(f"Validated {len(df)} rows in {dur:.2f}s — ok={len(valids)} ko={len(errors_df)} — {path}")

    # Determine output paths, defaulting to 'data/processed' if not specified
    if out_valid_path is None or out_errors_path is None:
        base_dir = Path("data/processed")
        base_dir.mkdir(parents=True, exist_ok=True)
        out_valid_path = out_valid_path or (base_dir / "validated.parquet")
        out_errors_path = out_errors_path or (base_dir / "validation_errors.csv")

    # Ensure output directories exist
    out_valid_path.parent.mkdir(parents=True, exist_ok=True)
    out_errors_path.parent.mkdir(parents=True, exist_ok=True)

    # Write validated records to parquet using alias names from the Pydantic model
    pd.DataFrame([m.model_dump(by_alias=True) for m in valids]).to_parquet(out_valid_path, index=False)
    # Write validation errors to CSV
    errors_df.to_csv(out_errors_path, index=False)

    # Print a summary of the validation results to the console
    print("\n" + "=" * 60)
    print(f"✅ Validation terminée : {len(valids):,} valides | {len(errors_df):,} erreurs | total {len(df):,}")
    print(f"📁 Fichier valide : {out_valid_path}")
    print(f"📄 Rapport erreurs : {out_errors_path}")
    print("=" * 60 + "\n")

    return len(valids), len(errors_df), len(df)


# --- Discovery utilities ------------------------------------------------------
def find_csvs(
    root: str | Path = "data", pattern: str = "*.csv", exclude_dir: str | Path = "data/processed"
) -> List[Path]:
    """
    Recursively find CSV files under a root directory, excluding those under a specified directory.

    This function searches for CSV files matching the given pattern recursively under the root directory,
    but skips any files located within the exclude_dir directory (to avoid processing output files).

    Parameters:
        root (str | Path): Root directory to start searching from.
        pattern (str): Glob pattern to match files (default '*.csv').
        exclude_dir (str | Path): Directory to exclude from search (default 'data/processed').

    Returns:
        List[Path]: Sorted list of Path objects pointing to CSV files found.
    """
    root_p = Path(root)
    excl_p = Path(exclude_dir).resolve()
    if not root_p.exists():
        return []
    files: List[Path] = []
    for p in root_p.rglob(pattern):
        if not p.is_file():
            # Skip non-files (directories, symlinks, etc.)
            continue
        # skip files located under the exclude directory
        try:
            _ = p.resolve().relative_to(excl_p)  # If this succeeds, file is under exclude_dir
            continue  # Skip this file
        except Exception:
            # File is not under exclude_dir, include it
            pass
        files.append(p)
    return sorted(files)


# --- Batch validation ---------------------------------------------------------
def validate_all(root: str | Path = "data", exclude_dir: str | Path = "data/processed") -> pd.DataFrame:
    """
    Validate all CSV files under a root directory recursively, excluding files under exclude_dir.

    For each CSV file found, this function performs validation and writes outputs mirroring the input tree
    under the exclude_dir directory. A summary DataFrame is returned containing validation statistics per file.

    Parameters:
        root (str | Path): Root directory to scan for CSV files.
        exclude_dir (str | Path): Directory to exclude from scanning and where outputs are stored.

    Returns:
        pd.DataFrame: Summary DataFrame with columns:
            - input_csv: Path to the input CSV file
            - valid: Number of valid rows
            - errors: Number of validation errors
            - total: Total rows processed
            - out_valid: Path to the validated parquet output
            - out_errors: Path to the validation errors CSV output
    """
    inputs = find_csvs(root=root, exclude_dir=exclude_dir)
    rows: List[Dict[str, object]] = []

    for inp in inputs:
        # Compute output directory mirroring input path under exclude_dir
        rel = inp.relative_to(root)
        out_base = Path(exclude_dir) / rel.parent
        out_base.mkdir(parents=True, exist_ok=True)
        out_valid = out_base / f"{inp.stem}.validated.parquet"
        out_errors = out_base / f"{inp.stem}.validation_errors.csv"

        # Validate the CSV file and collect counts
        n_ok, n_ko, n_tot = validate_csv(inp, out_valid_path=out_valid, out_errors_path=out_errors)
        rows.append(
            {
                "input_csv": str(inp),
                "valid": n_ok,
                "errors": n_ko,
                "total": n_tot,
                "out_valid": str(out_valid),
                "out_errors": str(out_errors),
            }
        )

    summary = pd.DataFrame(rows)

    # Print a concise summary of batch validation results
    print("\n" + "=" * 60)
    print(f"🗂  Batch validation: {len(summary)} files processed.")
    if not summary.empty:
        valid_sum = int(summary["valid"].sum())
        error_sum = int(summary["errors"].sum())
        total_sum = int(summary["total"].sum())
        print(
            "✅ Total valides : " f"{valid_sum:,} | ❌ Total erreurs : {error_sum:,} | 🧮 Total lignes : {total_sum:,}"
        )
        for _, row in summary.head(15).iterrows():
            print(f" - {row['input_csv']} -> ok={row['valid']:,} ko={row['errors']:,}")
        if len(summary) > 15:
            print(f"   … and {len(summary) - 15} more files")
    print("=" * 60 + "\n")

    return summary


# --- Main CLI ----------------------------------------------------------------
if __name__ == "__main__":
    """
    Command-line interface for DVF CSV validation.

    Usage modes:

    Single-file mode:
        uv run python -m fpi.utils.validation_dvf --in data/raw/raw2021/raw_75_2021.csv

    Batch mode (recursive on `data/`, excluding `data/processed/`):
        uv run python -m fpi.utils.validation_dvf

    Custom root and exclude directory:
        uv run python -m fpi.utils.validation_dvf --root data --exclude-dir data/processed
    """
    import argparse

    parser = argparse.ArgumentParser(description="DVF validation (single or batch)")
    parser.add_argument("--in", dest="input_csv", required=False, help="Path to a single CSV file to validate")
    parser.add_argument("--root", dest="root", default="data", help="Root directory to scan for CSV files (batch mode)")
    parser.add_argument(
        "--exclude-dir", dest="exclude_dir", default="data/processed", help="Directory to exclude (usually outputs)"
    )
    parser.add_argument("--log-level", dest="log_level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()
    # Configure logging level as requested by the user
    logging.basicConfig(level=getattr(logging, args.log_level))

    if args.input_csv:
        # Single-file validation mode
        validate_csv(args.input_csv)
    else:
        # Batch validation mode over the directory tree
        validate_all(root=args.root, exclude_dir=args.exclude_dir)

# ---------------------------------------------------------------------------
# 💡 TUTORIEL D’UTILISATION RAPIDE
#
# ▶ Valider un fichier :
#     uv run python -m fpi.utils.validation_dvf --in data/raw/raw2021/raw_75_2021.csv
#
# ▶ Valider tout un dossier (récursif, en excluant data/processed) :
#     uv run python -m fpi.utils.validation_dvf
#     # Options : --root data  --exclude-dir data/processed
#
# ▶ Sorties (par fichier) :
#     - data/processed/<same tree>/<name>.validated.parquet
#     - data/processed/<same tree>/<name>.validation_errors.csv
#
# ▶ Logs détaillés :
#     --log-level DEBUG
# ---------------------------------------------------------------------------
