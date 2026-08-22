"""
GreenFlow AI - Feature Engineering & Preprocessing Pipeline
Provides robust feature extraction adhering strictly to GreenFlow JSON contracts.
"""

import os
from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Core feature definitions
CATEGORICAL_FEATURES = ["vehicle_type", "fuel_type"]
RAW_NUMERIC_FEATURES = [
    "vehicle_age",
    "required_payload_kg",
    "max_payload_kg",
    "distance_km",
    "traffic_factor",
    "average_speed_kmph",
    "road_grade",
    "weather_factor",
]
TARGET_COL = "fuel_consumed_l"


class FleetFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Custom Scikit-Learn compatible transformer creating physics-informed features:
    1. payload_capacity_ratio: required_payload_kg / max_payload_kg (utilization ratio)
    2. speed_efficiency_deviation: (speed - 65)^2 (aerodynamic & idling penalty curve)
    3. traffic_speed_ratio: traffic_factor / (average_speed + 1.0) (congestion severity)
    4. grade_distance_work: distance_km * (1 + road_grade / 100.0) (elevation-weighted distance)
    5. payload_tonnage: required_payload_kg / 1000.0 (cargo in metric tonnes)
    6. weather_stress_index: (weather_factor - 1.0) * distance_km (meteorological drag)
    """

    def __init__(self):
        self.engineered_feature_names = [
            "payload_capacity_ratio",
            "speed_efficiency_deviation",
            "traffic_speed_ratio",
            "grade_distance_work",
            "payload_tonnage",
            "weather_stress_index",
        ]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if not isinstance(X, pd.DataFrame):
            X_df = pd.DataFrame(X).copy()
        else:
            X_df = X.copy()

        # Support alias compatibility for fuel_type / engine_type and load_kg / required_payload_kg
        if "fuel_type" not in X_df.columns and "engine_type" in X_df.columns:
            X_df["fuel_type"] = X_df["engine_type"]
        if "required_payload_kg" not in X_df.columns and "load_kg" in X_df.columns:
            X_df["required_payload_kg"] = X_df["load_kg"]
        if "max_payload_kg" not in X_df.columns:
            # Fallback default capacity
            type_cap = {"Van": 1500.0, "Light Commercial": 3500.0, "Truck": 8000.0, "Semi-Trailer": 26000.0, "Bus": 6000.0}
            X_df["max_payload_kg"] = X_df["vehicle_type"].map(type_cap).fillna(5000.0)
        if "average_speed_kmph" not in X_df.columns:
            X_df["average_speed_kmph"] = 60.0
        if "road_grade" not in X_df.columns:
            X_df["road_grade"] = 0.0
        if "weather_factor" not in X_df.columns:
            X_df["weather_factor"] = 1.0
        if "traffic_factor" not in X_df.columns:
            X_df["traffic_factor"] = 1.0

        speed = X_df["average_speed_kmph"].values.astype(float)
        traffic = X_df["traffic_factor"].values.astype(float)
        dist = X_df["distance_km"].values.astype(float)
        grade = X_df["road_grade"].values.astype(float)
        load = X_df["required_payload_kg"].values.astype(float)
        max_cap = np.maximum(X_df["max_payload_kg"].values.astype(float), 100.0)
        weather = X_df["weather_factor"].values.astype(float)

        X_df["payload_capacity_ratio"] = np.clip(load / max_cap, 0.0, 1.5)
        X_df["speed_efficiency_deviation"] = (speed - 65.0) ** 2
        X_df["traffic_speed_ratio"] = traffic / (speed + 1.0)
        X_df["grade_distance_work"] = dist * (1.0 + grade / 100.0)
        X_df["payload_tonnage"] = load / 1000.0
        X_df["weather_stress_index"] = (weather - 1.0) * dist

        return X_df


def get_all_numeric_features() -> List[str]:
    """Returns list of raw + engineered numeric feature names."""
    return RAW_NUMERIC_FEATURES + [
        "payload_capacity_ratio",
        "speed_efficiency_deviation",
        "traffic_speed_ratio",
        "grade_distance_work",
        "payload_tonnage",
        "weather_stress_index",
    ]


def build_preprocessor_pipeline() -> Pipeline:
    """Constructs preprocessing pipeline for model training and inference."""
    all_numeric = get_all_numeric_features()

    col_transformer = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
            (
                "num",
                StandardScaler(),
                all_numeric,
            ),
        ],
        remainder="drop",
    )

    pipeline = Pipeline(
        steps=[
            ("feature_engineer", FleetFeatureEngineer()),
            ("preprocessor", col_transformer),
        ]
    )
    return pipeline


def prepare_datasets(
    raw_data_path: str,
    processed_data_path: str = None,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Loads raw fleet data, performs train/validation/test split without data leakage.
    """
    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(f"Raw fleet data not found at: {raw_data_path}")

    df = pd.read_csv(raw_data_path)

    # Support column aliases
    if "fuel_type" not in df.columns and "engine_type" in df.columns:
        df["fuel_type"] = df["engine_type"]
    if "required_payload_kg" not in df.columns and "load_kg" in df.columns:
        df["required_payload_kg"] = df["load_kg"]

    required_cols = CATEGORICAL_FEATURES + RAW_NUMERIC_FEATURES + [TARGET_COL]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")

    feature_cols = CATEGORICAL_FEATURES + RAW_NUMERIC_FEATURES
    X = df[feature_cols].copy()
    y = df[TARGET_COL].values

    X_temp, X_test, y_temp, y_test, idx_temp, idx_test = train_test_split(
        X, y, df.index, test_size=test_size, random_state=random_state
    )

    val_relative_size = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val, idx_train, idx_val = train_test_split(
        X_temp, y_temp, idx_temp, test_size=val_relative_size, random_state=random_state
    )

    if processed_data_path:
        os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)
        engineer = FleetFeatureEngineer()
        processed_df = engineer.transform(df)
        processed_df.to_csv(processed_data_path, index=False)
        print(f"[GreenFlow ML] Processed data saved to: {processed_data_path}")

    return {
        "X_train": X_train.reset_index(drop=True),
        "y_train": y_train,
        "X_val": X_val.reset_index(drop=True),
        "y_val": y_val,
        "X_test": X_test.reset_index(drop=True),
        "y_test": y_test,
        "train_df": df.loc[idx_train].reset_index(drop=True),
        "val_df": df.loc[idx_val].reset_index(drop=True),
        "test_df": df.loc[idx_test].reset_index(drop=True),
    }


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(script_dir, "data", "raw", "fleet_data.csv")
    proc_path = os.path.join(script_dir, "data", "processed", "processed_fleet_data.csv")

    if os.path.exists(raw_path):
        data = prepare_datasets(raw_path, proc_path)
        print(f"Train samples: {len(data['X_train'])}")
        print(f"Val samples:   {len(data['X_val'])}")
        print(f"Test samples:  {len(data['X_test'])}")
