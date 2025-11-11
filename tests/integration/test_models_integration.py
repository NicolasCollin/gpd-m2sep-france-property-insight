"""
Integration tests for model training and prediction components.

These tests verify that model training and prediction workflows work correctly.
They cover end-to-end pipelines including:
- Data loading
- Target preparation
- Feature splitting
- Preprocessing
- Model training and saving
- Prediction generation from form inputs
"""

from pathlib import Path

import joblib
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from fpi.data_pipeline.loader import load_all_csv
from fpi.models.build_random_forest import (
    build_preprocessor,
    build_random_forest,
    load_data_from_folder,
    prepare_target,
    save_model,
    split_features_target,
    train_model,
)
from fpi.models.predict import predict_price


class TestModelTrainingWorkflow:
    """Integration tests for model training workflows."""

    def test_model_training_workflow(self, temp_data_dir: Path, sample_cleaned_csv_file: Path) -> None:
        """
        Test complete model training pipeline.

        Workflow tested:
        1. Load cleaned CSV data.
        2. Prepare target column.
        3. Split features and target.
        4. Build preprocessor and random forest model.
        5. Train the model.
        6. Save model to disk.
        7. Load model and verify predictions.
        """
        # Arrange
        cleaned_dir: Path = temp_data_dir / "cleaned" / "cleaned2024"
        model_path: Path = temp_data_dir / "test_model.joblib"
        target_col: str = "property_value"
        cat_cols: list[str] = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols: list[str] = ["building_area", "main_rooms", "land_area"]
        feature_cols: list[str] = cat_cols + num_cols

        # Act - Load data
        df: pd.DataFrame = load_data_from_folder(str(cleaned_dir), pattern="*.csv")
        assert len(df) > 0, "Should load data from folder"

        # Act - Prepare target
        df = prepare_target(df, target_col)
        assert target_col in df.columns, "Should have target column"
        assert df[target_col].notna().any(), "Should have valid target values"

        # Act - Split features and target
        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        assert len(X_train) > 0 and len(X_test) > 0
        assert len(y_train) == len(X_train) and len(y_test) == len(X_test)

        # Act - Build preprocessor
        preprocessor = build_preprocessor(cat_cols, num_cols)
        assert preprocessor is not None

        # Act - Build model
        model: Pipeline = build_random_forest(preprocessor)
        assert isinstance(model, Pipeline)

        # Act - Train model
        trained_model: Pipeline = train_model(model, X_train, y_train)
        assert trained_model is not None
        assert hasattr(trained_model, "predict")

        # Act - Save model
        save_model(trained_model, str(model_path))
        assert model_path.exists()

        # Assert - Load and test predictions
        loaded_model: Pipeline = joblib.load(model_path)
        assert hasattr(loaded_model, "predict")
        test_prediction = loaded_model.predict(X_test[:1])
        assert len(test_prediction) > 0
        assert isinstance(test_prediction[0], (int, float))

    def test_model_training_with_loader_integration(self, temp_data_dir: Path, sample_cleaned_csv_file: Path) -> None:
        """
        Test model training using `load_all_csv` for multiple cleaned files.

        Ensures that loading multiple CSVs and training works correctly.
        """
        # Arrange
        cleaned_dir: Path = temp_data_dir / "cleaned"
        model_path: Path = temp_data_dir / "test_model_loader.joblib"

        # Add additional cleaned CSV for previous year
        cleaned_2023_dir: Path = cleaned_dir / "cleaned2023"
        cleaned_2023_dir.mkdir(parents=True, exist_ok=True)
        df_2023: pd.DataFrame = pd.DataFrame(
            {
                "transaction_date": ["15/06/2023"],
                "transaction_type": ["Vente"],
                "property_value": [2000000.0],
                "postal_code": [75001],
                "town_name": ["PARIS 01"],
                "department_code": [75],
                "town_code": [101],
                "property_type_code": [2],
                "property_type": ["Appartement"],
                "building_area": [50.0],
                "main_rooms": [3.0],
                "land_area": [80.0],
            }
        )
        cleaned_2023_file: Path = cleaned_2023_dir / "cleaned_75_2023.csv"
        df_2023.to_csv(cleaned_2023_file, index=False)

        # Act - Load data
        df: pd.DataFrame = load_all_csv(data_root=str(cleaned_dir))
        assert len(df) > 0

        # Prepare for training
        target_col: str = "property_value"
        df = prepare_target(df, target_col)
        cat_cols: list[str] = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols: list[str] = ["building_area", "main_rooms", "land_area"]
        feature_cols: list[str] = cat_cols + num_cols
        df = df[feature_cols + [target_col]].dropna()
        assert len(df) > 0

        # Train model
        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))
        assert model_path.exists()


class TestPredictionPipeline:
    """Integration tests for prediction pipeline."""

    def test_prediction_pipeline_form_input_to_output(
        self, temp_data_dir: Path, sample_cleaned_csv_file: Path, sample_prediction_input: dict[str, int | float]
    ) -> None:
        """
        Test prediction pipeline end-to-end.

        Converts a sample form input to model input format and verifies
        that prediction is a float and non-negative.
        """
        # Arrange - Train a model first
        cleaned_dir: Path = temp_data_dir / "cleaned" / "cleaned2024"
        model_path: Path = temp_data_dir / "test_prediction_model.joblib"
        target_col: str = "property_value"
        cat_cols: list[str] = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols: list[str] = ["building_area", "main_rooms", "land_area"]
        feature_cols: list[str] = cat_cols + num_cols

        # Train model
        df: pd.DataFrame = load_data_from_folder(str(cleaned_dir), pattern="*.csv")
        df = prepare_target(df, target_col)
        df = df[feature_cols + [target_col]].dropna()
        if len(df) == 0:
            pytest.skip("No valid data for training")

        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))

        # Act
        input_data: dict[str, int | float] = sample_prediction_input.copy()
        predicted_price: float = predict_price(model_path=str(model_path), input_data=input_data)

        # Assert
        assert isinstance(predicted_price, float)
        assert predicted_price >= 0
        assert not pd.isna(predicted_price)

    def test_prediction_with_various_inputs(self, temp_data_dir: Path, sample_cleaned_csv_file: Path) -> None:
        """
        Test prediction with multiple input scenarios.

        Ensures that the model handles different property features correctly.
        """
        # Arrange - Train model
        cleaned_dir: Path = temp_data_dir / "cleaned" / "cleaned2024"
        model_path: Path = temp_data_dir / "test_prediction_various.joblib"
        target_col: str = "property_value"
        cat_cols: list[str] = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols: list[str] = ["building_area", "main_rooms", "land_area"]
        feature_cols: list[str] = cat_cols + num_cols

        df: pd.DataFrame = load_data_from_folder(str(cleaned_dir), pattern="*.csv")
        df = prepare_target(df, target_col)
        df = df[feature_cols + [target_col]].dropna()
        if len(df) == 0:
            pytest.skip("No valid data for training")

        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))

        # Act & Assert - Multiple test inputs
        test_inputs: list[dict[str, int | float]] = [
            {
                "building_area": 43.0,
                "main_rooms": 2,
                "land_area": 69.0,
                "postal_code": 75002,
                "property_type_code": 2,
                "town_code": 102,
                "department_code": 75,
            },
            {
                "building_area": 135.0,
                "main_rooms": 0,
                "land_area": 124.0,
                "postal_code": 75020,
                "property_type_code": 4,
                "town_code": 120,
                "department_code": 75,
            },
        ]

        for input_data in test_inputs:
            predicted_price: float = predict_price(model_path=str(model_path), input_data=input_data)
            assert isinstance(predicted_price, float)
            assert predicted_price >= 0

    def test_prediction_form_input_conversion(self, sample_prediction_input: dict[str, int | float]) -> None:
        """
        Test conversion from form inputs to model input format.

        Verifies that types and property type codes are correctly assigned.
        """
        # Arrange
        postal: str = "75002"
        dept: str = "75"
        town: str = "102"
        prop_type: str = "Apartment"
        area: float = 43.0
        rooms: int = 2
        land: float = 69.0

        # Act - Convert to model input
        property_type_code: int = 1 if prop_type.lower() == "house" else 2
        input_data: dict[str, int | float] = {
            "building_area": float(area),
            "main_rooms": int(rooms),
            "land_area": float(land),
            "postal_code": int(postal),
            "property_type_code": property_type_code,
            "town_code": int(town),
            "department_code": int(dept),
        }

        # Assert
        assert input_data["postal_code"] == 75002
        assert input_data["property_type_code"] == 2
        assert input_data["building_area"] == 43.0
        assert input_data["main_rooms"] == 2
        assert input_data["department_code"] == 75
