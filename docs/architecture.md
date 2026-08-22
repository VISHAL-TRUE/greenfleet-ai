# GreenFleet AI — System Architecture Specification

## 1. System Vision & Objective
GreenFleet AI is an end-to-end fleet decarbonization and smart dispatch platform that predicts vehicle-specific fuel/energy consumption and $\text{CO}_2$ emissions, executes constraint-aware mathematical optimization to match vehicles with demand routes, and simulates operational scenarios to demonstrate measurable carbon reduction.

---

## 2. Global Execution Pipeline

```
+-----------------------------------------------------------------------------------+
| 1. ML Output (ml_engine)                                                          |
|    Inference: (Vehicle, Route) -> (predicted_fuel_l, estimated_co2_kg)            |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------+-----------------------------------------+
| 2. Optimizer Input (backend/app/core)                                             |
|    Matrix of Predictions + Vehicle Constraints + Route Requirements               |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------+-----------------------------------------+
| 3. Optimizer Output (backend/app/core)                                            |
|    Optimal Assignments (vehicle_id, route_id, predicted_fuel_l, "assigned")       |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------+-----------------------------------------+
| 4. Simulation Input (simulation/)                                                 |
|    Assignments + Scenario Multipliers (Traffic, Payload, Weather)                 |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------+-----------------------------------------+
| 5. Simulation Output (simulation/)                                                |
|    Baseline vs. GreenFleet KPI Deltas (CO2 Saved %, Fuel Saved L, Cost Delta)      |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------+-----------------------------------------+
| 6. API Response (FastAPI)                                                         |
|    Standardized JSON REST payload to Frontend                                     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------+-----------------------------------------+
| 7. Frontend UI (React 19 + Tailwind v4 + Recharts + Leaflet)                      |
|    Operations Dashboard, Route Dispatch Map, Carbon Savings ROI Meter             |
+-----------------------------------------------------------------------------------+
```

---

## 3. High-Level Directory Layout

```
greenfleet-ai/
├── README.md
├── requirements.txt
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py                  # FastAPI server & route registration
│       ├── api/                     # Modular API endpoints
│       │   ├── __init__.py
│       │   ├── fleet.py             # Vehicle & Route registry
│       │   ├── prediction.py        # ML batch prediction proxy
│       │   ├── optimization.py      # Fleet solver proxy
│       │   └── simulation.py        # Simulation runner & benchmarks
│       ├── core/                    # Optimization & business logic
│       │   ├── __init__.py
│       │   └── optimizer.py         # PuLP MILP solver
│       ├── models/                  # Shared data schemas
│       │   ├── __init__.py
│       │   └── schemas.py           # Strict canonical Pydantic contracts
│       └── data/                    # Canonical sample seed data
│           ├── sample_vehicles.json
│           └── sample_routes.json
├── docs/                            # Architecture, API & Schema specs
│   ├── architecture.md
│   ├── data_schema.md
│   ├── api_contract.md
│   └── git_workflow.md
├── frontend/                        # React 19 + Tailwind UI
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── vite.config.js
├── ml_engine/                       # ML regression models
│   ├── data/
│   ├── models/
│   └── src/
├── simulation/                      # Operational simulation & benchmarks
│   ├── scenarios/
│   ├── simulator.py
│   └── benchmark.py
└── tests/                           # Integration & contract test suite
    └── test_contracts.py
```

---

## 4. Sub-System Ownership Matrix (5-Person Team)

| Role | Person | Dedicated Directory | Core Responsibilities |
|---|---|---|---|
| **Tech Lead & Integrator** | **Person 1** | `backend/app/models/`, `backend/app/api/`, `backend/app/main.py`, `docs/`, `tests/` | Central repository governance, shared Pydantic data schemas, FastAPI route wiring, end-to-end integration tests, contract compliance gatekeeping, and demo hardening. |
| **ML & Emissions Engineer** | **Person 2** | `ml_engine/` (`src/`, `data/`, `models/`) | Fleet consumption & emission feature engineering, regression model training, artifact serialization, and batch inference pipeline matching `Prediction`. |
| **Fleet Optimization Engineer** | **Person 3** | `backend/app/core/` (`optimizer.py`) | Mathematical modeling (PuLP MILP), constraint satisfaction (payload, fuel capacity, vehicle availability), priority weighting, and `Assignment` generation. |
| **Simulation & Benchmarking Engineer** | **Person 4** | `simulation/` (`simulator.py`, `benchmark.py`, `scenarios/`) | Fleet state machine, uncoordinated baseline comparison engine, scenario injection (traffic surges, payload spikes), and emission delta metrics. |
| **Frontend & UI/UX Engineer** | **Person 5** | `frontend/` (`src/components/`, `src/pages/`, `src/services/`) | React 19 + Tailwind operations dashboard, Leaflet dispatch map, interactive route-to-vehicle assignment matrix, real-time KPI dials, and scenario controls. |
