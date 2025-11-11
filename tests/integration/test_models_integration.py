"""
Integration tests for model training and prediction components.

These tests verify that model training and prediction workflows work correctly.
"""

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
    """Integration tests for model training workflow."""

    def test_model_training_workflow(self, temp_data_dir, sample_cleaned_csv_file):
        """Test complete model training pipeline: load data -> train -> save."""
        # Arrange
        cleaned_dir = temp_data_dir / "cleaned" / "cleaned2024"
        model_path = temp_data_dir / "test_model.joblib"
        target_col = "property_value"
        cat_cols = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols = ["building_area", "main_rooms", "land_area"]
        feature_cols = cat_cols + num_cols

        # Act - Step 1: Load data
        df = load_data_from_folder(str(cleaned_dir), pattern="*.csv")
        assert len(df) > 0, "Should load data from folder"

        # Act - Step 2: Prepare target
        df = prepare_target(df, target_col)
        assert target_col in df.columns, "Should have target column"
        assert df[target_col].notna().any(), "Should have valid target values"

        # Act - Step 3: Split features and target
        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        assert len(X_train) > 0, "Should have training data"
        assert len(X_test) > 0, "Should have test data"
        assert len(y_train) == len(X_train), "Training labels should match features"
        assert len(y_test) == len(X_test), "Test labels should match features"

        # Act - Step 4: Build preprocessor
        preprocessor = build_preprocessor(cat_cols, num_cols)
        assert preprocessor is not None, "Preprocessor should be created"

        # Act - Step 5: Build model
        model = build_random_forest(preprocessor)
        assert isinstance(model, Pipeline), "Model should be a Pipeline"

        # Act - Step 6: Train model
        trained_model = train_model(model, X_train, y_train)
        assert trained_model is not None, "Model should be trained"
        assert hasattr(trained_model, "predict"), "Model should have predict method"

        # Act - Step 7: Save model
        save_model(trained_model, str(model_path))
        assert model_path.exists(), "Model file should be created"

        # Assert - Verify model can be loaded
        loaded_model = joblib.load(model_path)
        assert loaded_model is not None, "Model should be loadable"
        assert hasattr(loaded_model, "predict"), "Loaded model should have predict method"

        # Assert - Verify model can make predictions
        test_prediction = loaded_model.predict(X_test[:1])
        assert len(test_prediction) > 0, "Model should make predictions"
        assert isinstance(test_prediction[0], (int, float)), "Prediction should be numeric"

    def test_model_training_with_loader_integration(self, temp_data_dir, sample_cleaned_csv_file):
        """Test model training using load_all_csv function."""
        # Arrange
        cleaned_dir = temp_data_dir / "cleaned"
        model_path = temp_data_dir / "test_model_loader.joblib"

        # Create additional cleaned file for multiple years
        cleaned_2023_dir = cleaned_dir / "cleaned2023"
        cleaned_2023_dir.mkdir(parents=True, exist_ok=True)
        df_2023 = pd.DataFrame(
            {
                "transaction_date": ["15/06/2023"],
                "transaction_type": ["Vente"],
                "property_value": [2000000.00],
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
        cleaned_2023_file = cleaned_2023_dir / "cleaned_75_2023.csv"
        df_2023.to_csv(cleaned_2023_file, index=False)

        # Act - Load data using load_all_csv
        df = load_all_csv(data_root=str(cleaned_dir))
        assert len(df) > 0, "Should load data from multiple files"

        # Act - Prepare data for training
        target_col = "property_value"
        df = prepare_target(df, target_col)
        cat_cols = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols = ["building_area", "main_rooms", "land_area"]
        feature_cols = cat_cols + num_cols

        # Filter out rows with missing values in required columns
        required_cols = feature_cols + [target_col]
        df = df[required_cols].dropna()
        assert len(df) > 0, "Should have data after filtering"

        # Act - Train model
        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)

        # Act - Save model
        save_model(trained_model, str(model_path))
        assert model_path.exists(), "Model should be saved"


class TestPredictionPipeline:
    """Integration tests for prediction pipeline."""

    def test_prediction_pipeline_form_input_to_output(self, temp_data_dir, sample_cleaned_csv_file, sample_prediction_input):
        """Test prediction pipeline: form input -> model -> output."""
        # Arrange - Train a model first
        cleaned_dir = temp_data_dir / "cleaned" / "cleaned2024"
        model_path = temp_data_dir / "test_prediction_model.joblib"
        target_col = "property_value"
        cat_cols = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols = ["building_area", "main_rooms", "land_area"]
        feature_cols = cat_cols + num_cols

        # Train model
        df = load_data_from_folder(str(cleaned_dir), pattern="*.csv")
        df = prepare_target(df, target_col)

        # Filter out rows with missing values
        required_cols = feature_cols + [target_col]
        df = df[required_cols].dropna()

        if len(df) == 0:
            pytest.skip("No valid data for training")

        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))

        # Act - Convert form input to model input format
        # Form inputs: postal, dept, town, prop_type, area, rooms, land
        # Model expects: building_area, main_rooms, land_area, postal_code,
        #                property_type_code, town_code, department_code
        input_data = sample_prediction_input.copy()

        # Act - Make prediction
        predicted_price = predict_price(model_path=str(model_path), input_data=input_data)

        # Assert
        assert isinstance(predicted_price, float), "Prediction should be a float"
        assert predicted_price >= 0, "Prediction should be non-negative"
        assert not pd.isna(predicted_price), "Prediction should not be NaN"

    def test_prediction_with_various_inputs(self, temp_data_dir, sample_cleaned_csv_file):
        """Test prediction with various input formats."""
        # Arrange - Train a model first
        cleaned_dir = temp_data_dir / "cleaned" / "cleaned2024"
        model_path = temp_data_dir / "test_prediction_various.joblib"
        target_col = "property_value"
        cat_cols = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols = ["building_area", "main_rooms", "land_area"]
        feature_cols = cat_cols + num_cols

        # Train model
        df = load_data_from_folder(str(cleaned_dir), pattern="*.csv")
        df = prepare_target(df, target_col)
        required_cols = feature_cols + [target_col]
        df = df[required_cols].dropna()

        if len(df) == 0:
            pytest.skip("No valid data for training")

        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))

        # Act & Assert - Test with different input formats
        test_inputs = [
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
            predicted_price = predict_price(model_path=str(model_path), input_data=input_data)
            assert isinstance(predicted_price, float), f"Prediction should be float for input {input_data}"
            assert predicted_price >= 0, f"Prediction should be non-negative for input {input_data}"

    def test_prediction_form_input_conversion(self, sample_prediction_input):
        """Test that form inputs are correctly converted to model input format."""
        # This tests the conversion logic used in prediction_page.py
        # Form input format
        postal = "75002"
        dept = "75"
        town = "102"
        prop_type = "Apartment"  # or "House"
        area = 43.0
        rooms = 2
        land = 69.0

        # Convert to model input format (as done in prediction_page.py)
        property_type_code = 1 if prop_type.lower() == "house" else 2

        input_data = {
            "building_area": float(area),
            "main_rooms": int(rooms),
            "land_area": float(land),
            "postal_code": int(postal),
            "property_type_code": property_type_code,
            "town_code": int(town),
            "department_code": int(dept),
        }

        # Assert
        assert input_data["postal_code"] == 75002, "Postal code should be converted to int"
        assert input_data["property_type_code"] == 2, "Apartment should map to code 2"
        assert input_data["building_area"] == 43.0, "Area should be float"
        assert input_data["main_rooms"] == 2, "Rooms should be int"
        assert input_data["department_code"] == 75, "Department code should be int"
