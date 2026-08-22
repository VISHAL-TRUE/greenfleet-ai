"""
Tests for Explainable Scoring Layer
"""

from backend.app.core.scoring import calculate_suitability_score, score_fleet_route_pairs
from backend.app.models.route import RouteModel
from backend.app.models.vehicle import VehicleModel


def test_unavailable_vehicle_score():
    v = VehicleModel(
        vehicle_id="V001",
        vehicle_type="Van",
        fuel_type="Diesel",
        vehicle_age=2,
        fuel_capacity_l=70.0,
        max_payload_kg=1500.0,
        available=False,
    )
    r = RouteModel(
        route_id="R001",
        origin="Depot A",
        destination="Zone 1",
        distance_km=30.0,
        required_payload_kg=800.0,
    )
    score = calculate_suitability_score(v, r)
    assert score.overall_score == 0.0
    assert "Infeasible" in score.recommendation


def test_capacity_shortfall_score():
    v = VehicleModel(
        vehicle_id="V002",
        vehicle_type="Van",
        fuel_type="Hybrid",
        vehicle_age=1,
        fuel_capacity_l=65.0,
        max_payload_kg=1000.0,
        available=True,
    )
    r = RouteModel(
        route_id="R002",
        origin="Depot A",
        destination="Zone 2",
        distance_km=50.0,
        required_payload_kg=3500.0,  # Exceeds max payload
    )
    score = calculate_suitability_score(v, r)
    assert score.overall_score == 0.0
    assert score.breakdown.capacity_match == 0.0
    assert "Capacity Shortfall" in score.recommendation


def test_ideal_hybrid_match():
    v = VehicleModel(
        vehicle_id="V003",
        vehicle_type="Van",
        fuel_type="Hybrid",
        vehicle_age=1,
        fuel_capacity_l=65.0,
        max_payload_kg=1200.0,
        available=True,
    )
    r = RouteModel(
        route_id="R003",
        origin="Depot Central",
        destination="Downtown",
        distance_km=25.0,
        required_payload_kg=850.0,  # ~71% payload utilization
        traffic_factor=1.3,
    )
    score = calculate_suitability_score(v, r, predicted_fuel_l=3.8)
    assert score.overall_score >= 80.0
    assert score.breakdown.traffic_resilience >= 85.0
    assert score.breakdown.capacity_match >= 90.0
    assert score.recommendation in ["Highly Recommended", "Recommended"]
