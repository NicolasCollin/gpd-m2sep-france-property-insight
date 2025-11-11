"""
End-to-end integration tests for complete workflows.

These tests verify that the entire system works from data import to prediction.
"""

import pandas as pd
import pytest

from fpi.data_pipeline.clean_data import clean_data
from fpi.data_pipeline.loader import load_all_csv
from fpi.data_pipeline.process_data import process_data
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


class TestCompleteUserJourney:
    """Integration tests for complete user journey: data import -> analysis -> prediction."""

    def test_complete_workflow_data_import_to_prediction(self, temp_data_dir, sample_raw_csv_file):
        """Test complete workflow: import raw data, clean, process, train model, make prediction."""
        # Arrange
        raw_path = temp_data_dir / "raw"
        cleaned_path = temp_data_dir / "cleaned"
        processed_path = temp_data_dir / "processed"
        model_path = temp_data_dir / "complete_workflow_model.joblib"

        # Act - Step 1: Import and clean raw data
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        cleaned_file = cleaned_path / "cleaned2024" / "cleaned_75_2024.csv"
        assert cleaned_file.exists(), "Cleaned file should be created"

        # Act - Step 2: Process cleaned data
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)
        processed_file = processed_path / "processed2024" / "processed_75_2024.csv"
        assert processed_file.exists(), "Processed file should be created"

        # Act - Step 3: Load processed data for model training
        # Use cleaned data for training (as models typically use cleaned data)
        df = load_data_from_folder(str(cleaned_path / "cleaned2024"), pattern="*.csv")
        assert len(df) > 0, "Should load data for training"

        # Act - Step 4: Prepare data for training
        target_col = "property_value"
        df = prepare_target(df, target_col)
        cat_cols = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols = ["building_area", "main_rooms", "land_area"]
        feature_cols = cat_cols + num_cols

        # Filter out rows with missing values
        required_cols = feature_cols + [target_col]
        df = df[required_cols].dropna()

        if len(df) == 0:
            pytest.skip("No valid data for training after filtering")

        # Act - Step 5: Train model
        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))
        assert model_path.exists(), "Model should be saved"

        # Act - Step 6: Make prediction using the trained model
        # Use data from the test set or create sample input
        if len(X_test) > 0:
            # Use first test example as input
            test_input = X_test.iloc[0].to_dict()
            # Ensure all required keys are present
            input_data = {
                "building_area": float(test_input.get("building_area", 43.0)),
                "main_rooms": int(test_input.get("main_rooms", 2)),
                "land_area": float(test_input.get("land_area", 69.0)),
                "postal_code": int(test_input.get("postal_code", 75002)),
                "property_type_code": int(test_input.get("property_type_code", 2)),
                "town_code": int(test_input.get("town_code", 102)),
                "department_code": int(test_input.get("department_code", 75)),
            }
        else:
            # Fallback to sample input
            input_data = {
                "building_area": 43.0,
                "main_rooms": 2,
                "land_area": 69.0,
                "postal_code": 75002,
                "property_type_code": 2,
                "town_code": 102,
                "department_code": 75,
            }

        predicted_price = predict_price(model_path=str(model_path), input_data=input_data)

        # Assert - Verify prediction was made (without checking if it's "reasonable" as requested)
        assert isinstance(predicted_price, float), "Prediction should be a float"
        assert not pd.isna(predicted_price), "Prediction should not be NaN"
        assert predicted_price >= 0, "Prediction should be non-negative"

    def test_complete_workflow_with_multiple_departments(self, temp_data_dir, sample_raw_csv_file):
        """Test complete workflow with data from multiple departments."""
        # Arrange - Create data for multiple departments
        raw_path = temp_data_dir / "raw"
        cleaned_path = temp_data_dir / "cleaned"
        processed_path = temp_data_dir / "processed"
        model_path = temp_data_dir / "multi_dept_model.joblib"

        # Create additional raw file for another department
        raw_2024_dir = raw_path / "raw2024"
        raw_77_file = raw_2024_dir / "raw_77_2024.csv"
        raw_77_data = """date_mutation,nature_mutation,valeur_fonciere,code_postal,commune,code_departement,\
            code_commune,code_type_local,type_local,surface_reelle_bati,nombre_pieces_principales,surface_terrain
15/06/2024,Vente,250000,00,77000,MELUN,77,77288,2,Appartement,60,3,100"""
        raw_77_file.write_text(raw_77_data, encoding="utf-8")

        # Act - Step 1: Clean data
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)

        # Act - Step 2: Process data
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        # Act - Step 3: Load all cleaned data
        df = load_all_csv(data_root=str(cleaned_path))
        assert len(df) > 0, "Should load data from multiple departments"

        # Act - Step 4: Prepare and train model
        target_col = "property_value"
        df = prepare_target(df, target_col)
        cat_cols = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols = ["building_area", "main_rooms", "land_area"]
        feature_cols = cat_cols + num_cols

        required_cols = feature_cols + [target_col]
        df = df[required_cols].dropna()

        if len(df) == 0:
            pytest.skip("No valid data for training")

        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))

        # Act - Step 5: Make prediction
        input_data = {
            "building_area": 60.0,
            "main_rooms": 3,
            "land_area": 100.0,
            "postal_code": 77000,
            "property_type_code": 2,
            "town_code": 77288,
            "department_code": 77,
        }

        predicted_price = predict_price(model_path=str(model_path), input_data=input_data)

        # Assert
        assert isinstance(predicted_price, float), "Prediction should be a float"
        assert not pd.isna(predicted_price), "Prediction should not be NaN"

    def test_complete_workflow_data_refresh(self, temp_data_dir, sample_raw_csv_file):
        """Test that system handles new data correctly (data refresh workflow)."""
        # Arrange
        raw_path = temp_data_dir / "raw"
        cleaned_path = temp_data_dir / "cleaned"
        processed_path = temp_data_dir / "processed"
        model_path = temp_data_dir / "refresh_model.joblib"

        # Act - Step 1: Initial data import and cleaning
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        # Act - Step 2: Train initial model
        df_initial = load_all_csv(data_root=str(cleaned_path))
        assert len(df_initial) > 0, "Should load initial data"

        # Act - Step 3: Add new data (simulate data refresh)
        raw_2024_dir = raw_path / "raw2024"
        new_raw_file = raw_2024_dir / "raw_92_2024.csv"
        new_raw_data = """date_mutation,nature_mutation,valeur_fonciere,code_postal,commune,code_departement,\
            code_commune,code_type_local,type_local,surface_reelle_bati,nombre_pieces_principales,surface_terrain
20/06/2024,Vente,500000,00,92000,COURBEVOIE,92,92026,2,Appartement,70,4,80"""
        new_raw_file.write_text(new_raw_data, encoding="utf-8")

        # Act - Step 4: Clean new data
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        # Act - Step 5: Load updated data
        df_updated = load_all_csv(data_root=str(cleaned_path))
        assert len(df_updated) >= len(df_initial), "Updated data should have more or equal rows"

        # Act - Step 6: Train model with updated data
        target_col = "property_value"
        df_updated = prepare_target(df_updated, target_col)
        cat_cols = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols = ["building_area", "main_rooms", "land_area"]
        feature_cols = cat_cols + num_cols

        required_cols = feature_cols + [target_col]
        df_updated = df_updated[required_cols].dropna()

        if len(df_updated) == 0:
            pytest.skip("No valid data for training")

        X_train, X_test, y_train, y_test = split_features_target(df_updated, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))

        # Assert - Model should be trained and usable
        assert model_path.exists(), "Model should be saved"

        # Act - Make prediction with new model
        input_data = {
            "building_area": 70.0,
            "main_rooms": 4,
            "land_area": 80.0,
            "postal_code": 92000,
            "property_type_code": 2,
            "town_code": 92026,
            "department_code": 92,
        }

        predicted_price = predict_price(model_path=str(model_path), input_data=input_data)

        # Assert
        assert isinstance(predicted_price, float), "Prediction should be a float"
        assert not pd.isna(predicted_price), "Prediction should not be NaN"
