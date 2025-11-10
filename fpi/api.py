# fpi/backend/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fpi.models.predict import predict_price

app = FastAPI(title="FPI Backend API")


class PredictionRequest(BaseModel):
    postal_code: int
    property_type_code: int
    building_area: float
    main_rooms: int
    land_area: float


@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        model_path = "fpi/models/random_forest.joblib"
        result = predict_price(model_path=model_path, input_data=request.dict())
        return {"predicted_price": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
