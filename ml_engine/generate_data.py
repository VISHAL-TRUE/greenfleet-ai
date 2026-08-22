"""
GreenFlow AI - Synthetic Fleet Dataset Generator
Generates realistic, physically-grounded fleet trip data adhering to GreenFlow system JSON contracts.
"""

import os
import argparse
import numpy as np
import pandas as pd

# Base fuel consumption rates (Litres / 100km) by vehicle and fuel type
BASE_CONSUMPTION_L_PER_100KM = {
    ("Van", "Diesel"): 9.0,
    ("Van", "Petrol"): 10.5,
    ("Van", "Hybrid"): 6.8,
    ("Van", "CNG"): 10.8,
    ("Light Commercial", "Diesel"): 13.5,
    ("Light Commercial", "Petrol"): 15.5,
    ("Light Commercial", "Hybrid"): 10.0,
    ("Light Commercial", "CNG"): 15.0,
    ("Truck", "Diesel"): 25.0,
    ("Truck", "Petrol"): 29.0,
    ("Truck", "Hybrid"): 19.5,
    ("Truck", "CNG"): 28.0,
    ("Semi-Trailer", "Diesel"): 34.0,
    ("Semi-Trailer", "Petrol"): 39.5,
    ("Semi-Trailer", "Hybrid"): 27.0,
    ("Semi-Trailer", "CNG"): 37.5,
    ("Bus", "Diesel"): 28.0,
    ("Bus", "Petrol"): 32.5,
    ("Bus", "Hybrid"): 21.0,
    ("Bus", "CNG"): 31.0,
}

# Vehicle specifications metadata
VEHICLE_SPECS = {
    "Van": {"max_payload_kg": 1500, "fuel_capacity_l": 75},
    "Light Commercial": {"max_payload_kg": 3500, "fuel_capacity_l": 100},
    "Truck": {"max_payload_kg": 8000, "fuel_capacity_l": 220},
    "Semi-Trailer": {"max_payload_kg": 26000, "fuel_capacity_l": 450},
    "Bus": {"max_payload_kg": 6000, "fuel_capacity_l": 280},
}

ORIGINS = ["Depot A", "Depot B", "Depot C", "Hub North", "Central Hub"]
DESTINATIONS = ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Metro Area", "Port Terminal", "Industrial Park"]


def generate_fleet_dataset(num_samples: int = 6000, seed: int = 42) -> pd.DataFrame:
    """
    Generates a synthetic dataset of fleet trips adhering strictly to GreenFlow JSON contracts.

    Features:
    - Vehicle: vehicle_id, vehicle_type, fuel_type, vehicle_age, fuel_capacity_l, max_payload_kg, available
    - Route: route_id, origin, destination, distance_km, required_payload_kg, traffic_factor, priority, average_speed_kmph, road_grade, weather_factor
    - Target: fuel_consumed_l
    """
    rng = np.random.default_rng(seed)

    vehicle_types = ["Van", "Light Commercial", "Truck", "Semi-Trailer", "Bus"]
    vehicle_type_probs = [0.25, 0.25, 0.25, 0.15, 0.10]
    fuel_types = ["Diesel", "Petrol", "Hybrid", "CNG"]
    fuel_type_probs = [0.55, 0.20, 0.15, 0.10]

    num_vehicles = 60
    num_routes = 30

    vehicle_pool = []
    for i in range(1, num_vehicles + 1):
        v_id = f"V{i:03d}"
        v_type = rng.choice(vehicle_types, p=vehicle_type_probs)
        if v_type in ["Truck", "Semi-Trailer"]:
            f_type = rng.choice(["Diesel", "CNG", "Hybrid"], p=[0.80, 0.12, 0.08])
        else:
            f_type = rng.choice(fuel_types, p=fuel_type_probs)
        v_age = int(rng.integers(1, 13))
        specs = VEHICLE_SPECS[v_type]
        vehicle_pool.append({
            "vehicle_id": v_id,
            "vehicle_type": v_type,
            "fuel_type": f_type,
            "vehicle_age": v_age,
            "fuel_capacity_l": specs["fuel_capacity_l"],
            "max_payload_kg": specs["max_payload_kg"],
            "available": True,
        })
    vehicle_df_pool = pd.DataFrame(vehicle_pool)

    route_pool = []
    for r in range(1, num_routes + 1):
        r_id = f"R{r:03d}"
        origin = rng.choice(ORIGINS)
        destination = rng.choice(DESTINATIONS)
        base_dist = float(rng.uniform(15.0, 320.0))
        base_grade = float(rng.uniform(-3.5, 4.5))
        base_traffic = float(rng.uniform(1.05, 1.85))
        priority = int(rng.choice([1, 2, 3], p=[0.25, 0.50, 0.25]))
        route_pool.append({
            "route_id": r_id,
            "origin": origin,
            "destination": destination,
            "base_distance_km": round(base_dist, 1),
            "base_grade": round(base_grade, 2),
            "base_traffic": round(base_traffic, 2),
            "priority": priority,
        })
    route_df_pool = pd.DataFrame(route_pool)

    sampled_vehicle_indices = rng.integers(0, num_vehicles, size=num_samples)
    sampled_route_indices = rng.integers(0, num_routes, size=num_samples)

    trips_v = vehicle_df_pool.iloc[sampled_vehicle_indices].reset_index(drop=True)
    trips_r = route_df_pool.iloc[sampled_route_indices].reset_index(drop=True)

    distances_km = np.maximum(
        5.0,
        trips_r["base_distance_km"].values + rng.normal(0, 1.5, size=num_samples)
    )
    road_grades = np.clip(
        trips_r["base_grade"].values + rng.normal(0, 0.4, size=num_samples),
        -5.0, 6.5
    )
    traffic_factors = np.clip(
        trips_r["base_traffic"].values + rng.normal(0, 0.15, size=num_samples),
        1.0, 2.5
    )

    # Required payload (kg)
    required_payloads_kg = []
    for i in range(num_samples):
        v_type = trips_v.loc[i, "vehicle_type"]
        max_cap = VEHICLE_SPECS[v_type]["max_payload_kg"]
        load_fraction = rng.uniform(0.10, 0.95)
        required_payloads_kg.append(round(load_fraction * max_cap, 1))
    required_payloads_kg = np.array(required_payloads_kg)

    # Average speed
    speed_base = np.where(distances_km > 100, 75.0, 50.0)
    avg_speeds = np.clip(
        speed_base / traffic_factors + rng.normal(0, 4.0, size=num_samples),
        18.0, 105.0
    )

    weather_factors = np.clip(rng.exponential(scale=0.08, size=num_samples) + 1.0, 1.0, 1.35)

    # Fuel consumption computation
    fuel_consumed = []
    for i in range(num_samples):
        v_type = trips_v.loc[i, "vehicle_type"]
        f_type = trips_v.loc[i, "fuel_type"]
        v_age = trips_v.loc[i, "vehicle_age"]
        dist = distances_km[i]
        load = required_payloads_kg[i]
        traffic = traffic_factors[i]
        speed = avg_speeds[i]
        grade = road_grades[i]
        weather = weather_factors[i]

        base_rate = BASE_CONSUMPTION_L_PER_100KM.get((v_type, f_type), 15.0)
        age_multiplier = 1.0 + (0.012 * v_age)
        max_cap = VEHICLE_SPECS[v_type]["max_payload_kg"]
        load_ratio = np.clip(load / max_cap, 0.0, 1.0)
        load_multiplier = 1.0 + (0.35 * load_ratio)
        traffic_multiplier = 1.0 + (0.28 * (traffic - 1.0))
        speed_penalty = 0.00015 * ((speed - 65.0) ** 2)
        speed_multiplier = 1.0 + speed_penalty

        if grade >= 0:
            grade_multiplier = 1.0 + (0.075 * grade)
        else:
            grade_multiplier = max(0.75, 1.0 + (0.040 * grade))

        weather_multiplier = 1.0 + (0.15 * (weather - 1.0))

        effective_rate = (
            base_rate
            * age_multiplier
            * load_multiplier
            * traffic_multiplier
            * speed_multiplier
            * grade_multiplier
            * weather_multiplier
        )

        trip_fuel_baseline = (effective_rate / 100.0) * dist
        noise = rng.normal(0.0, 0.03 * trip_fuel_baseline)
        trip_fuel = max(0.5, trip_fuel_baseline + noise)
        fuel_consumed.append(round(trip_fuel, 2))

    df = pd.DataFrame({
        "vehicle_id": trips_v["vehicle_id"].values,
        "vehicle_type": trips_v["vehicle_type"].values,
        "fuel_type": trips_v["fuel_type"].values,
        "vehicle_age": trips_v["vehicle_age"].values,
        "fuel_capacity_l": trips_v["fuel_capacity_l"].values,
        "max_payload_kg": trips_v["max_payload_kg"].values,
        "available": trips_v["available"].values,
        "route_id": trips_r["route_id"].values,
        "origin": trips_r["origin"].values,
        "destination": trips_r["destination"].values,
        "distance_km": np.round(distances_km, 1),
        "required_payload_kg": np.round(required_payloads_kg, 1),
        "traffic_factor": np.round(traffic_factors, 2),
        "priority": trips_r["priority"].values,
        "average_speed_kmph": np.round(avg_speeds, 1),
        "road_grade": np.round(road_grades, 2),
        "weather_factor": np.round(weather_factors, 2),
        "fuel_consumed_l": fuel_consumed,
    })

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic fleet dataset for GreenFlow AI ML Engine.")
    parser.add_argument("--samples", type=int, default=6000, help="Number of samples to generate (default: 6000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--output", type=str, default=None, help="Output path for raw CSV")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = args.output or os.path.join(script_dir, "data", "raw", "fleet_data.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"[GreenFlow ML] Generating {args.samples} synthetic fleet trip records (seed={args.seed})...")
    df = generate_fleet_dataset(num_samples=args.samples, seed=args.seed)

    df.to_csv(output_path, index=False)
    print(f"[GreenFlow ML] Successfully saved raw fleet data to: {output_path}")
    print(f"[GreenFlow ML] Dataset shape: {df.shape}")
    print("\nSample Preview matching JSON Contracts:")
    print(df.head(2).to_dict(orient="records"))


if __name__ == "__main__":
    main()
