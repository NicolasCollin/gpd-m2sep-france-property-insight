"""
DVF Validation Utility

This module provides a simplified validation script for DVF (Demande de Valeur Foncière) data using Pydantic.
It can validate a single CSV *or* recursively validate **all** CSV files under a root directory (default: `data/`),
while **excluding** any file located under the output folder (default: `data/processed/`).

Outputs mirror the input tree under `data/processed/`: for an input `data/raw/2021/x.csv`, you get:
- `data/processed/raw/2021/x.validated.csv`
- `data/processed/raw/2021/x.validation_errors.csv`

Main functionalities:
- Robust CSV reading with fallback encodings and separators.
- Row-wise validation with detailed error capturing.
- Output of validated data and error reports (per file).
- Command-line interface for single-file and batch modes.
"""

from __future__ import annotations

import csv
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


# --- Helpers: column alias normalization (case/spacing tolerant) -------------
def _norm_key(s: str) -> str:
    """Normalize a column key for fuzzy matching (lower + remove spaces/underscores)."""
    return "".join(ch for ch in str(s).lower() if ch not in {" ", "_"})


# Extra header aliases to tolerate alternative header names coming from cleaned exports
_EXTRA_ALIASES: Dict[str, str] = {
    # French -> canonical aliases used by DVFRecord
    "valeur_fonciere": "Valeur_fonciere",
    "surface_reelle_bati": "Surface_reelle_bati",
    "surface_terrain": "Surface_terrain",
    "nombre_pieces_principales": "Nombre_pieces_principales",
    # English-like cleaned headers -> canonical French aliases
    "property_value": "Valeur_fonciere",
    "building_area": "Surface_reelle_bati",
    "land_area": "Surface_terrain",
    "main_rooms": "Nombre_pieces_principales",
}


def _build_alias_map() -> Dict[str, str]:
    """Build a mapping from normalized input keys to DVFRecord aliases.

    This mapping collects:
    - model field aliases declared in `DVFRecord` (both alias and field name), and
    - additional tolerant aliases defined in `_EXTRA_ALIASES` to accept cleaned/export headers.
    """
    amap: Dict[str, str] = {}

    # 1) From the Pydantic model (both field name and alias)
    for fname, field in DVFRecord.model_fields.items():
        alias = field.alias or fname
        amap[_norm_key(alias)] = alias
        amap[_norm_key(fname)] = alias

    # 2) From extra tolerant aliases
    for k, v in _EXTRA_ALIASES.items():
        amap[_norm_key(k)] = v

    return amap


_ALIAS_MAP: Dict[str, str] = _build_alias_map()


# --- Value coercion for common CSV formats -----------------------------------
def _coerce_scalar(v: Any) -> Any:
    """
    Best-effort coercion for common DVF scalar formats coming from CSVs.

    - Strip surrounding whitespace
    - Convert empty strings / 'NA' / 'N/A' / 'NULL' to None
    - Convert French decimal commas to dots (e.g., '123,45' -> 123.45)
    - Try int conversion first, then float; otherwise return the cleaned string
    """
    # Handle pandas NA/NaN
    try:
        import math

        if v is None:
            return None
        # pandas NaN detection without importing numpy
        if isinstance(v, float) and math.isnan(v):
            return None
    except Exception:
        pass

    if isinstance(v, str):
        s = v.strip()
        if s == "" or s.upper() in {"NA", "N/A", "NULL"}:
            return None

        # remove inner spaces in numbers and convert French decimals
        s_num = s.replace(" ", "").replace("\xa0", "")  # handle non-breaking spaces
        if any(ch.isdigit() for ch in s_num):
            s_num = s_num.replace(",", ".")
            # Try integer first
            try:
                if s_num.isdigit() or (s_num.startswith("-") and s_num[1:].isdigit()):
                    return int(s_num)
            except Exception:
                pass
            # Then float
            try:
                return float(s_num)
            except Exception:
                return s  # keep as string if not purely numeric
        return s
    return v


def _coerce_keys_to_alias(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of `rec` with keys coerced to the model alias, if known, and values lightly normalized."""
    out: Dict[str, Any] = {}
    for k, v in rec.items():
        alias = _ALIAS_MAP.get(_norm_key(k))
        out[alias or k] = _coerce_scalar(v)
    return out


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
    last_err: Exception | None = None

    for sep, enc in attempts:
        try:
            df = pd.read_csv(path, sep=sep, encoding=enc, low_memory=False)
            # If we ended up with a single merged column (likely wrong separator), retry next combo
            if len(df.columns) == 1 and ("," in str(df.columns[0]) or ";" in str(df.columns[0])):
                continue
            return df
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Impossible de lire le fichier CSV : {path} (dernier essai: {last_err})")


"""
# Backward-compatibility shim for legacy imports
"""


def read_any_csv(path: str | Path) -> pd.DataFrame:
    """Legacy alias: forwards to read_csv_any for older callers."""
    return read_csv_any(path)


def validate_records(records: Iterable[dict]) -> Tuple[List[DVFRecord], pd.DataFrame]:
    """Validate an iterable of dict-like rows into DVFRecord models.
    Value coercion handles common CSV formats (empty strings, 'NA', and French decimal commas).
    Returns a tuple (valid_models, errors_df) with columns [row, column, message]."""
    valids: List[DVFRecord] = []
    errors: List[Dict[str, Any]] = []
    for i, rec in enumerate(records):
        try:
            fixed = _coerce_keys_to_alias(rec)
            valids.append(DVFRecord.model_validate(fixed))
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


# --- Small summary helper (exported) -----------------------------------------
def summarize(models, errors_df):
    """Return basic counts for validation results.

    Parameters
    ----------
    models : Sequence | None
        Collection of successfully validated records (Pydantic models) or None.
    errors_df : pandas.DataFrame | None
        DataFrame of validation errors, or None.

    Returns
    -------
    dict
        Dictionary with keys: 'valid', 'errors', 'total'.
    """
    valid_n = len(models) if models is not None else 0
    try:
        errors_n = int(getattr(errors_df, "shape", (0, 0))[0]) if errors_df is not None else 0
    except Exception:
        errors_n = 0
    return {"valid": valid_n, "errors": errors_n, "total": valid_n + errors_n}


# --- Core single-file validation ---------------------------------------------
def validate_csv(
    path: str | Path, out_valid_path: Path | None = None, out_errors_path: Path | None = None
) -> Tuple[int, int, int]:
    """
    Validate a single CSV file against the DVFRecord schema and output validated data and errors.

    This function reads the CSV file robustly, validates each row with the Pydantic model DVFRecord,
    collects validation errors with detailed information, and writes the validated data to a CSV file
    and the errors to a CSV file. Output paths default to 'data/processed' if not provided.

    Parameters:
        path (str | Path): Path to the input CSV file to validate.
        out_valid_path (Path | None): Optional path to write the validated CSV file.
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
    # Normalize header: strip accidental spaces around column names
    df.columns = [str(c).strip() for c in df.columns]
    records = df.to_dict(orient="records")

    valids, errors_df = validate_records(records)

    # Warn loudly if nothing validated at all (likely wrong separator/encoding earlier)
    if len(valids) == 0 and len(records) > 0:
        print(
            "⚠️  Warning: 0 valid records produced. Check separators/encodings or header aliases (e.g. ';' vs ',' or UTF-8 vs latin-1)."
        )

    dur = time.perf_counter() - start
    logger.info(f"Validated {len(df)} rows in {dur:.2f}s — ok={len(valids)} ko={len(errors_df)} — {path}")

    # Determine output paths, defaulting to 'data/processed' if not specified
    if out_valid_path is None or out_errors_path is None:
        base_dir = Path("data/processed")
        base_dir.mkdir(parents=True, exist_ok=True)
        out_valid_path = out_valid_path or (base_dir / "validated.csv")
        out_errors_path = out_errors_path or (base_dir / "validation_errors.csv")

    # Ensure output directories exist
    out_valid_path.parent.mkdir(parents=True, exist_ok=True)
    out_errors_path.parent.mkdir(parents=True, exist_ok=True)

    # Write validated records to CSV using alias names from the Pydantic model
    pd.DataFrame([m.model_dump(by_alias=True) for m in valids]).to_csv(
        out_valid_path,
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )
    # Write validation errors to CSV
    errors_df.to_csv(
        out_errors_path,
        index=False,
        quoting=csv.QUOTE_MINIMAL,
    )

    # Print a summary of the validation results to the console
    print("\n" + "=" * 60)
    print(f"✅ Validation terminée : {len(valids):,} valides | {len(errors_df):,} erreurs | total {len(df):,}")
    print(f"📁 Fichier valide : {out_valid_path}")
    print(f"📄 Rapport erreurs : {out_errors_path}")
    print("=" * 60 + "\n")

    return len(valids), len(errors_df), len(df)


# --- Discovery utilities ------------------------------------------------------
def find_csvs(
    root: str | Path = "data",
    pattern: str = "*.csv",
    exclude_dirs: Iterable[str | Path] = ("data/processed",),
) -> List[Path]:
    """
    Recursively find CSV files under a root directory, excluding those under specified directories.

    Parameters:
        root (str | Path): Root directory to start searching from.
        pattern (str): Glob pattern to match files (default '*.csv').
        exclude_dirs (Iterable[str | Path]): Directories to exclude from search (default ('data/processed',)).

    Returns:
        List[Path]: Sorted list of Path objects pointing to CSV files found.
    """
    root_p = Path(root)
    excl_ps = [Path(d).resolve() for d in exclude_dirs]
    if not root_p.exists():
        return []
    files: List[Path] = []
    for p in root_p.rglob(pattern):
        if not p.is_file():
            continue
        # Skip files located under any excluded directory
        resolved = p.resolve()
        skip = False
        for excl in excl_ps:
            try:
                _ = resolved.relative_to(excl)
                skip = True
                break
            except Exception:
                continue
        if skip:
            continue
        files.append(p)
    return sorted(files)


# --- Batch validation ---------------------------------------------------------
def validate_all(
    root: str | Path = "data",
    exclude_dirs: Iterable[str | Path] = ("data/processed", "data/raw"),
) -> pd.DataFrame:
    """
    Validate all CSV files under a root directory recursively, excluding files under exclude_dirs.

    For each CSV file found, this function performs validation and writes outputs mirroring the input tree
    under the first exclude_dirs directory. A summary DataFrame is returned containing validation statistics per file.

    Parameters:
        root (str | Path): Root directory to scan for CSV files.
        exclude_dirs (Iterable[str | Path]): Directories to exclude from scanning and where outputs are stored (default excludes both 'data/processed' and 'data/raw').

    Returns:
        pd.DataFrame: Summary DataFrame with columns:
            - input_csv: Path to the input CSV file
            - valid: Number of valid rows
            - errors: Number of validation errors
            - total: Total rows processed
            - out_valid: Path to the validated CSV output
            - out_errors: Path to the validation errors CSV output
    """
    inputs = find_csvs(root=root, exclude_dirs=exclude_dirs)
    rows: List[Dict[str, object]] = []

    for inp in inputs:
        # Compute output directory mirroring input path under the first exclude_dirs entry
        rel = inp.relative_to(root)
        out_base = Path(list(exclude_dirs)[0]) / rel.parent
        out_base.mkdir(parents=True, exist_ok=True)
        out_valid = out_base / f"{inp.stem}.validated.csv"
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


__all__ = [
    "read_csv_any",
    "read_any_csv",
    "validate_records",
    "validate_dataframe",
    "validate_csv",
    "find_csvs",
    "validate_all",
    "summarize",
    "_coerce_keys_to_alias",
]

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
        "--exclude-dirs",
        dest="exclude_dirs",
        default="data/processed,data/raw",
        help="Comma-separated directories to exclude (e.g. 'data/processed,data/raw')",
    )
    parser.add_argument("--log-level", dest="log_level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--diagnose", dest="diagnose", action="store_true", help="Show a brief error breakdown")
    parser.add_argument(
        "--out-dir",
        dest="out_dir",
        default="data/processed",
        help="Directory where outputs are written (mirrors input tree)",
    )

    args = parser.parse_args()
    # Configure logging level as requested by the user
    logging.basicConfig(level=getattr(logging, args.log_level))

    if args.input_csv:
        # Single-file validation with mirrored outputs under out_dir (default: data/processed)
        inp = Path(args.input_csv)
        root = Path(args.root).resolve()
        out_dir = Path(args.out_dir)

        try:
            rel = inp.resolve().relative_to(root)
            out_base = out_dir / rel.parent
        except Exception:
            # If input is outside root, just place files directly under out_dir
            out_base = out_dir

        out_base.mkdir(parents=True, exist_ok=True)
        out_valid = out_base / f"{inp.stem}.validated.csv"
        out_errors = out_base / f"{inp.stem}.validation_errors.csv"

        n_valid, n_errors, n_total = validate_csv(inp, out_valid_path=out_valid, out_errors_path=out_errors)

        # Summary (same style as batch)
        print("\n" + "=" * 60)
        print(f"✅ Validation terminée : {n_valid:,} valides | {n_errors:,} erreurs | total {n_total:,}")
        print(f"📁 Fichier valide : {out_valid}")
        print(f"📄 Rapport erreurs : {out_errors}")
        print("=" * 60 + "\n")

        if args.diagnose and out_errors.exists():
            try:
                _err_df = pd.read_csv(out_errors)
                if not _err_df.empty:
                    print("Top erreurs par colonne :")
                    print(_err_df["column"].value_counts().head(10).to_string())
                    if "message" in _err_df.columns:
                        print("\nTop messages d'erreur :")
                        print(_err_df["message"].value_counts().head(10).to_string())
                    print()
            except Exception:
                pass
    else:
        # Batch validation mode over the directory tree
        exclude_dirs = [d.strip() for d in str(args.exclude_dirs).split(",") if d.strip()]
        validate_all(root=args.root, exclude_dirs=exclude_dirs)

# ---------------------------------------------------------------------------
# 💡 QUICK USAGE GUIDE
#
#
# ▶ Validate a single file:
# saves to data/processed/<same tree>/<name>.validated.csv
# and data/processed/<same tree>/<name>.validation_errors.csv
# (use --out-dir to change the output root)
#     uv run python -m fpi.utils.validation_dvf --in data/raw/raw2021/raw_75_2021.csv
#
# ▶ Validate an entire folder (recursive, excluding data/processed and data/raw by default):
#     uv run python -m fpi.utils.validation_dvf
#     # Options: --root data  --exclude-dirs data/processed,data/raw
#
# ▶ Outputs (per file):
#     - data/processed/<same tree>/<name>.validated.csv
#     - data/processed/<same tree>/<name>.validation_errors.csv
#
# ▶ Detailed logs:
#     --log-level DEBUG
# ---------------------------------------------------------------------------
