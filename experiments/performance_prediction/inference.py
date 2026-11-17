"""
BuildWise-AI — Phase 11B: Inference Verification and Model Loading API

Provides helper functions to load persisted pipeline artifacts and run
predictions on new CPU and GPU hardware specification vectors.
"""
import json
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Any, Dict, List, Union

import joblib
import numpy as np
import pandas as pd

from experiments.performance_prediction import config

MODELS_DIR = config.CURRENT_DIR / "models"
CPU_MODEL_PATH = MODELS_DIR / "best_cpu_pipeline.joblib"
GPU_MODEL_PATH = MODELS_DIR / "best_gpu_pipeline.joblib"
CPU_METADATA_PATH = MODELS_DIR / "cpu_model_metadata.json"
GPU_METADATA_PATH = MODELS_DIR / "gpu_model_metadata.json"


class ModelNotFoundError(FileNotFoundError):
    """Raised when a trained model artifact cannot be found."""
    pass


def load_cpu_model():
    """Loads the serialized CPU performance prediction pipeline."""
    if not CPU_MODEL_PATH.exists():
        raise ModelNotFoundError(f"CPU model artifact not found at {CPU_MODEL_PATH}")
    return joblib.load(CPU_MODEL_PATH)


def load_gpu_model():
    """Loads the serialized GPU performance prediction pipeline."""
    if not GPU_MODEL_PATH.exists():
        raise ModelNotFoundError(f"GPU model artifact not found at {GPU_MODEL_PATH}")
    return joblib.load(GPU_MODEL_PATH)


def load_cpu_metadata() -> Dict[str, Any]:
    """Loads metadata for the trained CPU model."""
    if not CPU_METADATA_PATH.exists():
        raise ModelNotFoundError(f"CPU metadata not found at {CPU_METADATA_PATH}")
    with open(CPU_METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_gpu_metadata() -> Dict[str, Any]:
    """Loads metadata for the trained GPU model."""
    if not GPU_METADATA_PATH.exists():
        raise ModelNotFoundError(f"GPU metadata not found at {GPU_METADATA_PATH}")
    with open(GPU_METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def predict_cpu_performance(
    data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    pipeline=None,
) -> np.ndarray:
    """
    Predicts Cinebench R23 Multi-Core scores for one or more CPU specifications.

    Parameters
    ----------
    data : dict, list of dicts, or pd.DataFrame
        Hardware specifications containing CPU_PREDICTIVE_FEATURES:
        ['cores', 'threads', 'boost_clock_ghz', 'base_clock_ghz', 'tdp_w', 'brand', 'socket', 'ram_type']
    pipeline : sklearn.pipeline.Pipeline, optional
        Pre-loaded pipeline; if None, loads from disk.

    Returns
    -------
    np.ndarray
        Predicted Cinebench R23 Multi-Core scores (finite positive floats).
    """
    if pipeline is None:
        pipeline = load_cpu_model()

    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError(f"Unsupported data type for inference: {type(data)}")

    # Ensure all required features are present; missing columns filled with NaN for imputer
    for col in config.CPU_PREDICTIVE_FEATURES:
        if col not in df.columns:
            df[col] = np.nan

    X = df[config.CPU_PREDICTIVE_FEATURES]
    preds = pipeline.predict(X)

    # Sanity checks
    if not np.all(np.isfinite(preds)):
        raise ValueError("Model produced non-finite prediction values.")

    return np.round(preds, 1)


def predict_gpu_performance(
    data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    pipeline=None,
) -> np.ndarray:
    """
    Predicts 3DMark Time Spy Graphics scores for one or more GPU specifications.

    Parameters
    ----------
    data : dict, list of dicts, or pd.DataFrame
        Hardware specifications containing GPU_PREDICTIVE_FEATURES:
        ['vram_gb', 'memory_bus_width_bits', 'memory_bandwidth_gbps', 'base_clock_mhz',
         'boost_clock_mhz', 'board_power_w', 'architecture', 'chipmaker', 'memory_type']
    pipeline : sklearn.pipeline.Pipeline, optional
        Pre-loaded pipeline; if None, loads from disk.

    Returns
    -------
    np.ndarray
        Predicted 3DMark Time Spy Graphics scores (finite positive floats).
    """
    if pipeline is None:
        pipeline = load_gpu_model()

    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError(f"Unsupported data type for inference: {type(data)}")

    for col in config.GPU_PREDICTIVE_FEATURES:
        if col not in df.columns:
            df[col] = np.nan

    X = df[config.GPU_PREDICTIVE_FEATURES]
    preds = pipeline.predict(X)

    # Sanity checks
    if not np.all(np.isfinite(preds)):
        raise ValueError("Model produced non-finite prediction values.")

    return np.round(preds, 1)


def run_inference_smoke_test() -> Dict[str, Any]:
    """Runs a smoke test verifying loading and inference on representative hardware."""
    cpu_model = load_cpu_model()
    gpu_model = load_gpu_model()

    # Test sample CPUs
    cpu_samples = [
        {
            "name": "AMD Ryzen 7 7800X3D",
            "cores": 8,
            "threads": 16,
            "boost_clock_ghz": 5.0,
            "base_clock_ghz": 4.2,
            "tdp_w": 120,
            "brand": "AMD",
            "socket": "AM5",
            "ram_type": "DDR5",
        },
        {
            "name": "Intel Core i5-13600K",
            "cores": 14,
            "threads": 20,
            "boost_clock_ghz": 5.1,
            "base_clock_ghz": 3.5,
            "tdp_w": 125,
            "brand": "Intel",
            "socket": "LGA1700",
            "ram_type": "DDR5",
        },
        {
            "name": "Budget CPU with missing base clock",
            "cores": 6,
            "threads": 12,
            "boost_clock_ghz": 4.4,
            "base_clock_ghz": np.nan,  # tests median imputation
            "tdp_w": 65,
            "brand": "AMD",
            "socket": "AM4",
            "ram_type": "DDR4",
        },
    ]

    cpu_preds = predict_cpu_performance(cpu_samples, pipeline=cpu_model)

    # Test sample GPUs
    gpu_samples = [
        {
            "name": "NVIDIA GeForce RTX 4070",
            "vram_gb": 12.0,
            "memory_bus_width_bits": 192,
            "memory_bandwidth_gbps": 504.0,
            "base_clock_mhz": 1920,
            "boost_clock_mhz": 2475,
            "board_power_w": 200,
            "architecture": "Ada Lovelace",
            "chipmaker": "NVIDIA",
            "memory_type": "GDDR6X",
        },
        {
            "name": "AMD Radeon RX 7800 XT",
            "vram_gb": 16.0,
            "memory_bus_width_bits": 256,
            "memory_bandwidth_gbps": 624.0,
            "base_clock_mhz": 1295,
            "boost_clock_mhz": 2430,
            "board_power_w": 263,
            "architecture": "RDNA 3",
            "chipmaker": "AMD",
            "memory_type": "GDDR6",
        },
    ]

    gpu_preds = predict_gpu_performance(gpu_samples, pipeline=gpu_model)

    return {
        "cpu_samples": [
            {"spec": s["name"], "predicted_cinebench_r23": float(p)}
            for s, p in zip(cpu_samples, cpu_preds)
        ],
        "gpu_samples": [
            {"spec": s["name"], "predicted_timespy_graphics": float(p)}
            for s, p in zip(gpu_samples, gpu_preds)
        ],
    }


if __name__ == "__main__":
    results = run_inference_smoke_test()
    print("CPU Smoke Test Results:")
    for item in results["cpu_samples"]:
        print(f"  {item['spec']}: {item['predicted_cinebench_r23']:,.1f}")
    print("\nGPU Smoke Test Results:")
    for item in results["gpu_samples"]:
        print(f"  {item['spec']}: {item['predicted_timespy_graphics']:,.1f}")
