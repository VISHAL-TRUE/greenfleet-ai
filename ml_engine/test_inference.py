"""
GreenFleet AI - Inference Verification & Contract Test Suite
Validates model loading, single trip prediction, CO2 estimation,
and JSON contracts for Person 1, Person 3, Person 4, and Person 5.
"""

import os
import sys
import unittest
import json

# Ensure ml_engine directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from predict import (
    load_model,
    predict_fuel,
    predict_trip,
    create_assignment,
    estimate_co2,
    build_fuel_cost_matrix,
    build_trip_cost_matrix,
    EMISSION_FACTORS_KG_CO2_PER_LITRE,
)


class TestGreenFleetJSONContracts(unittest.TestCase):
    """Automated tests validating GreenFleet JSON Contracts."""

    @classmethod
    def setUpClass(cls):
        model_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "models", "fuel_model.pkl"
        )
        cls.model = load_model(model_path)
        cls.assertIsNotNone(cls, cls.model, "Model should load successfully.")

    def test_user_provided_contracts(self):
        """Test with exact JSON contracts provided by team architecture."""
        vehicle = {
            "vehicle_id": "V001",
            "vehicle_type": "Truck",
            "fuel_type": "Diesel",
            "vehicle_age": 4,
            "fuel_capacity_l": 180,
            "max_payload_kg": 5000,
            "available": True,
        }

        route = {
            "route_id": "R001",
            "origin": "Depot A",
            "destination": "Zone 1",
            "distance_km": 42.5,
            "required_payload_kg": 3200,
            "traffic_factor": 1.2,
            "priority": 2,
        }

        # 1. Prediction Contract Validation
        prediction = predict_trip(vehicle, route, model=self.model)
        print("\n[Contract 1] Prediction Output:")
        print(json.dumps(prediction, indent=2))

        self.assertEqual(prediction["vehicle_id"], "V001")
        self.assertEqual(prediction["route_id"], "R001")
        self.assertIn("predicted_fuel_l", prediction)
        self.assertIn("estimated_co2_kg", prediction)
        self.assertIsInstance(prediction["predicted_fuel_l"], float)
        self.assertIsInstance(prediction["estimated_co2_kg"], float)

        # 2. Assignment Contract Validation
        assignment = create_assignment(
            vehicle_id=prediction["vehicle_id"],
            route_id=prediction["route_id"],
            predicted_fuel_l=prediction["predicted_fuel_l"],
            status="assigned",
        )
        print("\n[Contract 2] Assignment Output:")
        print(json.dumps(assignment, indent=2))

        self.assertEqual(assignment["vehicle_id"], "V001")
        self.assertEqual(assignment["route_id"], "R001")
        self.assertEqual(assignment["predicted_fuel_l"], prediction["predicted_fuel_l"])
        self.assertEqual(assignment["status"], "assigned")

    def test_estimate_co2(self):
        """Test CO2 emission estimations based on fuel consumption and fuel type."""
        # 10 Litres of Diesel * 2.68 = 26.8 kg CO2
        co2_diesel = estimate_co2(10.0, fuel_type="Diesel")
        self.assertEqual(co2_diesel, 26.8)

        # 10 Litres of Petrol * 2.31 = 23.1 kg CO2
        co2_petrol = estimate_co2(10.0, fuel_type="Petrol")
        self.assertEqual(co2_petrol, 23.1)

    def test_fuel_cost_matrix_for_quantum_optimizer(self):
        """Test build_fuel_cost_matrix structure for Person 3 Quantum Optimizer."""
        vehicles = [
            {
                "vehicle_id": "V001",
                "vehicle_type": "Truck",
                "fuel_type": "Diesel",
                "vehicle_age": 4,
                "fuel_capacity_l": 180,
                "max_payload_kg": 5000,
                "available": True,
            },
            {
                "vehicle_id": "V002",
                "vehicle_type": "Van",
                "fuel_type": "Hybrid",
                "vehicle_age": 2,
                "fuel_capacity_l": 75,
                "max_payload_kg": 1500,
                "available": True,
            },
        ]
        routes = [
            {
                "route_id": "R001",
                "origin": "Depot A",
                "destination": "Zone 1",
                "distance_km": 42.5,
                "required_payload_kg": 1200,
                "traffic_factor": 1.2,
                "priority": 2,
            },
            {
                "route_id": "R002",
                "origin": "Depot B",
                "destination": "Zone 3",
                "distance_km": 110.0,
                "required_payload_kg": 1400,
                "traffic_factor": 1.4,
                "priority": 1,
            },
        ]

        matrix = build_fuel_cost_matrix(vehicles, routes, model=self.model)
        print("\n[Contract 3] Quantum Fuel Cost Matrix:")
        print(json.dumps(matrix, indent=2))

        self.assertIn("V001", matrix)
        self.assertIn("V002", matrix)
        self.assertIn("R001", matrix["V001"])
        self.assertIn("R002", matrix["V001"])
        self.assertGreater(matrix["V001"]["R002"], matrix["V001"]["R001"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
