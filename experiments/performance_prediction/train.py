"""
BuildWise-AI — Phase 11B: Supervised Machine Learning Model Training and Evaluation

Trains, evaluates, compares, and saves CPU and GPU performance prediction models.
Follows strict data leakage prevention with GroupKFold cross-validation and
GroupShuffleSplit holdout validation based on platform generation (CPU) and
silicon die family (GPU).
"""
import hashlib
import json
import logging
from datetime import datetime, timezone
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.performance_prediction import config
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("model_training")

MODELS_DIR = config.CURRENT_DIR / "models"
REPORTS_DIR = config.CURRENT_DIR / "reports"


def get_file_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def build_preprocessing_pipeline(
    numeric_features: List[str],
    categorical_features: List[str],
) -> ColumnTransformer:
    """
    Constructs a ColumnTransformer that imputes and scales numerical features,
    and imputes and one-hot encodes categorical features.
    
    Guarantees:
    - Numerical missing values (e.g., base_clock_ghz) imputed using median.
    - Categorical values imputed using most_frequent, then one-hot encoded.
    - Unknown categorical values at test/inference time are ignored (all zeros).
    """
    num_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    cat_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numeric_features),
            ("cat", cat_pipeline, categorical_features),
        ],
        remainder="drop",
    )
    return preprocessor


def get_candidate_models(device_type: str = "cpu") -> Dict[str, BaseEstimator]:
    """
    Returns candidate regression models to evaluate.
    Includes baseline DummyRegressor, linear models, and tree ensemble models.
    """
    models = {
        "Dummy Baseline (Mean)": DummyRegressor(strategy="mean"),
        "Linear Regression": LinearRegression(),
        "Ridge Regression (alpha=1.0)": Ridge(alpha=1.0, random_state=42),
        "Random Forest": RandomForestRegressor(
            n_estimators=100, max_depth=10, min_samples_split=4, random_state=42
        ),
        "Extra Trees": ExtraTreesRegressor(
            n_estimators=100, max_depth=10, min_samples_split=4, random_state=42
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=42
        ),
        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=100, max_depth=4, min_samples_leaf=3, random_state=42
        ),
    }
    if device_type == "cpu":
        # Add Ridge with alpha=10.0 for CPU which offers optimal regularization
        models["Ridge Regression (alpha=10.0)"] = Ridge(alpha=10.0, random_state=42)
    elif device_type == "gpu":
        # Add Ridge with alpha=0.1 for GPU
        models["Ridge Regression (alpha=0.1)"] = Ridge(alpha=0.1, random_state=42)
    return models


def evaluate_cv(
    model: BaseEstimator,
    numeric_features: List[str],
    categorical_features: List[str],
    df: pd.DataFrame,
    target_col: str,
    group_col: str,
    n_splits: int = 5,
) -> Dict[str, Any]:
    """
    Performs GroupKFold cross-validation on the complete dataset.
    Ensures preprocessor is fit solely on the training fold to prevent leakage.
    """
    all_features = numeric_features + categorical_features
    X = df[all_features]
    y = df[target_col]
    groups = df[group_col]

    gkf = GroupKFold(n_splits=n_splits)
    mae_list, rmse_list, r2_list = [], [], []
    fold_details = []

    for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=groups), 1):
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]

        # Verify zero group overlap
        train_grps = set(groups.iloc[train_idx])
        val_grps = set(groups.iloc[val_idx])
        assert not train_grps.intersection(val_grps), "Group leakage detected in CV split!"

        preprocessor = build_preprocessing_pipeline(numeric_features, categorical_features)
        pipeline = Pipeline([("preprocessor", preprocessor), ("regressor", model)])

        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_val)

        mae = float(mean_absolute_error(y_val, preds))
        rmse = float(root_mean_squared_error(y_val, preds))
        r2 = float(r2_score(y_val, preds))

        mae_list.append(mae)
        rmse_list.append(rmse)
        r2_list.append(r2)
        fold_details.append(
            {
                "fold": fold_idx,
                "train_samples": len(train_idx),
                "val_samples": len(val_idx),
                "val_groups": sorted(list(val_grps)),
                "mae": mae,
                "rmse": rmse,
                "r2": r2,
            }
        )

    return {
        "mae_mean": float(np.mean(mae_list)),
        "mae_std": float(np.std(mae_list)),
        "rmse_mean": float(np.mean(rmse_list)),
        "rmse_std": float(np.std(rmse_list)),
        "r2_mean": float(np.mean(r2_list)),
        "r2_std": float(np.std(r2_list)),
        "fold_details": fold_details,
    }


def evaluate_holdout(
    model: BaseEstimator,
    numeric_features: List[str],
    categorical_features: List[str],
    df: pd.DataFrame,
    target_col: str,
    group_col: str,
    test_size: float = 0.20,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Evaluates model on an unseen group-isolated holdout test set using GroupShuffleSplit.
    """
    all_features = numeric_features + categorical_features
    X = df[all_features]
    y = df[target_col]
    groups = df[group_col]

    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))

    X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
    X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

    train_grps = set(groups.iloc[train_idx])
    test_grps = set(groups.iloc[test_idx])
    assert not train_grps.intersection(test_grps), "Group leakage detected in holdout split!"

    preprocessor = build_preprocessing_pipeline(numeric_features, categorical_features)
    pipeline = Pipeline([("preprocessor", preprocessor), ("regressor", model)])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(root_mean_squared_error(y_test, preds))
    r2 = float(r2_score(y_test, preds))

    predictions_table = df.iloc[test_idx].copy()
    predictions_table["actual"] = y_test.values
    predictions_table["predicted"] = preds
    predictions_table["residual"] = y_test.values - preds
    predictions_table["absolute_error"] = np.abs(y_test.values - preds)
    predictions_table["percent_error"] = (
        np.abs(y_test.values - preds) / y_test.values
    ) * 100.0

    return {
        "train_samples": len(train_idx),
        "test_samples": len(test_idx),
        "train_groups": sorted(list(train_grps)),
        "test_groups": sorted(list(test_grps)),
        "test_target_mean": float(y_test.mean()),
        "test_target_std": float(y_test.std()),
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "predictions_table": predictions_table,
    }


def train_and_evaluate_suite(
    device_type: str,
    dataset_path: Path,
    numeric_features: List[str],
    categorical_features: List[str],
    target_col: str,
    group_col: str,
    n_cv_splits: int,
) -> Tuple[pd.DataFrame, Dict[str, Any], str, BaseEstimator]:
    """
    Trains all candidate models, calculates CV and holdout metrics,
    identifies the best model, and returns comprehensive evaluation data.
    """
    df = pd.read_csv(dataset_path)
    logger.info("Loaded %s dataset from %s: %d rows", device_type.upper(), dataset_path.name, len(df))

    candidates = get_candidate_models(device_type)
    results = []
    full_eval_data = {}

    for name, model in candidates.items():
        logger.info("Evaluating %s on %s...", name, device_type.upper())
        cv_res = evaluate_cv(
            model=model,
            numeric_features=numeric_features,
            categorical_features=categorical_features,
            df=df,
            target_col=target_col,
            group_col=group_col,
            n_splits=n_cv_splits,
        )
        holdout_res = evaluate_holdout(
            model=model,
            numeric_features=numeric_features,
            categorical_features=categorical_features,
            df=df,
            target_col=target_col,
            group_col=group_col,
        )

        results.append(
            {
                "Algorithm": name,
                "CV_MAE_Mean": cv_res["mae_mean"],
                "CV_MAE_Std": cv_res["mae_std"],
                "CV_RMSE_Mean": cv_res["rmse_mean"],
                "CV_RMSE_Std": cv_res["rmse_std"],
                "CV_R2_Mean": cv_res["r2_mean"],
                "CV_R2_Std": cv_res["r2_std"],
                "Holdout_MAE": holdout_res["mae"],
                "Holdout_RMSE": holdout_res["rmse"],
                "Holdout_R2": holdout_res["r2"],
            }
        )
        full_eval_data[name] = {"cv": cv_res, "holdout": holdout_res}

    comparison_df = pd.DataFrame(results)

    # Select best model:
    # We prioritize CV R2 and CV MAE since GroupKFold tests across ALL hardware groups,
    # avoiding idiosyncratic variance in a single holdout partition.
    # Exclude dummy baseline
    eligible = comparison_df[~comparison_df["Algorithm"].str.contains("Dummy Baseline")].copy()
    # Sort primarily by CV R2 descending, then CV MAE ascending
    eligible = eligible.sort_values(by=["CV_R2_Mean", "CV_MAE_Mean"], ascending=[False, True])
    best_algorithm_name = eligible.iloc[0]["Algorithm"]
    best_model = candidates[best_algorithm_name]

    logger.info("Best %s model selected: %s (CV R²=%.4f, CV MAE=%.1f)",
                device_type.upper(), best_algorithm_name,
                eligible.iloc[0]["CV_R2_Mean"], eligible.iloc[0]["CV_MAE_Mean"])

    return comparison_df, full_eval_data, best_algorithm_name, best_model


def save_trained_pipeline(
    device_type: str,
    dataset_path: Path,
    numeric_features: List[str],
    categorical_features: List[str],
    target_col: str,
    group_col: str,
    best_algorithm_name: str,
    best_model: BaseEstimator,
    eval_data: Dict[str, Any],
) -> Tuple[Path, Path]:
    """
    Fits the winning preprocessing + regressor pipeline on the full dataset,
    saves the joblib artifact, and generates a metadata JSON file.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(dataset_path)
    all_features = numeric_features + categorical_features
    X = df[all_features]
    y = df[target_col]

    preprocessor = build_preprocessing_pipeline(numeric_features, categorical_features)
    final_pipeline = Pipeline([("preprocessor", preprocessor), ("regressor", best_model)])
    final_pipeline.fit(X, y)

    model_filename = f"best_{device_type.lower()}_pipeline.joblib"
    model_path = MODELS_DIR / model_filename
    joblib.dump(final_pipeline, model_path)
    model_sha256 = get_file_sha256(model_path)
    dataset_sha256 = get_file_sha256(dataset_path)

    best_cv = eval_data[best_algorithm_name]["cv"]
    best_holdout = eval_data[best_algorithm_name]["holdout"]

    metadata = {
        "model_id": f"buildwise_{device_type.lower()}_perf_regressor_v1",
        "device_type": device_type.upper(),
        "task": f"{device_type.upper()} Empirical Benchmark Regression",
        "target_variable": target_col,
        "selected_algorithm": best_algorithm_name,
        "hyperparameters": {
            k: (str(v) if not isinstance(v, (int, float, bool, list, dict, type(None))) else v)
            for k, v in best_model.get_params().items()
        },
        "features": {
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "total_features": len(all_features),
            "feature_list": all_features,
        },
        "dataset": {
            "source_file": dataset_path.name,
            "sample_count": len(df),
            "group_column": group_col,
            "group_count": int(df[group_col].nunique()),
            "groups": sorted(df[group_col].unique().tolist()),
            "sha256": dataset_sha256,
        },
        "validation_strategy": {
            "cross_validation": "GroupKFold",
            "cv_splits": len(best_cv["fold_details"]),
            "holdout_method": "GroupShuffleSplit",
            "holdout_test_size": 0.20,
            "holdout_random_state": 42,
        },
        "metrics": {
            "cv": {
                "mae_mean": best_cv["mae_mean"],
                "mae_std": best_cv["mae_std"],
                "rmse_mean": best_cv["rmse_mean"],
                "rmse_std": best_cv["rmse_std"],
                "r2_mean": best_cv["r2_mean"],
                "r2_std": best_cv["r2_std"],
            },
            "holdout": {
                "train_samples": best_holdout["train_samples"],
                "test_samples": best_holdout["test_samples"],
                "test_groups": best_holdout["test_groups"],
                "mae": best_holdout["mae"],
                "rmse": best_holdout["rmse"],
                "r2": best_holdout["r2"],
            },
        },
        "artifacts": {
            "pipeline_file": model_filename,
            "pipeline_sha256": model_sha256,
            "file_size_bytes": model_path.stat().st_size,
        },
        "environment": {
            "scikit_learn_version": sklearn.__version__,
            "joblib_version": joblib.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    }

    metadata_filename = f"{device_type.lower()}_model_metadata.json"
    metadata_path = MODELS_DIR / metadata_filename
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Saved %s pipeline to %s (SHA-256: %s)", device_type.upper(), model_path, model_sha256[:12])
    logger.info("Saved %s metadata to %s", device_type.upper(), metadata_path)

    return model_path, metadata_path


def execute_full_training() -> Dict[str, Any]:
    """Orchestrates the entire training, evaluation, model saving, and reporting pipeline."""
    logger.info("Starting Phase 11B Model Training & Evaluation Suite...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. CPU Training & Evaluation
    cpu_comp_df, cpu_eval_data, best_cpu_name, best_cpu_model = train_and_evaluate_suite(
        device_type="cpu",
        dataset_path=config.CPU_TRAINING_CSV,
        numeric_features=config.CPU_NUMERIC_FEATURES,
        categorical_features=config.CPU_CATEGORICAL_FEATURES,
        target_col=config.CPU_TARGET,
        group_col="group_id",
        n_cv_splits=5,
    )
    cpu_model_path, cpu_meta_path = save_trained_pipeline(
        device_type="cpu",
        dataset_path=config.CPU_TRAINING_CSV,
        numeric_features=config.CPU_NUMERIC_FEATURES,
        categorical_features=config.CPU_CATEGORICAL_FEATURES,
        target_col=config.CPU_TARGET,
        group_col="group_id",
        best_algorithm_name=best_cpu_name,
        best_model=best_cpu_model,
        eval_data=cpu_eval_data,
    )

    # 2. GPU Training & Evaluation
    gpu_comp_df, gpu_eval_data, best_gpu_name, best_gpu_model = train_and_evaluate_suite(
        device_type="gpu",
        dataset_path=config.GPU_TRAINING_CSV,
        numeric_features=config.GPU_NUMERIC_FEATURES,
        categorical_features=config.GPU_CATEGORICAL_FEATURES,
        target_col=config.GPU_TARGET,
        group_col="group_id",
        n_cv_splits=4,
    )
    gpu_model_path, gpu_meta_path = save_trained_pipeline(
        device_type="gpu",
        dataset_path=config.GPU_TRAINING_CSV,
        numeric_features=config.GPU_NUMERIC_FEATURES,
        categorical_features=config.GPU_CATEGORICAL_FEATURES,
        target_col=config.GPU_TARGET,
        group_col="group_id",
        best_algorithm_name=best_gpu_name,
        best_model=best_gpu_model,
        eval_data=gpu_eval_data,
    )

    # 3. Export CSV Comparison Reports
    cpu_comp_df.to_csv(REPORTS_DIR / "cpu_model_comparison.csv", index=False)
    gpu_comp_df.to_csv(REPORTS_DIR / "gpu_model_comparison.csv", index=False)

    # 4. Export Holdout Predictions for Best Models
    cpu_holdout_preds = cpu_eval_data[best_cpu_name]["holdout"]["predictions_table"]
    gpu_holdout_preds = gpu_eval_data[best_gpu_name]["holdout"]["predictions_table"]
    cpu_holdout_preds.to_csv(REPORTS_DIR / "cpu_holdout_predictions.csv", index=False)
    gpu_holdout_preds.to_csv(REPORTS_DIR / "gpu_holdout_predictions.csv", index=False)

    logger.info("Phase 11B Model Training completed successfully.")

    return {
        "cpu": {
            "comparison": cpu_comp_df,
            "best_name": best_cpu_name,
            "model_path": cpu_model_path,
            "metadata_path": cpu_meta_path,
            "eval_data": cpu_eval_data,
        },
        "gpu": {
            "comparison": gpu_comp_df,
            "best_name": best_gpu_name,
            "model_path": gpu_model_path,
            "metadata_path": gpu_meta_path,
            "eval_data": gpu_eval_data,
        },
    }


if __name__ == "__main__":
    execute_full_training()
