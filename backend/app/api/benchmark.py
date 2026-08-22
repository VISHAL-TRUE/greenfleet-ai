"""
GreenFlow AI - Benchmark API Router
"""

from fastapi import APIRouter
from backend.app.models.simulation import BenchmarkComparison
from simulation.engine import simulation_engine

router = APIRouter(prefix="/benchmark", tags=["Benchmark & KPIs"])


@router.get("", response_model=BenchmarkComparison, summary="Get Baseline vs GreenFlow dynamic benchmark comparison")
def get_benchmark():
    """
    Returns the latest side-by-side benchmark comparison between the Baseline heuristic
    and GreenFlow's Quantum-Inspired Optimization.
    
    All KPIs (Total Fuel, Estimated CO2, Operating Cost, Utilisation, Inefficient Assignments,
    Fuel Saved, % Reduction) are calculated dynamically from actual assignment predictions.
    """
    return simulation_engine.get_benchmark()
