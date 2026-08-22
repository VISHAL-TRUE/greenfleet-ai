# GreenFleet AI — REST API Contract

Base URL: `http://localhost:8000`  
Interactive OpenAPI Documentation: `http://localhost:8000/docs`

---

## Summary of Endpoints

| Method | Endpoint | Description | Responsible Developer |
|---|---|---|---|
| `GET` | `/` | Service root and metadata | Person 1 |
| `GET` | `/health` | Health check endpoint | Person 1 |
| `GET` | `/api/fleet/vehicles` | List fleet vehicles | Person 1 |
| `POST` | `/api/fleet/vehicles` | Register a new vehicle | Person 1 |
| `GET` | `/api/fleet/routes` | List delivery routes | Person 1 |
| `POST` | `/api/fleet/routes` | Register a new route | Person 1 |
| `POST` | `/api/predict/batch` | Batch predict fuel & CO2 | Person 2 (ML) |
| `POST` | `/api/optimize/assign` | Compute optimal fleet assignment | Person 3 (Optimizer) |
| `POST` | `/api/simulate/run` | Execute operational simulation | Person 4 (Simulation) |
| `GET` | `/api/simulate/benchmarks/summary`| Fetch default benchmark report | Person 4 (Simulation) |

---

## 1. Fleet & Route Endpoints

### `GET /api/fleet/vehicles`
- **Query Parameters**:
  - `available_only` (optional, boolean): Filter by vehicle availability.
  - `vehicle_type` (optional, string): Filter by vehicle category (e.g. `Truck`, `Van`).
- **Response**: `200 OK`
```json
[
  {
    "vehicle_id": "V001",
    "vehicle_type": "Truck",
    "fuel_type": "Diesel",
    "vehicle_age": 4,
    "fuel_capacity_l": 180.0,
    "max_payload_kg": 5000.0,
    "available": true
  }
]
```

### `POST /api/fleet/vehicles`
- **Request Body**: `Vehicle` JSON object.
- **Response**: `201 Created` with created `Vehicle`.

### `GET /api/fleet/routes`
- **Query Parameters**:
  - `min_priority` (optional, integer): Filter routes with priority $\ge$ min_priority.
- **Response**: `200 OK` with list of `Route` objects.

### `POST /api/fleet/routes`
- **Request Body**: `Route` JSON object.
- **Response**: `201 Created` with created `Route`.

---

## 2. ML Prediction Endpoint

### `POST /api/predict/batch`
- **Request Body**:
```json
{
  "pairs": [
    {
      "vehicle": {
        "vehicle_id": "V001",
        "vehicle_type": "Truck",
        "fuel_type": "Diesel",
        "vehicle_age": 4,
        "fuel_capacity_l": 180.0,
        "max_payload_kg": 5000.0,
        "available": true
      },
      "route": {
        "route_id": "R001",
        "origin": "Depot A",
        "destination": "Zone 1",
        "distance_km": 42.5,
        "required_payload_kg": 3200.0,
        "traffic_factor": 1.2,
        "priority": 2
      }
    }
  ]
}
```
- **Response**: `200 OK`
```json
{
  "predictions": [
    {
      "vehicle_id": "V001",
      "route_id": "R001",
      "predicted_fuel_l": 18.4,
      "estimated_co2_kg": 48.8
    }
  ],
  "total_evaluated": 1
}
```

---

## 3. Fleet Optimization Endpoint

### `POST /api/optimize/assign`
- **Request Body**:
```json
{
  "vehicles": [ ... ],
  "routes": [ ... ],
  "predictions": [ ... ],
  "objective": "balanced"
}
```
- **Response**: `200 OK`
```json
{
  "assignments": [
    {
      "vehicle_id": "V001",
      "route_id": "R001",
      "predicted_fuel_l": 18.4,
      "status": "assigned"
    }
  ],
  "unassigned_routes": [],
  "total_fuel_l": 84.5,
  "total_co2_kg": 204.1,
  "solver_status": "OPTIMAL"
}
```

---

## 4. Simulation & Benchmark Endpoints

### `POST /api/simulate/run`
- **Request Body**:
```json
{
  "scenario": "peak_surge",
  "traffic_multiplier": 1.2,
  "payload_multiplier": 1.1
}
```
- **Response**: `200 OK`
```json
{
  "scenario": "peak_surge",
  "baseline": {
    "total_fuel_l": 135.2,
    "total_co2_kg": 358.9,
    "avg_efficiency_km_per_l": 2.2,
    "routes_completed": 5,
    "unassigned_count": 0,
    "total_cost_usd": 223.08
  },
  "optimized": {
    "total_fuel_l": 92.4,
    "total_co2_kg": 226.4,
    "avg_efficiency_km_per_l": 3.2,
    "routes_completed": 5,
    "unassigned_count": 0,
    "total_cost_usd": 152.46
  },
  "deltas": {
    "co2_saved_kg": 132.5,
    "co2_reduction_pct": 36.9,
    "fuel_saved_l": 42.8,
    "cost_saved_usd": 70.62
  }
}
```
