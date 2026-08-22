"""
Tests for Simulation Engine & Scenarios
"""

from backend.app.models.simulation import ScenarioType
from simulation.dataset import get_initial_fleet, get_initial_routes
from simulation.engine import SimulationEngine
from simulation.scenarios import generate_scenario


def test_initial_dataset():
    fleet = get_initial_fleet()
    routes = get_initial_routes()
    assert len(fleet) == 20
    assert len(routes) == 12
    available_count = sum(1 for v in fleet if v.available)
    assert available_count == 18


def test_scenario_generators():
    # Peak demand has higher payload and extra routes
    norm_v, norm_r = generate_scenario(ScenarioType.NORMAL)
    peak_v, peak_r = generate_scenario(ScenarioType.PEAK_DEMAND)
    assert len(peak_r) > len(norm_r)
    assert peak_r[0].required_payload_kg > norm_r[0].required_payload_kg

    # High traffic has higher traffic factors
    traf_v, traf_r = generate_scenario(ScenarioType.HIGH_TRAFFIC)
    assert traf_r[0].traffic_factor > norm_r[0].traffic_factor


def test_simulation_engine_lifecycle():
    engine = SimulationEngine()
    
    # 1. Reset
    state = engine.reset()
    assert state.scenario == ScenarioType.NORMAL
    assert len(state.vehicles) == 20
    assert len(state.routes) == 12
    assert len(state.baseline_assignments) == 12

    # 2. Run optimization
    opt_state = engine.run_optimization()
    assert opt_state.benchmark is not None
    assert opt_state.benchmark.fuel_saved_l >= 0.0
    assert opt_state.benchmark.co2_reduced_kg >= 0.0
    assert len(opt_state.greenflow_assignments) == 12

    # 3. Peak Demand Transition
    peak_state = engine.apply_scenario(ScenarioType.PEAK_DEMAND)
    assert peak_state.scenario == ScenarioType.PEAK_DEMAND
    assert len(peak_state.routes) == 15
    assert len(peak_state.baseline_assignments) == 15

    # 4. Optimize Peak Demand
    opt_peak = engine.run_optimization()
    assert opt_peak.benchmark is not None
    assert opt_peak.benchmark.baseline.total_fuel_l > 0
    assert opt_peak.benchmark.greenflow.total_fuel_l > 0
    assert opt_peak.benchmark.fuel_saved_pct >= 0.0
