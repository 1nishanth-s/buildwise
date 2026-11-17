"""
BuildWise-AI — Pure Compatibility Evaluator for Backend Recommender

Evaluates pairwise and system-level hardware compatibility using strictly
verified rules from src.compatibility without any Streamlit dependencies.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.compatibility import (
    check_cooler_case,
    check_cooler_socket,
    check_cpu_motherboard,
    check_cpu_motherboard_ram,
    check_gpu_case,
    check_motherboard_case,
    check_motherboard_ram_capacity,
    check_psu,
    check_ram_speed_qvl,
    check_storage_motherboard,
)
from src.recommender.catalog_data import parse_specs


def evaluate_component_compatibility(
    candidate: Dict[str, Any], selected_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates a candidate component against currently selected components.
    Returns:
        {
            "status": "compatible" | "incompatible" | "unknown",
            "checks": [{"pair": str, "status": str, "reason": str}]
        }
    """
    candidate_cat = str(candidate.get("category", "")).strip().casefold()
    candidate_specs = parse_specs(candidate.get("specs_json", candidate.get("specs", {})))
    candidate_id = str(candidate.get("component_id", "")).strip()

    checks: List[Dict[str, str]] = []

    def get_sel(cat: str):
        item = selected_dict.get(cat)
        if not item or not isinstance(item, dict):
            return None, None, {}
        mode = item.get("_status", item.get("status", "catalog"))
        if mode in ("unknown", "none", "skipped"):
            return mode, None, {}
        cid = item.get("component_id")
        sp = parse_specs(item.get("specs_json", item.get("specs", {})))
        return mode, cid, sp

    cpu_mode, cpu_id, cpu_specs = get_sel("cpu")
    mb_mode, mb_id, mb_specs = get_sel("motherboard")
    ram_mode, ram_id, ram_specs = get_sel("ram")
    case_mode, case_id, case_specs = get_sel("case")
    gpu_mode, gpu_id, gpu_specs = get_sel("gpu")
    psu_mode, psu_id, psu_specs = get_sel("psu")
    cooler_mode, cooler_id, cooler_specs = get_sel("cooler")
    storage_mode, storage_id, storage_specs = get_sel("storage")

    if candidate_cat == "cpu":
        if mb_mode == "catalog":
            res = check_cpu_motherboard(candidate_specs, mb_specs, cpu_component_id=candidate_id)
            checks.append({"pair": "CPU + Motherboard Socket", "status": res.status, "reason": res.reason})
        elif mb_mode == "unknown":
            checks.append({"pair": "CPU + Motherboard Socket", "status": "unknown", "reason": "Motherboard specs unknown; cannot verify socket compatibility."})

        if mb_mode == "catalog" and ram_mode == "catalog":
            res = check_cpu_motherboard_ram(candidate_specs, mb_specs, ram_specs)
            checks.append({"pair": "CPU + Motherboard + RAM Memory Generation", "status": res.status, "reason": res.reason})

        if cooler_mode == "catalog":
            res = check_cooler_socket(cooler_specs, candidate_specs, mb_specs if mb_mode == "catalog" else None)
            checks.append({"pair": "CPU Cooler + CPU Socket", "status": res.status, "reason": res.reason})

        if psu_mode == "catalog":
            res = check_psu(psu_specs, candidate_specs, gpu_specs if gpu_mode == "catalog" else {})
            checks.append({"pair": "PSU Wattage vs CPU Power", "status": res.status, "reason": res.reason})

    elif candidate_cat == "motherboard":
        if cpu_mode == "catalog":
            res = check_cpu_motherboard(cpu_specs, candidate_specs, cpu_component_id=cpu_id)
            checks.append({"pair": "CPU + Motherboard Socket", "status": res.status, "reason": res.reason})

        if cpu_mode == "catalog" and ram_mode == "catalog":
            res = check_cpu_motherboard_ram(cpu_specs, candidate_specs, ram_specs)
            checks.append({"pair": "CPU + Motherboard + RAM Memory Generation", "status": res.status, "reason": res.reason})
        elif ram_mode == "catalog":
            mb_rt = candidate_specs.get("ram_type")
            ram_rt = ram_specs.get("ram_type")
            if mb_rt and ram_rt:
                if str(mb_rt).strip().casefold() != str(ram_rt).strip().casefold():
                    checks.append({
                        "pair": "Motherboard + RAM Memory Generation",
                        "status": "incompatible",
                        "reason": f"Motherboard RAM type ({mb_rt}) does not match RAM kit type ({ram_rt}).",
                    })
                else:
                    checks.append({
                        "pair": "Motherboard + RAM Memory Generation",
                        "status": "compatible",
                        "reason": f"Motherboard and RAM kit both specify {mb_rt}.",
                    })

        if ram_mode == "catalog":
            res = check_motherboard_ram_capacity(candidate_specs, ram_specs)
            checks.append({"pair": "Motherboard + RAM Capacity", "status": res.status, "reason": res.reason})
            res_qvl = check_ram_speed_qvl(ram_specs, candidate_specs, ram_component_id=ram_id, cpu_specs=cpu_specs if cpu_mode == "catalog" else None)
            checks.append({"pair": "Motherboard + RAM Speed / QVL", "status": res_qvl.status, "reason": res_qvl.reason})

        if case_mode == "catalog":
            res = check_motherboard_case(candidate_specs, case_specs)
            checks.append({"pair": "Motherboard Form Factor + Case Support", "status": res.status, "reason": res.reason})

        if storage_mode == "catalog":
            res = check_storage_motherboard(storage_specs, candidate_specs)
            checks.append({"pair": "Storage + Motherboard Interface", "status": res.status, "reason": res.reason})

    elif candidate_cat == "ram":
        if mb_mode == "catalog":
            res = check_motherboard_ram_capacity(mb_specs, candidate_specs)
            checks.append({"pair": "Motherboard + RAM Capacity", "status": res.status, "reason": res.reason})
            res_qvl = check_ram_speed_qvl(candidate_specs, mb_specs, ram_component_id=candidate_id, cpu_specs=cpu_specs if cpu_mode == "catalog" else None)
            checks.append({"pair": "Motherboard + RAM Speed / QVL", "status": res_qvl.status, "reason": res_qvl.reason})

        if cpu_mode == "catalog" and mb_mode == "catalog":
            res = check_cpu_motherboard_ram(cpu_specs, mb_specs, candidate_specs)
            checks.append({"pair": "CPU + Motherboard + RAM Memory Generation", "status": res.status, "reason": res.reason})
        elif mb_mode == "catalog":
            mb_rt = mb_specs.get("ram_type")
            ram_rt = candidate_specs.get("ram_type")
            if mb_rt and ram_rt:
                if str(mb_rt).strip().casefold() != str(ram_rt).strip().casefold():
                    checks.append({
                        "pair": "Motherboard + RAM Memory Generation",
                        "status": "incompatible",
                        "reason": f"RAM kit type ({ram_rt}) does not match Motherboard RAM type ({mb_rt}).",
                    })
                else:
                    checks.append({
                        "pair": "Motherboard + RAM Memory Generation",
                        "status": "compatible",
                        "reason": f"Motherboard and RAM kit both specify {ram_rt}.",
                    })

    elif candidate_cat == "case":
        if mb_mode == "catalog":
            res = check_motherboard_case(mb_specs, candidate_specs)
            checks.append({"pair": "Motherboard Form Factor + Case Support", "status": res.status, "reason": res.reason})

        if gpu_mode == "catalog":
            res = check_gpu_case(gpu_specs, candidate_specs)
            checks.append({"pair": "GPU Length + Case Clearance", "status": res.status, "reason": res.reason})

        if cooler_mode == "catalog":
            res = check_cooler_case(cooler_specs, candidate_specs)
            checks.append({"pair": "CPU Cooler + Case Clearance", "status": res.status, "reason": res.reason})

    elif candidate_cat == "gpu":
        if case_mode == "catalog":
            res = check_gpu_case(candidate_specs, case_specs)
            checks.append({"pair": "GPU Length + Case Clearance", "status": res.status, "reason": res.reason})

        if psu_mode == "catalog":
            res = check_psu(psu_specs, cpu_specs if cpu_mode == "catalog" else {}, candidate_specs)
            checks.append({"pair": "PSU Wattage vs GPU Power Draw", "status": res.status, "reason": res.reason})

    elif candidate_cat == "psu":
        if cpu_mode == "catalog" or gpu_mode == "catalog":
            res = check_psu(candidate_specs, cpu_specs if cpu_mode == "catalog" else {}, gpu_specs if gpu_mode == "catalog" else {})
            checks.append({"pair": "PSU Wattage Sizing", "status": res.status, "reason": res.reason})

    elif candidate_cat == "cooler":
        if cpu_mode == "catalog":
            res = check_cooler_socket(candidate_specs, cpu_specs, mb_specs if mb_mode == "catalog" else None)
            checks.append({"pair": "CPU Cooler + CPU Socket", "status": res.status, "reason": res.reason})

        if case_mode == "catalog":
            res = check_cooler_case(candidate_specs, case_specs)
            checks.append({"pair": "CPU Cooler + Case Clearance", "status": res.status, "reason": res.reason})

    elif candidate_cat == "storage":
        if mb_mode == "catalog":
            res = check_storage_motherboard(candidate_specs, mb_specs)
            checks.append({"pair": "Storage + Motherboard Interface", "status": res.status, "reason": res.reason})

    if not checks:
        return {
            "status": "compatible",
            "checks": [{"pair": "Baseline Check", "status": "compatible", "reason": "No dependent components currently selected to check against."}],
        }

    if any(c["status"] == "incompatible" for c in checks):
        overall = "incompatible"
    elif any(c["status"] == "unknown" for c in checks):
        overall = "unknown"
    else:
        overall = "compatible"

    return {"status": overall, "checks": checks}


def validate_full_build(build_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates all component pairings across an entire completed build.
    """
    all_checks: List[Dict[str, str]] = []
    for cat, comp in build_dict.items():
        if not comp:
            continue
        eval_res = evaluate_component_compatibility(comp, build_dict)
        for chk in eval_res.get("checks", []):
            if chk not in all_checks and chk["pair"] != "Baseline Check":
                all_checks.append(chk)

    if any(c["status"] == "incompatible" for c in all_checks):
        status = "incompatible"
    elif any(c["status"] == "unknown" for c in all_checks):
        status = "unknown"
    else:
        status = "compatible"

    return {
        "status": status,
        "checks": all_checks,
    }
