"""
BuildWise-AI — Phase 3B: CPU Benchmark Regression Evaluation & Error Audit

Performs in-depth audit of out-of-fold cross-validation predictions, identifying:
- Top outlier predictions (largest absolute & percentage errors).
- Model performance across silicon microarchitectures.
- Handling of identical feature vectors (Intel K/KF twins and AMD APU vs desktop variants).
- Model comparison summary against baseline DummyRegressor.
"""

import json
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd


def get_project_root() -> Path:
    """Resolve repository root directory."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "data" / "components.csv").is_file() and (parent / "data" / "benchmarks.csv").is_file():
            return parent
    raise FileNotFoundError("Could not locate project root")


def run_evaluation_audit(project_root: Path = None) -> Dict[str, Any]:
    """Execute evaluation and prediction error audit."""
    if project_root is None:
        project_root = get_project_root()
    
    exp_dir = project_root / "experiments" / "cpu_benchmark_regression"
    oof_path = exp_dir / "oof_predictions.csv"
    eval_json_path = exp_dir / "evaluation.json"
    
    if not oof_path.is_file() or not eval_json_path.is_file():
        raise FileNotFoundError("OOF predictions or evaluation.json not found. Run train.py first.")
    
    oof_df = pd.read_csv(oof_path)
    with open(eval_json_path, "r", encoding="utf-8") as f:
        eval_metrics = json.load(f)
    
    print("=" * 80)
    print(" BUILDWISE-AI — CPU BENCHMARK REGRESSION EXPERIMENT: EVALUATION & ERROR AUDIT")
    print("=" * 80)
    
    # 1. Comparative Performance Table
    print("\n--- MODEL PERFORMANCE COMPARISON (5-Fold GroupKFold by Silicon Family) ---")
    print(f"{'Model':<24} | {'Agg OOF MAE':<12} | {'Agg OOF RMSE':<12} | {'Agg OOF R²':<10} | {'Mean Fold MAE ± Std':<22}")
    print("-" * 88)
    for algo, res in eval_metrics.items():
        mean_std = f"{res['mean_fold_mae']:.1f} ± {res['std_fold_mae']:.1f} pts"
        print(f"{algo.upper():<24} | {res['aggregated_oof_mae']:>9.1f} pts | {res['aggregated_oof_rmse']:>9.1f} pts | {res['aggregated_oof_r2']:>10.3f} | {mean_std:<22}")
    
    # 2. Out-of-Fold Prediction Errors for Ridge (Best Model)
    best_algo = "ridge"
    print(f"\n--- TOP 5 LARGEST ABSOLUTE ERRORS ({best_algo.upper()}) ---")
    top_abs = oof_df.sort_values(by=f"abs_err_{best_algo}", ascending=False).head(5)
    print(f"{'Model':<28} | {'Actual':<8} | {'Predicted':<10} | {'Abs Error':<10} | {'Pct Error':<10} | {'Fold':<4}")
    print("-" * 80)
    for _, r in top_abs.iterrows():
        print(f"{r['model']:<28} | {r['actual_score']:>8.0f} | {r[f'pred_{best_algo}']:>10.1f} | {r[f'abs_err_{best_algo}']:>10.1f} | {r[f'pct_err_{best_algo}']:>9.2f}% | {r['cv_fold']:>4}")
    
    print(f"\n--- TOP 5 LARGEST PERCENTAGE ERRORS ({best_algo.upper()}) ---")
    top_pct = oof_df.sort_values(by=f"pct_err_{best_algo}", ascending=False).head(5)
    print(f"{'Model':<28} | {'Actual':<8} | {'Predicted':<10} | {'Abs Error':<10} | {'Pct Error':<10} | {'Fold':<4}")
    print("-" * 80)
    for _, r in top_pct.iterrows():
        print(f"{r['model']:<28} | {r['actual_score']:>8.0f} | {r[f'pred_{best_algo}']:>10.1f} | {r[f'abs_err_{best_algo}']:>10.1f} | {r[f'pct_err_{best_algo}']:>9.2f}% | {r['cv_fold']:>4}")
    
    # 3. Silicon Family Error Breakdown
    print(f"\n--- MEAN ERROR BY SILICON DIE / ARCHITECTURE GROUP ({best_algo.upper()}) ---")
    grp_summary = oof_df.groupby("group_id").agg(
        sample_count=("actual_score", "count"),
        mean_actual=("actual_score", "mean"),
        mean_abs_err=(f"abs_err_{best_algo}", "mean"),
        mean_pct_err=(f"pct_err_{best_algo}", "mean")
    ).reset_index().sort_values(by="mean_abs_err", ascending=False)
    
    print(f"{'Group ID':<30} | {'Count':<5} | {'Mean Score':<10} | {'Mean Abs Err':<12} | {'Mean Pct Err':<12}")
    print("-" * 80)
    for _, gr in grp_summary.head(10).iterrows():
        print(f"{gr['group_id']:<30} | {int(gr['sample_count']):>5} | {gr['mean_actual']:>10.0f} | {gr['mean_abs_err']:>10.1f} pts | {gr['mean_pct_err']:>11.2f}%")
    
    # 4. Duplicate Feature Vector Analysis (Twin Pair Verification)
    print("\n--- TWIN PAIRS & IDENTICAL FEATURE VECTOR PREDICTION AUDIT ---")
    feature_cols = ["brand", "socket", "cores", "threads", "boost_clock_ghz", "tdp_w"]
    dup_mask = oof_df.duplicated(subset=feature_cols, keep=False)
    dup_df = oof_df[dup_mask].sort_values(by=feature_cols)
    print(f"Total processors sharing identical 6-feature vectors: {len(dup_df)} CPUs across {dup_df.groupby(feature_cols).ngroups} feature combinations.")
    
    for _, g in dup_df.groupby(feature_cols):
        models = g["model"].tolist()
        actuals = g["actual_score"].tolist()
        preds = g[f"pred_{best_algo}"].tolist()
        folds = g["cv_fold"].tolist()
        print(f"\nFeature Vector: {dict(zip(feature_cols, g.iloc[0][feature_cols]))}")
        for m, a, p, f in zip(models, actuals, preds, folds):
            print(f"  - {m:<28} | Actual: {a:>7.0f} | Pred: {p:>7.1f} | Fold: {f}")
    
    audit_summary = {
        "best_algorithm": best_algo,
        "dummy_baseline_mae": eval_metrics["dummy"]["aggregated_oof_mae"],
        "best_model_mae": eval_metrics[best_algo]["aggregated_oof_mae"],
        "best_model_rmse": eval_metrics[best_algo]["aggregated_oof_rmse"],
        "best_model_r2": eval_metrics[best_algo]["aggregated_oof_r2"],
        "top_outlier_model": top_abs.iloc[0]["model"],
        "top_outlier_abs_err": float(top_abs.iloc[0][f"abs_err_{best_algo}"]),
        "duplicate_vector_count": len(dup_df)
    }
    return audit_summary


if __name__ == "__main__":
    run_evaluation_audit()
