from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def load_data_from_folder(folder_path: str, pattern: str = "*_2024.csv") -> pd.DataFrame:
    files = sorted(Path(folder_path).rglob(pattern))
    assert len(files) > 0, f"No files found in {folder_path}!"
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def prepare_target(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    df[target_col] = df[target_col].astype(str).str.strip().replace("", None).str.replace(",", ".", regex=False)
    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")
    return df


def split_features_target(df: pd.DataFrame, target_col: str, feature_cols: list):
    X = df[feature_cols]
    y = df[target_col]
    return train_test_split(X, y, test_size=0.3, random_state=42)


def build_preprocessor(cat_cols: list[str], num_cols: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
            ("num", "passthrough", num_cols),
        ]
    )


def build_random_forest(preprocessor: ColumnTransformer) -> Pipeline:
    return Pipeline(
        [
            ("prep", preprocessor),
            (
                "model",
                RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_leaf=2, random_state=42, n_jobs=-1),
            ),
        ]
    )


def train_model(model: Pipeline, X_train, y_train) -> Pipeline:
    model.fit(X_train, y_train)
    return model


def evaluate_model(model: Pipeline, X_test, y_test):
    preds = model.predict(X_test)
    print(f"MAE: {mean_absolute_error(y_test, preds):.2f}")
    print(f"R²: {r2_score(y_test, preds):.3f}")


def save_model(model: Pipeline, path: str):
    joblib.dump(model, path, compress=("xz", 3))
    print(f"Model saved to {path}")


def predict_price(model_path: str, input_data: dict[str, float]) -> float:
    """
    Predict property price using a trained Random Forest pipeline.
    Accepts numeric codes for categorical features.
    """
    model: Pipeline = joblib.load(model_path)

    # Prepare input as a DataFrame with raw columns
    df: pd.DataFrame = pd.DataFrame([input_data])

    # Directly predict; the pipeline handles encoding internally
    return float(model.predict(df)[0])


def mock_predict_price():
    example_input = {
        "building_area": 135.0,
        "main_rooms": 2,
        "land_area": 124.0,
        "postal_code": 75020,
        "property_type_code": 4,
        "town_code": 120,
        "department_code": 75,
    }
    model_path = "fpi/models/random_forest.joblib"
    predicted_price = predict_price(model_path, example_input)
    print(f"Predicted price: €{predicted_price:,.0f}")


def main():
    folder_path = "data/cleaned/cleaned2024"
    model_path = "fpi/models/random_forest.joblib"
    target_col = "property_value"

    cat_cols = ["postal_code", "department_code", "town_code", "property_type_code"]
    num_cols = ["building_area", "main_rooms", "land_area"]
    feature_cols = cat_cols + num_cols

    df = load_data_from_folder(folder_path)
    df = prepare_target(df, target_col)
    X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)

    preprocessor = build_preprocessor(cat_cols, num_cols)
    model = build_random_forest(preprocessor)

    model = train_model(model, X_train, y_train)
    evaluate_model(model, X_test, y_test)
    save_model(model, model_path)


if __name__ == "__main__":
    main()
    mock_predict_price()
