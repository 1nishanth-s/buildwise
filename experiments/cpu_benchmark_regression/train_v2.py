"""
BuildWise-AI — Phase 3C: CPU Benchmark Regression Training Pipeline V2

Evaluates enriched architectural and cache features across controlled feature sets
using 5-fold GroupKFold cross-validation by verified silicon family.

Feature Sets:
- Set A (V1 Baseline): cores, threads, boost_clock_ghz, tdp_w, brand, socket (6 features)
- Set B (Architecture): Set A + architecture (7 features)
- Set C (Cache L3): Set A + cache_l3_mb (7 features)
- Set D (Combined Arch + L3): Set A + architecture, cache_l3_mb (8 features)
- Set E (Comprehensive): Set A + architecture, cache_l3_mb, cache_l2_mb, base_clock_ghz (10 features)

Algorithms Evaluated:
1. DummyRegressor (Baseline)
2. Ridge Regression (StandardScaler + OneHotEncoder + L2 Regularization, alpha=1.0)
3. RandomForestRegressor (max_depth=3, min_samples_leaf=2, random_state=42)
4. HistGradientBoostingRegressor (max_depth=3, min_samples_leaf=3, learning_rate=0.05, max_iter=40, random_state=42)

Leakage Prevention:
- 5-fold GroupKFold by group_id (30 verified silicon die families).
- Zero silicon family overlap between training and validation folds.
- Preprocessing fitted strictly inside each training fold.
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


def get_project_root() -> Path:
    """Resolve repository root directory."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "data" / "components.csv").is_file() and (parent / "data" / "benchmarks.csv").is_file():
            return parent
    raise FileNotFoundError("Could not locate project root containing data/components.csv")


FEATURE_CONFIGURATIONS = {
    "Set_A_V1_Baseline": {
        "description": "Original V1 6-feature baseline",
        "numeric": ["cores", "threads", "boost_clock_ghz", "tdp_w"],
        "categorical": ["brand", "socket"]
    },
    "Set_B_Architecture": {
        "description": "Original 6 features + microarchitecture generation",
        "numeric": ["cores", "threads", "boost_clock_ghz", "tdp_w"],
        "categorical": ["brand", "socket", "architecture"]
    },
    "Set_C_CacheL3": {
        "description": "Original 6 features + total shared L3 cache",
        "numeric": ["cores", "threads", "boost_clock_ghz", "tdp_w", "cache_l3_mb"],
        "categorical": ["brand", "socket"]
    },
    "Set_D_Combined_Arch_L3": {
        "description": "Original 6 features + architecture + cache_l3_mb",
        "numeric": ["cores", "threads", "boost_clock_ghz", "tdp_w", "cache_l3_mb"],
        "categorical": ["brand", "socket", "architecture"]
    },
    "Set_E_Comprehensive": {
        "description": "Original 6 features + architecture + cache_l3_mb + cache_l2_mb + base_clock_ghz",
        "numeric": ["cores", "threads", "boost_clock_ghz", "tdp_w", "cache_l3_mb", "cache_l2_mb", "base_clock_ghz"],
        "categorical": ["brand", "socket", "architecture"]
    }
}


def load_enriched_dataset(project_root: Path = None) -> pd.DataFrame:
    """Load and merge V1 training dataset with verified feature enrichment records."""
    if project_root is None:
        project_root = get_project_root()
    
    v1_path = project_root / "data" / "ml" / "cpu_benchmark_training_v1.csv"
    enrich_path = project_root / "data" / "ml" / "cpu_feature_enrichment_v1.csv"
    
    if not v1_path.is_file():
        raise FileNotFoundError(f"V1 dataset not found at {v1_path}")
    if not enrich_path.is_file():
        raise FileNotFoundError(f"Enrichment dataset not found at {enrich_path}")
    
    df_v1 = pd.read_csv(v1_path)
    df_enrich = pd.read_csv(enrich_path)
    
    # Pivot enrichment records from EAV to wide format
    pivoted = df_enrich.pivot(
        index="component_id",
        columns="feature_name",
        values="verified_value"
    ).reset_index()
    
    # Merge onto V1 records
    merged = df_v1.merge(pivoted, on="component_id", how="inner")
    if len(merged) != len(df_v1):
        raise ValueError(f"Merge row count mismatch: {len(merged)} vs {len(df_v1)}")
    
    # Ensure correct data types
    merged["cache_l3_mb"] = merged["cache_l3_mb"].astype(float)
    merged["cache_l2_mb"] = merged["cache_l2_mb"].astype(float)
    merged["base_clock_ghz"] = merged["base_clock_ghz"].astype(float)
    merged["architecture"] = merged["architecture"].astype(str)
    merged["cpu_codename"] = merged["cpu_codename"].astype(str)
    
    return merged


def get_v2_model_pipeline(algorithm: str, numeric_features: List[str], categorical_features: List[str], random_state: int = 42) -> Pipeline:
    """Build scikit-learn Pipeline with fold-safe ColumnTransformer."""
    if algorithm == "dummy":
        return Pipeline([("regressor", DummyRegressor(strategy="mean"))])
    
    elif algorithm == "ridge":
        preprocessor = ColumnTransformer([
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ])
        return Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", Ridge(alpha=1.0, random_state=random_state))
        ])
    
    elif algorithm == "random_forest":
        preprocessor = ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ], remainder="passthrough")
        return Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(
                n_estimators=100,
                max_depth=3,
                min_samples_leaf=2,
                random_state=random_state
            ))
        ])
    
    elif algorithm == "hist_gradient_boosting":
        preprocessor = ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ], remainder="passthrough")
        return Pipeline([
            ("preprocessor", preprocessor),
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


def cross_validate_feature_set(
    df: pd.DataFrame,
    fs_name: str,
    algorithm: str,
    n_splits: int = 5,
    random_state: int = 42
) -> Dict[str, Any]:
    """Execute 5-fold GroupKFold cross-validation for a specific feature set configuration."""
    fs = FEATURE_CONFIGURATIONS[fs_name]
    num_cols = fs["numeric"]
    cat_cols = fs["categorical"]
    all_features = num_cols + cat_cols
    
    gkf = GroupKFold(n_splits=n_splits)
    groups = df["group_id"].values
    X = df[all_features]
    y = df["score"].values
    
    oof_predictions = np.zeros(len(df))
    fold_records = []
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups), 1):
        # Strict zero-leakage check
        train_groups = set(groups[train_idx])
        val_groups = set(groups[val_idx])
        overlap = train_groups.intersection(val_groups)
        if overlap:
            raise AssertionError(f"Data leakage detected in {fs_name} fold {fold}: {overlap}")
        
        X_train, y_train = X.iloc[train_idx], y[train_idx]
        X_val, y_val = X.iloc[val_idx], y[val_idx]
        
        pipe = get_v2_model_pipeline(algorithm, num_cols, cat_cols, random_state=random_state)
        pipe.fit(X_train, y_train)
        
        preds = pipe.predict(X_val)
        oof_predictions[val_idx] = preds
        
        f_mae = float(mean_absolute_error(y_val, preds))
        f_rmse = float(root_mean_squared_error(y_val, preds))
        f_r2 = float(r2_score(y_val, preds))
        
        fold_records.append({
            "fold": fold,
            "train_samples": len(train_idx),
            "val_samples": len(val_idx),
            "mae": f_mae,
            "rmse": f_rmse,
            "r2": f_r2
        })
    
    agg_mae = float(mean_absolute_error(y, oof_predictions))
    agg_rmse = float(root_mean_squared_error(y, oof_predictions))
    agg_r2 = float(r2_score(y, oof_predictions))
    
    return {
        "feature_set": fs_name,
        "algorithm": algorithm,
        "n_features": len(all_features),
        "features": all_features,
        "numeric_features": num_cols,
        "categorical_features": cat_cols,
        "fold_metrics": fold_records,
        "mean_fold_mae": float(np.mean([f["mae"] for f in fold_records])),
        "std_fold_mae": float(np.std([f["mae"] for f in fold_records])),
        "mean_fold_rmse": float(np.mean([f["rmse"] for f in fold_records])),
        "std_fold_rmse": float(np.std([f["rmse"] for f in fold_records])),
        "mean_fold_r2": float(np.mean([f["r2"] for f in fold_records])),
        "std_fold_r2": float(np.std([f["r2"] for f in fold_records])),
        "aggregated_oof_mae": agg_mae,
        "aggregated_oof_rmse": agg_rmse,
        "aggregated_oof_r2": agg_r2,
        "oof_predictions": oof_predictions
    }


def run_phase3c_training(project_root: Path = None) -> Dict[str, Any]:
    """Execute complete Phase 3C training, feature ablation, and artifact generation."""
    if project_root is None:
        project_root = get_project_root()
    
    df = load_enriched_dataset(project_root=project_root)
    print(f"=== Loaded Enriched Dataset: {len(df)} CPUs across {df['group_id'].nunique()} silicon families ===")
    
    algorithms = ["dummy", "ridge", "random_forest", "hist_gradient_boosting"]
    all_results = {}
    comparison_rows = []
    
    exp_dir = project_root / "experiments" / "cpu_benchmark_regression"
    exp_dir.mkdir(parents=True, exist_ok=True)
    
    # Run cross-validation across all feature sets and algorithms
    for fs_name in FEATURE_CONFIGURATIONS.keys():
        all_results[fs_name] = {}
        for algo in algorithms:
            res = cross_validate_feature_set(df, fs_name, algo)
            all_results[fs_name][algo] = res
            
            comparison_rows.append({
                "feature_set": fs_name,
                "description": FEATURE_CONFIGURATIONS[fs_name]["description"],
                "algorithm": algo,
                "n_features": res["n_features"],
                "agg_oof_mae": round(res["aggregated_oof_mae"], 1),
                "agg_oof_rmse": round(res["aggregated_oof_rmse"], 1),
                "agg_oof_r2": round(res["aggregated_oof_r2"], 4),
                "mean_fold_mae": round(res["mean_fold_mae"], 1),
                "std_fold_mae": round(res["std_fold_mae"], 1),
                "mean_fold_rmse": round(res["mean_fold_rmse"], 1),
                "std_fold_rmse": round(res["std_fold_rmse"], 1),
                "mean_fold_r2": round(res["mean_fold_r2"], 4),
                "std_fold_r2": round(res["std_fold_r2"], 4)
            })
    
    # 1. Save feature_comparison.csv
    comp_df = pd.DataFrame(comparison_rows)
    comp_path = exp_dir / "feature_comparison.csv"
    comp_df.to_csv(comp_path, index=False)
    print(f"\nSaved feature comparison table to: {comp_path}")
    
    # 2. Build V2 Out-Of-Fold Predictions DataFrame
    gkf = GroupKFold(n_splits=5)
    fold_assignment = np.zeros(len(df), dtype=int)
    for fold, (_, val_idx) in enumerate(gkf.split(df, df["score"], df["group_id"]), 1):
        fold_assignment[val_idx] = fold
    
    v2_oof_df = df[["component_id", "model", "brand", "socket", "cores", "threads", "boost_clock_ghz", "tdp_w", "architecture", "cache_l3_mb", "cache_l2_mb", "base_clock_ghz", "group_id", "score"]].copy()
    v2_oof_df.rename(columns={"score": "actual_score"}, inplace=True)
    v2_oof_df["cv_fold"] = fold_assignment
    
    # Add predictions for key configurations
    for fs_name in ["Set_A_V1_Baseline", "Set_B_Architecture", "Set_D_Combined_Arch_L3", "Set_E_Comprehensive"]:
        for algo in ["ridge", "random_forest"]:
            v2_oof_df[f"pred_{fs_name}_{algo}"] = all_results[fs_name][algo]["oof_predictions"]
            v2_oof_df[f"abs_err_{fs_name}_{algo}"] = np.abs(v2_oof_df["actual_score"] - v2_oof_df[f"pred_{fs_name}_{algo}"])
            v2_oof_df[f"pct_err_{fs_name}_{algo}"] = (v2_oof_df[f"abs_err_{fs_name}_{algo}"] / v2_oof_df["actual_score"]) * 100.0
    
    v2_oof_path = exp_dir / "v2_oof_predictions.csv"
    v2_oof_df.to_csv(v2_oof_path, index=False)
    print(f"Saved V2 out-of-fold predictions to: {v2_oof_path}")
    
    # 3. Save v2_evaluation.json
    serializable = {}
    for fs_name, algos in all_results.items():
        serializable[fs_name] = {}
        for algo, res in algos.items():
            serializable[fs_name][algo] = {k: v for k, v in res.items() if k != "oof_predictions"}
    
    v2_eval_path = exp_dir / "v2_evaluation.json"
    with open(v2_eval_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)
    print(f"Saved V2 evaluation metrics to: {v2_eval_path}")
    
    # 4. Compare V2 vs V1 Baseline
    v1_ridge_mae = all_results["Set_A_V1_Baseline"]["ridge"]["aggregated_oof_mae"]
    v2_best_fs = "Set_E_Comprehensive"
    v2_best_ridge = all_results[v2_best_fs]["ridge"]
    v2_best_mae = v2_best_ridge["aggregated_oof_mae"]
    v2_best_rmse = v2_best_ridge["aggregated_oof_rmse"]
    v2_best_r2 = v2_best_ridge["aggregated_oof_r2"]
    
    error_reduction = ((v1_ridge_mae - v2_best_mae) / v1_ridge_mae) * 100.0
    v2_improves = v2_best_mae < v1_ridge_mae and v2_best_rmse < all_results["Set_A_V1_Baseline"]["ridge"]["aggregated_oof_rmse"]
    
    print("\n" + "=" * 70)
    print(" V1 (6 features) vs V2 (Enriched) COMPARISON SUMMARY")
    print("=" * 70)
    print(f"V1 Ridge Baseline MAE: {v1_ridge_mae:.1f} pts | RMSE: {all_results['Set_A_V1_Baseline']['ridge']['aggregated_oof_rmse']:.1f} pts | R²: {all_results['Set_A_V1_Baseline']['ridge']['aggregated_oof_r2']:.4f}")
    print(f"V2 Set B (Arch) MAE:  {all_results['Set_B_Architecture']['ridge']['aggregated_oof_mae']:.1f} pts | RMSE: {all_results['Set_B_Architecture']['ridge']['aggregated_oof_rmse']:.1f} pts | R²: {all_results['Set_B_Architecture']['ridge']['aggregated_oof_r2']:.4f}")
    print(f"V2 Set D (Combined) MAE: {all_results['Set_D_Combined_Arch_L3']['ridge']['aggregated_oof_mae']:.1f} pts | RMSE: {all_results['Set_D_Combined_Arch_L3']['ridge']['aggregated_oof_rmse']:.1f} pts | R²: {all_results['Set_D_Combined_Arch_L3']['ridge']['aggregated_oof_r2']:.4f}")
    print(f"V2 Set E (Compr.) MAE:   {v2_best_mae:.1f} pts | RMSE: {v2_best_rmse:.1f} pts | R²: {v2_best_r2:.4f}")
    print(f"Error Reduction over V1: {error_reduction:.2f}%")
    print(f"V2 Improves on V1: {v2_improves}")
    print("=" * 70)
    
    # 5. Save V2 Experimental Model Artifact
    if v2_improves:
        models_dir = project_root / "models" / "experimental"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        fs_config = FEATURE_CONFIGURATIONS[v2_best_fs]
        best_num = fs_config["numeric"]
        best_cat = fs_config["categorical"]
        best_features = best_num + best_cat
        
        v2_pipeline = get_v2_model_pipeline("ridge", best_num, best_cat, random_state=42)
        v2_pipeline.fit(df[best_features], df["score"].values)
        
        v2_joblib_path = models_dir / "cpu_cinebench_r23_v2.joblib"
        joblib.dump(v2_pipeline, v2_joblib_path)
        print(f"\nSaved V2 experimental model artifact to: {v2_joblib_path}")
        
        v2_metadata = {
            "model_name": "CPU Cinebench R23 Multi-Core Predictor V2 (Enriched Ridge)",
            "model_version": "v2",
            "model_type": "Pipeline(StandardScaler + OneHotEncoder + Ridge(alpha=1.0))",
            "algorithm": "ridge",
            "status": "EXPERIMENTAL",
            "target_variable": "score",
            "target_unit": "Cinebench R23 Multi-Core points (pts)",
            "feature_set": v2_best_fs,
            "feature_set_description": fs_config["description"],
            "predictive_features": best_features,
            "numeric_features": best_num,
            "categorical_features": best_cat,
            "training_samples_count": len(df),
            "silicon_family_groups_count": int(df["group_id"].nunique()),
            "validation_strategy": "5-fold GroupKFold by verified silicon die family",
            "leakage_prevention": "Strict zero-overlap group splitting with preprocessing inside folds",
            "evaluation_metrics": {
                "dummy_baseline": {
                    "mae": round(all_results[v2_best_fs]["dummy"]["aggregated_oof_mae"], 1),
                    "rmse": round(all_results[v2_best_fs]["dummy"]["aggregated_oof_rmse"], 1),
                    "r2": round(all_results[v2_best_fs]["dummy"]["aggregated_oof_r2"], 4)
                },
                "v1_ridge_baseline": {
                    "mae": round(v1_ridge_mae, 1),
                    "rmse": round(all_results["Set_A_V1_Baseline"]["ridge"]["aggregated_oof_rmse"], 1),
                    "r2": round(all_results["Set_A_V1_Baseline"]["ridge"]["aggregated_oof_r2"], 4)
                },
                "v2_enriched_model": {
                    "mean_fold_mae": round(v2_best_ridge["mean_fold_mae"], 1),
                    "std_fold_mae": round(v2_best_ridge["std_fold_mae"], 1),
                    "mean_fold_rmse": round(v2_best_ridge["mean_fold_rmse"], 1),
                    "std_fold_rmse": round(v2_best_ridge["std_fold_rmse"], 1),
                    "mean_fold_r2": round(v2_best_ridge["mean_fold_r2"], 4),
                    "std_fold_r2": round(v2_best_ridge["std_fold_r2"], 4),
                    "aggregated_oof_mae": round(v2_best_mae, 1),
                    "aggregated_oof_rmse": round(v2_best_rmse, 1),
                    "aggregated_oof_r2": round(v2_best_r2, 4),
                    "mae_reduction_vs_v1_pct": round(error_reduction, 2),
                    "mae_reduction_vs_dummy_pct": round(((all_results[v2_best_fs]["dummy"]["aggregated_oof_mae"] - v2_best_mae) / all_results[v2_best_fs]["dummy"]["aggregated_oof_mae"]) * 100, 2)
                }
            },
            "disclaimer": "EXPERIMENTAL ONLY: Trained on 55 desktop CPU observations across 30 silicon families. Do not deploy to production recommendation logic without broader sample coverage."
        }
        
        v2_meta_path = models_dir / "cpu_cinebench_r23_v2_metadata.json"
        with open(v2_meta_path, "w", encoding="utf-8") as f:
            json.dump(v2_metadata, f, indent=2)
        print(f"Saved V2 experimental model metadata to: {v2_meta_path}")
    
    return all_results


if __name__ == "__main__":
    run_phase3c_training()
