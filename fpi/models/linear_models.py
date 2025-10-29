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

from typing import List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from fpi.utils.constants import DEFAULT_TEST_SIZE, LM_PATH, RANDOM_STATE


def prepare_data_for_lm(filepath: str) -> pd.DataFrame:
    """
    Prepare data from CSV for linear modeling.

    Args:
        - filepath(str): Path to the CSV file.

    Returns:
        - pd.DataFrame: Cleaned DataFrame with numeric columns for quantitative variables and a log-transformed price.
    """
    df: pd.DataFrame = pd.read_csv(filepath, sep=",")

    # Convert comma decimal to dot and cast to float
    df["property_value"] = df["property_value"].str.replace(",", ".").astype(float)

    # Convert numeric columns
    num_cols: List[str] = ["building_area", "main_rooms", "land_area"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric)

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


def save_model(model: LinearRegression, path: str) -> None:
    """
    Save the trained model to disk.

    Args:
        - model(LinearRegression): Fitted LinearRegression model.
        - path(str): Destination file path (e.g. 'fpi/models/linear_model.pkl').
    """
    joblib.dump(model, path)


def build_lm(filepath: str, model_path: str) -> LinearRegression:
    """
    Train, evaluate, and save a linear regression model for property prices.

    Args:
        - filepath(str): Path to the cleaned CSV dataset.
        - model_path(str): Destination file path where the trained model will be saved.

    Returns:
        LinearRegression: Trained LinearRegression model.
    """
    df: pd.DataFrame = prepare_data_for_lm(filepath)
    X, y = set_lm_variables(
        df=df,
        x_cols=["building_area", "main_rooms", "land_area"],
        y_col="log_value",
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=DEFAULT_TEST_SIZE, random_state=RANDOM_STATE)

    model: LinearRegression = train_lm(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    display_top_coefficients(model, X)

    save_model(model, model_path)
    print(f"\nModel saved at: {model_path}")
    return model


def load_model(path: str) -> LinearRegression:
    """
    Load a trained model from disk.

    Args:
        - path(str): Path to the saved model file.

    Returns:
        LinearRegression: Loaded LinearRegression model.
    """
    return joblib.load(path)


def predict_with_model(model: LinearRegression, X_new: pd.DataFrame) -> np.ndarray:
    """
    Predict property values (in original scale) for new data.

    Args:
        - model(LinearRegression): Trained LinearRegression model.
        - X_new(pd.DataFrame): Input features (must match training columns).

    Returns:
        np.ndarray: Array of predicted property values (not log-transformed).
    """
    log_preds: np.ndarray = model.predict(X_new)
    preds: np.ndarray = np.exp(log_preds)
    return preds


def predict_property(building_area: float, main_rooms: int, land_area: float) -> float:
    """
    Predict a property value from user-provided features.

    Args:
        - building_area(float): Size of the building in square meters.
        - main_rooms(int): Number of main rooms.
        - land_area(float): Size of the land in square meters.

    Returns:
        - float: Predicted property value in original scale.
    """
    # Load the model (or you could load once at module import)
    model: LinearRegression = load_model(LM_PATH)

    # Create DataFrame with single row for prediction
    X_new = pd.DataFrame([{"building_area": building_area, "main_rooms": main_rooms, "land_area": land_area}])

    # Make prediction
    predicted_value: float = predict_with_model(model, X_new)[0]
    return predicted_value


# to predict
if __name__ == "__main__":
    # Example interactive prediction
    val = predict_property(building_area=120.0, main_rooms=5, land_area=300.0)
    print(f"Predicted property value: {val:.2f}€")

# to build lm
# if __name__ == "__main__":
#     build_lm(
#         filepath="data/cleaned/cleaned2024/cleaned_75_2024.csv",
#         model_path="fpi/models/linear_model.pkl",
#     )
