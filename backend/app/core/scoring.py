"""
GreenFlow AI - Explainable Multi-Factor Scoring Layer
Provides explainable suitability breakdown for Vehicle-Route pairs.
"""

from typing import Dict, List, Any
from ..models.vehicle import VehicleModel
from ..models.route import RouteModel
from ..models.simulation import ScoreBreakdown, VehicleRouteScore


def calculate_suitability_score(
    vehicle: VehicleModel,
    route: RouteModel,
    predicted_fuel_l: float = None,
) -> VehicleRouteScore:
    """
    Computes an explainable 5-factor suitability score (0-100) for assigning
    a vehicle to a specific route.
    """
    # 1. Availability check (Hard constraint)
    if not vehicle.available:
        breakdown = ScoreBreakdown(
            fuel_efficiency=0.0,
            capacity_match=0.0,
            distance_suitability=0.0,
            traffic_resilience=0.0,
            availability=0.0,
        )
        return VehicleRouteScore(
            vehicle_id=vehicle.vehicle_id,
            route_id=route.route_id,
            overall_score=0.0,
            breakdown=breakdown,
            recommendation="Infeasible (Vehicle Unavailable)",
        )

    # 2. Capacity Matching (Hard constraint + Right-sizing)
    if vehicle.max_payload_kg < route.required_payload_kg:
        # Overload violation
        capacity_score = 0.0
    else:
        # Payload utilization ratio
        utilization = route.required_payload_kg / max(vehicle.max_payload_kg, 1.0)
        if 0.50 <= utilization <= 0.95:
            # Ideal right-sized allocation
            capacity_score = 90.0 + (utilization * 10.0)
        elif utilization > 0.95:
            # Near capacity limit
            capacity_score = 80.0
        elif 0.20 <= utilization < 0.50:
            # Moderate under-utilization
            capacity_score = 65.0 + (utilization * 40.0)
        else:
            # Extreme overkill (e.g. 26t Semi-trailer assigned to 300kg cargo)
            capacity_score = max(20.0, utilization * 100.0)

    # 3. Fuel Efficiency Score
    # Hybrids and newer engines have highest inherent efficiency
    powertrain_base = {
        "Hybrid": 95.0,
        "CNG": 85.0,
        "Petrol": 75.0,
        "Diesel": 70.0,
    }.get(vehicle.fuel_type, 70.0)
    
    # Age penalty (-3 pts per year of vehicle age)
    age_penalty = min(25.0, vehicle.vehicle_age * 3.0)
    fuel_eff_score = max(20.0, powertrain_base - age_penalty)

    # If predicted fuel is supplied, adjust based on fuel per km
    if predicted_fuel_l and route.distance_km > 0:
        l_per_100km = (predicted_fuel_l / route.distance_km) * 100.0
        if l_per_100km < 12.0:
            fuel_eff_score = min(100.0, fuel_eff_score + 10.0)
        elif l_per_100km > 35.0:
            fuel_eff_score = max(20.0, fuel_eff_score - 15.0)

    # 4. Distance & Range Suitability
    # Check if vehicle has sufficient fuel capacity with safe reserve (30%)
    est_fuel = predicted_fuel_l if predicted_fuel_l else (route.distance_km * 0.25)
    fuel_tank_margin = vehicle.fuel_capacity_l / max(est_fuel, 1.0)
    
    if fuel_tank_margin < 1.2:
        distance_score = 30.0  # High risk of running out
    elif fuel_tank_margin < 2.0:
        distance_score = 75.0
    else:
        # Distance-type alignment: Long hauls (>100km) favor heavy trucks/semis, short trips favor vans
        if route.distance_km > 100 and vehicle.vehicle_type in ["Truck", "Semi-Trailer"]:
            distance_score = 95.0
        elif route.distance_km <= 50 and vehicle.vehicle_type in ["Van", "Light Commercial"]:
            distance_score = 95.0
        else:
            distance_score = 80.0

    # 5. Traffic Resilience
    # Stop-and-go traffic (traffic_factor > 1.2) heavily penalizes heavy diesel engines,
    # but hybrids and lighter vehicles regenerate/idle efficiently.
    if route.traffic_factor > 1.2:
        if vehicle.fuel_type == "Hybrid":
            traffic_score = 92.0
        elif vehicle.vehicle_type in ["Van", "Light Commercial"]:
            traffic_score = 80.0 - ((route.traffic_factor - 1.0) * 15.0)
        else:
            traffic_score = max(25.0, 70.0 - ((route.traffic_factor - 1.0) * 35.0))
    else:
        traffic_score = 90.0

    availability_score = 100.0

    # Overall Composite Score Calculation
    # Weights: Capacity Match (0.30), Fuel Efficiency (0.25), Distance (0.15), Traffic (0.15), Availability (0.15)
    if capacity_score == 0.0:
        overall = 0.0
        rec = "Infeasible (Capacity Shortfall)"
    else:
        overall = (
            (capacity_score * 0.30)
            + (fuel_eff_score * 0.25)
            + (distance_score * 0.15)
            + (traffic_score * 0.15)
            + (availability_score * 0.15)
        )
        overall = round(max(0.0, min(100.0, overall)), 1)
        
        if overall >= 85.0:
            rec = "Highly Recommended"
        elif overall >= 70.0:
            rec = "Recommended"
        elif overall >= 50.0:
            rec = "Acceptable"
        else:
            rec = "Suboptimal"

    breakdown = ScoreBreakdown(
        fuel_efficiency=round(fuel_eff_score, 1),
        capacity_match=round(capacity_score, 1),
        distance_suitability=round(distance_score, 1),
        traffic_resilience=round(traffic_score, 1),
        availability=round(availability_score, 1),
    )

    return VehicleRouteScore(
        vehicle_id=vehicle.vehicle_id,
        route_id=route.route_id,
        overall_score=overall,
        breakdown=breakdown,
        recommendation=rec,
    )


def score_fleet_route_pairs(
    vehicles: List[VehicleModel],
    routes: List[RouteModel],
    predictions_dict: Dict[tuple, float] = None,
) -> List[VehicleRouteScore]:
    """Scores all vehicle-route combinations."""
    scores = []
    for v in vehicles:
        for r in routes:
            pred_fuel = None
            if predictions_dict:
                pred_fuel = predictions_dict.get((v.vehicle_id, r.route_id))
            score = calculate_suitability_score(v, r, predicted_fuel_l=pred_fuel)
            scores.append(score)
    return scores
