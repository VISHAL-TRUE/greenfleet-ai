# GreenFleet AI — Shared Data Schemas Specification

All five developers must strictly adhere to these shared contracts. Field names, types, and constraints must not be modified unilaterally.

---

## 1. Canonical Core Schemas

### 1.1 Vehicle Schema
Represents a vehicle in the fleet.
```json
{
  "vehicle_id": "V001",
  "vehicle_type": "Truck",
  "fuel_type": "Diesel",
  "vehicle_age": 4,
  "fuel_capacity_l": 180.0,
  "max_payload_kg": 5000.0,
  "available": true
}
```

| Field | Type | Description | Constraints |
|---|---|---|---|
| `vehicle_id` | `string` | Unique vehicle ID | Non-empty string |
| `vehicle_type` | `string` | Category (e.g. `Truck`, `Van`, `EV_Van`, `Heavy_Truck`) | Non-empty |
| `fuel_type` | `string` | Fuel / Powertrain (`Diesel`, `Electric`, `Petrol`, `Hybrid`, `CNG`) | Case-sensitive |
| `vehicle_age` | `integer` | Age in years | $\ge 0$ |
| `fuel_capacity_l` | `number` (float) | Tank or battery capacity (L or kWh) | $> 0$ |
| `max_payload_kg` | `number` (float) | Maximum allowed payload cargo weight (kg) | $> 0$ |
| `available` | `boolean` | Whether vehicle is currently free for dispatch | `true` or `false` |

---

### 1.2 Route Schema
Represents a transport/delivery route request.
```json
{
  "route_id": "R001",
  "origin": "Depot A",
  "destination": "Zone 1",
  "distance_km": 42.5,
  "required_payload_kg": 3200.0,
  "traffic_factor": 1.2,
  "priority": 2
}
```

| Field | Type | Description | Constraints |
|---|---|---|---|
| `route_id` | `string` | Unique route ID | Non-empty string |
| `origin` | `string` | Origin location / Depot name | Non-empty |
| `destination` | `string` | Destination / Delivery Zone name | Non-empty |
| `distance_km` | `number` (float) | Route distance in kilometers | $> 0$ |
| `required_payload_kg` | `number` (float) | Cargo weight to transport | $\ge 0$ |
| `traffic_factor` | `number` (float) | Congestion multiplier (1.0 = baseline) | $0.5 \le x \le 5.0$ |
| `priority` | `integer` | Priority rating (1 = lowest, 5 = urgent) | $1 \le x \le 5$ |

---

### 1.3 Prediction Schema
Output of the Machine Learning Engine (Person 2).
```json
{
  "vehicle_id": "V001",
  "route_id": "R001",
  "predicted_fuel_l": 18.4,
  "estimated_co2_kg": 48.8
}
```

| Field | Type | Description | Constraints |
|---|---|---|---|
| `vehicle_id` | `string` | Target vehicle ID | Matches existing vehicle |
| `route_id` | `string` | Target route ID | Matches existing route |
| `predicted_fuel_l` | `number` (float) | Predicted fuel / energy consumed | $\ge 0$ |
| `estimated_co2_kg` | `number` (float) | Predicted greenhouse gas emissions ($\text{kg CO}_2\text{e}$) | $\ge 0$ |

---

### 1.4 Assignment Schema
Output of the Optimization Engine (Person 3).
```json
{
  "vehicle_id": "V001",
  "route_id": "R001",
  "predicted_fuel_l": 18.4,
  "status": "assigned"
}
```

| Field | Type | Description | Constraints |
|---|---|---|---|
| `vehicle_id` | `string` | Selected vehicle ID | Matches existing vehicle |
| `route_id` | `string` | Selected route ID | Matches existing route |
| `predicted_fuel_l` | `number` (float) | Expected fuel consumption for this assignment | $\ge 0$ |
| `status` | `string` | Dispatch status | One of: `"assigned"`, `"unassigned"`, `"failed"`, `"pending"` |

---

## 2. Composite Request & Response Schemas

### 2.1 Optimization Request (`POST /api/optimize/assign`)
```json
{
  "vehicles": [ ... ],
  "routes": [ ... ],
  "predictions": [ ... ],
  "objective": "balanced"
}
```

### 2.2 Optimization Response
```json
{
  "assignments": [ ... ],
  "unassigned_routes": ["R005"],
  "total_fuel_l": 82.4,
  "total_co2_kg": 194.2,
  "solver_status": "FEASIBLE_PARTIAL"
}
```

### 2.3 Simulation Request (`POST /api/simulate/run`)
```json
{
  "scenario": "peak_surge",
  "traffic_multiplier": 1.3,
  "payload_multiplier": 1.15
}
```

### 2.4 Simulation Response
```json
{
  "scenario": "peak_surge",
  "baseline": {
    "total_fuel_l": 142.5,
    "total_co2_kg": 378.1,
    "avg_efficiency_km_per_l": 2.1,
    "routes_completed": 5,
    "unassigned_count": 0,
    "total_cost_usd": 235.12
  },
  "optimized": {
    "total_fuel_l": 98.2,
    "total_co2_kg": 242.6,
    "avg_efficiency_km_per_l": 3.05,
    "routes_completed": 5,
    "unassigned_count": 0,
    "total_cost_usd": 162.03
  },
  "deltas": {
    "co2_saved_kg": 135.5,
    "co2_reduction_pct": 35.8,
    "fuel_saved_l": 44.3,
    "cost_saved_usd": 73.09
  }
}
```
