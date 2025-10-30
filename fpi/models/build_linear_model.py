"""
Linear Regression Baseline Model for Property Prices
This module provides a simple linear regression baseline for real estate data.

Functions:
    - prepare_data_for_lm: Load csv, convert some vars to numeric and apply log transformation.
    - set_lm_variables: set linear model's feature and target matrices.
    - train_lm: Fit a linear regression model.
    - evaluate_lm: Compute and print R²/RMSE metrics.
    - display_top_coefficients: Show most influential variables.
    - save_model / load_model: Persist and restore trained models.
    - predict_with_model: Make predictions from trained model.
    - build_lm: High-level pipeline to train, evaluate, and save the model.
"""

from __future__ import annotations

import os
from typing import List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from fpi.utils.constants import DEFAULT_TEST_SIZE, RANDOM_STATE


def load_csv_folder(folderpath: str) -> pd.DataFrame:
    """
    Load and concatenate all CSV files from a given folder for training.

    Args:
        - folderpath (str): Path to folder containing CSV files.

    Returns:
        - pd.DataFrame: Combined DataFrame (raw, before preprocessing).
    """
    csv_files = [f for f in os.listdir(folderpath) if f.endswith(".csv")]
    dfs = [pd.read_csv(os.path.join(folderpath, f), sep=",") for f in csv_files]
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
    num_cols: List[str] = ["building_area", "main_rooms", "land_area"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

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


def evaluate_model(model: LinearRegression, X_test: pd.DataFrame, y_test: pd.Series) -> Tuple[float, float]:
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
    Display the top n coefficients by magnitude.

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
    Save any scikit-learn model to disk.

    Args:
        - model (BaseEstimator): Fitted scikit-learn model.
        - path (str): Destination file path (e.g. 'fpi/models/model.pkl').
    """
    joblib.dump(model, path)


def build_ridge(folderpath: str, model_path: str, alpha: float = 1.0) -> Ridge:
    """
    Train, evaluate, and save a Ridge regression model using specified numeric and categorical features.

    Args:
        folderpath (str): Path to folder containing cleaned CSV files.
        model_path (str): Destination file path where the trained model will be saved.
        alpha (float): Regularization strength for Ridge (default=1.0).

    Returns:
        Ridge: Trained Ridge regression model.
    """
    # Load and prepare data
    df_raw = load_csv_folder(folderpath)
    df = process_data_for_lm(df_raw)

    # Specify features (same as build_lm)
    numeric_features = ["building_area", "main_rooms", "land_area"]
    categorical_features = ["postal_code", "property_type_code", "town_code", "department_code"]

    X, y = set_lm_variables(
        df=df,
        x_cols=numeric_features + categorical_features,
        y_col="log_value",
        cat_cols=categorical_features,
    )

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=DEFAULT_TEST_SIZE, random_state=RANDOM_STATE)

    # Train Ridge regression
    model = Ridge(alpha=alpha, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    # Evaluate
    evaluate_model(model, X_test, y_test)
    display_top_coefficients(model, X, 500)

    # Save model
    save_model(model, model_path)
    print(f"\nModel saved at: {model_path}")

    return model


def build_lm(folderpath: str, model_path: str) -> LinearRegression:
    """
    Train, evaluate, and save a linear regression model using all CSV files in a folder.

    Args:
        - folderpath (str): Path to folder containing cleaned CSV files.
        - model_path (str): Destination file path where the trained model will be saved.

    Returns:
        LinearRegression: Trained LinearRegression model.
    """
    # Load and prepare data
    df_raw = load_csv_folder(folderpath)
    df = process_data_for_lm(df_raw)

    # Specify features
    numeric_features = ["building_area", "main_rooms", "land_area"]
    categorical_features = ["postal_code", "property_type_code", "town_code", "department_code"]

    X, y = set_lm_variables(
        df=df,
        x_cols=numeric_features + categorical_features,
        y_col="log_value",
        cat_cols=categorical_features,
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=DEFAULT_TEST_SIZE, random_state=RANDOM_STATE)

    model: LinearRegression = train_lm(X_train, y_train)

    evaluate_model(model, X_test, y_test)
    display_top_coefficients(model, X, 500)

    save_model(model, model_path)
    print(f"\nModel saved at: {model_path}")
    return model


# if __name__ == "__main__":
#     build_lm(
#         folderpath="data/cleaned/cleaned2024",
#         model_path="fpi/models/linear_model.pkl",
#     )

if __name__ == "__main__":
    build_ridge(
        folderpath="data/cleaned/cleaned2024",
        model_path="fpi/models/ridge_model.pkl",
        alpha=10.0,  # adjust regularization strength if desired
    )
