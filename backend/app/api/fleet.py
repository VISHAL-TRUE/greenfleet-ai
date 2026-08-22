"""
GreenFleet AI - Fleet & Route Management API Router
===================================================
Endpoints to fetch, list, and register Vehicles and Routes.
"""

import json
import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import Vehicle, Route

router = APIRouter(prefix="/fleet", tags=["Fleet & Routes"])

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _load_sample_vehicles() -> List[Vehicle]:
    filepath = os.path.join(DATA_DIR, "sample_vehicles.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Vehicle(**v) for v in data]
    return []


def _load_sample_routes() -> List[Route]:
    filepath = os.path.join(DATA_DIR, "sample_routes.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Route(**r) for r in data]
    return []


# In-memory storage seeded with canonical samples
_vehicles_store: List[Vehicle] = _load_sample_vehicles()
_routes_store: List[Route] = _load_sample_routes()


@router.get("/vehicles", response_model=List[Vehicle])
def get_vehicles(
    available_only: Optional[bool] = None,
    vehicle_type: Optional[str] = None,
):
    """Retrieve list of registered fleet vehicles."""
    vehicles = _vehicles_store
    if isinstance(available_only, bool):
        vehicles = [v for v in vehicles if v.available == available_only]
    if isinstance(vehicle_type, str) and vehicle_type:
        vehicles = [v for v in vehicles if v.vehicle_type.lower() == vehicle_type.lower()]
    return vehicles


@router.post("/vehicles", response_model=Vehicle, status_code=201)
def add_vehicle(vehicle: Vehicle):
    """Add a new vehicle to the fleet registry."""
    for v in _vehicles_store:
        if v.vehicle_id == vehicle.vehicle_id:
            raise HTTPException(status_code=409, detail=f"Vehicle {vehicle.vehicle_id} already exists.")
    _vehicles_store.append(vehicle)
    return vehicle


@router.get("/routes", response_model=List[Route])
def get_routes(
    min_priority: Optional[int] = None,
):
    """Retrieve list of demand routes."""
    routes = _routes_store
    if isinstance(min_priority, int):
        routes = [r for r in routes if r.priority >= min_priority]
    return routes


@router.post("/routes", response_model=Route, status_code=201)
def add_route(route: Route):
    """Add a new route requiring assignment."""
    for r in _routes_store:
        if r.route_id == route.route_id:
            raise HTTPException(status_code=409, detail=f"Route {route.route_id} already exists.")
    _routes_store.append(route)
    return route
