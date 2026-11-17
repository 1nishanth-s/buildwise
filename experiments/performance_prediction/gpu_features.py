"""
BuildWise-AI — Phase 10: GPU Feature Extraction and Normalization

Extracts, validates, and standardizes GPU hardware features from catalog specifications,
hardware enrichment data, and silicon die family groupings.
"""
import json
from typing import Any, Dict, Mapping, Optional


def parse_gpu_specs(specs_raw: Any) -> Dict[str, Any]:
    """Safely decodes specs_json if string, or returns dict."""
    if isinstance(specs_raw, dict):
        return specs_raw
    if not specs_raw:
        return {}
    try:
        return json.loads(str(specs_raw))
    except (json.JSONDecodeError, TypeError):
        return {}


def extract_gpu_record_features(
    component_row: Mapping[str, Any],
    enrichment_map: Optional[Mapping[str, Any]] = None,
    family_group_row: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Extracts standardized GPU predictive features and metadata from a component record.
    
    Args:
        component_row: Row or dict from data/components.csv.
        enrichment_map: Dict of feature_name -> value from gpu_feature_enrichment_v1.csv.
        family_group_row: Dict from data/ml/gpu_family_groups_v1.csv.
        
    Returns:
        Dict of standardized numerical and categorical features plus group_id.
    """
    specs = parse_gpu_specs(component_row.get("specs_json", {}))
    enrich = enrichment_map if enrichment_map is not None else {}
    fam = family_group_row if family_group_row is not None else {}

    # 1. VRAM Capacity (GB)
    vram_raw = specs.get("vram_gb") or enrich.get("vram_gb")
    try:
        vram_gb = int(vram_raw)
        if vram_gb <= 0:
            raise ValueError(f"vram_gb must be positive, got {vram_gb}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid GPU vram_gb value '{vram_raw}': {exc}") from exc

    # 2. Memory Bus Width (bits)
    bus_raw = enrich.get("memory_bus_width_bits") or specs.get("memory_bus_bits")
    try:
        memory_bus_width_bits = int(bus_raw)
        if memory_bus_width_bits <= 0:
            raise ValueError(f"memory_bus_width_bits must be positive, got {memory_bus_width_bits}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid GPU memory bus width value '{bus_raw}': {exc}") from exc

    # 3. Memory Bandwidth (GB/s)
    bw_raw = enrich.get("memory_bandwidth_gbps") or specs.get("memory_bandwidth_gbps")
    try:
        memory_bandwidth_gbps = float(bw_raw)
        if memory_bandwidth_gbps <= 0:
            raise ValueError(f"memory_bandwidth_gbps must be positive, got {memory_bandwidth_gbps}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid GPU memory bandwidth value '{bw_raw}': {exc}") from exc

    # 4. Base Clock (MHz)
    base_raw = enrich.get("base_clock_mhz") or specs.get("core_clock_mhz")
    try:
        base_clock_mhz = float(base_raw)
        if base_clock_mhz <= 0:
            raise ValueError(f"base_clock_mhz must be positive, got {base_clock_mhz}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid GPU base clock value '{base_raw}': {exc}") from exc

    # 5. Boost Clock (MHz)
    boost_raw = enrich.get("boost_clock_mhz") or specs.get("boost_clock_mhz")
    try:
        boost_clock_mhz = float(boost_raw)
        if boost_clock_mhz <= 0:
            raise ValueError(f"boost_clock_mhz must be positive, got {boost_raw}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid GPU boost clock value '{boost_raw}': {exc}") from exc

    # 6. Board Power (Watts)
    power_raw = enrich.get("board_power_w") or specs.get("tgp_w")
    try:
        board_power_w = float(power_raw)
        if board_power_w <= 0:
            raise ValueError(f"board_power_w must be positive, got {power_raw}")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid GPU board power value '{power_raw}': {exc}") from exc

    # 7. Categorical features
    architecture = str(enrich.get("architecture") or fam.get("architecture", "")).strip()
    if not architecture:
        raise ValueError("Missing GPU architecture")

    chipmaker = str(enrich.get("chipmaker") or fam.get("brand", component_row.get("brand", ""))).strip()
    if not chipmaker:
        raise ValueError("Missing GPU chipmaker/brand")

    memory_type = str(enrich.get("memory_type", "GDDR6")).strip()
    if not memory_type:
        memory_type = "GDDR6"

    # 8. Silicon Die and SKU Groupings for GroupKFold
    base_die_group_id = str(fam.get("base_die_group_id", "")).strip() or f"{chipmaker.lower()}_{architecture.lower().replace(' ', '_')}"
    sku_group_id = str(fam.get("sku_group_id", "")).strip() or base_die_group_id
    group_id = base_die_group_id

    return {
        "vram_gb": vram_gb,
        "memory_bus_width_bits": memory_bus_width_bits,
        "memory_bandwidth_gbps": memory_bandwidth_gbps,
        "base_clock_mhz": base_clock_mhz,
        "boost_clock_mhz": boost_clock_mhz,
        "board_power_w": board_power_w,
        "architecture": architecture,
        "chipmaker": chipmaker,
        "memory_type": memory_type,
        "base_die_group_id": base_die_group_id,
        "sku_group_id": sku_group_id,
        "group_id": group_id,
    }
