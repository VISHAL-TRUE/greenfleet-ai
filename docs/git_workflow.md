# GreenFleet AI — Git Workflow & Integration Guidelines

To ensure the central repository remains functional, runnable, and conflict-free throughout the 24-hour sprint, all developers must adhere to the following Git conventions.

---

## 1. Branch Strategy

The `main` branch is protected and must always be in a **runnable and tested state**.

| Developer | Assigned Branch | Primary Work Scope |
|---|---|---|
| **Person 1 (Tech Lead)** | `main` / `feat/integration-core` | Schemas, central routing, orchestrator, integration gatekeeper. |
| **Person 2 (ML)** | `feat/ml-engine` | `ml_engine/` (feature engineering, training, inference API). |
| **Person 3 (Optimizer)** | `feat/fleet-optimizer` | `backend/app/core/optimizer.py` (PuLP MILP solver & scoring). |
| **Person 4 (Simulation)** | `feat/simulation-benchmark` | `simulation/` (simulator, scenario definitions, benchmarks). |
| **Person 5 (Frontend)** | `feat/frontend-dashboard` | `frontend/` (React components, pages, dashboard, map view). |

---

## 2. Golden Integration Rules

1. **Strict Data Contract Compliance**:
   - Never alter field names, types, or nullability in `backend/app/models/schemas.py` without Person 1 review and consensus.
2. **Directory Isolation**:
   - Work strictly within your assigned module directory to prevent merge conflicts.
3. **Pre-PR Self-Verification**:
   - Before submitting a Pull Request, run the automated test suite locally:
     ```bash
     pytest tests/test_contracts.py
     ```
   - Ensure the FastAPI server boots up with zero import errors:
     ```bash
     python -m uvicorn backend.app.main:app --port 8000
     ```
4. **Integration Windows**:
   - Person 1 will merge PRs in scheduled waves:
     - **Wave 1 (Hour 8–12):** ML Engine + Optimizer integration.
     - **Wave 2 (Hour 12–16):** Simulation & Benchmark integration.
     - **Wave 3 (Hour 16–20):** Frontend Dashboard integration.
     - **Wave 4 (Hour 20–24):** End-to-End Demo hardening.
