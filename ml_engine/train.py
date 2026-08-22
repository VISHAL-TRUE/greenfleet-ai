"""
GreenFleet AI - Model Training Pipeline
Trains LightGBM (with baseline model comparison) to predict vehicle fuel consumption.
"""

import os
import sys
import json
import argparse
import joblib
import numpy as np
import pandas as pd

# Ensure ml_engine directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from features import (
    build_preprocessor_pipeline,
    prepare_datasets,
    TARGET_COL,
    CATEGORICAL_FEATURES,
    RAW_NUMERIC_FEATURES,
    get_all_numeric_features,
)

import importlib

# Attempt LightGBM import dynamically to avoid IDE unresolved-import warnings if not installed
def _load_lightgbm():
    try:
        return importlib.import_module("lightgbm")
    except Exception:
        return None

lgb = _load_lightgbm()
HAS_LIGHTGBM = lgb is not None


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calculates MAE, RMSE, R2, and MAPE metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1e-5))) * 100.0

    return {
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2": round(float(r2), 4),
        "mape_percent": round(float(mape), 2),
    }


def get_model_instance(model_name: str, seed: int = 42):
    """Factory to initialize model instances with fixed seed."""
    if model_name.lower() in ["lightgbm", "lgbm"]:
        if HAS_LIGHTGBM and lgb is not None:
            return lgb.LGBMRegressor(
                n_estimators=300,
                learning_rate=0.05,
                num_leaves=31,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=seed,
                n_jobs=-1,
                verbose=-1,
            )
        else:
            print("[GreenFleet ML Warning] LightGBM C++ package not present in current environment. "
                  "Using Scikit-Learn HistGradientBoostingRegressor (native histogram GBDT equivalent).")
            return HistGradientBoostingRegressor(
                max_iter=300,
                learning_rate=0.05,
                max_leaf_nodes=31,
                random_state=seed,
            )
    elif model_name.lower() in ["random_forest", "rf"]:
        return RandomForestRegressor(
            n_estimators=150,
            max_depth=16,
            random_state=seed,
            n_jobs=-1,
        )
    elif model_name.lower() in ["linear_regression", "linear"]:
        return LinearRegression()
    else:
        raise ValueError(f"Unknown model name: {model_name}")


def train_and_evaluate(
    raw_data_path: str,
    output_model_path: str,
    seed: int = 42,
    compare_baselines: bool = True,
) -> dict:
    """
    Main training workflow:
    1. Loads and splits data into Train / Val / Test (no leakage).
    2. Builds end-to-end preprocessing + ML pipeline.
    3. Trains LightGBM & baseline models.
    4. Evaluates performance across all splits.
    5. Persists the best trained pipeline artifact and metadata.
    """
    print(f"[GreenFleet ML] Loading data from {raw_data_path}...")
    datasets = prepare_datasets(
        raw_data_path=raw_data_path,
        processed_data_path=os.path.join(
            os.path.dirname(raw_data_path), "..", "processed", "processed_fleet_data.csv"
        ),
        test_size=0.15,
        val_size=0.15,
        random_state=seed,
    )

    X_train = datasets["X_train"]
    y_train = datasets["y_train"]
    X_val = datasets["X_val"]
    y_val = datasets["y_val"]
    X_test = datasets["X_test"]
    y_test = datasets["y_test"]

    print(f"[GreenFleet ML] Split sizes: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

    models_to_run = ["lightgbm"]
    if compare_baselines:
        models_to_run.extend(["linear_regression", "random_forest"])

    results = {}
    best_model_name = None
    best_val_r2 = -float("inf")
    best_pipeline = None

    for m_name in models_to_run:
        print(f"\n[GreenFleet ML] Training {m_name.upper()}...")
        preprocessor = build_preprocessor_pipeline()
        regressor = get_model_instance(m_name, seed=seed)

        pipeline = Pipeline(
            steps=[
                ("feature_pipeline", preprocessor),
                ("regressor", regressor),
            ]
        )

        pipeline.fit(X_train, y_train)

        # Predict
        train_preds = pipeline.predict(X_train)
        val_preds = pipeline.predict(X_val)
        test_preds = pipeline.predict(X_test)

        train_metrics = calculate_metrics(y_train, train_preds)
        val_metrics = calculate_metrics(y_val, val_preds)
        test_metrics = calculate_metrics(y_test, test_preds)

        print(f"  Train: MAE={train_metrics['mae']:.2f} L, RMSE={train_metrics['rmse']:.2f} L, R²={train_metrics['r2']:.4f}")
        print(f"  Val:   MAE={val_metrics['mae']:.2f} L, RMSE={val_metrics['rmse']:.2f} L, R²={val_metrics['r2']:.4f}")
        print(f"  Test:  MAE={test_metrics['mae']:.2f} L, RMSE={test_metrics['rmse']:.2f} L, R²={test_metrics['r2']:.4f}")

        results[m_name] = {
            "train": train_metrics,
            "val": val_metrics,
            "test": test_metrics,
        }

        if val_metrics["r2"] > best_val_r2:
            best_val_r2 = val_metrics["r2"]
            best_model_name = m_name
            best_pipeline = pipeline

    # Save best model artifact
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    joblib.dump(best_pipeline, output_model_path)
    print(f"\n[GreenFleet ML] Best model ({best_model_name.upper()}) saved to: {output_model_path}")

    # Save evaluation summary and metadata
    metadata = {
        "best_model": best_model_name,
        "is_lightgbm_native": HAS_LIGHTGBM,
        "random_seed": seed,
        "features": {
            "categorical": CATEGORICAL_FEATURES,
            "raw_numeric": RAW_NUMERIC_FEATURES,
            "all_numeric": get_all_numeric_features(),
        },
        "target": TARGET_COL,
        "metrics_summary": results,
    }

    metrics_path = os.path.join(os.path.dirname(output_model_path), "evaluation_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"[GreenFleet ML] Evaluation metrics saved to: {metrics_path}")

    return {
        "best_model_name": best_model_name,
        "best_pipeline": best_pipeline,
        "results": results,
        "datasets": datasets,
    }


def main():
    parser = argparse.ArgumentParser(description="Train GreenFleet AI Fuel Consumption Model")
    parser.add_argument("--data", type=str, default=None, help="Path to raw fleet_data.csv")
    parser.add_argument("--output", type=str, default=None, help="Path to save fuel_model.pkl")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--no-baselines", action="store_true", help="Skip baseline model comparison")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = args.data or os.path.join(script_dir, "data", "raw", "fleet_data.csv")
    output_path = args.output or os.path.join(script_dir, "models", "fuel_model.pkl")

    train_and_evaluate(
        raw_data_path=raw_path,
        output_model_path=output_path,
        seed=args.seed,
        compare_baselines=not args.no_baselines,
    )


if __name__ == "__main__":
    main()
