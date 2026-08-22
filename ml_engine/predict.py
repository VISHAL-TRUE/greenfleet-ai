"""
GreenFleet AI - ML Inference & Decision Support Interface
Provides lightweight, standalone inference functions strictly adhering to GreenFleet JSON contracts.
"""

import os
import sys
from typing import Dict, List, Any, Union, Optional
import joblib
import numpy as np
import pandas as pd

# Ensure ml_engine directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from features import FleetFeatureEngineer

# Standard Greenhouse Gas (GHG) Emission Factors (kg CO2 per litre of fuel)
# References: DEFRA / UK Gov GHG Conversion Factors, US EPA Fleet Standards
EMISSION_FACTORS_KG_CO2_PER_LITRE = {
    "Diesel": 2.68,   # Standard diesel fuel
    "Petrol": 2.31,   # Standard gasoline
    "Hybrid": 2.31,   # Hybrid powertrain gasoline equivalent
    "CNG": 1.95,      # Compressed natural gas (equivalent factor)
    "Default": 2.65,  # Fleet blended average
}

# Global in-memory cache for loaded model
_LOADED_MODEL = None
_DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "models", "fuel_model.pkl"
)


def load_model(model_path: Optional[str] = None):
    """
    Loads the trained fuel consumption model artifact.
    Caches model in memory for high-throughput batch inference.
    """
    global _LOADED_MODEL
    path = model_path or _DEFAULT_MODEL_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model artifact not found at '{path}'. Please train the model using 'python train.py' first."
        )

    _LOADED_MODEL = joblib.load(path)
    return _LOADED_MODEL


def get_model(model_path: Optional[str] = None):
    """Returns the cached model instance or loads it if not already loaded."""
    global _LOADED_MODEL
    if _LOADED_MODEL is None or model_path is not None:
        return load_model(model_path)
    return _LOADED_MODEL


def estimate_co2(fuel_litres: float, fuel_type: str = "Diesel") -> float:
    """
    Estimates carbon dioxide emissions (kg CO2) resulting from fuel combustion.

    Formula:
    --------
    CO2 (kg) = Fuel Consumed (Litres) * Emission Factor (kg CO2 / Litre)

    Emission Factors:
    - Diesel: 2.68 kg CO2 / L
    - Petrol: 2.31 kg CO2 / L
    - Hybrid: 2.31 kg CO2 / L
    - CNG:    1.95 kg CO2 / L
    - Default: 2.65 kg CO2 / L

    Parameters:
    -----------
    fuel_litres : float
        Fuel consumed in litres.
    fuel_type : str, default="Diesel"
        Fuel / engine type of the vehicle.

    Returns:
    --------
    float: Estimated CO2 emissions in kilograms (rounded to 1 or 2 decimal places).
    """
    factor = EMISSION_FACTORS_KG_CO2_PER_LITRE.get(
        fuel_type, EMISSION_FACTORS_KG_CO2_PER_LITRE["Default"]
    )
    co2_kg = float(fuel_litres) * factor
    return round(co2_kg, 1)


def _prepare_inference_row(vehicle: Dict[str, Any], route: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs a feature row from Vehicle and Route JSON contracts:
    - Vehicle contract: { vehicle_id, vehicle_type, fuel_type, vehicle_age, fuel_capacity_l, max_payload_kg, available }
    - Route contract: { route_id, origin, destination, distance_km, required_payload_kg, traffic_factor, priority }
    """
    # Support both fuel_type and legacy engine_type
    fuel_type = vehicle.get("fuel_type") or vehicle.get("engine_type", "Diesel")
    
    # Support both required_payload_kg and legacy load_kg
    required_payload = route.get("required_payload_kg")
    if required_payload is None:
        required_payload = vehicle.get("load_kg", 500.0)
    
    max_payload = vehicle.get("max_payload_kg")
    if max_payload is None:
        type_defaults = {"Van": 1500.0, "Light Commercial": 3500.0, "Truck": 8000.0, "Semi-Trailer": 26000.0, "Bus": 6000.0}
        max_payload = type_defaults.get(vehicle.get("vehicle_type", "Truck"), 5000.0)

    # Route travel characteristics
    distance_km = float(route.get("distance_km", 50.0))
    traffic_factor = float(route.get("traffic_factor", 1.0))
    
    # Optional physics features with sensible operational defaults if omitted by route generator
    avg_speed = route.get("average_speed_kmph")
    if avg_speed is None:
        avg_speed = 70.0 / traffic_factor if distance_km > 60 else 45.0 / traffic_factor
    
    road_grade = float(route.get("road_grade", 0.0))
    weather_factor = float(route.get("weather_factor", 1.0))

    return {
        "vehicle_id": str(vehicle.get("vehicle_id", "V_UNKNOWN")),
        "vehicle_type": str(vehicle.get("vehicle_type", "Truck")),
        "fuel_type": str(fuel_type),
        "vehicle_age": float(vehicle.get("vehicle_age", 3)),
        "fuel_capacity_l": float(vehicle.get("fuel_capacity_l", 180)),
        "max_payload_kg": float(max_payload),
        "available": bool(vehicle.get("available", True)),
        "route_id": str(route.get("route_id", "R_UNKNOWN")),
        "origin": str(route.get("origin", "Depot A")),
        "destination": str(route.get("destination", "Zone 1")),
        "distance_km": distance_km,
        "required_payload_kg": float(required_payload),
        "traffic_factor": traffic_factor,
        "priority": int(route.get("priority", 1)),
        "average_speed_kmph": float(avg_speed),
        "road_grade": road_grade,
        "weather_factor": weather_factor,
    }


def predict_fuel(
    vehicle_data: Dict[str, Any],
    route_data: Dict[str, Any],
    model: Any = None,
) -> float:
    """
    Predicts the fuel consumption in litres for a vehicle assigned to a route.

    Parameters:
    -----------
    vehicle_data : dict
        Vehicle contract JSON
    route_data : dict
        Route contract JSON
    model : Pipeline, optional
        Pre-loaded model pipeline.

    Returns:
    --------
    float: Predicted fuel consumption in litres (rounded to 1 decimal place).
    """
    mdl = model or get_model()
    row = _prepare_inference_row(vehicle_data, route_data)
    df = pd.DataFrame([row])
    pred = mdl.predict(df)[0]
    return round(float(max(0.1, pred)), 1)


def predict_trip(
    vehicle_data: Dict[str, Any],
    route_data: Dict[str, Any],
    model: Any = None,
) -> Dict[str, Any]:
    """
    Generates Prediction JSON contract:
    {
      "vehicle_id": "V001",
      "route_id": "R001",
      "predicted_fuel_l": 18.4,
      "estimated_co2_kg": 48.8
    }
    """
    fuel_l = predict_fuel(vehicle_data, route_data, model=model)
    fuel_type = vehicle_data.get("fuel_type") or vehicle_data.get("engine_type", "Diesel")
    co2_kg = estimate_co2(fuel_l, fuel_type=fuel_type)

    return {
        "vehicle_id": str(vehicle_data.get("vehicle_id", "V001")),
        "route_id": str(route_data.get("route_id", "R001")),
        "predicted_fuel_l": fuel_l,
        "estimated_co2_kg": co2_kg,
    }


def create_assignment(
    vehicle_id: str,
    route_id: str,
    predicted_fuel_l: float,
    status: str = "assigned",
) -> Dict[str, Any]:
    """
    Generates Assignment JSON contract:
    {
      "vehicle_id": "V001",
      "route_id": "R001",
      "predicted_fuel_l": 18.4,
      "status": "assigned"
    }
    """
    return {
        "vehicle_id": str(vehicle_id),
        "route_id": str(route_id),
        "predicted_fuel_l": round(float(predicted_fuel_l), 1),
        "status": str(status),
    }


def build_fuel_cost_matrix(
    vehicles: List[Dict[str, Any]],
    routes: List[Dict[str, Any]],
    model: Any = None,
) -> Dict[str, Dict[str, float]]:
    """
    Constructs the vehicle-route fuel consumption cost matrix for Person 3 (Quantum Optimizer).
    Uses high-performance vectorized batch inference.

    Returns:
    --------
    dict:
        {
            "V001": {
                "R001": 18.4,
                "R002": 24.2
            },
            ...
        }
    """
    mdl = model or get_model()

    if not vehicles or not routes:
        return {}

    batch_records = []
    mapping_indices = []

    for v in vehicles:
        v_id = str(v.get("vehicle_id", "V_UNKNOWN"))
        for r in routes:
            r_id = str(r.get("route_id", "R_UNKNOWN"))
            row = _prepare_inference_row(v, r)
            batch_records.append(row)
            mapping_indices.append((v_id, r_id))

    batch_df = pd.DataFrame(batch_records)
    raw_predictions = mdl.predict(batch_df)

    matrix: Dict[str, Dict[str, float]] = {
        str(v.get("vehicle_id", "V_UNKNOWN")): {} for v in vehicles
    }

    for (v_id, r_id), pred_fuel in zip(mapping_indices, raw_predictions):
        matrix[v_id][r_id] = round(float(max(0.1, pred_fuel)), 1)

    return matrix


def build_trip_cost_matrix(
    vehicles: List[Dict[str, Any]],
    routes: List[Dict[str, Any]],
    model: Any = None,
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Constructs matrix with both predicted_fuel_l and estimated_co2_kg for every vehicle-route pair.
    """
    fuel_matrix = build_fuel_cost_matrix(vehicles, routes, model=model)
    v_fuel_type_lookup = {
        str(v.get("vehicle_id", "V_UNKNOWN")): v.get("fuel_type") or v.get("engine_type", "Diesel")
        for v in vehicles
    }

    full_matrix: Dict[str, Dict[str, Dict[str, float]]] = {}
    for v_id, routes_dict in fuel_matrix.items():
        full_matrix[v_id] = {}
        f_type = v_fuel_type_lookup.get(v_id, "Diesel")
        for r_id, fuel_val in routes_dict.items():
            full_matrix[v_id][r_id] = {
                "predicted_fuel_l": fuel_val,
                "estimated_co2_kg": estimate_co2(fuel_val, fuel_type=f_type),
            }

    return full_matrix


if __name__ == "__main__":
    import json

    # Direct test with user JSON contracts
    sample_vehicle = {
        "vehicle_id": "V001",
        "vehicle_type": "Truck",
        "fuel_type": "Diesel",
        "vehicle_age": 4,
        "fuel_capacity_l": 180,
        "max_payload_kg": 5000,
        "available": True,
    }

    sample_route = {
        "route_id": "R001",
        "origin": "Depot A",
        "destination": "Zone 1",
        "distance_km": 42.5,
        "required_payload_kg": 3200,
        "traffic_factor": 1.2,
        "priority": 2,
    }

    print("[GreenFleet ML] Contract Testing...")
    pred_contract = predict_trip(sample_vehicle, sample_route)
    print("\n--- Prediction Contract ---")
    print(json.dumps(pred_contract, indent=2))

    assign_contract = create_assignment(
        pred_contract["vehicle_id"],
        pred_contract["route_id"],
        pred_contract["predicted_fuel_l"],
        status="assigned",
    )
    print("\n--- Assignment Contract ---")
    print(json.dumps(assign_contract, indent=2))
