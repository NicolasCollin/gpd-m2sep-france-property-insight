"""
End-to-end integration tests for complete workflows.

These tests verify that the entire system works from data import, cleaning,
processing, model training, to making predictions. They simulate realistic user
workflows, including handling multiple departments and data refresh scenarios.

Each test ensures that:
- Files are correctly created at each stage.
- Data transformations maintain integrity.
- Models can be trained and produce valid predictions.
"""

from pathlib import Path

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
    """Integration tests for complete user journey: data import -> cleaning -> processing -> training -> prediction."""

    def test_complete_workflow_data_import_to_prediction(self, temp_data_dir: Path, sample_raw_csv_file: Path) -> None:
        """
        Test the full workflow from raw data to prediction.

        Steps verified:
        1. Cleaning raw CSV data and creating cleaned files.
        2. Processing cleaned data and creating processed files.
        3. Loading cleaned data for model training.
        4. Preparing features and target column for model.
        5. Training a Random Forest model and saving it.
        6. Making a prediction using the trained model.

        Assertions:
        - All expected files are created.
        - Model training completes successfully.
        - Prediction output is a non-negative float.
        """
        raw_path: Path = temp_data_dir / "raw"
        cleaned_path: Path = temp_data_dir / "cleaned"
        processed_path: Path = temp_data_dir / "processed"
        model_path: Path = temp_data_dir / "complete_workflow_model.joblib"

        # Step 1: Clean raw data
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        cleaned_file: Path = cleaned_path / "cleaned2024" / "cleaned_75_2024.csv"
        assert cleaned_file.exists(), "Cleaned file should be created"

        # Step 2: Process cleaned data
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)
        processed_file: Path = processed_path / "processed2024" / "processed_75_2024.csv"
        assert processed_file.exists(), "Processed file should be created"

        # Step 3: Load cleaned data for training
        df: pd.DataFrame = load_data_from_folder(str(cleaned_path / "cleaned2024"), pattern="*.csv")
        assert len(df) > 0, "Should load data for training"

        # Step 4: Prepare features and target
        target_col: str = "property_value"
        df = prepare_target(df, target_col)
        cat_cols: list[str] = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols: list[str] = ["building_area", "main_rooms", "land_area"]
        feature_cols: list[str] = cat_cols + num_cols

        required_cols: list[str] = feature_cols + [target_col]
        df = df[required_cols].dropna()
        if len(df) == 0:
            pytest.skip("No valid data for training after filtering")

        # Step 5: Train and save model
        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))
        assert model_path.exists(), "Model should be saved"

        # Step 6: Make prediction
        if len(X_test) > 0:
            test_input: dict = X_test.iloc[0].to_dict()
            input_data: dict = {
                "building_area": float(test_input.get("building_area", 43.0)),
                "main_rooms": int(test_input.get("main_rooms", 2)),
                "land_area": float(test_input.get("land_area", 69.0)),
                "postal_code": int(test_input.get("postal_code", 75002)),
                "property_type_code": int(test_input.get("property_type_code", 2)),
                "town_code": int(test_input.get("town_code", 102)),
                "department_code": int(test_input.get("department_code", 75)),
            }
        else:
            input_data = {
                "building_area": 43.0,
                "main_rooms": 2,
                "land_area": 69.0,
                "postal_code": 75002,
                "property_type_code": 2,
                "town_code": 102,
                "department_code": 75,
            }

        predicted_price: float = predict_price(model_path=str(model_path), input_data=input_data)
        assert isinstance(predicted_price, float), "Prediction should be a float"
        assert not pd.isna(predicted_price), "Prediction should not be NaN"
        assert predicted_price >= 0, "Prediction should be non-negative"

    def test_complete_workflow_with_multiple_departments(self, temp_data_dir: Path, sample_raw_csv_file: Path) -> None:
        """
        Test full workflow using data from multiple departments.

        Ensures:
        - Cleaning and processing work across multiple department datasets.
        - Model training includes all departments.
        - Prediction is possible for arbitrary department input.
        """
        raw_path: Path = temp_data_dir / "raw"
        cleaned_path: Path = temp_data_dir / "cleaned"
        processed_path: Path = temp_data_dir / "processed"
        model_path: Path = temp_data_dir / "multi_dept_model.joblib"

        # Add raw data for another department
        raw_2024_dir: Path = raw_path / "raw2024"
        raw_77_file: Path = raw_2024_dir / "raw_77_2024.csv"
        raw_77_data: str = """date_mutation,nature_mutation,valeur_fonciere,code_postal,commune,code_departement,\
code_commune,code_type_local,type_local,surface_reelle_bati,nombre_pieces_principales,surface_terrain
15/06/2024,Vente,250000,77000,MELUN,77,77288,2,Appartement,60,3,100"""
        raw_77_file.write_text(raw_77_data, encoding="utf-8")

        # Clean, process, and load all data
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)
        df: pd.DataFrame = load_all_csv(data_root=str(cleaned_path))
        assert len(df) > 0, "Should load data from multiple departments"

        # Prepare features and train model
        target_col: str = "property_value"
        df = prepare_target(df, target_col)
        cat_cols: list[str] = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols: list[str] = ["building_area", "main_rooms", "land_area"]
        feature_cols: list[str] = cat_cols + num_cols

        required_cols: list[str] = feature_cols + [target_col]
        df = df[required_cols].dropna()
        if len(df) == 0:
            pytest.skip("No valid data for training")

        X_train, X_test, y_train, y_test = split_features_target(df, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))

        # Make a prediction
        input_data: dict = {
            "building_area": 60.0,
            "main_rooms": 3,
            "land_area": 100.0,
            "postal_code": 77000,
            "property_type_code": 2,
            "town_code": 77288,
            "department_code": 77,
        }
        predicted_price: float = predict_price(model_path=str(model_path), input_data=input_data)
        assert isinstance(predicted_price, float), "Prediction should be a float"
        assert not pd.isna(predicted_price), "Prediction should not be NaN"

    def test_complete_workflow_data_refresh(self, temp_data_dir: Path, sample_raw_csv_file: Path) -> None:
        """
        Test the workflow handles new incoming data (data refresh scenario).

        Verifies:
        - Cleaning, processing, and training work after adding new data.
        - Updated dataset has increased or equal rows.
        - Model can produce predictions after data refresh.
        """
        raw_path: Path = temp_data_dir / "raw"
        cleaned_path: Path = temp_data_dir / "cleaned"
        processed_path: Path = temp_data_dir / "processed"
        model_path: Path = temp_data_dir / "refresh_model.joblib"

        # Initial import, cleaning, processing
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)

        df_initial: pd.DataFrame = load_all_csv(data_root=str(cleaned_path))
        assert len(df_initial) > 0, "Should load initial data"

        # Add new raw data for refresh
        raw_2024_dir: Path = raw_path / "raw2024"
        new_raw_file: Path = raw_2024_dir / "raw_92_2024.csv"
        new_raw_data: str = """date_mutation,nature_mutation,valeur_fonciere,code_postal,commune,code_departement,\
code_commune,code_type_local,type_local,surface_reelle_bati,nombre_pieces_principales,surface_terrain
20/06/2024,Vente,500000,92000,COURBEVOIE,92,92026,2,Appartement,70,4,80"""
        new_raw_file.write_text(new_raw_data, encoding="utf-8")

        # Clean, process, and load updated data
        clean_data(raw_path=raw_path, cleaned_path=cleaned_path)
        process_data(cleaned_path=cleaned_path, processed_path=processed_path)
        df_updated: pd.DataFrame = load_all_csv(data_root=str(cleaned_path))
        assert len(df_updated) >= len(df_initial), "Updated data should have more or equal rows"

        # Prepare features and train model
        target_col: str = "property_value"
        df_updated = prepare_target(df_updated, target_col)
        cat_cols: list[str] = ["postal_code", "department_code", "town_code", "property_type_code"]
        num_cols: list[str] = ["building_area", "main_rooms", "land_area"]
        feature_cols: list[str] = cat_cols + num_cols
        required_cols: list[str] = feature_cols + [target_col]
        df_updated = df_updated[required_cols].dropna()
        if len(df_updated) == 0:
            pytest.skip("No valid data for training")

        X_train, X_test, y_train, y_test = split_features_target(df_updated, target_col, feature_cols)
        preprocessor = build_preprocessor(cat_cols, num_cols)
        model = build_random_forest(preprocessor)
        trained_model = train_model(model, X_train, y_train)
        save_model(trained_model, str(model_path))
        assert model_path.exists(), "Model should be saved"

        # Make prediction
        input_data: dict = {
            "building_area": 70.0,
            "main_rooms": 4,
            "land_area": 80.0,
            "postal_code": 92000,
            "property_type_code": 2,
            "town_code": 92026,
            "department_code": 92,
        }
        predicted_price: float = predict_price(model_path=str(model_path), input_data=input_data)
        assert isinstance(predicted_price, float), "Prediction should be a float"
        assert not pd.isna(predicted_price), "Prediction should not be NaN"
