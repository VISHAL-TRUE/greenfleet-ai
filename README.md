# GreenFleet AI — Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization

GreenFleet AI is a smart fleet management and decarbonization platform that optimizes vehicle-route assignments to minimize total fuel consumption and greenhouse gas ($CO_2$) emissions.

## Architecture & Subsystems
- **ML Engine (`ml_engine/`):** Physics-grounded machine learning models (LightGBM/GBDT) that predict fuel consumption and construct vehicle-route cost matrices for downstream optimization.
- **Quantum-Inspired Optimization Engine:** QUBO & Simulated Annealing solver for constrained green fleet assignment.
- **Backend Simulation & Benchmarking:** Fast simulation engine for before/after KPI metrics.
- **Dashboard:** Interactive React dashboard for fleet analytics and carbon tracking.

## ML Engine Quickstart
Refer to [ml_engine/README.md](file:///ml_engine/README.md) for full documentation, training workflows, and API interfaces.
