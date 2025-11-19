from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fpi.data_pipeline.schemas import PredictionFormSchema
from fpi.models.predict import predict_price

app = FastAPI(title="FPI Backend API")


def map_property_type_to_code(prop_type: str) -> int:
    """
    Convert a human-readable property type string into the numeric code
    expected by the machine learning model.

    Mapping:
        - House / Maison      -> 1
        - Apartment / Flat    -> 2
        - Other / Autre       -> 3
        - Land / Terrain      -> 4

    Any unknown value defaults to 1.

    Args:
        prop_type (str): The user-provided property type string.

    Returns:
        int: The corresponding numeric code.
    """
    normalized = prop_type.strip().lower()
    if normalized in {"house", "maison"}:
        return 1
    if normalized in {"apartment", "flat", "appartement"}:
        return 2
    if normalized in {"other", "autre"}:
        return 3
    if normalized in {"land", "terrain"}:
        return 4
    return 1


class PredictionResponse(BaseModel):
    """Response model returned by the /predict endpoint."""

    predicted_price: float


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionFormSchema) -> PredictionResponse:
    """
    Predict the sale price of a property using a trained model.

    This endpoint:
    1. Receives user inputs from the frontend (postal, property type, area, rooms, land).
    2. Converts them into the feature dictionary required by the model.
    3. Calls the model prediction function.
    4. Returns a structured response.

    Error handling:
    - ValueError -> 400 Bad Request
    - FileNotFoundError -> 500 Internal Server Error (model missing)
    - Other unexpected exceptions -> 500

    Args:
        request (PredictionFormSchema): Validated Pydantic schema with user inputs.

    Returns:
        PredictionResponse: The predicted property price.
    """

    try:
        model_path: str = "fpi/models/random_forest.joblib"

        # Prepare model input features
        input_data: dict[str, float | int] = {
            "postal_code": int(request.postal),
            "property_type_code": map_property_type_to_code(request.prop_type),
            "building_area": float(request.area),
            "main_rooms": int(request.rooms),
            "land_area": float(request.land),
        }

        prediction_result: float = float(predict_price(model_path=model_path, input_data=input_data))

        return PredictionResponse(predicted_price=prediction_result)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid input value: {ve}")

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Model file not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
