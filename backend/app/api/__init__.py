from .fleet import router as fleet_router
from .prediction import router as prediction_router
from .optimization import router as optimization_router
from .simulation import router as simulation_router

__all__ = [
    "fleet_router",
    "prediction_router",
    "optimization_router",
    "simulation_router",
]
