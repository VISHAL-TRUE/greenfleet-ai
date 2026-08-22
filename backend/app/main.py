"""
GreenFleet AI — FastAPI Central Backend
======================================
Main application with CORS, modular routing, health checks, and OpenAPI docs.
Established by Person 1 (Tech Lead / Integrator).
"""

import os
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.fleet import router as fleet_router
from backend.app.api.prediction import router as prediction_router
from backend.app.api.optimization import router as optimization_router
from backend.app.api.simulation import router as simulation_router

app = FastAPI(
    title="GreenFleet AI",
    description="Intelligent Fleet Decarbonization & Route Optimization Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for Frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register modular API routers
app.include_router(fleet_router, prefix="/api")
app.include_router(prediction_router, prefix="/api")
app.include_router(optimization_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "GreenFleet AI",
        "tagline": "Intelligent Fleet Decarbonization & Route Optimization",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "contracts": {
            "Vehicle": "/api/fleet/vehicles",
            "Route": "/api/fleet/routes",
            "Prediction": "/api/predict/batch",
            "Assignment": "/api/optimize/assign",
            "Simulation": "/api/simulate/run",
        }
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "greenfleet-ai"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
