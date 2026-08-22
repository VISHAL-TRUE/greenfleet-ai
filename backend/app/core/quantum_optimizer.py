"""
GreenFlow AI — Quantum-Inspired Optimisation Engine
====================================================

Owner: Person 3 (Quantum Optimisation)
File:  backend/app/core/quantum_optimizer.py
Docs:  docs/algorithm.md  (full mathematical formulation lives there)

This module solves the **vehicle-route assignment problem**:

    Given N vehicles and M routes, decide the binary assignment matrix

        x_ij ∈ {0, 1}    (1 if vehicle i is assigned to route j)

    minimising a composite objective:

        cost(x) = fuel_cost(x)
                 + co2_penalty(x)
                 + distance_penalty(x)
                 + imbalance_penalty(x)
                 + constraint_penalty(x)

Two solvers are implemented so they can be benchmarked against each other:

  1. `solve_classical_baseline()`  — exact MILP (PuLP/CBC), falls back to the
     Hungarian algorithm (scipy) if PuLP isn't installed. This is the
     "ground truth" / control group.

  2. `solve_simulated_annealing()` — a quantum-inspired classical heuristic.
     Simulated Annealing is used here as a *defensible stand-in for quantum
     annealing* (e.g. D-Wave-style QUBO solvers): it uses the same core idea
     — probabilistically accepting worse moves early on (high "temperature")
     so the search can tunnel out of local minima, then cooling down so it
     settles into a low-cost basin — without needing real quantum hardware.
     See docs/algorithm.md §5 for the QUBO framing and why SA is a fair
     representative of that family for this project.

Both solvers return an `AssignmentResult`, and `verify_solution()` runs the
same constraint/sanity checks against either result so they're compared on
equal footing.

CONTRACTS (locked): `Vehicle`, `Route`, `Prediction`, and the assignment dict
shape returned by `to_assignment_list()` mirror the exact JSON payloads
agreed with the rest of the team — field names must not change here. See the
"Contract-driven design decisions" note below `Prediction`.
"""

from __future__ import annotations

import logging
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    import pulp

    PULP_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when pulp missing
    PULP_AVAILABLE = False
    logger.warning("PuLP not installed; classical baseline will fall back to "
                    "the Hungarian algorithm (scipy).")


# --------------------------------------------------------------------------
# Domain models — locked contracts, field names must match the team schema
# --------------------------------------------------------------------------

@dataclass
class Vehicle:
    vehicle_id: str
    vehicle_type: str
    fuel_type: str
    vehicle_age: int
    fuel_capacity_l: float
    max_payload_kg: float
    available: bool = True


@dataclass
class Route:
    route_id: str
    origin: str
    destination: str
    distance_km: float
    required_payload_kg: float
    traffic_factor: float = 1.0
    priority: int = 1


@dataclass
class Prediction:
    """One row of Person 1's fuel/CO2 prediction output for a specific
    (vehicle, route) pair. The optimizer looks these up rather than deriving
    fuel/CO2 from a static per-vehicle efficiency figure."""
    vehicle_id: str
    route_id: str
    predicted_fuel_l: float
    estimated_co2_kg: float


# Contract-driven design decisions (no field in the locked schema covers
# these, so they're resolved here rather than left as open questions):
#
# - No `max_routes` field exists on Vehicle, so this is a strict one-to-one
#   assignment problem: each vehicle serves at most one route per planning
#   window, matching the flat, non-repeating shape of the Assignment output.
# - `predicted_fuel_l` / `estimated_co2_kg` come from `Prediction` rows
#   (Person 1's module), looked up per (vehicle_id, route_id) pair. If no
#   Prediction exists for a pair, that cell is treated as infeasible
#   (cost = 1e9) rather than silently costed as zero — an unpriced
#   assignment must never look cheap.
# - `traffic_factor` scales the distance penalty (heavier traffic makes a
#   route more expensive to serve, independent of which vehicle is chosen).
# - `priority` (higher = more critical route) scales that route's whole
#   assignment cost column, the same role `priority_weight` played before —
#   it does not affect coverage, since every route must be assigned
#   regardless of priority; it only steers which vehicle gets chosen for it.


@dataclass
class OptimizationConfig:
    fuel_weight: float = 1.0
    co2_weight: float = 1.0
    distance_weight: float = 0.3
    imbalance_weight: float = 0.5
    capacity_shortfall_penalty: float = 5_000.0   # vehicle too small for the route
    constraint_penalty: float = 50_000.0          # hard-constraint violations (SA only)
    initial_temp: float = 1_000.0
    cooling_rate: float = 0.995
    min_temp: float = 1e-3
    max_iterations: int = 20_000
    seed: Optional[int] = None


@dataclass
class AssignmentResult:
    assignment_matrix: np.ndarray     # shape (n_vehicles, n_routes), binary
    total_cost: float
    base_cost: float                  # fuel + CO2 + distance component
    imbalance_penalty: float
    constraint_penalty: float
    constraint_violations: int
    runtime_seconds: float
    method: str
    iterations: int = 0


# --------------------------------------------------------------------------
# Optimiser
# --------------------------------------------------------------------------

class QuantumInspiredOptimizer:
    """Builds the cost matrix once, then exposes both solvers against it."""

    def __init__(
        self,
        vehicles: List[Vehicle],
        routes: List[Route],
        predictions: List[Prediction],
        config: Optional[OptimizationConfig] = None,
    ):
        if not vehicles or not routes:
            raise ValueError("At least one vehicle and one route are required.")

        self.vehicles = vehicles
        self.routes = routes
        self.config = config or OptimizationConfig()
        self.n = len(vehicles)
        self.m = len(routes)

        if self.config.seed is not None:
            random.seed(self.config.seed)
            np.random.seed(self.config.seed)

        self._available_idx = [i for i, v in enumerate(vehicles) if v.available]
        if not self._available_idx:
            raise ValueError("No available vehicles: assignment is infeasible.")

        self._prediction_lookup: Dict[Tuple[str, str], Prediction] = {
            (p.vehicle_id, p.route_id): p for p in predictions
        }

        self.cost_matrix = self._build_cost_matrix()

    # ---- cost matrix ------------------------------------------------

    def _build_cost_matrix(self) -> np.ndarray:
        """cost_ij = fuel_cost + co2_penalty + distance_penalty (+ capacity shortfall),
        scaled by route priority. fuel/CO2 come from the Prediction lookup, not
        a formula — a missing prediction makes the cell infeasible."""
        cost = np.zeros((self.n, self.m))
        for i, v in enumerate(self.vehicles):
            for j, r in enumerate(self.routes):
                if not v.available:
                    cost[i, j] = 1e9  # never worth choosing; hard-blocked separately too
                    continue

                pred = self._prediction_lookup.get((v.vehicle_id, r.route_id))
                if pred is None:
                    cost[i, j] = 1e9  # no fuel/CO2 prediction for this pair: unpriceable
                    continue

                fuel_cost = pred.predicted_fuel_l * self.config.fuel_weight
                co2_penalty = pred.estimated_co2_kg * self.config.co2_weight
                distance_penalty = r.distance_km * r.traffic_factor * self.config.distance_weight

                if v.max_payload_kg < r.required_payload_kg:
                    capacity_penalty = self.config.capacity_shortfall_penalty * (
                        r.required_payload_kg - v.max_payload_kg
                    )
                else:
                    # mild penalty for wasted over-capacity, keeps well-matched vehicles cheapest
                    capacity_penalty = 0.05 * (v.max_payload_kg - r.required_payload_kg)

                cost[i, j] = (
                    fuel_cost + co2_penalty + distance_penalty + capacity_penalty
                ) * r.priority
        return cost

    # ---- shared cost/penalty evaluation ------------------------------

    def _imbalance_penalty(self, matrix: np.ndarray) -> float:
        """Penalise uneven fleet utilisation (variance of routes-served per vehicle)."""
        loads = matrix.sum(axis=1)
        if loads.sum() == 0:
            return 0.0
        return float(np.var(loads)) * self.config.imbalance_weight

    def _constraint_penalty(self, matrix: np.ndarray) -> Tuple[float, int]:
        """
        Soft-constraint penalty used by Simulated Annealing (the MILP instead
        encodes these as hard constraints — see `_solve_milp`). Checks:
          - every route assigned exactly once
          - no vehicle assigned more than one route (one-to-one assignment)
          - unavailable vehicles never used
        """
        penalty = 0.0
        violations = 0

        route_sums = matrix.sum(axis=0)
        for s in route_sums:
            if s != 1:
                violations += 1
                penalty += self.config.constraint_penalty * abs(s - 1)

        vehicle_loads = matrix.sum(axis=1)
        for i, v in enumerate(self.vehicles):
            if vehicle_loads[i] > 1:
                violations += 1
                penalty += self.config.constraint_penalty * (vehicle_loads[i] - 1)
            if not v.available and vehicle_loads[i] > 0:
                violations += 1
                penalty += self.config.constraint_penalty * vehicle_loads[i]

        return penalty, violations

    def _evaluate(self, matrix: np.ndarray) -> Dict[str, float]:
        base = float(np.sum(matrix * self.cost_matrix))
        imbalance = self._imbalance_penalty(matrix)
        constraint_pen, violations = self._constraint_penalty(matrix)
        return {
            "total": base + imbalance + constraint_pen,
            "base": base,
            "imbalance": imbalance,
            "constraint_penalty": constraint_pen,
            "violations": violations,
        }

    # ---- Simulated Annealing (quantum-inspired) ----------------------

    def _random_valid_start(self) -> np.ndarray:
        """Each route gets a random *available* vehicle. May still breach
        the one-vehicle-per-route cap / capacity — SA anneals those out via
        penalties."""
        matrix = np.zeros((self.n, self.m))
        for j in range(self.m):
            i = random.choice(self._available_idx)
            matrix[i, j] = 1
        return matrix

    def _neighbor(self, matrix: np.ndarray) -> np.ndarray:
        """Move: reassign one random route to a different available vehicle."""
        new_matrix = matrix.copy()
        j = random.randrange(self.m)
        new_matrix[:, j] = 0
        i = random.choice(self._available_idx)
        new_matrix[i, j] = 1
        return new_matrix

    def solve_simulated_annealing(self) -> AssignmentResult:
        start = time.time()
        current = self._random_valid_start()
        current_eval = self._evaluate(current)
        best, best_eval = current.copy(), current_eval

        temp = self.config.initial_temp
        iteration = 0
        while temp > self.config.min_temp and iteration < self.config.max_iterations:
            candidate = self._neighbor(current)
            candidate_eval = self._evaluate(candidate)
            delta = candidate_eval["total"] - current_eval["total"]

            if delta < 0 or random.random() < math.exp(-delta / temp):
                current, current_eval = candidate, candidate_eval
                if current_eval["total"] < best_eval["total"]:
                    best, best_eval = current.copy(), current_eval

            temp *= self.config.cooling_rate
            iteration += 1

        return AssignmentResult(
            assignment_matrix=best,
            total_cost=best_eval["total"],
            base_cost=best_eval["base"],
            imbalance_penalty=best_eval["imbalance"],
            constraint_penalty=best_eval["constraint_penalty"],
            constraint_violations=best_eval["violations"],
            runtime_seconds=time.time() - start,
            method="simulated_annealing",
            iterations=iteration,
        )

    # ---- Classical baseline ------------------------------------------

    def solve_classical_baseline(self) -> AssignmentResult:
        start = time.time()
        result = self._solve_milp() if PULP_AVAILABLE else self._solve_hungarian()
        result.runtime_seconds = time.time() - start
        return result

    def _solve_milp(self) -> AssignmentResult:
        prob = pulp.LpProblem("GreenFlow_Assignment", pulp.LpMinimize)
        x = {
            (i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
            for i in range(self.n)
            for j in range(self.m)
        }

        prob += pulp.lpSum(
            x[i, j] * self.cost_matrix[i, j] for i in range(self.n) for j in range(self.m)
        )

        # every route assigned exactly once (hard constraint)
        for j in range(self.m):
            prob += pulp.lpSum(x[i, j] for i in range(self.n)) == 1

        # each vehicle serves at most one route (hard constraint; one-to-one assignment)
        for i in range(self.n):
            prob += pulp.lpSum(x[i, j] for j in range(self.m)) <= 1

        # unavailable vehicles get zero assignments (hard constraint)
        for i, v in enumerate(self.vehicles):
            if not v.available:
                for j in range(self.m):
                    prob += x[i, j] == 0

        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        matrix = np.zeros((self.n, self.m))
        for i in range(self.n):
            for j in range(self.m):
                val = pulp.value(x[i, j])
                if val and val > 0.5:
                    matrix[i, j] = 1

        ev = self._evaluate(matrix)
        return AssignmentResult(
            assignment_matrix=matrix,
            total_cost=ev["total"],
            base_cost=ev["base"],
            imbalance_penalty=ev["imbalance"],
            constraint_penalty=ev["constraint_penalty"],
            constraint_violations=ev["violations"],
            runtime_seconds=0.0,
            method="classical_milp",
        )

    def _solve_hungarian(self) -> AssignmentResult:
        """Fallback when PuLP isn't installed. Exact for this one-to-one
        assignment problem (N vehicles, M routes, each vehicle <= 1 route)."""
        from scipy.optimize import linear_sum_assignment

        cost = self.cost_matrix.copy()
        for i, v in enumerate(self.vehicles):
            if not v.available:
                cost[i, :] = 1e9

        row_idx, col_idx = linear_sum_assignment(cost)
        matrix = np.zeros((self.n, self.m))
        for i, j in zip(row_idx, col_idx):
            matrix[i, j] = 1

        ev = self._evaluate(matrix)
        return AssignmentResult(
            assignment_matrix=matrix,
            total_cost=ev["total"],
            base_cost=ev["base"],
            imbalance_penalty=ev["imbalance"],
            constraint_penalty=ev["constraint_penalty"],
            constraint_violations=ev["violations"],
            runtime_seconds=0.0,
            method="classical_hungarian",
        )

    # ---- Comparison entry point ---------------------------------------

    def compare(self) -> Dict[str, AssignmentResult]:
        """Runs both solvers so they can be benchmarked head-to-head."""
        return {
            "quantum_inspired": self.solve_simulated_annealing(),
            "classical_baseline": self.solve_classical_baseline(),
        }

    # ---- Verification ---------------------------------------------------

    def verify_solution(self, result: AssignmentResult) -> Dict[str, object]:
        """
        Runs the full sanity/constraint checklist against a result, regardless
        of which solver produced it, so both can be graded identically:

          - shape_correct / is_binary          — not nonsense
          - every_route_assigned                — every route gets its required assignment
          - no_double_booking                    — no vehicle assigned more than one route
          - no_unavailable_vehicles_used          — unavailable vehicles aren't selected
          - no_capacity_violations                — assigned vehicle can actually serve the route
          - no_nan_or_negative_cost / cost_in_sane_bounds — solution isn't nonsense
        """
        matrix = result.assignment_matrix
        checks: Dict[str, object] = {}

        checks["shape_correct"] = matrix.shape == (self.n, self.m)
        checks["is_binary"] = bool(np.all((matrix == 0) | (matrix == 1)))

        route_sums = matrix.sum(axis=0)
        checks["every_route_assigned"] = bool(np.all(route_sums == 1))
        unassigned = [self.routes[j].route_id for j, s in enumerate(route_sums) if s == 0]
        overassigned = [self.routes[j].route_id for j, s in enumerate(route_sums) if s > 1]

        vehicle_loads = matrix.sum(axis=1)
        double_booked = [
            v.vehicle_id for i, v in enumerate(self.vehicles) if vehicle_loads[i] > 1
        ]
        checks["no_double_booking"] = len(double_booked) == 0

        unavailable_used = [
            v.vehicle_id for i, v in enumerate(self.vehicles)
            if not v.available and vehicle_loads[i] > 0
        ]
        checks["no_unavailable_vehicles_used"] = len(unavailable_used) == 0

        capacity_violations = []
        for i, v in enumerate(self.vehicles):
            for j, r in enumerate(self.routes):
                if matrix[i, j] == 1 and v.max_payload_kg < r.required_payload_kg:
                    capacity_violations.append((v.vehicle_id, r.route_id))
        checks["no_capacity_violations"] = len(capacity_violations) == 0

        checks["no_nan_or_negative_cost"] = bool(
            not math.isnan(result.total_cost) and result.total_cost >= 0
        )
        # "sane bounds": cost shouldn't be anywhere near the hard-penalty magnitude
        checks["cost_in_sane_bounds"] = bool(result.total_cost < self.config.constraint_penalty)

        checks["all_constraints_satisfied"] = bool(
            checks["every_route_assigned"]
            and checks["no_double_booking"]
            and checks["no_unavailable_vehicles_used"]
            and checks["no_capacity_violations"]
        )

        checks["is_valid"] = bool(
            checks["shape_correct"]
            and checks["is_binary"]
            and checks["all_constraints_satisfied"]
            and checks["no_nan_or_negative_cost"]
            and checks["cost_in_sane_bounds"]
        )

        checks["details"] = {
            "unassigned_routes": unassigned,
            "overassigned_routes": overassigned,
            "vehicles_double_booked": double_booked,
            "unavailable_vehicles_used": unavailable_used,
            "capacity_violations": capacity_violations,
        }
        return checks

    def to_assignment_list(self, result: AssignmentResult) -> List[Dict[str, object]]:
        """Turns the matrix into the locked Assignment output contract:
        [{"vehicle_id", "route_id", "predicted_fuel_l", "status"}, ...].
        `predicted_fuel_l` is pulled from the Prediction lookup for the
        chosen pair, not recomputed."""
        pairs = []
        rows, cols = np.where(result.assignment_matrix == 1)
        for i, j in zip(rows, cols):
            vehicle = self.vehicles[i]
            route = self.routes[j]
            pred = self._prediction_lookup.get((vehicle.vehicle_id, route.route_id))
            pairs.append({
                "vehicle_id": vehicle.vehicle_id,
                "route_id": route.route_id,
                "predicted_fuel_l": pred.predicted_fuel_l if pred else None,
                "status": "assigned",
            })
        return pairs
