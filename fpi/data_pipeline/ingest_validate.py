from __future__ import annotations
from pathlib import Path
import pandas as pd
from fpi.utils.validation_dvf import read_any_csv, validate_dataframe

def run_validation(input_csv: str | Path,
                   out_valid_parquet: str | Path,
                   out_errors_csv: str | Path) -> None:
    df = read_any_csv(input_csv)
    models, err_df = validate_dataframe(df)
    pd.DataFrame([m.model_dump(by_alias=True) for m in models]).to_parquet(out_valid_parquet, index=False)
    err_df.to_csv(out_errors_csv, index=False)
    print(f"Valid rows: {len(models)} | Errors: {len(err_df)}")
