"""
BuildWise-AI — Phase 3B: CPU Benchmark Regression Training Pipeline

Trains and cross-validates 4 regression models to predict CPU Cinebench R23 Multi-Core scores
from physical hardware specifications using 5-fold GroupKFold by silicon family.

Algorithms:
1. DummyRegressor (Baseline: mean prediction)
2. Ridge Regression (StandardScaler + OneHotEncoder + L2 Regularization)
3. RandomForestRegressor (Ensemble decision trees with depth limiting)
4. HistGradientBoostingRegressor (Gradient boosting with small leaf constraints)

Strict Leakage & Governance Rules:
- Features strictly limited to: cores, threads, boost_clock_ghz, tdp_w, brand, socket.
- No prices, tiers, sellers, or identifiers in predictive features.
- Preprocessing fitted inside each fold.
- GroupKFold strictly ensures 0% silicon family overlap across train and test.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

try:
    from experiments.cpu_benchmark_regression.prepare_dataset import (
        get_project_root,
        prepare_cpu_benchmark_dataset,
        PREDICTIVE_NUMERIC_FEATURES,
        PREDICTIVE_CATEGORICAL_FEATURES,
        PREDICTIVE_FEATURES,
        TARGET_COLUMN
    )
except ImportError:
    from prepare_dataset import (
        get_project_root,
        prepare_cpu_benchmark_dataset,
        PREDICTIVE_NUMERIC_FEATURES,
        PREDICTIVE_CATEGORICAL_FEATURES,
        PREDICTIVE_FEATURES,
        TARGET_COLUMN
    )


def build_preprocessor(scale_numerics: bool = True) -> ColumnTransformer:
    """Construct ColumnTransformer for numerical and categorical features."""
    transformers = []
    if scale_numerics:
        transformers.append(("num", StandardScaler(), PREDICTIVE_NUMERIC_FEATURES))
    else:
        transformers.append(("num", "passthrough", PREDICTIVE_NUMERIC_FEATURES))
    
    transformers.append((
        "cat",
        OneHotEncoder(handle_unknown="ignore", sparse_output=False),
        PREDICTIVE_CATEGORICAL_FEATURES
    ))
    return ColumnTransformer(transformers=transformers)


def get_model_pipeline(algorithm: str, random_state: int = 42) -> Pipeline:
    """Return configured scikit-learn Pipeline for candidate algorithm."""
    if algorithm == "dummy":
        return Pipeline([
            ("regressor", DummyRegressor(strategy="mean"))
        ])
    elif algorithm == "ridge":
        return Pipeline([
            ("preprocessor", build_preprocessor(scale_numerics=True)),
            ("regressor", Ridge(alpha=1.0, random_state=random_state))
        ])
    elif algorithm == "random_forest":
        return Pipeline([
            ("preprocessor", build_preprocessor(scale_numerics=False)),
            ("regressor", RandomForestRegressor(
                n_estimators=100,
                max_depth=3,
                min_samples_leaf=2,
                random_state=random_state
            ))
        ])
    elif algorithm == "hist_gradient_boosting":
        return Pipeline([
            ("preprocessor", build_preprocessor(scale_numerics=False)),
            ("regressor", HistGradientBoostingRegressor(
                max_iter=40,
                max_depth=3,
                learning_rate=0.05,
                min_samples_leaf=3,
                early_stopping=False,
                random_state=random_state
            ))
        ])
    else:
        raise ValueError(f"Unknown algorithm '{algorithm}'")


def cross_validate_model(
    df: pd.DataFrame,
    algorithm: str,
    n_splits: int = 5,
    random_state: int = 42
) -> Dict[str, Any]:
    """Perform 5-fold GroupKFold cross-validation and compute evaluation metrics."""
    gkf = GroupKFold(n_splits=n_splits)
    groups = df["group_id"].values
    X = df[PREDICTIVE_FEATURES]
    y = df[TARGET_COLUMN].values
    
    oof_predictions = np.zeros(len(df))
    fold_records = []
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups), 1):
        # Strict zero-leakage check
        train_groups = set(groups[train_idx])
        val_groups = set(groups[val_idx])
        leakage = train_groups.intersection(val_groups)
        if leakage:
            raise AssertionError(f"Data leakage detected in fold {fold}: {leakage}")
        
        X_train, y_train = X.iloc[train_idx], y[train_idx]
        X_val, y_val = X.iloc[val_idx], y[val_idx]
        
        # Fit pipeline strictly on training fold
        pipe = get_model_pipeline(algorithm, random_state=random_state)
        pipe.fit(X_train, y_train)
        
        # Predict on validation fold
        preds = pipe.predict(X_val)
        oof_predictions[val_idx] = preds
        
        # Fold metrics
        f_mae = float(mean_absolute_error(y_val, preds))
        f_rmse = float(root_mean_squared_error(y_val, preds))
        f_r2 = float(r2_score(y_val, preds))
        
        fold_records.append({
            "fold": fold,
            "train_samples": len(train_idx),
            "val_samples": len(val_idx),
            "val_groups_count": len(val_groups),
            "mae": f_mae,
            "rmse": f_rmse,
            "r2": f_r2
        })
    
    # Aggregated Out-Of-Fold metrics
    agg_mae = float(mean_absolute_error(y, oof_predictions))
    agg_rmse = float(root_mean_squared_error(y, oof_predictions))
    agg_r2 = float(r2_score(y, oof_predictions))
    
    mean_fold_mae = float(np.mean([f["mae"] for f in fold_records]))
    std_fold_mae = float(np.std([f["mae"] for f in fold_records]))
    mean_fold_rmse = float(np.mean([f["rmse"] for f in fold_records]))
    std_fold_rmse = float(np.std([f["rmse"] for f in fold_records]))
    mean_fold_r2 = float(np.mean([f["r2"] for f in fold_records]))
    std_fold_r2 = float(np.std([f["r2"] for f in fold_records]))
    
    return {
        "algorithm": algorithm,
        "n_samples": len(df),
        "n_splits": n_splits,
        "features": PREDICTIVE_FEATURES,
        "fold_metrics": fold_records,
        "mean_fold_mae": mean_fold_mae,
        "std_fold_mae": std_fold_mae,
        "mean_fold_rmse": mean_fold_rmse,
        "std_fold_rmse": std_fold_rmse,
        "mean_fold_r2": mean_fold_r2,
        "std_fold_r2": std_fold_r2,
        "aggregated_oof_mae": agg_mae,
        "aggregated_oof_rmse": agg_rmse,
        "aggregated_oof_r2": agg_r2,
        "oof_predictions": oof_predictions
    }


def run_experiment(project_root: Path = None) -> Dict[str, Any]:
    """Execute complete ML training and cross-validation experiment."""
    if project_root is None:
        project_root = get_project_root()
    
    dataset_path = project_root / "data" / "ml" / "cpu_benchmark_training_v1.csv"
    if not dataset_path.is_file():
        df = prepare_cpu_benchmark_dataset(project_root=project_root)
    else:
        df = pd.read_csv(dataset_path)
    
    print(f"=== Loaded dataset with {len(df)} samples and {df['group_id'].nunique()} silicon family groups ===")
    
    algorithms = ["dummy", "ridge", "random_forest", "hist_gradient_boosting"]
    results = {}
    
    for algo in algorithms:
        res = cross_validate_model(df, algo)
        results[algo] = res
        print(f"\n[Algorithm: {algo.upper()}]")
        print(f"  Fold MAE: {[round(f['mae'], 1) for f in res['fold_metrics']]} -> Mean: {res['mean_fold_mae']:.1f} ± {res['std_fold_mae']:.1f}")
        print(f"  Fold RMSE: {[round(f['rmse'], 1) for f in res['fold_metrics']]} -> Mean: {res['mean_fold_rmse']:.1f} ± {res['std_fold_rmse']:.1f}")
        print(f"  Fold R²: {[round(f['r2'], 3) for f in res['fold_metrics']]} -> Mean: {res['mean_fold_r2']:.3f} ± {res['std_fold_r2']:.3f}")
        print(f"  Aggregated OOF: MAE={res['aggregated_oof_mae']:.1f} pts, RMSE={res['aggregated_oof_rmse']:.1f} pts, R²={res['aggregated_oof_r2']:.3f}")
    
    # Generate Out-Of-Fold predictions DataFrame
    gkf = GroupKFold(n_splits=5)
    fold_assignment = np.zeros(len(df), dtype=int)
    for fold, (_, val_idx) in enumerate(gkf.split(df, df[TARGET_COLUMN], df["group_id"]), 1):
        fold_assignment[val_idx] = fold
    
    oof_df = df[["component_id", "model", "brand", "socket", "cores", "threads", "boost_clock_ghz", "tdp_w", "group_id", "score"]].copy()
    oof_df.rename(columns={"score": "actual_score"}, inplace=True)
    oof_df["cv_fold"] = fold_assignment
    
    for algo in algorithms:
        oof_df[f"pred_{algo}"] = results[algo]["oof_predictions"]
        oof_df[f"abs_err_{algo}"] = np.abs(oof_df["actual_score"] - oof_df[f"pred_{algo}"])
        oof_df[f"pct_err_{algo}"] = (oof_df[f"abs_err_{algo}"] / oof_df["actual_score"]) * 100.0
    
    exp_dir = project_root / "experiments" / "cpu_benchmark_regression"
    exp_dir.mkdir(parents=True, exist_ok=True)
    oof_path = exp_dir / "oof_predictions.csv"
    oof_df.to_csv(oof_path, index=False)
    print(f"\nSaved out-of-fold predictions to: {oof_path}")
    
    # Save evaluation.json (excluding numpy arrays for serialization)
    serializable_results = {}
    for algo, res in results.items():
        copy_res = {k: v for k, v in res.items() if k != "oof_predictions"}
        serializable_results[algo] = copy_res
    
    eval_json_path = exp_dir / "evaluation.json"
    with open(eval_json_path, "w", encoding="utf-8") as f:
        json.dump(serializable_results, f, indent=2)
    print(f"Saved evaluation metrics to: {eval_json_path}")
    
    # Determine best model and check if it beats dummy baseline
    dummy_mae = results["dummy"]["aggregated_oof_mae"]
    dummy_rmse = results["dummy"]["aggregated_oof_rmse"]
    
    candidate_algos = [a for a in algorithms if a != "dummy"]
    best_algo = min(candidate_algos, key=lambda a: results[a]["aggregated_oof_mae"])
    best_metrics = results[best_algo]
    
    beats_baseline = (
        best_metrics["aggregated_oof_mae"] < dummy_mae and
        best_metrics["aggregated_oof_rmse"] < dummy_rmse and
        best_metrics["aggregated_oof_r2"] > 0.0
    )
    
    print("\n=== MODEL COMPARISON vs BASELINE ===")
    print(f"Baseline DummyRegressor MAE: {dummy_mae:.1f} pts, RMSE: {dummy_rmse:.1f} pts")
    print(f"Best Candidate ({best_algo}): MAE: {best_metrics['aggregated_oof_mae']:.1f} pts, RMSE: {best_metrics['aggregated_oof_rmse']:.1f} pts, R²: {best_metrics['aggregated_oof_r2']:.3f}")
    print(f"Error Reduction: {((dummy_mae - best_metrics['aggregated_oof_mae']) / dummy_mae) * 100:.2f}%")
    print(f"Beats baseline: {beats_baseline}")
    
    if beats_baseline:
        models_exp_dir = project_root / "models" / "experimental"
        models_exp_dir.mkdir(parents=True, exist_ok=True)
        
        # Fit final pipeline on all 55 verified training samples
        final_pipeline = get_model_pipeline(best_algo)
        final_pipeline.fit(df[PREDICTIVE_FEATURES], df[TARGET_COLUMN].values)
        
        model_artifact_path = models_exp_dir / "cpu_cinebench_r23_v1.joblib"
        joblib.dump(final_pipeline, model_artifact_path)
        print(f"\nSaved experimental model artifact to: {model_artifact_path}")
        
        metadata = {
            "model_name": f"CPU Cinebench R23 Multi-Core Predictor ({best_algo})",
            "model_type": "Pipeline(StandardScaler + OneHotEncoder + Ridge(alpha=1.0))" if best_algo == "ridge" else best_algo,
            "algorithm": best_algo,
            "status": "EXPERIMENTAL",
            "target_variable": TARGET_COLUMN,
            "target_unit": "Cinebench R23 Multi-Core points (pts)",
            "predictive_features": PREDICTIVE_FEATURES,
            "numeric_features": PREDICTIVE_NUMERIC_FEATURES,
            "categorical_features": PREDICTIVE_CATEGORICAL_FEATURES,
            "training_dataset": "data/ml/cpu_benchmark_training_v1.csv",
            "n_training_samples": len(df),
            "n_silicon_families": int(df["group_id"].nunique()),
            "validation_strategy": "5-fold GroupKFold by verified silicon die family",
            "leakage_prevention": "Strict zero-overlap group splitting",
            "evaluation_metrics": {
                "dummy_baseline": {
                    "mae": round(dummy_mae, 1),
                    "rmse": round(dummy_rmse, 1),
                    "r2": round(results["dummy"]["aggregated_oof_r2"], 4)
                },
                "experimental_model": {
                    "mean_fold_mae": round(best_metrics["mean_fold_mae"], 1),
                    "std_fold_mae": round(best_metrics["std_fold_mae"], 1),
                    "mean_fold_rmse": round(best_metrics["mean_fold_rmse"], 1),
                    "std_fold_rmse": round(best_metrics["std_fold_rmse"], 1),
                    "mean_fold_r2": round(best_metrics["mean_fold_r2"], 4),
                    "std_fold_r2": round(best_metrics["std_fold_r2"], 4),
                    "aggregated_oof_mae": round(best_metrics["aggregated_oof_mae"], 1),
                    "aggregated_oof_rmse": round(best_metrics["aggregated_oof_rmse"], 1),
                    "aggregated_oof_r2": round(best_metrics["aggregated_oof_r2"], 4),
                    "mae_reduction_pct": round(((dummy_mae - best_metrics["aggregated_oof_mae"]) / dummy_mae) * 100, 2)
                }
            },
            "disclaimer": "EXPERIMENTAL ONLY: Trained on 55 desktop CPU observations across 30 silicon families. Do not deploy to production recommendation logic without broader sample coverage and architecture-level features."
        }
        
        metadata_path = models_exp_dir / "cpu_cinebench_r23_v1_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved experimental model metadata to: {metadata_path}")
    
    return results


if __name__ == "__main__":
    run_experiment()
