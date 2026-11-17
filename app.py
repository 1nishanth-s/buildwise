import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import streamlit as st

from src.compatibility import (
    check_cpu_motherboard,
    check_cpu_motherboard_ram,
    check_cooler_case,
    check_cooler_socket,
    check_gpu_case,
    check_motherboard_case,
    check_motherboard_ram_capacity,
    check_psu,
    check_ram_speed_qvl,
    check_storage_motherboard,
)
from src.performance_service import get_performance_service
from src.validator import load_and_validate

ROOT = Path(__file__).parent
DEFAULT_AVAILABILITY_FRESHNESS_DAYS = 7

INDIAN_RETAILER_DOMAINS = {
    "primeabgb.com",
    "flipkart.com",
    "mdcomputers.in",
    "pcstudio.in",
    "computechstore.in",
    "vedantcomputers.com",
    "elitehubs.com",
    "theitdepot.com",
    "clarioncomputers.in",
    "tpstech.in",
    "compify.in",
    "amazon.in",
}

BUILD_CATEGORIES = [
    "cpu",
    "motherboard",
    "ram",
    "case",
    "gpu",
    "psu",
    "cooler",
    "storage",
]

CATEGORY_LABELS = {
    "cpu": "CPU / Processor",
    "motherboard": "Motherboard",
    "ram": "RAM Memory",
    "case": "PC Case / Chassis",
    "gpu": "Graphics Card (GPU)",
    "psu": "Power Supply Unit (PSU)",
    "cooler": "CPU Cooler",
    "storage": "Storage Drive",
}

INTENDED_PURPOSES = [
    "Gaming",
    "Office and everyday use",
    "Programming and development",
    "Content creation",
    "Workstation",
    "General-purpose PC",
]


# =============================================================================
# REUSABLE PURE UTILITY FUNCTIONS
# =============================================================================

def is_indian_retailer_url(url):
    """Returns True if the URL belongs to a verified Indian hardware retailer."""
    if not url or pd.isna(url):
        return False
    url_str = str(url).strip()
    if not url_str:
        return False
    try:
        from urllib.parse import urlparse
        domain = urlparse(url_str).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain in INDIAN_RETAILER_DOMAINS
    except Exception:
        return False


def evaluate_indian_market_presence(entries):
    """Categorizes retail price entries into Indian presence status."""
    if not entries:
        return {
            "status": "unknown",
            "retailer": None,
            "listing_url": None,
            "checked_at": None,
        }
    for item in entries:
        if item.get("price_type") == "planning_estimate":
            continue
        url = item.get("source_url")
        if is_indian_retailer_url(url):
            return {
                "status": "verified_indian_listing",
                "retailer": item.get("seller"),
                "listing_url": url,
                "checked_at": item.get("checked_at"),
            }
    has_seller_obs = any(
        item.get("price_type") != "planning_estimate" and item.get("source_url")
        for item in entries
    )
    if has_seller_obs:
        first_seller = next(
            item for item in entries
            if item.get("price_type") != "planning_estimate" and item.get("source_url")
        )
        return {
            "status": "no_verified_indian_listing",
            "retailer": first_seller.get("seller"),
            "listing_url": first_seller.get("source_url"),
            "checked_at": first_seller.get("checked_at"),
        }
    return {
        "status": "unknown",
        "retailer": None,
        "listing_url": None,
        "checked_at": None,
    }


def parse_specs(raw_value):
    """Safely decodes JSON specifications from catalog strings or dicts."""
    if isinstance(raw_value, dict):
        return raw_value
    if not raw_value or pd.isna(raw_value):
        return {}
    try:
        return json.loads(str(raw_value))
    except (json.JSONDecodeError, TypeError):
        return {}


def price_to_int(raw_value):
    """Converts price values safely to integer INR."""
    if pd.isna(raw_value) or raw_value is None or raw_value == "":
        return None
    try:
        numeric = float(raw_value)
        if numeric < 0:
            return None
        return int(round(numeric))
    except (TypeError, ValueError):
        return None


def observation_freshness(checked_at, freshness_days, now=None):
    """Categorizes observation age into recent (<= freshness_days) or stale."""
    if not checked_at or pd.isna(checked_at):
        return "unknown", None
    now_dt = now or datetime.now(timezone.utc)
    try:
        checked_str = str(checked_at).strip()
        if "T" in checked_str:
            checked_dt = datetime.fromisoformat(checked_str)
        else:
            checked_dt = datetime.strptime(checked_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        if checked_dt.tzinfo is None:
            checked_dt = checked_dt.replace(tzinfo=timezone.utc)
        age = now_dt - checked_dt
        days = age.days
        if days < 0:
            return "recent", 0
        status = "recent" if days <= freshness_days else "stale"
        return status, days
    except Exception:
        return "unknown", None


def price_lookup(prices_frame, freshness_days=DEFAULT_AVAILABILITY_FRESHNESS_DAYS, now=None):
    """Builds a structured dictionary index of prices mapped by component_id."""
    if prices_frame is None or prices_frame.empty:
        return {}
    lookup = {}
    for _, row in prices_frame.iterrows():
        component_id = str(row.get("component_id", "")).strip()
        if not component_id:
            continue
        price_val = price_to_int(row.get("price_inr"))
        if price_val is None:
            continue
        freshness, age_days = observation_freshness(
            row.get("checked_at"), freshness_days, now=now
        )
        entry = {
            "price_id": str(row.get("price_id", "")).strip(),
            "component_id": component_id,
            "seller": str(row.get("seller", "")).strip(),
            "price_inr": price_val,
            "source_url": str(row.get("source_url", "")).strip(),
            "checked_at": str(row.get("checked_at", "")).strip(),
            "availability": str(row.get("availability", "unknown")).strip().casefold(),
            "freshness": freshness,
            "age_days": age_days,
            "price_type": str(row.get("price_type", "seller_observation")).strip().casefold() or "seller_observation",
            "price_basis": "User-provided planning estimate" if str(row.get("price_type", "")).strip().casefold() == "planning_estimate" else "Verified retailer observation",
            "provenance": str(row.get("provenance", "")).strip(),
        }
        lookup.setdefault(component_id, []).append(entry)
    for cid in lookup:
        lookup[cid].sort(key=lambda item: item["price_inr"])
    return lookup


def choose_cheapest_price(component_id, prices_lookup, prefer_available=False):
    """Picks lowest price observation or lowest available observation."""
    entries = prices_lookup.get(component_id, [])
    if not entries:
        return None
    if not prefer_available:
        return min(
            entries,
            key=lambda item: (
                item["price_inr"],
                item["price_type"] == "planning_estimate",
            ),
        )

    def availability_priority(item):
        if item["price_type"] == "planning_estimate":
            return 4
        if item["availability"] == "available" and item["freshness"] == "recent":
            return 0
        if item["availability"] == "unknown" or item["freshness"] == "unknown":
            return 1
        if item["availability"] == "available":
            return 2
        return 3

    return min(
        entries,
        key=lambda item: (
            availability_priority(item),
            item["price_inr"],
        ),
    )


# =============================================================================
# GUIDED WORKFLOW COMPATIBILITY, BUDGET & BENCHMARK FUNCTIONS
# =============================================================================

def evaluate_component_compatibility(candidate, selected_dict):
    """
    Evaluates a candidate component against currently selected/retained components.
    Uses strictly verified deterministic rules from src/compatibility.py.
    Returns:
      {
        'status': 'compatible' | 'incompatible' | 'unknown',
        'checks': [{'pair': str, 'status': str, 'reason': str}]
      }
    """
    candidate_cat = str(candidate.get("category", "")).strip().casefold()
    candidate_specs = parse_specs(candidate.get("specs_json", candidate.get("specs", {})))
    candidate_id = str(candidate.get("component_id", "")).strip()

    checks = []

    def get_sel(cat):
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
            checks.append({"pair": "CPU + Motherboard Socket", "status": "unknown", "reason": "Existing motherboard specs unknown; cannot verify socket compatibility."})

        if mb_mode == "catalog" and ram_mode == "catalog":
            res = check_cpu_motherboard_ram(candidate_specs, mb_specs, ram_specs)
            checks.append({"pair": "CPU + Motherboard + RAM Memory Generation", "status": res.status, "reason": res.reason})
        elif (mb_mode == "unknown" or ram_mode == "unknown") and mb_mode is not None and ram_mode is not None:
            checks.append({"pair": "CPU + Motherboard + RAM Generation", "status": "unknown", "reason": "Motherboard or RAM specs unknown; cannot verify memory generation match."})

        if cooler_mode == "catalog":
            res = check_cooler_socket(cooler_specs, candidate_specs, mb_specs if mb_mode == "catalog" else None)
            checks.append({"pair": "CPU Cooler + CPU Socket", "status": res.status, "reason": res.reason})
        elif cooler_mode == "unknown":
            checks.append({"pair": "CPU Cooler + CPU Socket", "status": "unknown", "reason": "Cooler specs unknown; cannot verify socket bracket compatibility."})

        if psu_mode == "catalog":
            res = check_psu(psu_specs, candidate_specs, gpu_specs if gpu_mode == "catalog" else {})
            checks.append({"pair": "PSU Wattage vs CPU Power", "status": res.status, "reason": res.reason})

    elif candidate_cat == "motherboard":
        if cpu_mode == "catalog":
            res = check_cpu_motherboard(cpu_specs, candidate_specs, cpu_component_id=cpu_id)
            checks.append({"pair": "CPU + Motherboard Socket", "status": res.status, "reason": res.reason})
        elif cpu_mode == "unknown":
            checks.append({"pair": "CPU + Motherboard Socket", "status": "unknown", "reason": "Existing CPU specs unknown; cannot verify socket compatibility."})

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
        elif ram_mode == "unknown":
            checks.append({"pair": "Motherboard + RAM Generation", "status": "unknown", "reason": "RAM specs unknown; cannot verify memory generation match."})

        if case_mode == "catalog":
            res = check_motherboard_case(candidate_specs, case_specs)
            checks.append({"pair": "Motherboard Form Factor + Case Support", "status": res.status, "reason": res.reason})
        elif case_mode == "unknown":
            checks.append({"pair": "Motherboard + Case Form Factor", "status": "unknown", "reason": "Case specs unknown; cannot verify form factor clearance."})

        if storage_mode == "catalog":
            res = check_storage_motherboard(storage_specs, candidate_specs)
            checks.append({"pair": "Storage + Motherboard Interface", "status": res.status, "reason": res.reason})

    elif candidate_cat == "ram":
        if mb_mode == "catalog":
            res = check_motherboard_ram_capacity(mb_specs, candidate_specs)
            checks.append({"pair": "Motherboard + RAM Capacity", "status": res.status, "reason": res.reason})
            res_qvl = check_ram_speed_qvl(candidate_specs, mb_specs, ram_component_id=candidate_id, cpu_specs=cpu_specs if cpu_mode == "catalog" else None)
            checks.append({"pair": "Motherboard + RAM Speed / QVL", "status": res_qvl.status, "reason": res_qvl.reason})
        elif mb_mode == "unknown":
            checks.append({"pair": "Motherboard + RAM Generation", "status": "unknown", "reason": "Motherboard specs unknown; cannot verify memory generation match."})

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
                        "reason": f"RAM type ({ram_rt}) does not match motherboard RAM type ({mb_rt}).",
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
        elif mb_mode == "unknown":
            checks.append({"pair": "Motherboard + Case Form Factor", "status": "unknown", "reason": "Motherboard specs unknown; cannot verify form factor support."})

        if gpu_mode == "catalog":
            res = check_gpu_case(gpu_specs, candidate_specs)
            checks.append({"pair": "GPU Length + Case Clearance", "status": res.status, "reason": res.reason})
        elif gpu_mode == "unknown":
            checks.append({"pair": "GPU + Case Physical Clearance", "status": "unknown", "reason": "GPU dimensions unknown; cannot verify physical clearance."})

        if cooler_mode == "catalog":
            res = check_cooler_case(cooler_specs, candidate_specs)
            checks.append({"pair": "CPU Cooler + Case Clearance", "status": res.status, "reason": res.reason})

    elif candidate_cat == "gpu":
        if case_mode == "catalog":
            res = check_gpu_case(candidate_specs, case_specs)
            checks.append({"pair": "GPU Length + Case Clearance", "status": res.status, "reason": res.reason})
        elif case_mode == "unknown":
            checks.append({"pair": "GPU + Case Clearance", "status": "unknown", "reason": "Case dimensions unknown; cannot verify physical clearance."})

        if psu_mode == "catalog":
            res = check_psu(psu_specs, cpu_specs if cpu_mode == "catalog" else {}, candidate_specs)
            checks.append({"pair": "PSU Wattage vs GPU Power Draw", "status": res.status, "reason": res.reason})
        elif psu_mode == "unknown":
            checks.append({"pair": "PSU Wattage vs GPU Power Draw", "status": "unknown", "reason": "PSU capacity unknown; cannot verify recommended power headroom."})

    elif candidate_cat == "psu":
        if cpu_mode == "catalog" or gpu_mode == "catalog":
            res = check_psu(candidate_specs, cpu_specs if cpu_mode == "catalog" else {}, gpu_specs if gpu_mode == "catalog" else {})
            checks.append({"pair": "PSU Wattage Sizing", "status": res.status, "reason": res.reason})

    elif candidate_cat == "cooler":
        if cpu_mode == "catalog":
            res = check_cooler_socket(candidate_specs, cpu_specs, mb_specs if mb_mode == "catalog" else None)
            checks.append({"pair": "CPU Cooler + CPU Socket", "status": res.status, "reason": res.reason})
        elif cpu_mode == "unknown":
            checks.append({"pair": "CPU Cooler + CPU Socket", "status": "unknown", "reason": "CPU socket unknown; cannot verify cooler mounting bracket."})

        if case_mode == "catalog":
            res = check_cooler_case(candidate_specs, case_specs)
            checks.append({"pair": "CPU Cooler + Case Clearance", "status": res.status, "reason": res.reason})
        elif case_mode == "unknown":
            checks.append({"pair": "CPU Cooler + Case Clearance", "status": "unknown", "reason": "Case dimensions unknown; cannot verify cooler height clearance."})

    elif candidate_cat == "storage":
        if mb_mode == "catalog":
            res = check_storage_motherboard(candidate_specs, mb_specs)
            checks.append({"pair": "Storage + Motherboard Interface", "status": res.status, "reason": res.reason})
        elif mb_mode == "unknown":
            checks.append({"pair": "Storage + Motherboard Interface", "status": "unknown", "reason": "Motherboard interfaces unknown; cannot verify storage slot."})

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


def reevaluate_build_selections(selections):
    """
    Revalidates all selected components against each other.
    Returns:
      {
        'is_valid': bool,
        'has_incompatibilities': bool,
        'has_unknowns': bool,
        'conflicts': list of conflict dicts
      }
    """
    conflicts = []
    has_incompatibilities = False
    has_unknowns = False

    active_cats = [c for c in BUILD_CATEGORIES if c in selections and selections[c].get("_status") != "skipped"]
    for i, cat in enumerate(active_cats):
        item = selections[cat]
        # Evaluate against all other active items
        context_items = {other_cat: selections[other_cat] for other_cat in active_cats if other_cat != cat}
        eval_result = evaluate_component_compatibility(item, context_items)
        if eval_result["status"] == "incompatible":
            has_incompatibilities = True
            for chk in eval_result["checks"]:
                if chk["status"] == "incompatible":
                    conflicts.append({
                        "category": cat,
                        "component_id": item.get("component_id"),
                        "pair": chk["pair"],
                        "status": "incompatible",
                        "reason": chk["reason"],
                    })
        elif eval_result["status"] == "unknown":
            has_unknowns = True
            for chk in eval_result["checks"]:
                if chk["status"] == "unknown":
                    conflicts.append({
                        "category": cat,
                        "component_id": item.get("component_id"),
                        "pair": chk["pair"],
                        "status": "unknown",
                        "reason": chk["reason"],
                    })

    # Deduplicate conflicts by (pair, reason)
    unique_conflicts = []
    seen = set()
    for conf in conflicts:
        key = (conf["pair"], conf["reason"])
        if key not in seen:
            seen.add(key)
            unique_conflicts.append(conf)

    return {
        "is_valid": not has_incompatibilities,
        "has_incompatibilities": has_incompatibilities,
        "has_unknowns": has_unknowns,
        "conflicts": unique_conflicts,
    }


def calculate_build_budget(selections, pricing_index, budget_inr=None):
    """
    Calculates build budget totals, distinguishing seller observations from planning estimates.
    Returns structured summary dict.
    """
    items = []
    total_recorded_price = 0
    total_confirmed_available_price = 0
    has_unpriced = False
    unpriced_count = 0
    verified_seller_count = 0
    planning_estimate_count = 0

    for cat in BUILD_CATEGORIES:
        item = selections.get(cat)
        if not item or not isinstance(item, dict):
            continue
        if item.get("_status") == "skipped":
            items.append({
                "category": cat,
                "component_id": "skipped",
                "brand": "Optional",
                "model": "Skipped (Not Selected)",
                "price_inr": 0,
                "price_display": "₹0 (Skipped)",
                "seller": "—",
                "availability": "—",
                "freshness": "—",
                "price_type": "skipped",
            })
            continue

        cid = item.get("component_id")
        cheapest = choose_cheapest_price(cid, pricing_index)
        if cheapest and cheapest.get("price_inr") is not None:
            p_val = cheapest["price_inr"]
            total_recorded_price += p_val
            p_type = cheapest.get("price_type", "seller_observation")
            if p_type == "planning_estimate":
                planning_estimate_count += 1
            else:
                verified_seller_count += 1
                if cheapest.get("availability") == "available":
                    total_confirmed_available_price += p_val
            price_display = f"₹{p_val:,}"
            seller_display = cheapest.get("seller", "—")
            avail_display = cheapest.get("availability", "unknown")
            freshness_display = cheapest.get("freshness", "unknown")
        else:
            p_val = None
            price_display = "Price unavailable"
            seller_display = "—"
            avail_display = "—"
            freshness_display = "—"
            p_type = "unpriced"
            has_unpriced = True
            unpriced_count += 1

        items.append({
            "category": cat,
            "component_id": cid,
            "brand": item.get("brand", ""),
            "model": item.get("model", ""),
            "price_inr": p_val,
            "price_display": price_display,
            "seller": seller_display,
            "availability": avail_display,
            "freshness": freshness_display,
            "price_type": p_type,
        })

    remaining = None
    is_over_budget = False
    if budget_inr is not None:
        remaining = budget_inr - total_recorded_price
        is_over_budget = remaining < 0

    return {
        "budget_inr": budget_inr,
        "total_recorded_price": total_recorded_price,
        "total_confirmed_available_price": total_confirmed_available_price,
        "remaining_budget": remaining,
        "is_over_budget": is_over_budget,
        "has_unpriced": has_unpriced,
        "unpriced_count": unpriced_count,
        "verified_seller_count": verified_seller_count,
        "planning_estimate_count": planning_estimate_count,
        "items": items,
    }


def compare_benchmarks(comp_a_id, comp_b_id, benchmarks_df):
    """
    Empirical benchmark comparison between two components of the same category.
    Compares Cinebench R23 Multi-Core for CPUs and 3DMark Time Spy Graphics for GPUs.
    Returns structured comparison result.
    """
    if benchmarks_df is None or benchmarks_df.empty or not comp_a_id or not comp_b_id:
        return {"status": "unavailable", "message": "Benchmark data unavailable"}

    match_a = benchmarks_df[benchmarks_df["component_id"] == comp_a_id]
    match_b = benchmarks_df[benchmarks_df["component_id"] == comp_b_id]

    if match_a.empty or match_b.empty:
        return {"status": "unavailable", "message": "Benchmark data unavailable"}

    row_a = match_a.iloc[0]
    row_b = match_b.iloc[0]

    suite_a = str(row_a.get("benchmark_suite", "")).strip()
    suite_b = str(row_b.get("benchmark_suite", "")).strip()
    metric_a = str(row_a.get("benchmark_metric", "")).strip()
    metric_b = str(row_b.get("benchmark_metric", "")).strip()

    if suite_a != suite_b or metric_a != metric_b:
        return {
            "status": "unavailable",
            "message": f"Incompatible benchmark suites/metrics: {suite_a} ({metric_a}) vs {suite_b} ({metric_b})",
        }

    score_a = float(row_a["score"]) if pd.notna(row_a.get("score")) else None
    score_b = float(row_b["score"]) if pd.notna(row_b.get("score")) else None

    if score_a is None or score_b is None:
        return {"status": "unavailable", "message": "Benchmark data unavailable"}

    delta = score_b - score_a
    pct = ((score_b - score_a) / score_a * 100.0) if score_a > 0 else 0.0

    return {
        "status": "available",
        "suite": suite_a,
        "metric": metric_a,
        "score_a": score_a,
        "score_b": score_b,
        "delta": delta,
        "pct_change": pct,
        "source_a": row_a.get("source_name", "empirical"),
        "source_b": row_b.get("source_name", "empirical"),
        "summary": f"{score_b:,.0f} vs {score_a:,.0f} pts ({pct:+.1f}%)",
    }


def reset_build_mode():
    """Resets Build Mode session state while preserving Upgrade Mode state."""
    st.session_state.build_selections = {}
    st.session_state.build_step = 0


def reset_upgrade_mode():
    """Resets Upgrade Mode session state while preserving Build Mode state."""
    st.session_state.upgrade_existing = {}
    st.session_state.selected_upgrade = None


# =============================================================================
# STREAMLIT USER INTERFACE & STATE MANAGEMENT
# =============================================================================

st.set_page_config(page_title="BuildWise-AI", page_icon="🖥️", layout="wide")

# Initialize session state keys
if "build_budget" not in st.session_state:
    st.session_state.build_budget = 75000
if "build_purpose" not in st.session_state:
    st.session_state.build_purpose = "Gaming"
if "build_selections" not in st.session_state:
    st.session_state.build_selections = {}
if "build_step" not in st.session_state:
    st.session_state.build_step = 0

if "upgrade_budget" not in st.session_state:
    st.session_state.upgrade_budget = 30000
if "upgrade_existing" not in st.session_state:
    st.session_state.upgrade_existing = {}
if "upgrade_category" not in st.session_state:
    st.session_state.upgrade_category = "gpu"
if "selected_upgrade" not in st.session_state:
    st.session_state.selected_upgrade = None

# Header banner
st.title("BuildWise-AI — PC Component Intelligence System")
st.caption(
    "PC hardware selection, verified Indian retail price tracking, compatibility analysis, "
    "and empirical benchmark intelligence · India · INR"
)

# Load production datasets
components, prices, issues = load_and_validate(ROOT / "data")
benchmarks_path = ROOT / "data" / "benchmarks.csv"
benchmarks = (
    pd.read_csv(benchmarks_path)
    if benchmarks_path.exists()
    else pd.DataFrame()
)
pricing_index = price_lookup(prices)


@st.cache_resource
def load_performance_service():
    """Loads and caches the ML performance prediction service."""
    return get_performance_service()


perf_service = load_performance_service()

# Sidebar Navigation
st.sidebar.title("BuildWise-AI Navigation")
page = st.sidebar.radio(
    "Select Mode / View",
    [
        "Home / Dataset Overview",
        "Build Mode (Guided)",
        "Upgrade Mode",
        "Component Catalog Browser",
        "Compatibility Inspector",
    ],
    index=0,
)


# =============================================================================
# VIEW 1: HOME / DATASET OVERVIEW
# =============================================================================
if page == "Home / Dataset Overview":
    st.subheader("1. Production Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Component Catalog", f"{len(components):,} records")
    col2.metric("Retail Price Observations", f"{len(prices):,} records")
    col3.metric("Benchmark Observations", f"{len(benchmarks):,} records")
    col4.metric("Data Validation Issues", len(issues))

    if issues:
        st.warning(f"{len(issues)} validation issues detected in production data.")
        with st.expander("View Validation Issues"):
            st.dataframe(pd.DataFrame([{"Issue": item} for item in issues]), hide_index=True)
    else:
        st.success("All production dataset schemas, referential foreign keys, and JSON integrity checks verified.")

    # Category distribution
    cat_counts = (
        components["category"].str.casefold().value_counts().rename_axis("Category").reset_index(name="Components")
    )
    st.dataframe(cat_counts, hide_index=True)

    st.divider()
    st.markdown("### Supervised Machine Learning Performance Prediction Models")
    st.caption("Active supervised regression pipelines trained on verified empirical benchmark observations.")
    ml_col1, ml_col2 = st.columns(2)
    with ml_col1:
        st.markdown("#### CPU Performance Model")
        if perf_service.is_cpu_model_available():
            cpu_meta = perf_service.get_cpu_metadata()
            st.success("🟢 **Model Status: Active & Loaded**")
            st.markdown("- **Target Metric:** Cinebench R23 Multi-Core Score")
            st.markdown(f"- **Algorithm:** `{cpu_meta.get('selected_algorithm', 'Ridge Regression (alpha=10.0)')}`")
            st.markdown("- **Training Dataset:** 180 empirical observations across 10 platform families")
            st.markdown("- **Cross-Validation Accuracy:** R² = 0.9170, MAE = 2,420.4 pts")
        else:
            st.error("🔴 **Model Status: Unavailable** — CPU model artifact not loaded.")

    with ml_col2:
        st.markdown("#### GPU Performance Model")
        if perf_service.is_gpu_model_available():
            gpu_meta = perf_service.get_gpu_metadata()
            st.success("🟢 **Model Status: Active & Loaded**")
            st.markdown("- **Target Metric:** 3DMark Time Spy Graphics Score")
            st.markdown(f"- **Algorithm:** `{gpu_meta.get('selected_algorithm', 'Ridge Regression (alpha=1.0)')}`")
            st.markdown("- **Training Dataset:** 57 empirical observations across 14 silicon die groups")
            st.markdown("- **Cross-Validation Accuracy:** R² = 0.9017, MAE = 1,355.3 pts")
            st.caption("Limited training sample size (57 empirical observations): Predictions are available for GPUs with verified silicon architecture and memory bus specifications.")
        else:
            st.error("🔴 **Model Status: Unavailable** — GPU model artifact not loaded.")

    st.info(
        "The legacy exhaustive recommendation engine has been retired. "
        "Guided Build Mode and Upgrade Mode are now active for step-by-step PC component selection. "
        "Supervised ML models (Cinebench R23 for CPU and 3DMark Time Spy for GPU) provide empirical performance estimates."
    )


# =============================================================================
# VIEW 2: BUILD MODE (GUIDED)
# =============================================================================
elif page == "Build Mode (Guided)":
    st.subheader("2. Guided PC Build Mode")
    st.caption(
        "Select components sequentially step-by-step. BuildWise-AI verifies deterministic compatibility rules, "
        "tracks your recorded budget in INR, and presents verified benchmark information without arbitrary rankings."
    )

    # Build Preferences
    b_col1, b_col2, b_col3 = st.columns([2, 2, 1])
    with b_col1:
        new_budget = st.number_input(
            "Total Build Budget (INR)",
            min_value=10000,
            max_value=1000000,
            value=int(st.session_state.build_budget),
            step=5000,
            key="input_build_budget",
        )
        st.session_state.build_budget = new_budget
    with b_col2:
        new_purpose = st.selectbox(
            "Primary Intended Use (Contextual)",
            INTENDED_PURPOSES,
            index=INTENDED_PURPOSES.index(st.session_state.build_purpose) if st.session_state.build_purpose in INTENDED_PURPOSES else 0,
            key="input_build_purpose",
        )
        st.session_state.build_purpose = new_purpose
    with b_col3:
        st.write("")
        st.write("")
        if st.button("Reset Build", type="secondary", key="btn_reset_build"):
            reset_build_mode()
            st.rerun()

    st.caption("Intended use provides descriptive context; components are not artificially scored or ranked by arbitrary formulas.")

    # Check for conflicts caused by changing an earlier component
    reval = reevaluate_build_selections(st.session_state.build_selections)
    if reval["has_incompatibilities"]:
        st.error("⚠️ Incompatibility Conflict Detected: A previously selected component is conflicting with other selections.")
        for conf in reval["conflicts"]:
            if conf["status"] == "incompatible":
                st.markdown(f"- **{CATEGORY_LABELS.get(conf['category'], conf['category'])}** (`{conf['component_id']}`): {conf['pair']} — {conf['reason']}")
    elif reval["has_unknowns"] and reval["conflicts"]:
        with st.expander("ℹ️ Unverified Compatibility Checks (Insufficient Evidence)"):
            for conf in reval["conflicts"]:
                if conf["status"] == "unknown":
                    st.markdown(f"- **{CATEGORY_LABELS.get(conf['category'], conf['category'])}** (`{conf['component_id']}`): {conf['pair']} — {conf['reason']}")

    # Step Progress Selector
    step_labels = [f"{i+1}. {CATEGORY_LABELS[c]}" for i, c in enumerate(BUILD_CATEGORIES)]
    active_step = st.radio(
        "Build Progress & Category Steps",
        step_labels,
        index=min(st.session_state.build_step, len(BUILD_CATEGORIES) - 1),
        horizontal=True,
        key="radio_build_step",
    )
    current_cat_idx = step_labels.index(active_step)
    st.session_state.build_step = current_cat_idx
    current_cat = BUILD_CATEGORIES[current_cat_idx]

    st.divider()

    # Layout: Selection Area (Left 7) and Live Budget Tracker (Right 5)
    main_col, budget_col = st.columns([7, 5])

    with main_col:
        st.markdown(f"### Step {current_cat_idx + 1} of 8: Select {CATEGORY_LABELS[current_cat]}")

        # Current selection for this category if already chosen
        curr_selected = st.session_state.build_selections.get(current_cat)
        if curr_selected:
            if curr_selected.get("_status") == "skipped":
                st.info(f"You chose to skip {CATEGORY_LABELS[current_cat]} (e.g., using integrated graphics or stock cooler).")
                if st.button(f"Choose a {CATEGORY_LABELS[current_cat]}", key=f"btn_unskip_{current_cat}"):
                    del st.session_state.build_selections[current_cat]
                    st.rerun()
            else:
                st.success(f"Selected: **{curr_selected.get('brand')} {curr_selected.get('model')}** (`{curr_selected.get('component_id')}`)")
                cheapest_sel = choose_cheapest_price(curr_selected.get('component_id'), pricing_index)
                if cheapest_sel:
                    st.markdown(f"Lowest Recorded Price: **₹{cheapest_sel['price_inr']:,}** ({cheapest_sel['seller']}) · Status: {cheapest_sel['availability'].title()}")
                else:
                    st.markdown("Lowest Recorded Price: **Price unavailable**")

                if st.button(f"Remove / Change {CATEGORY_LABELS[current_cat]}", key=f"btn_remove_{current_cat}"):
                    del st.session_state.build_selections[current_cat]
                    st.rerun()

        # Selection Interface
        cat_df = components[components["category"].str.casefold() == current_cat].copy()
        search_kw = st.text_input(f"Filter {CATEGORY_LABELS[current_cat]} by Brand or Model", "", key=f"search_{current_cat}")
        if search_kw:
            kw = search_kw.lower()
            cat_df = cat_df[
                cat_df["brand"].str.lower().str.contains(kw, na=False)
                | cat_df["model"].str.lower().str.contains(kw, na=False)
            ]

        if cat_df.empty:
            st.warning("No components match the search filter.")
        else:
            # Candidate sorting options
            sort_options = ["Default Catalog Order", "Lowest Recorded Price"]
            if current_cat in ("cpu", "gpu"):
                sort_options.insert(1, "Predicted Performance (High to Low)")

            sort_choice = st.selectbox(
                f"Sort {CATEGORY_LABELS[current_cat]} Candidates by",
                sort_options,
                key=f"sort_sel_{current_cat}",
            )

            # Pre-compute predictions for CPU/GPU if sorting or labeling
            pred_cache = {}
            if current_cat in ("cpu", "gpu"):
                for _, r in cat_df.iterrows():
                    cid = r["component_id"]
                    pred_cache[cid] = perf_service.predict_component(r.to_dict())

            if sort_choice == "Predicted Performance (High to Low)" and current_cat in ("cpu", "gpu"):
                cat_df["_sort_score"] = cat_df["component_id"].map(
                    lambda cid: pred_cache.get(cid, {}).get("score") or -1.0
                )
                cat_df = cat_df.sort_values(by="_sort_score", ascending=False).drop(columns=["_sort_score"])
            elif sort_choice == "Lowest Recorded Price":
                cat_df["_sort_price"] = cat_df["component_id"].map(
                    lambda cid: (choose_cheapest_price(cid, pricing_index) or {}).get("price_inr") or 9999999
                )
                cat_df = cat_df.sort_values(by="_sort_price", ascending=True).drop(columns=["_sort_price"])

            cand_options = {}
            for _, r in cat_df.iterrows():
                cid = r["component_id"]
                label_base = f"{r['brand']} {r['model']} ({cid})"
                if current_cat in ("cpu", "gpu") and cid in pred_cache:
                    pred_info = pred_cache[cid]
                    if pred_info.get("status") == "available":
                        label_base += f" — Est. {pred_info['score_formatted']}"
                cand_options[label_base] = cid

            cand_label = st.selectbox(
                f"Choose candidate {CATEGORY_LABELS[current_cat]}",
                list(cand_options.keys()),
                key=f"cand_select_{current_cat}",
            )
            cand_id = cand_options[cand_label]
            cand_row = cat_df[cat_df["component_id"] == cand_id].iloc[0].to_dict()

            # Evaluate compatibility live against other selections
            eval_res = evaluate_component_compatibility(cand_row, st.session_state.build_selections)
            status = eval_res["status"]

            if status == "compatible":
                st.success("✅ **Compatibility: COMPATIBLE** with currently selected hardware.")
            elif status == "unknown":
                st.warning("⚠️ **Compatibility: UNKNOWN (Evidence Required)** — Documented evidence is missing or incomplete.")
            else:
                st.error("❌ **Compatibility: INCOMPATIBLE** — Documented hardware conflict detected.")

            with st.expander("View Compatibility Evaluation Details", expanded=(status != "compatible")):
                for chk in eval_res["checks"]:
                    st.markdown(f"- **{chk['pair']}**: `{chk['status'].upper()}` — {chk['reason']}")

            # Pricing & Benchmark info
            p_cand = choose_cheapest_price(cand_id, pricing_index)
            cand_b_col1, cand_b_col2 = st.columns(2)
            with cand_b_col1:
                st.markdown("**Recorded Pricing Observation:**")
                if p_cand:
                    st.markdown(f"- Price: **₹{p_cand['price_inr']:,}**")
                    st.markdown(f"- Seller: {p_cand['seller']}")
                    st.markdown(f"- Availability: {p_cand['availability'].title()}")
                    st.markdown(f"- Price Type: {p_cand['price_basis']}")
                else:
                    st.markdown("- Price: **Price unavailable**")

            with cand_b_col2:
                st.markdown("**Recorded Empirical Benchmark:**")
                b_match = benchmarks[benchmarks["component_id"] == cand_id]
                if not b_match.empty:
                    b_row = b_match.iloc[0]
                    st.markdown(f"- Measured Score: **{b_row['score']:,.0f} pts** ({b_row['benchmark_metric']})")
                    st.markdown(f"- Benchmark Suite: {b_row['benchmark_suite']}")
                    st.markdown(f"- Evidence Source: {b_row.get('source_name', 'empirical')}")
                else:
                    st.markdown("- Empirical Benchmark: **No empirical observation recorded**")

            # Supervised ML Performance Prediction Section
            if current_cat in ("cpu", "gpu"):
                st.markdown("---")
                st.markdown(f"**Supervised ML Performance Estimate ({CATEGORY_LABELS[current_cat]}):**")
                ml_pred = perf_service.predict_component(cand_row)
                if ml_pred["status"] == "available":
                    pred_col_a, pred_col_b = st.columns(2)
                    with pred_col_a:
                        st.markdown(f"- Predicted **{ml_pred['target_metric']}**: **{ml_pred['score_formatted']}** `[ML Estimate]`")
                        st.markdown(f"- Benchmark Suite: {ml_pred['target_suite']}")
                    with pred_col_b:
                        st.markdown(f"- Model Architecture: `{ml_pred['model_name']}`")
                        st.caption(f"{ml_pred.get('training_context', '')}. Statistical regression estimate; does not guarantee specific application or gaming FPS.")
                else:
                    st.warning(f"⚠️ **Prediction Unavailable:** {ml_pred.get('message', 'Insufficient hardware specifications.')}")

            # Selection Actions
            act_col1, act_col2 = st.columns([2, 3])
            with act_col1:
                if status != "incompatible":
                    if st.button(f"Select this {CATEGORY_LABELS[current_cat]}", type="primary", key=f"btn_confirm_{current_cat}"):
                        st.session_state.build_selections[current_cat] = cand_row
                        if current_cat_idx < len(BUILD_CATEGORIES) - 1:
                            st.session_state.build_step = current_cat_idx + 1
                        st.rerun()
                else:
                    st.button("Cannot Select Incompatible Component", disabled=True, key=f"btn_dis_{current_cat}")
                    st.caption("Cannot select: documented hardware conflict.")

            with act_col2:
                if current_cat in ("gpu", "cooler"):
                    if st.button(f"Skip {CATEGORY_LABELS[current_cat]} (Optional)", key=f"btn_skip_act_{current_cat}"):
                        st.session_state.build_selections[current_cat] = {
                            "_status": "skipped",
                            "category": current_cat,
                            "brand": "Optional",
                            "model": f"Skipped (No {CATEGORY_LABELS[current_cat]})",
                            "component_id": f"skipped_{current_cat}",
                        }
                        if current_cat_idx < len(BUILD_CATEGORIES) - 1:
                            st.session_state.build_step = current_cat_idx + 1
                        st.rerun()

    with budget_col:
        st.markdown("### Live Budget & Build Tracker")
        b_summary = calculate_build_budget(
            st.session_state.build_selections,
            pricing_index,
            budget_inr=st.session_state.build_budget,
        )

        st.metric("Total Budget", f"₹{b_summary['budget_inr']:,}")
        st.metric("Recorded Total", f"₹{b_summary['total_recorded_price']:,}")
        st.metric(
            "Remaining Budget",
            f"₹{b_summary['remaining_budget']:,}",
            delta=f"{b_summary['remaining_budget']:,}",
            delta_color="normal" if not b_summary["is_over_budget"] else "inverse",
        )

        if b_summary["is_over_budget"]:
            st.error("⚠️ Over Budget: Current configuration exceeds target budget.")

        if b_summary["has_unpriced"]:
            st.warning(f"⚠️ {b_summary['unpriced_count']} component(s) have unrecorded prices and are not included in total.")

        st.markdown(f"- Verified Retailer Prices: **{b_summary['verified_seller_count']}**")
        st.markdown(f"- Planning Estimates: **{b_summary['planning_estimate_count']}**")
        st.markdown(f"- Components Selected: **{len(st.session_state.build_selections)} / 8**")

        st.markdown("#### Selected Hardware Summary")
        if not b_summary["items"]:
            st.caption("No components selected yet.")
        else:
            summary_table = [
                {
                    "Category": CATEGORY_LABELS.get(it["category"], it["category"]),
                    "Component": f"{it['brand']} {it['model']}",
                    "Price": it["price_display"],
                    "Seller": it["seller"],
                }
                for it in b_summary["items"]
            ]
            st.dataframe(pd.DataFrame(summary_table), hide_index=True)


# =============================================================================
# VIEW 3: UPGRADE MODE
# =============================================================================
elif page == "Upgrade Mode":
    st.subheader("3. Upgrade Mode — Hardware Replacement & Empirical Analysis")
    st.caption(
        "Specify your existing PC hardware, choose a component to upgrade, evaluate replacement candidates "
        "against retained components, and inspect empirical benchmark improvements."
    )

    u_col1, u_col2 = st.columns([3, 1])
    with u_col1:
        new_up_budget = st.number_input(
            "Upgrade Budget (INR)",
            min_value=0,
            max_value=500000,
            value=int(st.session_state.upgrade_budget),
            step=2000,
            key="input_up_budget",
        )
        st.session_state.upgrade_budget = new_up_budget
    with u_col2:
        st.write("")
        st.write("")
        if st.button("Reset Upgrade Mode", type="secondary", key="btn_reset_up"):
            reset_upgrade_mode()
            st.rerun()

    st.markdown("### Step 1: Specify Existing Installed PC Components")
    st.caption("Select your current components from catalog, mark as unknown hardware, or mark as not installed.")

    # Configure existing PC hardware across all 8 categories
    with st.expander("Configure Existing Hardware Configuration", expanded=len(st.session_state.upgrade_existing) < 4):
        for cat in BUILD_CATEGORIES:
            st.markdown(f"**{CATEGORY_LABELS[cat]}**")
            sub_c1, sub_c2 = st.columns([2, 5])
            existing_entry = st.session_state.upgrade_existing.get(cat, {"status": "unknown"})
            curr_mode = existing_entry.get("status", "unknown")

            with sub_c1:
                mode_choice = st.selectbox(
                    f"Status for {CATEGORY_LABELS[cat]}",
                    ["Catalog Component", "Unknown / Not Listed Hardware", "Not Installed / None"],
                    index=0 if curr_mode == "catalog" else (1 if curr_mode == "unknown" else 2),
                    key=f"up_mode_{cat}",
                )

            with sub_c2:
                if mode_choice == "Catalog Component":
                    cat_items = components[components["category"].str.casefold() == cat]
                    opts = {f"{r['brand']} {r['model']} ({r['component_id']})": r["component_id"] for _, r in cat_items.iterrows()}
                    sel_opt = st.selectbox(
                        f"Select {CATEGORY_LABELS[cat]} Model",
                        list(opts.keys()),
                        key=f"up_sel_{cat}",
                    )
                    chosen_cid = opts[sel_opt]
                    chosen_row = cat_items[cat_items["component_id"] == chosen_cid].iloc[0].to_dict()
                    st.session_state.upgrade_existing[cat] = {
                        "status": "catalog",
                        "component_id": chosen_cid,
                        "brand": chosen_row.get("brand"),
                        "model": chosen_row.get("model"),
                        "specs_json": chosen_row.get("specs_json"),
                    }
                elif mode_choice == "Unknown / Not Listed Hardware":
                    st.session_state.upgrade_existing[cat] = {
                        "status": "unknown",
                        "component_id": f"unknown_{cat}",
                        "brand": "Generic / Unlisted",
                        "model": "Unknown Hardware",
                    }
                    st.caption("Dependent compatibility checks will report unknown (evidence missing).")
                else:
                    st.session_state.upgrade_existing[cat] = {
                        "status": "none",
                        "component_id": f"none_{cat}",
                        "brand": "None",
                        "model": "Not Installed",
                    }
                    st.caption("Component not installed.")

    st.divider()

    # Step 2: Choose Upgrade Target
    st.markdown("### Step 2: Choose Hardware Category to Upgrade")
    up_cat = st.selectbox(
        "Select Hardware to Upgrade",
        BUILD_CATEGORIES,
        index=BUILD_CATEGORIES.index(st.session_state.upgrade_category) if st.session_state.upgrade_category in BUILD_CATEGORIES else 4,
        format_func=lambda c: CATEGORY_LABELS[c],
        key="sel_up_target_cat",
    )
    st.session_state.upgrade_category = up_cat

    # Retained hardware (all categories except up_cat, excluding 'none')
    retained_dict = {}
    for c, entry in st.session_state.upgrade_existing.items():
        if c != up_cat and entry.get("status") != "none":
            retained_dict[c] = entry

    st.markdown(f"**Retained Components:** {', '.join([CATEGORY_LABELS[c] for c in retained_dict.keys()]) or 'None specified'}")

    st.divider()

    # Step 3: Replacement Candidate Selection & Evaluation
    st.markdown(f"### Step 3: Evaluate Replacement Candidates for {CATEGORY_LABELS[up_cat]}")
    up_candidates_df = components[components["category"].str.casefold() == up_cat].copy()

    up_search = st.text_input(f"Filter Replacement {CATEGORY_LABELS[up_cat]} by Brand or Model", "", key="up_search_input")
    if up_search:
        kw = up_search.lower()
        up_candidates_df = up_candidates_df[
            up_candidates_df["brand"].str.lower().str.contains(kw, na=False)
            | up_candidates_df["model"].str.lower().str.contains(kw, na=False)
        ]

    if up_candidates_df.empty:
        st.warning("No replacement candidates match filter.")
    else:
        up_opts = {f"{r['brand']} {r['model']} ({r['component_id']})": r["component_id"] for _, r in up_candidates_df.iterrows()}
        up_chosen_label = st.selectbox(f"Select Replacement {CATEGORY_LABELS[up_cat]} Candidate", list(up_opts.keys()), key="up_cand_select")
        up_cid = up_opts[up_chosen_label]
        up_cand_row = up_candidates_df[up_candidates_df["component_id"] == up_cid].iloc[0].to_dict()

        # Compatibility check against retained components
        up_compat = evaluate_component_compatibility(up_cand_row, retained_dict)

        st_col1, st_col2 = st.columns([3, 2])
        with st_col1:
            st.markdown(f"#### Replacement: {up_cand_row.get('brand')} {up_cand_row.get('model')}")
            if up_compat["status"] == "compatible":
                st.success("✅ **Compatible** with your retained PC components.")
            elif up_compat["status"] == "unknown":
                st.warning("⚠️ **Compatibility Unknown** — Retained hardware specifications are missing or incomplete.")
            else:
                st.error("❌ **Incompatible** — Hardware conflict detected with retained components.")

            with st.expander("Compatibility Analysis with Retained Hardware"):
                for chk in up_compat["checks"]:
                    st.markdown(f"- **{chk['pair']}**: `{chk['status'].upper()}` — {chk['reason']}")

            # Pricing
            up_price_rec = choose_cheapest_price(up_cid, pricing_index)
            if up_price_rec:
                cand_cost = up_price_rec["price_inr"]
                st.markdown(f"Lowest Recorded Price: **₹{cand_cost:,}** ({up_price_rec['seller']})")
                rem_up_budget = st.session_state.upgrade_budget - cand_cost
                if rem_up_budget >= 0:
                    st.success(f"Within Upgrade Budget: **₹{rem_up_budget:,}** remaining.")
                else:
                    st.error(f"Exceeds Upgrade Budget by **₹{abs(rem_up_budget):,}**.")
            else:
                st.markdown("Lowest Recorded Price: **Price unavailable**")

        with st_col2:
            st.markdown("#### Performance Evaluation & Comparison")
            baseline_entry = st.session_state.upgrade_existing.get(up_cat, {})
            baseline_cid = baseline_entry.get("component_id")

            # 1. Empirical Benchmark Comparison (data/benchmarks.csv)
            st.markdown("**1. Recorded Empirical Benchmarks:**")
            if up_cat in ("cpu", "gpu") and baseline_entry.get("status") == "catalog":
                b_res = compare_benchmarks(baseline_cid, up_cid, benchmarks)
                if b_res["status"] == "available":
                    st.metric("Recorded Baseline Score", f"{b_res['score_a']:,.0f} pts")
                    st.metric("Recorded Upgrade Score", f"{b_res['score_b']:,.0f} pts")
                    st.metric("Empirical Performance Delta", f"{b_res['delta']:+,.0f} pts", delta=f"{b_res['pct_change']:+.1f}%")
                    st.caption(f"Suite: {b_res['suite']} ({b_res['metric']}) · Sources: {b_res['source_a']} / {b_res['source_b']}")
                else:
                    st.info(f"Empirical Comparison: {b_res['message']}")
            else:
                st.info("Empirical benchmark comparison unavailable (baseline component is not a catalog record or lacks recorded benchmark).")

            # 2. Supervised ML Performance Prediction
            if up_cat in ("cpu", "gpu"):
                st.markdown("---")
                st.markdown("**2. Supervised ML Performance Prediction:**")
                if baseline_entry.get("status") == "catalog":
                    baseline_match = components[components["component_id"] == baseline_cid]
                    if not baseline_match.empty:
                        base_row = baseline_match.iloc[0].to_dict()
                        ml_comp = perf_service.compare_predicted_performance(base_row, up_cand_row)
                        if ml_comp["status"] == "available":
                            m_col1, m_col2 = st.columns(2)
                            with m_col1:
                                st.metric("Baseline (Estimated)", f"{ml_comp['score_a']:,.0f} pts")
                            with m_col2:
                                st.metric("Upgrade (Estimated)", f"{ml_comp['score_b']:,.0f} pts")
                            st.metric("Estimated Performance Delta", f"{ml_comp['delta']:+,.0f} pts", delta=f"{ml_comp['pct_change']:+.1f}%")
                            st.caption(f"Model-estimated comparison ({ml_comp['suite']} {ml_comp['metric']}) via {ml_comp['model_name']}. Statistical regression estimate; does not guarantee actual frame rates.")
                        else:
                            st.info(f"ML Estimated Comparison: {ml_comp.get('message', 'Unavailable')}")
                            cand_pred = perf_service.predict_component(up_cand_row)
                            if cand_pred["status"] == "available":
                                st.markdown(f"- Upgrade Candidate Predicted **{cand_pred['target_metric']}**: **{cand_pred['score_formatted']}** `[ML Estimate]`")
                    else:
                        st.info("Baseline catalog component not found.")
                else:
                    cand_pred = perf_service.predict_component(up_cand_row)
                    if cand_pred["status"] == "available":
                        st.metric("Upgrade Candidate (Estimated)", cand_pred['score_formatted'])
                        st.caption(f"{cand_pred['target_suite']} ({cand_pred['target_metric']}) · ML Model Estimate (`{cand_pred['model_name']}`)")
                    st.info("Baseline prediction unavailable (existing hardware specifications missing or unlisted) — cannot compute estimated delta.")
            else:
                st.caption("ML-based performance predictions are only available for CPU and GPU categories. Motherboards, RAM, storage, PSU, cases, and coolers do not have trained regression models.")


# =============================================================================
# VIEW 4: COMPONENT CATALOG BROWSER (PRESERVED)
# =============================================================================
elif page == "Component Catalog Browser":
    st.subheader("4. Component Catalog Browser")
    st.caption("Inspect genuine desktop PC hardware components, technical specifications, observed INR retail prices, and verified benchmark scores.")

    categories = sorted(components["category"].str.casefold().unique().tolist())
    selected_category = st.selectbox("Select Hardware Category", categories, index=0)

    cat_components = components[
        components["category"].str.casefold() == selected_category
    ].copy()

    search_term = st.text_input("Filter by Brand or Model Name", "")
    if search_term:
        search_lower = search_term.lower()
        cat_components = cat_components[
            cat_components["brand"].str.lower().str.contains(search_lower, na=False)
            | cat_components["model"].str.lower().str.contains(search_lower, na=False)
        ]

    browser_rows = []
    for _, row in cat_components.iterrows():
        cid = str(row["component_id"]).strip()
        specs = parse_specs(row.get("specs_json"))
        cheapest = choose_cheapest_price(cid, pricing_index)
        presence = evaluate_indian_market_presence(pricing_index.get(cid, []))

        bench_match = benchmarks[benchmarks["component_id"] == cid]
        bench_display = "—"
        if not bench_match.empty:
            score_val = bench_match.iloc[0].get("score")
            metric_name = bench_match.iloc[0].get("benchmark_metric", "")
            bench_display = f"{score_val:,.0f} pts ({metric_name})" if pd.notna(score_val) else "—"

        browser_rows.append({
            "ID": cid,
            "Brand": row.get("brand", ""),
            "Model": row.get("model", ""),
            "Lowest Price (INR)": f"₹{cheapest['price_inr']:,}" if cheapest else "Unpriced",
            "Seller": cheapest["seller"] if cheapest else "—",
            "Availability": cheapest["availability"] if cheapest else "—",
            "Indian Retailer Presence": presence["status"].replace("_", " ").title(),
            "Empirical Benchmark": bench_display,
        })

    browser_df = pd.DataFrame(browser_rows)
    st.dataframe(browser_df, hide_index=True)

    if not cat_components.empty:
        with st.expander(f"Inspect Detailed Component Specifications ({len(cat_components)} items)"):
            item_options = {
                f"{r['brand']} {r['model']} ({r['component_id']})": r['component_id']
                for _, r in cat_components.iterrows()
            }
            chosen_label = st.selectbox("Select Component to Inspect", list(item_options.keys()))
            chosen_id = item_options[chosen_label]
            comp_row = cat_components[cat_components["component_id"] == chosen_id].iloc[0]
            specs_data = parse_specs(comp_row.get("specs_json"))

            insp_col1, insp_col2 = st.columns(2)
            with insp_col1:
                st.markdown(f"**Component ID:** `{chosen_id}`")
                st.markdown(f"**Brand:** {comp_row.get('brand')}")
                st.markdown(f"**Model:** {comp_row.get('model')}")
                st.markdown(f"**Source:** [{comp_row.get('source_name')}]({comp_row.get('source_url')})")
                st.markdown("**Technical Specifications (JSON):**")
                st.json(specs_data)
            with insp_col2:
                st.markdown("**Recorded Indian Retail Price Observations:**")
                comp_prices = pricing_index.get(chosen_id, [])
                if comp_prices:
                    st.dataframe(pd.DataFrame(comp_prices)[[
                        "seller", "price_inr", "availability", "freshness", "price_type", "checked_at"
                    ]], hide_index=True)
                else:
                    st.info("No retail price observations recorded yet for this component.")

                st.markdown("**Empirical Benchmark Observations:**")
                comp_bench = benchmarks[benchmarks["component_id"] == chosen_id]
                if not comp_bench.empty:
                    st.dataframe(comp_bench[[
                        "benchmark_suite", "benchmark_metric", "score", "score_unit", "source_name"
                    ]], hide_index=True)
                else:
                    st.info("No benchmark observations recorded for this component.")

                if selected_category in ("cpu", "gpu"):
                    st.markdown("**Supervised ML Performance Prediction:**")
                    pred_insp = perf_service.predict_component(comp_row.to_dict())
                    if pred_insp["status"] == "available":
                        st.markdown(f"- Predicted **{pred_insp['target_metric']}**: **{pred_insp['score_formatted']}** `[ML Estimate]`")
                        st.markdown(f"- Model Architecture: `{pred_insp['model_name']}`")
                        st.caption(f"{pred_insp.get('training_context', '')}. Statistical regression estimate.")
                    else:
                        st.info(f"Prediction Unavailable: {pred_insp.get('message', 'Insufficient hardware specifications.')}")


# =============================================================================
# VIEW 5: COMPATIBILITY INSPECTOR (PRESERVED)
# =============================================================================
elif page == "Compatibility Inspector":
    st.subheader("5. Deterministic Hardware Compatibility Inspection")
    st.caption("Inspect cross-component hardware compatibility rules directly using the BuildWise-AI compatibility engine.")

    check_mode = st.selectbox(
        "Select Compatibility Check Mode",
        [
            "CPU + Motherboard Socket Compatibility",
            "Motherboard + RAM Generation & Capacity",
            "GPU + Case Physical Clearance",
            "CPU Cooler + Case Clearance",
            "CPU Cooler + CPU Socket Support",
            "Storage + Motherboard Interface Support",
        ],
    )

    cpus = components[components["category"].str.casefold() == "cpu"]
    motherboards = components[components["category"].str.casefold() == "motherboard"]
    rams = components[components["category"].str.casefold() == "ram"]
    gpus = components[components["category"].str.casefold() == "gpu"]
    cases = components[components["category"].str.casefold() == "case"]
    coolers = components[components["category"].str.casefold() == "cooler"]
    storages = components[components["category"].str.casefold() == "storage"]

    def make_options(df):
        return {f"{r['brand']} {r['model']} ({r['component_id']})": r['component_id'] for _, r in df.iterrows()}

    if check_mode == "CPU + Motherboard Socket Compatibility":
        c1, c2 = st.columns(2)
        with c1:
            cpu_opts = make_options(cpus)
            sel_cpu_label = st.selectbox("Select CPU", list(cpu_opts.keys()))
            sel_cpu = cpus[cpus["component_id"] == cpu_opts[sel_cpu_label]].iloc[0]
        with c2:
            mb_opts = make_options(motherboards)
            sel_mb_label = st.selectbox("Select Motherboard", list(mb_opts.keys()))
            sel_mb = motherboards[motherboards["component_id"] == mb_opts[sel_mb_label]].iloc[0]

        result = check_cpu_motherboard(
            parse_specs(sel_cpu.get("specs_json")),
            parse_specs(sel_mb.get("specs_json")),
            cpu_component_id=sel_cpu.get("component_id"),
        )
        status_color = {"compatible": "success", "incompatible": "error", "unknown": "warning"}[result.status]
        getattr(st, status_color)(f"**Compatibility Status: {result.status.upper()}**\n\n{result.reason}")

    elif check_mode == "GPU + Case Physical Clearance":
        c1, c2 = st.columns(2)
        with c1:
            gpu_opts = make_options(gpus)
            sel_gpu_label = st.selectbox("Select GPU", list(gpu_opts.keys()))
            sel_gpu = gpus[gpus["component_id"] == gpu_opts[sel_gpu_label]].iloc[0]
        with c2:
            case_opts = make_options(cases)
            sel_case_label = st.selectbox("Select Case", list(case_opts.keys()))
            sel_case = cases[cases["component_id"] == case_opts[sel_case_label]].iloc[0]

        result = check_gpu_case(
            parse_specs(sel_gpu.get("specs_json")),
            parse_specs(sel_case.get("specs_json")),
        )
        status_color = {"compatible": "success", "incompatible": "error", "unknown": "warning"}[result.status]
        getattr(st, status_color)(f"**Compatibility Status: {result.status.upper()}**\n\n{result.reason}")

    elif check_mode == "Motherboard + RAM Generation & Capacity":
        c1, c2 = st.columns(2)
        with c1:
            mb_opts = make_options(motherboards)
            sel_mb_label = st.selectbox("Select Motherboard", list(mb_opts.keys()))
            sel_mb = motherboards[motherboards["component_id"] == mb_opts[sel_mb_label]].iloc[0]
        with c2:
            ram_opts = make_options(rams)
            sel_ram_label = st.selectbox("Select RAM Kit", list(ram_opts.keys()))
            sel_ram = rams[rams["component_id"] == ram_opts[sel_ram_label]].iloc[0]

        result = check_motherboard_ram_capacity(
            parse_specs(sel_mb.get("specs_json")),
            parse_specs(sel_ram.get("specs_json")),
        )
        status_color = {"compatible": "success", "incompatible": "error", "unknown": "warning"}[result.status]
        getattr(st, status_color)(f"**Compatibility Status: {result.status.upper()}**\n\n{result.reason}")

    elif check_mode == "CPU Cooler + Case Clearance":
        c1, c2 = st.columns(2)
        with c1:
            cooler_opts = make_options(coolers)
            sel_clr_label = st.selectbox("Select CPU Cooler", list(cooler_opts.keys()))
            sel_clr = coolers[coolers["component_id"] == cooler_opts[sel_clr_label]].iloc[0]
        with c2:
            case_opts = make_options(cases)
            sel_case_label = st.selectbox("Select Case", list(case_opts.keys()))
            sel_case = cases[cases["component_id"] == case_opts[sel_case_label]].iloc[0]

        result = check_cooler_case(
            parse_specs(sel_clr.get("specs_json")),
            parse_specs(sel_case.get("specs_json")),
        )
        status_color = {"compatible": "success", "incompatible": "error", "unknown": "warning"}[result.status]
        getattr(st, status_color)(f"**Compatibility Status: {result.status.upper()}**\n\n{result.reason}")

    elif check_mode == "CPU Cooler + CPU Socket Support":
        c1, c2 = st.columns(2)
        with c1:
            cooler_opts = make_options(coolers)
            sel_clr_label = st.selectbox("Select CPU Cooler", list(cooler_opts.keys()))
            sel_clr = coolers[coolers["component_id"] == cooler_opts[sel_clr_label]].iloc[0]
        with c2:
            cpu_opts = make_options(cpus)
            sel_cpu_label = st.selectbox("Select CPU", list(cpu_opts.keys()))
            sel_cpu = cpus[cpus["component_id"] == cpu_opts[sel_cpu_label]].iloc[0]

        result = check_cooler_socket(
            parse_specs(sel_clr.get("specs_json")),
            parse_specs(sel_cpu.get("specs_json")),
        )
        status_color = {"compatible": "success", "incompatible": "error", "unknown": "warning"}[result.status]
        getattr(st, status_color)(f"**Compatibility Status: {result.status.upper()}**\n\n{result.reason}")

    elif check_mode == "Storage + Motherboard Interface Support":
        c1, c2 = st.columns(2)
        with c1:
            stg_opts = make_options(storages)
            sel_stg_label = st.selectbox("Select Storage Drive", list(stg_opts.keys()))
            sel_stg = storages[storages["component_id"] == stg_opts[sel_stg_label]].iloc[0]
        with c2:
            mb_opts = make_options(motherboards)
            sel_mb_label = st.selectbox("Select Motherboard", list(mb_opts.keys()))
            sel_mb = motherboards[motherboards["component_id"] == mb_opts[sel_mb_label]].iloc[0]

        result = check_storage_motherboard(
            parse_specs(sel_stg.get("specs_json")),
            parse_specs(sel_mb.get("specs_json")),
        )
        status_color = {"compatible": "success", "incompatible": "error", "unknown": "warning"}[result.status]
        getattr(st, status_color)(f"**Compatibility Status: {result.status.upper()}**\n\n{result.reason}")
