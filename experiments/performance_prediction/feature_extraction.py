"""
BuildWise-AI — Phase 10: Unified Feature Extraction Facade

Provides clean, leak-free feature extraction for CPU and GPU records.
Enforces strict exclusion of benchmark targets, pricing data, and arbitrary identifiers
from the predictive feature matrix.
"""
from typing import Any, Dict, List, Mapping, Optional

from experiments.performance_prediction.config import (
    CPU_PREDICTIVE_FEATURES,
    CPU_TARGET,
    GPU_PREDICTIVE_FEATURES,
    GPU_TARGET,
)
from experiments.performance_prediction.cpu_features import extract_cpu_record_features
from experiments.performance_prediction.gpu_features import extract_gpu_record_features


def extract_cpu_features(component_row: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Extracts validated CPU predictive features.
    
    Guarantees:
    - Never includes benchmark targets.
    - Never includes prices or URLs.
    - Output keys strictly adhere to CPU_PREDICTIVE_FEATURES plus group_id.
    """
    extracted = extract_cpu_record_features(component_row)
    # Target leakage assertion
    assert CPU_TARGET not in extracted, f"Data leakage error: target '{CPU_TARGET}' detected in extracted features"
    return extracted


def extract_gpu_features(
    component_row: Mapping[str, Any],
    enrichment_map: Optional[Mapping[str, Any]] = None,
    family_group_row: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Extracts validated GPU predictive features.
    
    Guarantees:
    - Never includes benchmark targets.
    - Never includes prices or URLs.
    - Output keys strictly adhere to GPU_PREDICTIVE_FEATURES plus group metadata.
    """
    extracted = extract_gpu_record_features(
        component_row=component_row,
        enrichment_map=enrichment_map,
        family_group_row=family_group_row,
    )
    # Target leakage assertion
    assert GPU_TARGET not in extracted, f"Data leakage error: target '{GPU_TARGET}' detected in extracted features"
    return extracted


def get_feature_names(category: str) -> List[str]:
    """Returns the sanctioned predictive feature allowlist for the category."""
    cat = str(category).strip().casefold()
    if cat == "cpu":
        return list(CPU_PREDICTIVE_FEATURES)
    elif cat == "gpu":
        return list(GPU_PREDICTIVE_FEATURES)
    else:
        raise ValueError(f"Unknown hardware category '{category}'")
