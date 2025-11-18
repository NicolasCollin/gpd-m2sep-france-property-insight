# fpi/backend/loader.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fpi.data_pipeline.schemas import PredictionFormSchema
from fpi.models.predict import predict_price

app = FastAPI(title="FPI Backend API")


def map_property_type_to_code(prop_type: str) -> int:
    """
    Map human-readable property type to the numeric code expected by the model.
    Defaults to 1 (House) if the value is unknown.
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
    predicted_price: float


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionFormSchema) -> PredictionResponse:
    """
    FastAPI endpoint used by the frontend to get a price prediction.

    It receives the same fields as the Gradio form (postal, prop_type, area, rooms, land),
    converts them into the feature dictionary expected by the model, and returns the
    predicted price.
    """
    try:
        model_path = "fpi/models/random_forest.joblib"

        # Map form schema to model features
        input_data = {
            "postal_code": int(request.postal),
            "property_type_code": map_property_type_to_code(request.prop_type),
            "building_area": float(request.area),
            "main_rooms": int(request.rooms),
            "land_area": float(request.land),
        }

        result = predict_price(model_path=model_path, input_data=input_data)
        return PredictionResponse(predicted_price=float(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
