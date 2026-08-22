"""
GreenFleet AI - ML Prediction API Router
========================================
Batch prediction endpoints for Vehicle Fuel/Energy Consumption and CO2 Emissions.
Integrates Person 2's trained LightGBM ML Engine.
"""

import logging
from typing import List
from fastapi import APIRouter
from backend.app.models.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    Prediction,
    VehiclePair,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["ML Prediction"])

# Attempt to load Person 2's ML Engine
ML_AVAILABLE = False
try:
    from ml_engine.predict import predict_trip
    ML_AVAILABLE = True
except Exception as e:
    logger.warning(f"ML engine could not be loaded: {e}. Using fallback physics predictor.")


def _calculate_stub_prediction(pair: VehiclePair) -> Prediction:
    """
    Fallback deterministic physics-based prediction estimation.
    """
    v = pair.vehicle
    r = pair.route

    base_rate = {
        "Diesel": 28.0 if "Truck" in v.vehicle_type else 12.0,
        "Electric": 20.0,
        "Petrol": 14.0,
        "Hybrid": 10.0,
        "CNG": 16.0,
    }.get(v.fuel_type, 20.0)

    emission_factor = {
        "Diesel": 2.68,
        "Electric": 0.45,
        "Petrol": 2.31,
        "Hybrid": 1.50,
        "CNG": 1.80,
    }.get(v.fuel_type, 2.50)

    payload_ratio = min(1.0, r.required_payload_kg / max(1.0, v.max_payload_kg))
    payload_multiplier = 1.0 + (0.35 * payload_ratio)
    age_multiplier = 1.0 + (0.01 * v.vehicle_age)

    pred_fuel = (r.distance_km / 100.0) * base_rate * r.traffic_factor * payload_multiplier * age_multiplier
    pred_fuel = round(pred_fuel, 2)
    pred_co2 = round(pred_fuel * emission_factor, 2)

    return Prediction(
        vehicle_id=v.vehicle_id,
        route_id=r.route_id,
        predicted_fuel_l=pred_fuel,
        estimated_co2_kg=pred_co2,
    )


@router.post("/batch", response_model=BatchPredictionResponse)
def batch_predict(request: BatchPredictionRequest):
    """
    Evaluate fuel consumption and CO2 emissions for a batch of candidate (Vehicle, Route) pairs.
    Uses Person 2's trained LightGBM ML model artifact.
    """
    predictions: List[Prediction] = []
    for pair in request.pairs:
        if ML_AVAILABLE:
            try:
                v_dict = pair.vehicle.model_dump()
                r_dict = pair.route.model_dump()
                res = predict_trip(v_dict, r_dict)
                pred = Prediction(
                    vehicle_id=res["vehicle_id"],
                    route_id=res["route_id"],
                    predicted_fuel_l=float(res["predicted_fuel_l"]),
                    estimated_co2_kg=float(res["estimated_co2_kg"]),
                )
                predictions.append(pred)
                continue
            except Exception as ex:
                logger.debug(f"Inference error on pair ({pair.vehicle.vehicle_id}, {pair.route.route_id}): {ex}")

        # Fallback if ML inference not available
        predictions.append(_calculate_stub_prediction(pair))

    return BatchPredictionResponse(
        predictions=predictions,
        total_evaluated=len(predictions),
    )
