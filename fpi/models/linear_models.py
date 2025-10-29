"""
Linear Regression Baseline Model for Property Prices
----------------------------------------------------
This module provides a simple linear regression baseline for real estate data.

Functions:
- data_preparation_for_predict: Load and clean CSV data.
- prepare_features: Build feature and target matrices.
- train_linear_model: Fit a linear regression model.
- evaluate_model: Compute and print R²/RMSE metrics.
- display_top_coefficients: Show most influential variables.
- save_model / load_model: Persist and restore trained models.
- predict_with_model: Make predictions from trained model.
- train_lm: High-level pipeline to train, evaluate, and save the model.
"""

from __future__ import annotations

from typing import Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from fpi.utils.constants import DEFAULT_TEST_SIZE, RANDOM_STATE

# ---------------------------------------------------------------------
# Data loading and preprocessing
# ---------------------------------------------------------------------


def data_preparation_for_predict(filepath: str) -> pd.DataFrame:
    """
    Load and clean a property dataset from CSV for prediction.

    Args:
        filepath: Path to the CSV file.

    Returns:
        A cleaned pandas DataFrame with numeric columns and a log-transformed price.
    """
    df: pd.DataFrame = pd.read_csv(filepath, sep=",")

    # Convert comma decimal to dot and cast to float
    df["property_value"] = df["property_value"].str.replace(",", ".").astype(float)

    # Convert numeric columns
    num_cols: list[str] = ["building_area", "main_rooms", "land_area"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric)

    # Add log of target for regression
    df["log_value"] = np.log(df["property_value"])
    return df


def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare input features (X) and target variable (y).

    Args:
        df: Cleaned DataFrame.

    Returns:
        X: Feature matrix (after one-hot encoding).
        y: Target vector (log-transformed property values).
    """
    X: pd.DataFrame = df[["building_area", "main_rooms", "land_area", "property_type_code", "town_code"]]
    y: pd.Series = df["log_value"]

    X = pd.get_dummies(X, columns=["property_type_code", "town_code"], drop_first=True)
    return X, y


# ---------------------------------------------------------------------
# Model training, evaluation, and interpretation
# ---------------------------------------------------------------------


def train_linear_model(X_train: pd.DataFrame, y_train: pd.Series) -> LinearRegression:
    """
    Fit a basic linear regression model.

    Args:
        X_train: Training features.
        y_train: Training target.

    Returns:
        Trained LinearRegression model.
    """
    model: LinearRegression = LinearRegression()
    model.fit(X_train, y_train)
    return model


def evaluate_model(model: LinearRegression, X_test: pd.DataFrame, y_test: pd.Series) -> Tuple[float, float]:
    """
    Evaluate model performance using R² and RMSE.

    Args:
        model: Fitted regression model.
        X_test: Test features.
        y_test: True test target values.

    Returns:
        (r2, rmse): R² and RMSE scores.
    """
    y_pred: np.ndarray = model.predict(X_test)
    r2: float = r2_score(y_test, y_pred)
    rmse: float = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    print(f"R²: {r2:.3f}")
    print(f"RMSE: {rmse:.3f}")
    return r2, rmse


def display_top_coefficients(model: LinearRegression, X: pd.DataFrame, n: int = 10) -> None:
    """
    Display the top n coefficients by magnitude.

    Args:
        model: Trained linear regression model.
        X: Feature matrix (used for column names).
        n: Number of top coefficients to display.
    """
    coeffs: pd.Series = pd.Series(model.coef_, index=X.columns).sort_values(ascending=False)
    print("\nTop coefficients:")
    print(coeffs.head(n))


# ---------------------------------------------------------------------
# Model persistence and prediction
# ---------------------------------------------------------------------


def save_model(model: LinearRegression, path: str) -> None:
    """
    Save the trained model to disk.

    Args:
        model: Fitted LinearRegression model.
        path: Destination file path (e.g. 'models/linear_model.pkl').
    """
    joblib.dump(model, path)


def load_model(path: str) -> LinearRegression:
    """
    Load a trained model from disk.

    Args:
        path: Path to the saved model file.

    Returns:
        Loaded LinearRegression model.
    """
    return joblib.load(path)


def predict_with_model(model: LinearRegression, X_new: pd.DataFrame) -> np.ndarray:
    """
    Predict property values (in original scale) for new data.

    Args:
        model: Trained LinearRegression model.
        X_new: Input features (must match training columns).

    Returns:
        Array of predicted property values (not log-transformed).
    """
    log_preds: np.ndarray = model.predict(X_new)
    preds: np.ndarray = np.exp(log_preds)
    return preds


# ---------------------------------------------------------------------
# High-level training pipeline
# ---------------------------------------------------------------------


def train_lm(
    filepath: str = "data/cleaned/cleaned2024/cleaned_75_2024.csv", model_path: str = "models/linear_model.pkl"
) -> LinearRegression:
    """
    Train, evaluate, and save a linear regression model for property prices.

    Args:
        filepath: Path to the cleaned CSV dataset.
        model_path: Where to save the trained model.

    Returns:
        The trained LinearRegression model.
    """
    df: pd.DataFrame = data_preparation_for_predict(filepath)
    X, y = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=DEFAULT_TEST_SIZE, random_state=RANDOM_STATE)

    model: LinearRegression = train_linear_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    display_top_coefficients(model, X)

    save_model(model, model_path)
    print(f"\nModel saved at: {model_path}")
    return model


# ---------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    train_lm()
