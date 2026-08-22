"""
End-to-End Tests for FastAPI Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_and_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] in ["running", "online"]

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"


def test_get_fleet_and_routes():
    # Fleet
    res_fleet = client.get("/api/fleet/vehicles")
    assert res_fleet.status_code == 200
    fleet_data = res_fleet.json()
    assert len(fleet_data) >= 5

    # Routes
    res_routes = client.get("/api/fleet/routes")
    assert res_routes.status_code == 200
    routes_data = res_routes.json()
    assert len(routes_data) >= 5


def test_forecasting_endpoint():
    payload = {
        "vehicles": [
            {
                "vehicle_id": "V001",
                "vehicle_type": "Van",
                "fuel_type": "Hybrid",
                "vehicle_age": 1,
                "fuel_capacity_l": 65.0,
                "max_payload_kg": 1200.0,
                "available": True,
            }
        ],
        "routes": [
            {
                "route_id": "R001",
                "origin": "Depot Central",
                "destination": "Downtown Hub",
                "distance_km": 30.0,
                "required_payload_kg": 750.0,
                "traffic_factor": 1.1,
                "priority": 2,
            }
        ],
    }
    res = client.post("/api/forecast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_predictions"] == 1
    assert data["predictions"][0]["predicted_fuel_l"] > 0
    assert data["predictions"][0]["estimated_co2_kg"] > 0


def test_scoring_endpoint():
    payload = {
        "vehicles": [
            {
                "vehicle_id": "V001",
                "vehicle_type": "Van",
                "fuel_type": "Hybrid",
                "vehicle_age": 1,
                "fuel_capacity_l": 65.0,
                "max_payload_kg": 1200.0,
                "available": True,
            }
        ],
        "routes": [
            {
                "route_id": "R001",
                "origin": "Depot Central",
                "destination": "Downtown Hub",
                "distance_km": 30.0,
                "required_payload_kg": 750.0,
                "traffic_factor": 1.2,
                "priority": 2,
            }
        ],
    }
    res = client.post("/api/scoring", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_scores"] == 1
    score_obj = data["scores"][0]
    assert 0 <= score_obj["overall_score"] <= 100
    assert "fuel_efficiency" in score_obj["breakdown"]


def test_optimize_endpoint():
    payload = {
        "vehicles": [
            {
                "vehicle_id": "V001",
                "vehicle_type": "Van",
                "fuel_type": "Hybrid",
                "vehicle_age": 1,
                "fuel_capacity_l": 65.0,
                "max_payload_kg": 1200.0,
                "available": True,
            },
            {
                "vehicle_id": "V002",
                "vehicle_type": "Truck",
                "fuel_type": "Diesel",
                "vehicle_age": 3,
                "fuel_capacity_l": 180.0,
                "max_payload_kg": 8000.0,
                "available": True,
            },
        ],
        "routes": [
            {
                "route_id": "R001",
                "origin": "Depot Central",
                "destination": "Downtown Hub",
                "distance_km": 30.0,
                "required_payload_kg": 750.0,
                "traffic_factor": 1.1,
                "priority": 1,
            }
        ],
        "method": "quantum_inspired",
    }
    res = client.post("/api/optimize/assign", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["solver_status"] in ["OPTIMAL", "FEASIBLE_PARTIAL"]
    assert len(data["assignments"]) == 1
    assert data["total_fuel_l"] > 0


def test_simulation_demo_flow():
    """
    Simulates the exact hackathon demo flow:
    Reset -> Normal State -> Peak Scenario -> Optimize -> Benchmark
    """
    # 1. Reset
    res_reset = client.post("/api/simulate/reset")
    assert res_reset.status_code == 200
    reset_data = res_reset.json()
    assert reset_data["scenario"] == "normal"
    assert reset_data["vehicles_count"] == 20
    assert reset_data["routes_count"] == 12

    # 2. Peak Demand Scenario
    res_peak = client.post("/api/simulate/peak")
    assert res_peak.status_code == 200
    peak_data = res_peak.json()
    assert peak_data["scenario"] == "peak_demand"
    assert peak_data["routes_count"] == 15

    # 3. Run Optimization
    res_opt = client.post("/api/simulate/optimize")
    assert res_opt.status_code == 200
    opt_data = res_opt.json()
    assert opt_data["benchmark"] is not None
    assert opt_data["benchmark"]["fuel_saved_l"] >= 0.0

    # 4. Get Benchmark
    res_bench = client.get("/api/benchmark")
    assert res_bench.status_code == 200
    bench = res_bench.json()
    assert bench["scenario"] == "peak_demand"
    assert bench["baseline"]["total_fuel_l"] > 0
    assert bench["greenflow"]["total_fuel_l"] > 0
    assert "fuel_saved_pct" in bench
