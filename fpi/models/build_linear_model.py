"""
Linear Regression Baseline Model for Property Prices

This module provides tools to train, evaluate, and use linear and Ridge regression models
for predicting real estate prices based on numeric and categorical property features.

Main functions:

    - build_lm(folder_path: str, model_path: str, numeric_features: List[str],
               categorical_features: List[str], target_col: str) -> LinearRegression
        Train, evaluate, and save a LinearRegression model using specified numeric and categorical features.

    - build_ridge(folder_path: str, model_path: str, numeric_features: List[str],
                  categorical_features: List[str], target_col: str, alpha: float = 10.0) -> Ridge
        Train, evaluate, and save a Ridge regression model using specified features and regularization.

    - predict_price(model_path: str, input_data: Dict[str, float]) -> float
        Predict property price in euros using a trained model, automatically handling one-hot encoding
        and feature alignment.

Notes:
    - Categorical features are one-hot encoded; the first category is dropped to avoid multicollinearity.
    - Target values are log-transformed; predictions are returned in the original price scale.
    - Default test/train split and random state are imported from `fpi.utils.constants`.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from fpi.utils.constants import DEFAULT_TEST_SIZE, RANDOM_STATE


def load_csv_folder(folder_path: str) -> pd.DataFrame:
    """
    Load and concatenate all CSV files from a given folder into one pd.DataFrame

    Args:
        - folder_path (str): Path to folder containing CSV files.

    Returns:
        - pd.DataFrame: Combined DataFrame (raw, before preprocessing).
    """
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    dfs = [pd.read_csv(os.path.join(folder_path, f), sep=",") for f in csv_files]
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(csv_files)} files, total {len(combined_df)} rows.")
    return combined_df


def process_data_for_lm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process pd.DataFrame data for linear modeling.

    Args:
        - df (pd.DataFrame): Raw DataFrame.

    Returns:
        - pd.DataFrame: Cleaned DataFrame with numeric columns and log-transformed target.
    """
    # Convert comma decimal to dot and cast to float
    df["property_value"] = df["property_value"].astype(str).str.replace(",", ".").astype(float)

    # Convert numeric columns
    numeric_features: List[str] = ["building_area", "main_rooms", "land_area"]

    df[numeric_features] = df[numeric_features].apply(pd.to_numeric, errors="coerce")

    # Add log of target for regression
    df["log_value"] = np.log(df["property_value"])
    return df


def set_lm_variables(
    df: pd.DataFrame,
    x_cols: List[str],
    y_col: str,
    cat_cols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Set feature matrix (X) and target vector (y) for regression.

    Args:
        - df(pd.DataFrame): Input DataFrame.
        - x_cols(List[str]): List of column names to use as predictors.
        - y_col(str): Name of the target column.
        - cat_cols(Optional[List[str]]): Optional list of categorical columns to one-hot encode.

    Returns:
        Tuple[pd.DataFrame, pd.Series]:
            - X: Processed feature matrix (numeric, after one-hot encoding if applicable).
            - y: Target vector (Series).
    """
    X: pd.DataFrame = df[x_cols].copy()
    y: pd.Series = df[y_col].copy()

    # Apply one-hot encoding to categorical variables if provided
    if cat_cols:
        X = pd.get_dummies(X, columns=cat_cols, drop_first=True)

    return X, y


def train_lm(X_train: pd.DataFrame, y_train: pd.Series) -> LinearRegression:
    """
    Train a linear regression model using given features and target data.

    Args:
        - X_train(pd.DataFrame): Training features.
        - y_train(pd.Series): Training target.

    Returns:
        LinearRegression: Trained LinearRegression model.
    """
    model: LinearRegression = LinearRegression()
    model.fit(X_train, y_train)
    return model


def evaluate_lm(model: LinearRegression, X_test: pd.DataFrame, y_test: pd.Series) -> Tuple[float, float]:
    """
    Evaluate model performance using R² and RMSE.

    Args:
        - model(LinearRegression): Fitted regression model.
        - X_test(pd.DataFrame): Test features.
        - y_test(pd.Series): True test target values.

    Returns:
        Tuple[float, float]: (r2, rmse) scores.
    """
    y_pred: np.ndarray = model.predict(X_test)
    r2: float = r2_score(y_test, y_pred)
    rmse: float = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    print(f"R²: {r2:.3f}")
    print(f"RMSE: {rmse:.3f}")
    return r2, rmse


def display_top_coefficients(model: LinearRegression, X: pd.DataFrame, n: int = 10) -> None:
    """
    Display the top n coefficients of the models.

    Args:
        - model(LinearRegression): Trained linear regression model.
        - X(pd.DataFrame): Feature matrix (used for column names).
        - n(int): Number of top coefficients to display (default: 10).
    """
    coeffs: pd.Series = pd.Series(model.coef_, index=X.columns).sort_values(key=abs, ascending=False)
    print("\nTop coefficients by magnitude:")
    print(coeffs.head(n))


def save_model(model: BaseEstimator, path: str) -> None:
    """
    Save any scikit-learn model to given path.

    Args:
        - model (BaseEstimator): Fitted scikit-learn model.
        - path (str): Destination file path (e.g. 'fpi/models/model.pkl').
    """
    joblib.dump(model, path)


def build_lm(
    folder_path: str,
    model_path: str,
    numeric_features: List[str],
    categorical_features: List[str],
    target_col: str,
) -> LinearRegression:
    """
    Train, evaluate, and save a linear regression model using specified features.

    Args:
        - folder_path (str): Path to folder containing cleaned CSV files.
        - model_path (str): Destination file path where the trained model will be saved.
        - numeric_features (List[str]): List of numeric feature names.
        - categorical_features (List[str]): List of categorical feature names.
        - target_col (str): Target column name (typically 'log_value').

    Returns:
        LinearRegression: Trained LinearRegression model.
    """
    df_raw = load_csv_folder(folder_path)
    df = process_data_for_lm(df_raw)

    X, y = set_lm_variables(
        df=df,
        x_cols=numeric_features + categorical_features,
        y_col=target_col,
        cat_cols=categorical_features,
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=DEFAULT_TEST_SIZE, random_state=RANDOM_STATE)

    model = train_lm(X_train, y_train)

    evaluate_lm(model, X_test, y_test)
    display_top_coefficients(model, X, 500)

    save_model(model, model_path)
    print(f"\nModel saved at: {model_path}")
    return model


def build_ridge(
    folder_path: str,
    model_path: str,
    numeric_features: List[str],
    categorical_features: List[str],
    target_col: str,
    alpha: float = 10.0,
) -> Ridge:
    """
    Train, evaluate, and save a Ridge regression model using specified features.

    Args:
        - folder_path (str): Path to folder containing cleaned CSV files.
        - model_path (str): Destination file path where the trained model will be saved.
        - numeric_features (List[str]): List of numeric feature names.
        - categorical_features (List[str]): List of categorical feature names.
        - target_col (str): Target column name (typically 'log_value').
        - alpha (float): Regularization strength for Ridge (default=1.0).

    Returns:
        Ridge: Trained Ridge regression model.
    """
    df_raw = load_csv_folder(folder_path)
    df = process_data_for_lm(df_raw)

    X, y = set_lm_variables(
        df=df,
        x_cols=numeric_features + categorical_features,
        y_col=target_col,
        cat_cols=categorical_features,
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=DEFAULT_TEST_SIZE, random_state=RANDOM_STATE)

    model = Ridge(alpha=alpha, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    evaluate_lm(model, X_test, y_test)
    display_top_coefficients(model, X, 500)

    save_model(model, model_path)
    print(f"\nModel saved at: {model_path}")
    return model


def mock_build_lm() -> None:
    """
    Example mock builder for a Linear Regression model with flexible features.

    Outputs: Saves the trained model to the specified path.
    """
    folder_path: str = "data/cleaned/cleaned2024"
    model_path: str = "fpi/models/linear_model.pkl"
    numeric_features: List[str] = ["building_area", "main_rooms", "land_area"]
    categorical_features: List[str] = ["postal_code", "property_type_code", "town_code", "department_code"]
    target_col: str = "log_value"

    build_lm(
        folder_path=folder_path,
        model_path=model_path,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        target_col=target_col,
    )


def mock_build_ridge() -> None:
    """
    Example mock builder for a Ridge Regression model with flexible features.

    Outputs: Saves the trained model to the specified path.
    """
    folder_path: str = "data/cleaned/cleaned2024"
    model_path: str = "fpi/models/ridge_model.pkl"
    numeric_features: List[str] = ["building_area", "main_rooms", "land_area"]
    categorical_features: List[str] = ["postal_code", "property_type_code", "town_code", "department_code"]
    target_col: str = "log_value"
    alpha: float = 10.0

    build_ridge(
        folder_path=folder_path,
        model_path=model_path,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        target_col=target_col,
        alpha=alpha,
    )


def predict_price(model_path: str, input_data: Dict[str, float]) -> float:
    """
    Predict property price in euros using a trained linear or ridge model.
    Handles one-hot encoding of categorical features and auto-aligns columns.

    Args:
        - model_path (str): Path to the trained model (.pkl file).
        - input_data (Dict[str, float]): Dictionary of property features.

    Returns:
        float: Predicted property price in euros.
    """
    # Load model
    model: BaseEstimator = joblib.load(model_path)

    # Prepare input as DataFrame
    df: pd.DataFrame = pd.DataFrame([input_data])

    # One-hot encode categorical columns
    categorical_features: List[str] = ["postal_code", "property_type_code", "town_code", "department_code"]
    df = pd.get_dummies(df, columns=categorical_features, drop_first=True)

    # Auto-align columns with the model
    X_aligned: pd.DataFrame = df.reindex(columns=model.feature_names_in_, fill_value=0)

    # Predict log-price and convert back to euros
    y_pred_log: float = model.predict(X_aligned)[0]
    return float(np.exp(y_pred_log))


def mock_predict_price() -> None:
    """
    Mock prediction using a hardcoded property input.

    Prints:
        The predicted property price in euros.
    """
    example_input: Dict[str, Any] = {
        "building_area": 135.0,
        "main_rooms": 2,
        "land_area": 124.0,
        "postal_code": 75020,
        "property_type_code": 4,
        "town_code": 120,
        "department_code": 75,
    }

    model_path: str = "fpi/models/linear_model.pkl"

    predicted_price: float = predict_price(model_path=model_path, input_data=example_input)
    print(f"Mock predicted price: €{predicted_price:,.0f}")
