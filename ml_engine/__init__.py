"""
GreenFleet AI - ML Engine Package
Machine Learning Fuel Consumption Prediction & Matrix Generation for Green Fleet Optimization.
"""

from .predict import (
    load_model,
    get_model,
    predict_fuel,
    predict_trip,
    estimate_co2,
    build_fuel_cost_matrix,
    build_trip_cost_matrix,
    EMISSION_FACTORS_KG_CO2_PER_LITRE,
)

__all__ = [
    "load_model",
    "get_model",
    "predict_fuel",
    "predict_trip",
    "estimate_co2",
    "build_fuel_cost_matrix",
    "build_trip_cost_matrix",
    "EMISSION_FACTORS_KG_CO2_PER_LITRE",
]
