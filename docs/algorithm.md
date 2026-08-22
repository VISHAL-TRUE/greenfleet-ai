# GreenFleet AI — Optimisation Algorithm

**Module:** `backend/app/core/quantum_optimizer.py`
**Owner:** Person 3 — Quantum Optimisation

This document specifies the mathematical formulation behind the vehicle-route
assignment problem, why Simulated Annealing is used as the "quantum-inspired"
solver, and how solutions are verified before being trusted anywhere else in
the system.

---

## 1. Problem statement

We have:

- **N vehicles** (`Vehicle`: `vehicle_id`, `vehicle_type`, `fuel_type`,
  `vehicle_age`, `fuel_capacity_l`, `max_payload_kg`, `available`).
- **M routes** (`Route`: `route_id`, `origin`, `destination`, `distance_km`,
  `required_payload_kg`, `traffic_factor`, `priority`).
- **Predictions** (`Prediction`: `vehicle_id`, `route_id`,
  `predicted_fuel_l`, `estimated_co2_kg`) — Person 1's fuel/CO2 module
  output, one row per feasible (vehicle, route) pair, consumed as a lookup
  rather than derived from a static efficiency formula.

These three shapes, plus the `Assignment` output shape (§7), are **locked
contracts** shared across the team — field names here must not diverge from
them.

There is no `max_routes` field on `Vehicle`, so this is a strict
**one-to-one assignment problem**: each vehicle serves at most one route per
planning window.

We need a **binary assignment matrix**:

```
x_ij ∈ {0, 1}      for i = 1..N, j = 1..M
```

where `x_ij = 1` means vehicle *i* is assigned to route *j*.

---

## 2. Objective function

We minimise a single composite cost:

```
cost(x) = fuel_cost(x)
        + co2_penalty(x)
        + distance_penalty(x)
        + imbalance_penalty(x)
        + constraint_penalty(x)
```

### 2.1 Fuel cost

`predicted_fuel_l` comes directly from the matching `Prediction` row for
`(vehicle_id, route_id)` — not computed from a static efficiency figure. If
no `Prediction` exists for a pair, that cell is infeasible (§2.4a).

```
fuel_cost(x) = Σ_ij  x_ij · predicted_fuel_l_ij · w_fuel
```

### 2.2 CO2 penalty

`estimated_co2_kg` likewise comes from the matching `Prediction` row:

```
co2_penalty(x) = Σ_ij  x_ij · estimated_co2_kg_ij · w_co2
```

### 2.3 Distance penalty

A term on route distance scaled by the route's `traffic_factor` (heavier
traffic makes a route more expensive to serve, independent of which vehicle
is chosen), so the optimiser doesn't only chase low-fuel vehicles onto very
long or congested routes when a shorter, better-fit route exists:

```
distance_penalty(x) = Σ_ij  x_ij · distance_km_j · traffic_factor_j · w_distance
```

### 2.4 Capacity shortfall (folded into the per-cell cost)

Before the sum above runs, each cell of the cost matrix is inflated if the
vehicle can't actually carry the route's required load:

```
if max_payload_kg_i < required_payload_kg_j:
    cell_penalty_ij = capacity_shortfall_weight · (required_payload_kg_j − max_payload_kg_i)
else:
    cell_penalty_ij = 0.05 · (max_payload_kg_i − required_payload_kg_j)   # small, discourages waste
```

#### 2.4a Missing prediction / unavailable vehicle

If a vehicle is unavailable, or no `Prediction` row exists for a
`(vehicle_id, route_id)` pair, that cell is set to a large constant
(`1e9`) — unpriceable or disallowed assignments must never look
artificially cheap.

Every cell is finally scaled by the route's `priority` (higher = more
critical route; steers *which* vehicle gets chosen for it — it does not
affect coverage, since every route must be assigned regardless of
priority):

```
cost_ij = (fuel_cost_ij + co2_penalty_ij + distance_penalty_ij + capacity_penalty_ij) · priority_j
```

This keeps under-capacity vehicles mathematically unattractive, and is
**also enforced as a hard constraint during verification** (see §6) so it
can never silently slip through as "just an expensive choice."

### 2.5 Imbalance penalty

Penalises uneven fleet utilisation — one vehicle running ragged while
another sits idle:

```
load_i = Σ_j x_ij
imbalance_penalty(x) = w_imbalance · Var(load_1, ..., load_N)
```

### 2.6 Constraint penalty (soft, SA only)

Simulated Annealing explores the search space including temporarily invalid
states, so violations are penalised heavily rather than forbidden outright:

```
constraint_penalty(x) = Σ_j  C · |Σ_i x_ij − 1|                (every route needs exactly 1 vehicle)
                       + Σ_i  C · max(0, load_i − 1)             (no vehicle serves more than 1 route)
                       + Σ_i  C · [vehicle_i unavailable] · load_i
```

where `C` is a large constant (default `50,000`) — large enough that no
accumulation of small savings elsewhere in the objective can make a
violation worthwhile.

The **classical MILP baseline instead encodes these as hard linear
constraints** (see §4) — it never even considers an infeasible matrix.

---

## 3. Quantum-inspired solver: Simulated Annealing

**Why Simulated Annealing stands in for a quantum annealer:** the assignment
problem above can be written as a Quadratic Unconstrained Binary Optimization
(QUBO) problem — the natural input format for quantum annealers like D-Wave.
Real quantum annealing hardware isn't available to this project, so we use
Simulated Annealing, which:

- operates over the same binary decision variables (`x_ij`),
- uses the same underlying mechanism quantum annealers approximate physically:
  accepting a worse move with probability `exp(-Δcost / T)`, letting the
  search "tunnel" out of local minima early on (high temperature `T`), then
  cooling down (`T ← T · cooling_rate`) so it settles into a low-cost basin
  by the end of the run,
- is a standard, well-documented, and defensible classical proxy for
  QUBO/quantum-annealing behaviour used throughout the quantum-inspired
  optimisation literature.

**Algorithm:**

1. Start from a random valid-ish assignment (every route gets a random
   *available* vehicle).
2. Repeat until the temperature cools below a floor or the iteration cap is
   hit:
   - Propose a neighbour: reassign one random route to a different
     available vehicle.
   - Accept if it's cheaper, or accept anyway with probability
     `exp(-Δcost / T)` if it's worse.
   - Track the best matrix seen so far (not just the current one — SA can
     wander away from a good solution late in the run).
   - Cool: `T ← T · cooling_rate`.
3. Return the best matrix found, evaluated exactly the same way as the
   baseline.

Default schedule: `T₀ = 1000`, `cooling_rate = 0.995`, `T_min = 1e-3`,
`max_iterations = 20,000` — tunable via `OptimizationConfig`.

---

## 4. Classical baseline: exact MILP

Implemented with PuLP/CBC (falls back to the Hungarian algorithm via
`scipy.optimize.linear_sum_assignment` if PuLP isn't installed):

```
minimise   Σ_ij x_ij · cost_ij
subject to Σ_i x_ij = 1                for every route j        (fully covered)
           Σ_j x_ij ≤ 1                for every vehicle i       (one-to-one assignment)
           x_ij = 0                    for every unavailable vehicle i
           x_ij ∈ {0, 1}
```

This is the **ground truth**: it's guaranteed optimal for the instance size
GreenFleet operates at, and gives Simulated Annealing something honest to be
benchmarked against — including an **optimality gap** (`(SA_cost −
MILP_cost) / MILP_cost`), expected to land in the low single-digit-to-~5%
range on mid-sized random instances, a normal gap for a metaheuristic vs. an
exact solver. This should be measured on real fixtures once built (see
PERSON3_PLANNING.md §6), not assumed.

---

## 5. Why compare classical vs. quantum-inspired at all

The point isn't that SA "beats" MILP on solution quality — it structurally
can't, MILP is exact at this scale. The point is:

- MILP solve time grows with problem size and constraint complexity; SA's
  cost is tunable (iteration cap) and scales more gracefully to larger,
  messier, real-world fleets where an exact solver becomes impractical.
- The QUBO/annealing formulation is the same one a real quantum annealer
  would consume, so this comparison is a legitimate, documented rehearsal
  for swapping in actual quantum hardware later without changing the
  problem formulation — only the solver.

Both numbers (cost, runtime, optimality gap) should be surfaced on the
dashboard so this trade-off is visible, not asserted.

---

## 6. Verification suite

Every result — from either solver — is run through `verify_solution()`
before it's trusted anywhere downstream (API responses, dashboard,
benchmarking). It checks:

| Check | What it catches |
|---|---|
| `shape_correct`, `is_binary` | Malformed output — not a real 0/1 assignment matrix |
| `every_route_assigned` | A route silently dropped (Σ_i x_ij ≠ 1) |
| `no_double_booking` | A vehicle assigned more than one route |
| `no_unavailable_vehicles_used` | An unavailable vehicle sneaking into the solution |
| `no_capacity_violations` | A vehicle assigned a route whose load it can't carry |
| `no_nan_or_negative_cost` | NaN/negative cost — a numerically broken result |
| `cost_in_sane_bounds` | Cost anywhere near the hard-penalty magnitude — a sign constraints were silently violated and merely penalised rather than actually fixed |

`verify_solution()` returns a dict with each boolean check plus an overall
`is_valid`, and a `details` block listing exactly which routes/vehicles
failed which check — this is what should be logged and surfaced if a
solution is ever rejected.

This should be tested against both a correct result (passes) and a
hand-corrupted matrix with an unavailable vehicle used and a capacity
mismatch (must correctly fail, with the exact offending vehicle/route pairs
listed) — the verification logic is not meant to be a rubber stamp. See
PERSON3_PLANNING.md §5–§6 for the adversarial test-case spec.

---

## 7. Interfaces exposed to the rest of the system

```python
optimizer = QuantumInspiredOptimizer(vehicles, routes, predictions, config)

sa_result   = optimizer.solve_simulated_annealing()
milp_result = optimizer.solve_classical_baseline()
both        = optimizer.compare()          # {"quantum_inspired": ..., "classical_baseline": ...}

verification = optimizer.verify_solution(sa_result)   # or milp_result
assignments  = optimizer.to_assignment_list(sa_result)
```

`to_assignment_list()` is what the FastAPI layer should call to hand results
to the dashboard/benchmarking modules — it returns the **locked Assignment
contract**:

```json
{
  "vehicle_id": "V001",
  "route_id": "R001",
  "predicted_fuel_l": 18.4,
  "status": "assigned"
}
```

`predicted_fuel_l` is looked up from the matching `Prediction` row, not
recomputed.

The rest of the team should generally call `optimize_routes()` in
`backend/app/core/optimizer.py` instead of using `QuantumInspiredOptimizer`
directly — it wraps the steps above (solve → verify → flatten) behind one
function and raises if verification ever fails:

```python
from backend.app.core.optimizer import optimize_routes

assignments = optimize_routes(vehicles, routes, predictions)  # -> [Assignment, ...]
```

---

## 8. Config knobs (`OptimizationConfig`)

| Field | Default | Meaning |
|---|---|---|
| `fuel_weight` | 1.0 | Weight on fuel cost term |
| `co2_weight` | 1.0 | Weight on CO2 penalty term |
| `distance_weight` | 0.3 | Weight on raw distance term |
| `imbalance_weight` | 0.5 | Weight on fleet-utilisation variance |
| `capacity_shortfall_penalty` | 5,000 | Per-unit penalty for an under-capacity match |
| `constraint_penalty` | 50,000 | Per-violation penalty used by SA only |
| `initial_temp` | 1,000 | SA starting temperature |
| `cooling_rate` | 0.995 | SA per-step cooling multiplier |
| `min_temp` | 1e-3 | SA stopping temperature |
| `max_iterations` | 20,000 | SA iteration cap |
| `seed` | `None` | Fix for reproducible benchmarking runs |

These should be tuned once real fuel-consumption and route data are
available (Person 1/2's modules) — the defaults above are starting points
validated only on synthetic test fixtures (see PERSON3_PLANNING.md §6).
