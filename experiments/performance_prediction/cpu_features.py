"""
BuildWise-AI — Phase 10: CPU Feature Extraction and Normalization

Extracts, validates, and standardizes CPU hardware features from catalog specifications.
"""
import json
from typing import Any, Dict, Mapping, Optional


def parse_cpu_specs(specs_raw: Any) -> Dict[str, Any]:
    """Safely decodes specs_json if string, or returns dict."""
    if isinstance(specs_raw, dict):
        return specs_raw
    if not specs_raw:
        return {}
    try:
        return json.loads(str(specs_raw))
    except (json.JSONDecodeError, TypeError):
        return {}


def extract_cpu_record_features(
    component_row: Mapping[str, Any],
    specs: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Extracts standardized CPU predictive features and metadata from a component record.
    
    Args:
        component_row: Row or dict from data/components.csv (brand, model, specs_json, component_id).
        specs: Pre-parsed specs dict (optional).
        
    Returns:
        Dict of standardized numerical and categorical features plus group_id.
    """
    if specs is None:
        specs = parse_cpu_specs(component_row.get("specs_json", {}))

    # 1. Numerical feature extraction with validation
    cores_raw = specs.get("cores")
    try:
        cores = int(cores_raw)
        if cores <= 0:
            raise ValueError(f"cores must be positive, got {cores}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid CPU cores value '{cores_raw}': {exc}") from exc

    threads_raw = specs.get("threads")
    try:
        threads = int(threads_raw)
        if threads <= 0 or threads < cores:
            raise ValueError(f"threads ({threads}) must be >= cores ({cores})")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid CPU threads value '{threads_raw}': {exc}") from exc

    boost_raw = specs.get("boost_ghz") or specs.get("boost_clock_ghz")
    try:
        boost_clock_ghz = float(boost_raw)
        if boost_clock_ghz <= 0:
            raise ValueError(f"boost_clock_ghz must be positive, got {boost_clock_ghz}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid CPU boost clock value '{boost_raw}': {exc}") from exc

    base_raw = specs.get("base_clock_ghz")
    base_clock_ghz: Optional[float] = None
    if base_raw is not None and str(base_raw).strip() != "":
        try:
            base_clock_ghz = float(base_raw)
            if base_clock_ghz <= 0:
                base_clock_ghz = None
        except (TypeError, ValueError):
            base_clock_ghz = None

    tdp_raw = specs.get("tdp_w") or specs.get("tdp") or specs.get("base_power_w")
    try:
        tdp_w = float(tdp_raw)
        if tdp_w <= 0:
            raise ValueError(f"tdp_w must be positive, got {tdp_w}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid CPU tdp_w value '{tdp_raw}': {exc}") from exc

    # 2. Categorical feature extraction and normalization
    brand = str(component_row.get("brand", "")).strip()
    if not brand:
        raise ValueError("Missing CPU brand")

    socket = str(specs.get("socket", "")).strip()
    if not socket:
        raise ValueError("Missing CPU socket specification")

    ram_type = str(specs.get("ram_type", "DDR4")).strip()
    if not ram_type:
        ram_type = "DDR4"

    # 3. Silicon platform group ID generation for GroupKFold
    group_id = f"{brand.lower()}_{socket.lower().replace('-', '')}"

    return {
        "cores": cores,
        "threads": threads,
        "boost_clock_ghz": boost_clock_ghz,
        "base_clock_ghz": base_clock_ghz,
        "tdp_w": tdp_w,
        "brand": brand,
        "socket": socket,
        "ram_type": ram_type,
        "group_id": group_id,
    }
