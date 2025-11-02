from __future__ import annotations
from typing import Iterable, Tuple, List, Dict
from pathlib import Path
import pandas as pd
from pydantic import ValidationError

from fpi.models.utils.schemas_dvf import DVFRecord  # ← chemin mis à jour

def read_any_csv(path: str | Path) -> pd.DataFrame:
    for kw in (
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ",", "encoding": "latin-1"},
        {"sep": ";", "encoding": "latin-1"},
    ):
        try:
            return pd.read_csv(path, **kw)
        except Exception:
            continue
    raise RuntimeError(f"Cannot read CSV: {path}")

def validate_records(records: Iterable[dict]) -> Tuple[List[DVFRecord], pd.DataFrame]:
    valids: List[DVFRecord] = []
    errors: List[Dict[str, str]] = []
    for idx, rec in enumerate(records):
        try:
            valids.append(DVFRecord.model_validate(rec))
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(map(str, err.get("loc", [])))
                errors.append({
                    "row": idx,
                    "column": loc,
                    "message": err.get("msg", ""),
                    "type": err.get("type", ""),
                    "raw_value": str(rec.get(loc, "")),
                })
    return valids, pd.DataFrame(errors)

def validate_dataframe(df: pd.DataFrame) -> Tuple[List[DVFRecord], pd.DataFrame]:
    return validate_records(df.to_dict(orient="records"))
