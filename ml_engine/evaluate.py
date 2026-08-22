"""
GreenFleet AI - Model Evaluation & Visualisation Engine
Evaluates the trained model against test data and generates publication-grade diagnostics plots.
"""

import os
import sys
import json
import argparse
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure ml_engine directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

from features import prepare_datasets, CATEGORICAL_FEATURES, RAW_NUMERIC_FEATURES

# Set styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10


def plot_actual_vs_predicted(y_true: np.ndarray, y_pred: np.ndarray, output_path: str):
    """Generates an Actual vs. Predicted scatter plot with regression reference."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    ax.scatter(y_true, y_pred, alpha=0.45, color="#10b981", edgecolors="none", s=28, label="Test Trips")

    min_val = min(np.min(y_true), np.min(y_pred))
    max_val = max(np.max(y_true), np.max(y_pred))
    ax.plot([min_val, max_val], [min_val, max_val], color="#ef4444", linestyle="--", lw=2, label="Ideal (y = x)")

    ax.set_title("GreenFleet AI - Actual vs Predicted Fuel Consumption (Litres)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Actual Fuel Consumed (Litres)", fontsize=11, fontweight="medium")
    ax.set_ylabel("Predicted Fuel Consumed (Litres)", fontsize=11, fontweight="medium")

    # Metrics annotation box
    metrics_text = f"Test Metrics:\n$R^2$: {r2:.4f}\nMAE: {mae:.2f} L\nRMSE: {rmse:.2f} L"
    ax.text(
        0.05, 0.95, metrics_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#d1d5db", alpha=0.9),
    )

    ax.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[GreenFleet ML] Actual vs Predicted plot saved to: {output_path}")


def plot_feature_importance(pipeline, X_val: pd.DataFrame, y_val: np.ndarray, output_path: str):
    """Calculates and plots feature importance using permutation importance."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # Compute permutation importance on validation set (model agnostic & handles pipelines)
    perm_importance = permutation_importance(
        pipeline, X_val, y_val, n_repeats=5, random_state=42, n_jobs=1
    )

    feature_names = list(X_val.columns)
    importances = perm_importance.importances_mean
    std = perm_importance.importances_std

    # Sort descending
    indices = np.argsort(importances)[::-1]
    sorted_names = [feature_names[i] for i in indices]
    sorted_importances = importances[indices]
    sorted_std = std[indices]

    y_pos = np.arange(len(sorted_names))
    ax.barh(y_pos, sorted_importances, xerr=sorted_std, align="center", color="#3b82f6", alpha=0.85, ecolor="#1e3a8a", capsize=3)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_names, fontsize=10)
    ax.invert_yaxis()  # top-down
    ax.set_xlabel("Mean Permutation Importance (Drop in $R^2$)", fontsize=11, fontweight="medium")
    ax.set_title("GreenFleet AI - Feature Importance (Permutation)", fontsize=13, fontweight="bold", pad=12)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[GreenFleet ML] Feature importance plot saved to: {output_path}")


def plot_residual_analysis(y_true: np.ndarray, y_pred: np.ndarray, output_path: str):
    """Generates residual distribution and residual vs predicted diagnostic plots."""
    residuals = y_true - y_pred

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # Residuals vs Predicted
    ax1.scatter(y_pred, residuals, alpha=0.4, color="#6366f1", edgecolors="none", s=25)
    ax1.axhline(0, color="#ef4444", linestyle="--", lw=1.8)
    ax1.set_title("Residuals vs Predicted Fuel", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Predicted Fuel (Litres)", fontsize=10)
    ax1.set_ylabel("Residual (Actual - Predicted) [L]", fontsize=10)

    # Residuals Distribution
    sns.histplot(residuals, kde=True, ax=ax2, color="#059669", bins=30)
    ax2.axvline(0, color="#ef4444", linestyle="--", lw=1.8)
    ax2.set_title("Residual Distribution (Error Normality)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Residual (Litres)", fontsize=10)
    ax2.set_ylabel("Frequency", fontsize=10)

    plt.suptitle("GreenFleet AI - Error & Residual Diagnostic Analysis", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[GreenFleet ML] Residual analysis plot saved to: {output_path}")


def run_evaluation(
    model_path: str,
    raw_data_path: str,
    output_dir: str,
    seed: int = 42,
) -> dict:
    """Loads saved model and runs full evaluation suite on holdout test data."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}. Train the model first.")

    pipeline = joblib.load(model_path)
    os.makedirs(output_dir, exist_ok=True)

    datasets = prepare_datasets(
        raw_data_path=raw_data_path,
        test_size=0.15,
        val_size=0.15,
        random_state=seed,
    )

    X_val = datasets["X_val"]
    y_val = datasets["y_val"]
    X_test = datasets["X_test"]
    y_test = datasets["y_test"]

    # Predict on test set
    test_preds = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, test_preds)
    rmse = np.sqrt(mean_squared_error(y_test, test_preds))
    r2 = r2_score(y_test, test_preds)
    mape = np.mean(np.abs((y_test - test_preds) / np.maximum(y_test, 1e-5))) * 100.0

    metrics = {
        "test_mae_l": round(float(mae), 4),
        "test_rmse_l": round(float(rmse), 4),
        "test_r2": round(float(r2), 4),
        "test_mape_percent": round(float(mape), 2),
        "test_sample_count": len(y_test),
    }

    print("\n=======================================================")
    print("           GREENFLEET AI - MODEL EVALUATION             ")
    print("=======================================================")
    print(f" Test Samples:     {metrics['test_sample_count']}")
    print(f" Mean Absolute Error (MAE):     {metrics['test_mae_l']:.2f} Litres")
    print(f" Root Mean Squared Error (RMSE): {metrics['test_rmse_l']:.2f} Litres")
    print(f" Coefficient of Determination (R²): {metrics['test_r2']:.4f}")
    print(f" Mean Absolute Percentage Error: {metrics['test_mape_percent']:.2f}%")
    print("=======================================================\n")

    # Generate plots
    plot_actual_vs_predicted(
        y_test, test_preds, os.path.join(output_dir, "actual_vs_predicted.png")
    )
    plot_feature_importance(
        pipeline, X_val, y_val, os.path.join(output_dir, "feature_importance.png")
    )
    plot_residual_analysis(
        y_test, test_preds, os.path.join(output_dir, "residual_analysis.png")
    )

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate GreenFleet AI Fuel Model")
    parser.add_argument("--model", type=str, default=None, help="Path to fuel_model.pkl")
    parser.add_argument("--data", type=str, default=None, help="Path to raw fleet_data.csv")
    parser.add_argument("--output_dir", type=str, default=None, help="Directory to save evaluation plots")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = args.model or os.path.join(script_dir, "models", "fuel_model.pkl")
    raw_path = args.data or os.path.join(script_dir, "data", "raw", "fleet_data.csv")
    output_dir = args.output_dir or os.path.join(script_dir, "models")

    run_evaluation(
        model_path=model_path,
        raw_data_path=raw_path,
        output_dir=output_dir,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
