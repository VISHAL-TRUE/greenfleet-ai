"""
GreenFlow AI - Forecasting API Router
"""

from fastapi import APIRouter, HTTPException
from backend.app.core.integration import predict_fuel_and_co2
from backend.app.models.assignment import ForecastRequest, ForecastResponse

router = APIRouter(prefix="/forecast", tags=["Forecasting"])


@router.post("", response_model=ForecastResponse, summary="Predict fuel consumption and CO2 emissions")
def generate_forecast(payload: ForecastRequest):
    """
    Generates predicted fuel (L) and estimated CO2 (kg) for all vehicle-route combinations
    using Person 1's machine learning model (or physics fallback).
    """
    if not payload.vehicles:
        raise HTTPException(status_code=400, detail="Vehicle list cannot be empty")
    if not payload.routes:
        raise HTTPException(status_code=400, detail="Route list cannot be empty")
        
    predictions = predict_fuel_and_co2(payload.vehicles, payload.routes)
    
    return ForecastResponse(
        total_predictions=len(predictions),
        predictions=predictions,
    )
