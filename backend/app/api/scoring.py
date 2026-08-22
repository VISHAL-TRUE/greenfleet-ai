"""
GreenFlow AI - Explainable Scoring API Router
"""

from fastapi import APIRouter, HTTPException
from backend.app.core.integration import predict_fuel_and_co2
from backend.app.core.scoring import score_fleet_route_pairs
from backend.app.models.simulation import ScoringRequest, ScoringResponse

router = APIRouter(prefix="/scoring", tags=["Scoring & Explainability"])


@router.post("", response_model=ScoringResponse, summary="Compute explainable vehicle-route suitability scores")
def compute_scores(payload: ScoringRequest):
    """
    Computes explainable 5-factor suitability breakdown for all vehicle-route pairs:
    - Fuel Efficiency Score
    - Capacity Match Score
    - Distance Suitability Score
    - Traffic Resilience Score
    - Availability Score
    """
    if not payload.vehicles:
        raise HTTPException(status_code=400, detail="Vehicle list cannot be empty")
    if not payload.routes:
        raise HTTPException(status_code=400, detail="Route list cannot be empty")

    preds = predict_fuel_and_co2(payload.vehicles, payload.routes)
    pred_map = {(p.vehicle_id, p.route_id): p.predicted_fuel_l for p in preds}
    
    scores = score_fleet_route_pairs(payload.vehicles, payload.routes, predictions_dict=pred_map)
    
    return ScoringResponse(
        total_scores=len(scores),
        scores=scores,
    )
