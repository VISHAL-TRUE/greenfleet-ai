"""
Tests for Data Models & Pydantic Validation
"""

import pytest
from pydantic import ValidationError
from backend.app.models.vehicle import VehicleModel
from backend.app.models.route import RouteModel
from backend.app.models.assignment import (
    PredictionModel,
    AssignmentModel,
    OptimizationConfigModel,
)
from backend.app.models.simulation import ScenarioType, ScoreBreakdown, VehicleRouteScore


def test_vehicle_model_validation():
    # Valid vehicle
    v = VehicleModel(
        vehicle_id="V001",
        vehicle_type="Van",
        fuel_type="Hybrid",
        vehicle_age=2,
        fuel_capacity_l=65.0,
        max_payload_kg=1200.0,
        available=True,
    )
    assert v.vehicle_id == "V001"
    assert v.available is True

    # Invalid payload <= 0
    with pytest.raises(ValidationError):
        VehicleModel(
            vehicle_id="V002",
            vehicle_type="Van",
            fuel_type="Diesel",
            vehicle_age=1,
            fuel_capacity_l=60.0,
            max_payload_kg=-100.0,
        )


def test_route_model_validation():
    # Valid route
    r = RouteModel(
        route_id="R001",
        origin="Depot North",
        destination="Zone A",
        distance_km=45.0,
        required_payload_kg=800.0,
        traffic_factor=1.2,
        priority=3,
    )
    assert r.route_id == "R001"
    assert r.priority == 3

    # Invalid distance <= 0
    with pytest.raises(ValidationError):
        RouteModel(
            route_id="R002",
            origin="Depot North",
            destination="Zone B",
            distance_km=0.0,
            required_payload_kg=500.0,
        )


def test_prediction_and_assignment_models():
    p = PredictionModel(
        vehicle_id="V001",
        route_id="R001",
        predicted_fuel_l=14.5,
        estimated_co2_kg=33.5,
    )
    assert p.predicted_fuel_l == 14.5

    a = AssignmentModel(
        vehicle_id="V001",
        route_id="R001",
        predicted_fuel_l=14.5,
        estimated_co2_kg=33.5,
        operating_cost=42.50,
        status="assigned",
    )
    assert a.status == "assigned"
    assert a.operating_cost == 42.50


def test_optimization_config_defaults():
    config = OptimizationConfigModel()
    assert config.fuel_weight == 1.0
    assert config.initial_temp == 1000.0
    assert config.seed == 42
