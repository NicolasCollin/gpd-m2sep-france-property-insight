# src/analysis/reg.py
from __future__ import annotations
import joblib
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# constants - adapt if needed
RANDOM_STATE = 42
MODEL_PATH = Path("models")
MODEL_PATH.mkdir(parents=True, exist_ok=True)
MODEL_FILE = MODEL_PATH / "rf_pipeline.joblib"

# Features selected (as discussed)
NUMERIC_FEATURES = [
    "Nombre_de_lots",
    "Surface_reelle_bati",
    "Nombre_pieces_principales",
    "Surface_terrain",
]

CATEGORICAL_FEATURES = [
    "Type_de_voie",
    "Code_departement",
    "Code_commune",
    "Code_type_local",
]


TARGET_COL = "Valeur_fonciere"


def build_pipeline(
    numeric_features: List[str],
    categorical_features: List[str],
) -> Pipeline:
    """
    Build a sklearn Pipeline that preprocesses numeric and categorical features
    and fits a RandomForestRegressor.

    :param numeric_features: list of numeric column names
    :param categorical_features: list of categorical column names
    :return: sklearn Pipeline (preprocessor + model)
    """
    # numeric preprocessing: impute (median) then scale
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    # categorical preprocessing: impute (constant) then one-hot (ignore unknown)
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop",
    )

    rf = RandomForestRegressor(
        n_estimators=200,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", rf),
        ]
    )

    return pipeline


def train_and_save(
    data_path: str = "data/raw/sample2024.txt",
    model_file: Path = MODEL_FILE,
    test_size: float = 0.2,
) -> None:
    """
    Load data, train the pipeline and save it to disk.

    This function:
    - loads dataset from CSV (sep='|')
    - keeps only the features in NUMERIC_FEATURES + CATEGORICAL_FEATURES + TARGET_COL
    - drops rows where target is missing after conversion
    - applies log1p to target for training (to stabilize)
    - trains RandomForest pipeline
    - prints MAE, RMSE, R2 on hold-out set
    - stores pipeline + metadata with joblib

    :param data_path: path to raw dataset
    :param model_file: output file path to save trained pipeline
    :param test_size: proportion of data used as test
    """
    df = pd.read_csv(data_path, sep="|", header=0)
    needed_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET_COL]
    missing_cols = [c for c in needed_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in data: {missing_cols}")

    # Keep only needed columns
    df_model = df[needed_cols].copy()

    # Clean numeric columns: remove spaces/commas/euro for target and numeric features if needed
    def clean_numeric_series(s: pd.Series) -> pd.Series:
        s = s.astype(str).str.replace("€", "", regex=False).str.replace(",", "", regex=False).str.strip()
        return pd.to_numeric(s, errors="coerce")

    # Clean numeric features
    for col in NUMERIC_FEATURES + [TARGET_COL]:
        df_model[col] = clean_numeric_series(df_model[col])

    # Drop rows with missing target
    df_model = df_model.dropna(subset=[TARGET_COL]).copy()

    # Optionally, remove implausible targets (<=0)
    df_model = df_model[df_model[TARGET_COL] > 0].copy()

    if df_model.shape[0] < 10:
        raise ValueError("Not enough rows after cleaning to train a model.")

    X = df_model[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df_model[TARGET_COL].values

    # log-transform target to stabilize variance
    y_trans = np.log1p(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_trans, test_size=test_size, random_state=RANDOM_STATE
    )

    pipeline = build_pipeline(NUMERIC_FEATURES, CATEGORICAL_FEATURES)
    print("Training pipeline on", X_train.shape[0], "rows...")
    pipeline.fit(X_train, y_train)

    # Predict on test set (remember predictions are in log space)
    y_pred_log = pipeline.predict(X_test)
    y_pred = np.expm1(y_pred_log)  # inverse of log1p
    y_true = np.expm1(y_test)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred, squared=False)
    r2 = r2_score(y_true, y_pred)

    print("=== Test metrics (original scale) ===")
    print(f"MAE : {mae:,.2f}")
    print(f"RMSE: {rmse:,.2f}")
    print(f"R2  : {r2:.4f}")

    # Save pipeline + metadata (store the fact that we used log1p)
    to_save = {
        "pipeline": pipeline,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "target": TARGET_COL,
        "target_transform": "log1p",
    }
    joblib.dump(to_save, model_file)
    print(f"Model saved to {model_file}")


if __name__ == "__main__":
    # Run training from CLI: python -m src.analysis.model (or python src/analysis/model.py)
    train_and_save()
