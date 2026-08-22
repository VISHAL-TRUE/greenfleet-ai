"""
GreenFlow AI - Routes API Router
"""

from fastapi import APIRouter
from backend.app.models.route import RouteListResponse
from simulation.engine import simulation_engine

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("", response_model=RouteListResponse, summary="Get active delivery routes")
def get_routes():
    """
    Returns all active routes requiring vehicle dispatch.
    """
    state = simulation_engine.get_state()
    total_dist = sum(r.distance_km for r in state.routes)
    total_load = sum(r.required_payload_kg for r in state.routes)
    
    return RouteListResponse(
        total_routes=len(state.routes),
        total_distance_km=round(total_dist, 1),
        total_payload_kg=round(total_load, 1),
        routes=state.routes,
    )
