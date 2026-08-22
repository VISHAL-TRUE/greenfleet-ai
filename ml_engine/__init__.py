"""
GreenFlow AI - ML Engine Package
Machine Learning Fuel Consumption Prediction, Real-Time Telemetry Intelligence,
Behavior Detection, Fuel Waste Estimation, and Driver Coaching Alerts.
"""

from .predict import (
    load_model,
    get_model,
    predict_fuel,
    predict_trip,
    create_assignment,
    estimate_co2,
    build_fuel_cost_matrix,
    build_trip_cost_matrix,
    EMISSION_FACTORS_KG_CO2_PER_LITRE,
    # Real-Time Telemetry Intelligence
    predict_fuel_consumption,
    estimate_fuel_waste,
    estimate_remaining_range,
    process_telemetry,
)

__all__ = [
    "load_model",
    "get_model",
    "predict_fuel",
    "predict_trip",
    "create_assignment",
    "estimate_co2",
    "build_fuel_cost_matrix",
    "build_trip_cost_matrix",
    "EMISSION_FACTORS_KG_CO2_PER_LITRE",
    "predict_fuel_consumption",
    "estimate_fuel_waste",
    "estimate_remaining_range",
    "process_telemetry",
]
