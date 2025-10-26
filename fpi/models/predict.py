# src/analysis/predict.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd

MODEL_FILE = Path("models/rf_pipeline.joblib")


def load_model(model_file: Path = MODEL_FILE) -> Dict[str, Any]:
    """
    Load the saved model dict (pipeline + metadata).
    """
    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_file}. Train model first.")
    return joblib.load(model_file)


def predict_from_inputs(inputs: Dict[str, Any], model_file: Path = MODEL_FILE) -> float:
    """
    Predict land value from a dict of user inputs.

    Expected keys in inputs:
      - 'Type_de_voie' (str)
      - 'Code_departement' (str or int)
      - 'Code_commune' (str or int)
      - 'Code_type_local' (str)
      - 'Nombre_de_lots' (int/float)
      - 'Surface_reelle_bati' (int/float)
      - 'Nombre_pieces_principales' (int/float)
      - 'Surface_terrain' (int/float)

    :param inputs: mapping of feature name -> value (raw user inputs)
    :return: predicted Valeur_fonciere (float, original euros scale)
    """
    saved = load_model(model_file)
    pipeline = saved["pipeline"]
    t_info = saved.get("target_transform", None)

    # Build a 1-row DataFrame
    # ensure column order matches training features
    feature_cols = saved["numeric_features"] + saved["categorical_features"]
    df = pd.DataFrame([inputs], columns=feature_cols)

    # Ensure numeric columns are numeric (coerce)
    for col in saved["numeric_features"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Run pipeline prediction (pipeline expects training feature order)
    pred_trans = pipeline.predict(df)
    # inverse transform
    if t_info == "log1p":
        pred = np.expm1(pred_trans)
    else:
        pred = float(pred_trans)

    # Round to euros and return
    return float(round(pred, 2))
