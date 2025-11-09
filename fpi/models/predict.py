import joblib
import pandas as pd


def predict_price(model_path: str, input_data: dict[str, float]) -> float:
    """
    Predict property price using a trained Random Forest pipeline.

    Args:
        model_path (str): Path to the trained pipeline (.joblib file).
        input_data (Dict[str, float]): Dictionary of property features.
            Expected keys: 'building_area', 'main_rooms', 'land_area',
            'postal_code', 'property_type_code', 'town_code', 'department_code'.

    Returns:
        float: Predicted property price in euros.
    """
    # Load the trained pipeline
    model = joblib.load(model_path)

    # Convert input dictionary to DataFrame
    df = pd.DataFrame([input_data])

    # Predict using the pipeline (handles one-hot encoding internally)
    prediction = model.predict(df)

    # Return the single prediction as float
    return float(prediction[0])


def mock_predict_price() -> None:
    """
    Mock prediction using a hardcoded property input.

    Prints:
        The predicted property price in euros.
    """
    example_input: dict[str, float | int] = {
        "building_area": 13.0,
        "main_rooms": 1,
        "land_area": 20.0,
        "postal_code": 75020,
        "property_type_code": 2,
        "town_code": 120,
        "department_code": 75,
    }

    # Update to the Random Forest model path
    model_path: str = "fpi/models/random_forest.joblib"

    predicted_price: float = predict_price(model_path=model_path, input_data=example_input)
    print(f"Mock predicted price: €{predicted_price:,.0f}")
