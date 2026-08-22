"""
GreenFlow AI - Scenario Generators
Generates deterministic stress scenarios (Normal, Peak Demand, High Traffic).
"""

from typing import List, Tuple
from backend.app.models.route import RouteModel
from backend.app.models.simulation import ScenarioType
from backend.app.models.vehicle import VehicleModel
from .dataset import get_initial_fleet, get_initial_routes


def generate_scenario(scenario_type: ScenarioType) -> Tuple[List[VehicleModel], List[RouteModel]]:
    """
    Returns (vehicles, routes) for the specified scenario.
    """
    vehicles = [v.model_copy(deep=True) for v in get_initial_fleet()]
    routes = [r.model_copy(deep=True) for r in get_initial_routes()]

    if scenario_type == ScenarioType.NORMAL:
        return vehicles, routes

    elif scenario_type == ScenarioType.PEAK_DEMAND:
        # 1. Stress existing route payloads by +15% to +30% to force tight vehicle matching
        for r in routes:
            if r.route_id in ["R001", "R002", "R012"]:
                r.required_payload_kg = round(r.required_payload_kg * 1.25, 1)
            elif r.route_id in ["R003", "R004", "R005"]:
                r.required_payload_kg = round(r.required_payload_kg * 1.15, 1)
            elif r.route_id in ["R006", "R007", "R008"]:
                r.required_payload_kg = round(r.required_payload_kg * 1.20, 1)
            elif r.route_id == "R009":
                r.required_payload_kg = 8900.0  # Fits V014 (9500kg)
            elif r.route_id == "R010":
                r.required_payload_kg = 22500.0  # Fits Semis (24t-26t)
            elif r.route_id == "R011":
                r.required_payload_kg = 24500.0  # Fits Semis (26t)
            else:
                r.required_payload_kg = round(r.required_payload_kg * 1.20, 1)

        # 2. Inject 3 additional high-priority peak surge routes (total 15 routes for 18 available vehicles)
        peak_routes = [
            RouteModel(
                route_id="R013_PEAK",
                origin="Depot West",
                destination="Emergency Medical Hub",
                distance_km=62.0,
                required_payload_kg=2800.0,
                traffic_factor=1.20,
                priority=5,
                time_window="07:00-10:00",
            ),
            RouteModel(
                route_id="R014_PEAK",
                origin="Depot Central",
                destination="Urgent Retail Replenishment",
                distance_km=48.0,
                required_payload_kg=1100.0,
                traffic_factor=1.35,
                priority=4,
                time_window="08:00-11:00",
            ),
            RouteModel(
                route_id="R015_PEAK",
                origin="Depot South",
                destination="Automotive Component Assembly",
                distance_km=110.0,
                required_payload_kg=6800.0,
                traffic_factor=1.10,
                priority=4,
                time_window="06:30-13:30",
            ),
        ]
        routes.extend(peak_routes)
        return vehicles, routes

    elif scenario_type == ScenarioType.HIGH_TRAFFIC:
        # Increase traffic factors on urban/arterial delivery routes significantly
        for r in routes:
            if "Urban" in r.destination or "Metro" in r.destination or "Tech" in r.destination:
                r.traffic_factor = 1.75
            elif "District" in r.destination or "Airport" in r.destination:
                r.traffic_factor = 1.60
            else:
                r.traffic_factor = min(2.5, round(r.traffic_factor * 1.35, 2))
        return vehicles, routes

    else:
        return vehicles, routes
