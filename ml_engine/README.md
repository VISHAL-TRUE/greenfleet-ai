# GreenFleet AI — ML Engine Component

> **Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization**  
> **Team Role: Person 2 — Machine Learning Engine**

---

## 1. Purpose & System Architecture

The **ML Engine** is the predictive foundation of GreenFleet AI. It predicts trip fuel consumption ($L$) and estimated $CO_2$ emissions ($kg$) across all feasible vehicle-route combinations.

### End-to-End Pipeline:
```
Fleet & Route Data 
       ↓
   ML Engine ──→ [LightGBM / GBDT Feature Pipeline]
       ↓
 Prediction Contract & Vehicle-Route Fuel Cost Matrix
       ↓
 Quantum-Inspired QUBO / Annealing Optimizer (Person 3)
       ↓
 Optimal Vehicle-Route Assignments
       ↓
 Fleet Simulation & Benchmark KPIs (Person 4)
       ↓
 Interactive Dashboard (Person 5)
```

---

## 2. Standard GreenFleet JSON Contracts

The ML Engine natively ingests and produces data adhering strictly to project architecture contracts:

### 1. Vehicle Contract
```json
{
  "vehicle_id": "V001",
  "vehicle_type": "Truck",
  "fuel_type": "Diesel",
  "vehicle_age": 4,
  "fuel_capacity_l": 180,
  "max_payload_kg": 5000,
  "available": true
}
```

### 2. Route Contract
```json
{
  "route_id": "R001",
  "origin": "Depot A",
  "destination": "Zone 1",
  "distance_km": 42.5,
  "required_payload_kg": 3200,
  "traffic_factor": 1.2,
  "priority": 2
}
```

### 3. Prediction Contract (Produced by ML Engine)
```json
{
  "vehicle_id": "V001",
  "route_id": "R001",
  "predicted_fuel_l": 18.4,
  "estimated_co2_kg": 48.8
}
```

### 4. Assignment Contract (For Optimizer & Backend)
```json
{
  "vehicle_id": "V001",
  "route_id": "R001",
  "predicted_fuel_l": 18.4,
  "status": "assigned"
}
```

---

## 3. Dataset Schema & Synthetic Generation

Dataset generation is deterministic (`seed=42`) and incorporates domain physical formulas:
- **Baseline Fuel Rates ($L/100\text{km}$):** Calibrated for Diesel, Petrol, Hybrid, and CNG across Vans, Light Commercials, Trucks, Semi-Trailers, and Buses.
- **Cargo Load Factor:** Scaled by $\frac{\text{required\_payload\_kg}}{\text{max\_payload\_kg}}$.
- **Traffic Congestion:** Quadratic stop-and-go penalty from `traffic_factor`.
- **Topography & Weather:** Incline resistance (`road_grade`) and meteorological drag (`weather_factor`).

```bash
# Generate synthetic dataset adhering to contracts
python ml_engine/generate_data.py --samples 6000 --seed 42
```

---

## 4. Feature Engineering

The feature pipeline in `features.py` transforms raw inputs into physics-grounded regressors:
- `payload_capacity_ratio`: $\frac{\text{required\_payload\_kg}}{\text{max\_payload\_kg}}$
- `speed_efficiency_deviation`: $(\text{average\_speed\_kmph} - 65.0)^2$
- `traffic_speed_ratio`: $\frac{\text{traffic\_factor}}{\text{average\_speed\_kmph} + 1.0}$
- `grade_distance_work`: $\text{distance\_km} \times \left(1.0 + \frac{\text{road\_grade}}{100.0}\right)$
- `weather_stress_index`: $(\text{weather\_factor} - 1.0) \times \text{distance\_km}$

---

## 5. Model Training & Evaluation

- **Methodology:** 70% Train ($N=4,199$), 15% Validation ($N=901$), 15% Holdout Test ($N=900$) with zero data leakage.

```bash
# Train models
python ml_engine/train.py --seed 42
```

### Holdout Test Set Performance:
| Model | MAE (Litres) | RMSE (Litres) | $R^2$ Score | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: |
| **LightGBM / HistGBDT (Primary)** | **1.99 L** | **3.19 L** | **0.9939** | **4.17%** |
| Random Forest (Baseline) | 2.71 L | 4.39 L | 0.9885 | 5.82% |
| Linear Regression (Baseline) | 10.71 L | 14.43 L | 0.8752 | 23.94% |

---

## 6. How to Use the Inference Interface

### Predict a Single Trip (Returns Prediction Contract)
```python
from ml_engine.predict import predict_trip, create_assignment

vehicle = {
    "vehicle_id": "V001",
    "vehicle_type": "Truck",
    "fuel_type": "Diesel",
    "vehicle_age": 4,
    "fuel_capacity_l": 180,
    "max_payload_kg": 5000,
    "available": True
}

route = {
    "route_id": "R001",
    "origin": "Depot A",
    "destination": "Zone 1",
    "distance_km": 42.5,
    "required_payload_kg": 3200,
    "traffic_factor": 1.2,
    "priority": 2
}

# Returns Prediction Contract
pred = predict_trip(vehicle, route)
print(pred)
# {'vehicle_id': 'V001', 'route_id': 'R001', 'predicted_fuel_l': 14.6, 'estimated_co2_kg': 39.1}

# Create Assignment Contract
assign = create_assignment(pred["vehicle_id"], pred["route_id"], pred["predicted_fuel_l"])
print(assign)
# {'vehicle_id': 'V001', 'route_id': 'R001', 'predicted_fuel_l': 14.6, 'status': 'assigned'}
```

### Build Fuel Cost Matrix for Quantum Optimizer (Person 3)
```python
from ml_engine.predict import build_fuel_cost_matrix

matrix = build_fuel_cost_matrix(vehicles_list, routes_list)
# Matrix format: {"V001": {"R001": 14.6, "R002": 32.1}, "V002": {...}}
```

---

## 7. Automated Tests
```bash
python ml_engine/test_inference.py
```
