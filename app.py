import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

from src.compatibility import (
    check_cpu_motherboard,
    check_cpu_motherboard_ram,
    check_gpu_case,
    check_motherboard_case,
    check_motherboard_ram_capacity,
    check_psu,
    check_storage_motherboard,
    check_cooler_socket,
    check_cooler_case,
    check_ram_speed_qvl,
)
from src.validator import load_and_validate


ROOT = Path(__file__).parent
DEFAULT_AVAILABILITY_FRESHNESS_DAYS = 7
PURPOSE_LAYOUT = {
    "study/office": ["cpu", "motherboard", "ram", "storage", "case", "psu"],
    "programming": ["cpu", "motherboard", "ram", "storage", "case", "psu"],
    "gaming": ["cpu", "motherboard", "gpu", "ram", "storage", "case", "psu", "cooler"],
    "content creation": ["cpu", "motherboard", "gpu", "ram", "storage", "case", "psu"],
}

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


def is_indian_retailer_url(url):
    if not url or pd.isna(url):
        return False
    url_str = str(url).strip()
    if not url_str:
        return False
    try:
        parsed = urlparse(url_str)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        if netloc in INDIAN_RETAILER_DOMAINS:
            return True
        for domain in INDIAN_RETAILER_DOMAINS:
            if netloc.endswith("." + domain):
                return True
        if netloc.endswith(".in") or ".in:" in netloc:
            return True
    except Exception:
        return False
    return False


def evaluate_indian_market_presence(entries):
    if not entries:
        return {
            "status": "unknown",
            "retailer": "",
            "listing_url": "",
            "checked_at": "",
        }
    for item in entries:
        if item.get("price_type") == "planning_estimate":
            continue
        source_url = item.get("source_url", "")
        seller = item.get("seller", "")
        checked_at = item.get("checked_at", "")
        if is_indian_retailer_url(source_url):
            return {
                "status": "verified_indian_listing",
                "retailer": seller or "Indian Retailer",
                "listing_url": source_url,
                "checked_at": checked_at,
            }
        known_indian_sellers = {
            "prime abgb", "flipkart", "retailnet", "mdcomputers", "pc studio",
            "computech store", "vedant computers", "elitehubs", "alltech trading",
            "global klamp", "the it depot", "clarion computers"
        }
        if seller.lower().strip() in known_indian_sellers and source_url:
            return {
                "status": "verified_indian_listing",
                "retailer": seller,
                "listing_url": source_url,
                "checked_at": checked_at,
            }
    has_seller_observations = any(
        item.get("price_type") != "planning_estimate" and item.get("source_url")
        for item in entries
    )
    has_only_estimates = all(
        item.get("price_type") == "planning_estimate" for item in entries
    )
    if has_seller_observations or has_only_estimates:
        return {
            "status": "no_verified_indian_listing",
            "retailer": "",
            "listing_url": "",
            "checked_at": "",
        }
    return {
        "status": "unknown",
        "retailer": "",
        "listing_url": "",
        "checked_at": "",
    }


def parse_specs(raw_value):
    if raw_value is None or pd.isna(raw_value):
        return {}
    try:
        parsed = json.loads(str(raw_value))
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def price_to_int(raw_value):
    if raw_value is None or pd.isna(raw_value):
        return None
    cleaned = str(raw_value).strip().replace(",", "")
    if not cleaned:
        return None
    try:
        value = float(cleaned)
    except ValueError:
        return None
    if not math.isfinite(value) or value <= 0:
        return None
    return int(value)


def observation_freshness(checked_at, freshness_days, now=None):
    checked_at = str(checked_at or "").strip()
    if not checked_at:
        return "unknown", None

    current_time = now or datetime.now().astimezone()
    try:
        checked_time = datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
    except ValueError:
        return "unknown", None
    if checked_time.tzinfo is None:
        checked_time = checked_time.replace(tzinfo=current_time.tzinfo)
    else:
        checked_time = checked_time.astimezone(current_time.tzinfo)

    age = current_time - checked_time
    if age.total_seconds() < 0:
        return "unknown", None
    age_days = age.days
    if age > timedelta(days=freshness_days):
        return "stale", age_days
    return "recent", age_days


def price_lookup(prices_frame, freshness_days=DEFAULT_AVAILABILITY_FRESHNESS_DAYS, now=None):
    lookup = {}
    if prices_frame is None or prices_frame.empty:
        return lookup
    current_time = now or datetime.now().astimezone()
    for _, row in prices_frame.iterrows():
        component_id = str(row.get("component_id", "")).strip()
        if not component_id:
            continue
        price_value = price_to_int(row.get("price_inr"))
        availability = str(row.get("availability", "")).strip().lower()
        if price_value is None or price_value <= 0:
            continue
        price_type = str(row.get("price_type", "")).strip().lower()
        is_estimate = price_type == "planning_estimate"
        freshness, age_days = observation_freshness(
            row.get("checked_at", ""),
            freshness_days,
            current_time,
        )
        lookup.setdefault(component_id, []).append({
            "price_inr": price_value,
            "seller": str(row.get("seller", "")).strip() or "Unknown seller",
            "source_url": str(row.get("source_url", "")).strip(),
            "checked_at": str(row.get("checked_at", "")).strip(),
            "availability": availability if availability in {"available", "unavailable"} else "unknown",
            "freshness": freshness,
            "age_days": age_days,
            "price_type": "planning_estimate" if is_estimate else "seller_observation",
            "price_basis": (
                "User-provided planning estimate"
                if is_estimate else "Recorded seller observation"
            ),
            "provenance": str(row.get("provenance", "")).strip(),
        })
    for component_id in lookup:
        lookup[component_id] = sorted(
            lookup[component_id],
            key=lambda item: item["price_inr"],
        )
    return lookup


def choose_cheapest_price(
    component_id,
    prices_lookup,
    prefer_available=False,
):
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


def _check_candidate_compatibility(selected_rows):
    selected_rows = [
        {**entry, "_compatibility_results": []}
        for entry in selected_rows
    ]
    warnings = []
    checks = []
    selected_by_category = {
        entry["category"].casefold(): entry for entry in selected_rows
    }
    cpu_row = selected_by_category.get("cpu")
    motherboard_row = selected_by_category.get("motherboard")
    ram_row = selected_by_category.get("ram")
    case_row = selected_by_category.get("case")
    gpu_row = selected_by_category.get("gpu")
    psu_row = selected_by_category.get("psu")
    cooler_row = selected_by_category.get("cooler")

    def record_result(entries, result):
        checks.append(result)
        for entry in entries:
            entry["_compatibility_results"].append(result)

    if cpu_row and motherboard_row:
        result = check_cpu_motherboard(
            parse_specs(cpu_row.get("specs_json")),
            parse_specs(motherboard_row.get("specs_json")),
            cpu_component_id=str(cpu_row.get("component_id", "")).strip(),
        )
        record_result((cpu_row, motherboard_row), result)
        if result.status != "compatible":
            warnings.append(f"CPU/motherboard compatibility {result.status}: {result.reason}")

    if cpu_row and motherboard_row and ram_row:
        result = check_cpu_motherboard_ram(
            parse_specs(cpu_row.get("specs_json")),
            parse_specs(motherboard_row.get("specs_json")),
            parse_specs(ram_row.get("specs_json")),
        )
        record_result((cpu_row, motherboard_row, ram_row), result)
        if result.status != "compatible":
            warnings.append(f"CPU/motherboard/RAM compatibility {result.status}: {result.reason}")

    if motherboard_row and ram_row:
        result = check_motherboard_ram_capacity(
            parse_specs(motherboard_row.get("specs_json")),
            parse_specs(ram_row.get("specs_json")),
        )
        record_result((motherboard_row, ram_row), result)
        if result.status != "compatible":
            warnings.append(f"Motherboard/RAM capacity compatibility {result.status}: {result.reason}")

        qvl_result = check_ram_speed_qvl(
            parse_specs(ram_row.get("specs_json")),
            parse_specs(motherboard_row.get("specs_json")),
            ram_component_id=str(ram_row.get("component_id", "")).strip(),
            cpu_specs=parse_specs(cpu_row.get("specs_json")) if cpu_row else None,
        )
        record_result((ram_row,), qvl_result)
        if qvl_result.status != "compatible":
            warnings.append(f"RAM speed/QVL compatibility {qvl_result.status}: {qvl_result.reason}")

    if motherboard_row and case_row:
        result = check_motherboard_case(
            parse_specs(motherboard_row.get("specs_json")),
            parse_specs(case_row.get("specs_json")),
        )
        record_result((motherboard_row, case_row), result)
        if result.status != "compatible":
            warnings.append(f"Motherboard/case compatibility {result.status}: {result.reason}")

    storage_row = selected_by_category.get("storage")
    if motherboard_row and storage_row:
        result = check_storage_motherboard(
            parse_specs(storage_row.get("specs_json")),
            parse_specs(motherboard_row.get("specs_json")),
        )
        record_result((motherboard_row, storage_row), result)
        if result.status != "compatible":
            warnings.append(f"Motherboard/storage compatibility {result.status}: {result.reason}")

    if gpu_row and case_row:
        result = check_gpu_case(
            parse_specs(gpu_row.get("specs_json")),
            parse_specs(case_row.get("specs_json")),
        )
        record_result((gpu_row, case_row), result)
        if result.status != "compatible":
            warnings.append(f"GPU/case compatibility {result.status}: {result.reason}")

    if psu_row and cpu_row:
        gpu_specs = (
            parse_specs(gpu_row.get("specs_json")) if gpu_row else {}
        )
        result = check_psu(
            parse_specs(psu_row.get("specs_json")),
            parse_specs(cpu_row.get("specs_json")),
            gpu_specs,
        )
        involved_rows = (psu_row, cpu_row, gpu_row) if gpu_row else (psu_row, cpu_row)
        record_result(involved_rows, result)
        if result.status != "compatible":
            warnings.append(f"PSU/system compatibility {result.status}: {result.reason}")

    if cooler_row and cpu_row:
        result = check_cooler_socket(
            parse_specs(cooler_row.get("specs_json")),
            parse_specs(cpu_row.get("specs_json")),
            parse_specs(motherboard_row.get("specs_json")) if motherboard_row else None,
        )
        record_result((cooler_row, cpu_row), result)
        if result.status != "compatible":
            warnings.append(f"CPU cooler socket compatibility {result.status}: {result.reason}")

    if cooler_row and case_row:
        result = check_cooler_case(
            parse_specs(cooler_row.get("specs_json")),
            parse_specs(case_row.get("specs_json")),
        )
        record_result((cooler_row, case_row), result)
        if result.status != "compatible":
            warnings.append(f"CPU cooler/case clearance compatibility {result.status}: {result.reason}")

    for entry in selected_rows:
        results = entry.pop("_compatibility_results")
        if results:
            statuses = {result.status for result in results}
            entry["compatibility"] = (
                "incompatible" if "incompatible" in statuses
                else "unknown" if "unknown" in statuses
                else "compatible"
            )
            entry["compatibility_reason"] = " ".join(
                result.reason for result in results
            )
    compatibility_score = (
        sum(result.status == "incompatible" for result in checks),
        sum(result.status == "unknown" for result in checks),
    )
    return selected_rows, warnings, compatibility_score


def build_recommendation(
    components,
    prices,
    budget_inr,
    purpose,
    includes_peripherals,
    selected_categories=None,
    prefer_available=False,
    freshness_days=DEFAULT_AVAILABILITY_FRESHNESS_DAYS,
):
    pricing = price_lookup(prices, freshness_days=freshness_days)
    warnings = []
    is_upgrade = selected_categories is not None
    supported_categories = {
        category for layout in PURPOSE_LAYOUT.values() for category in layout
    }
    required_categories = (
        list(dict.fromkeys(
            str(category).strip().casefold()
            for category in selected_categories
            if str(category).strip().casefold() in supported_categories
        ))
        if is_upgrade
        else PURPOSE_LAYOUT.get(
            purpose, ["cpu", "motherboard", "ram", "storage", "case", "psu"]
        )
    )
    if is_upgrade and not required_categories:
        return [], ["Choose at least one component category for an upgrade recommendation."], {
            "total_price": 0,
            "remaining_budget": budget_inr,
            "build_status": "none",
            "missing_categories": [],
            "compatibility_status": "unknown",
            "includes_estimates": False,
            "is_upgrade": True,
            "price_selection": "available_first" if prefer_available else "lowest_price",
        }

    category_options = []
    missing_categories = []
    for category in required_categories:
        matches = components[components["category"].astype(str).str.casefold() == category].copy()
        if matches.empty:
            missing_categories.append(category)
            warnings.append(f"No {category} records are present in the catalog.")
            continue
        priced_records = []
        for _, row in matches.iterrows():
            entry = choose_cheapest_price(
                str(row["component_id"]).strip(),
                pricing,
                prefer_available=prefer_available,
            )
            if entry is not None:
                component_id_str = str(row["component_id"]).strip()
                presence = evaluate_indian_market_presence(
                    pricing.get(component_id_str, [entry])
                )
                priced_records.append({
                    "component_id": component_id_str,
                    "category": str(row["category"]).strip(),
                    "brand": str(row.get("brand", "")).strip(),
                    "model": str(row.get("model", "")).strip(),
                    "price_inr": entry["price_inr"],
                    "seller": entry["seller"],
                    "source_url": entry["source_url"],
                    "checked_at": entry["checked_at"],
                    "availability": entry["availability"],
                    "availability_freshness": entry["freshness"],
                    "observation_age_days": entry["age_days"],
                    "price_type": entry["price_type"],
                    "price_basis": entry["price_basis"],
                    "provenance": entry["provenance"],
                    "specs_json": row.get("specs_json", ""),
                    "compatibility": "unknown",
                    "compatibility_reason": "No documented cross-component rule has been evaluated for this component.",
                    "indian_market_presence": presence["status"],
                    "indian_retailer": presence["retailer"],
                    "indian_listing_url": presence["listing_url"],
                    "indian_listing_checked_at": presence["checked_at"],
                })
        if not priced_records:
            missing_categories.append(category)
            warnings.append(f"No priced {category} records are available, so this category cannot be included safely.")
            continue
        category_options.append(sorted(priced_records, key=lambda item: item["price_inr"]))

    if not category_options:
        warnings.append("The catalog does not contain enough priced entries for a safe recommendation at this moment.")
        return [], warnings, {
            "total_price": 0,
            "remaining_budget": budget_inr,
            "build_status": "none",
            "missing_categories": missing_categories,
            "compatibility_status": "unknown",
            "includes_estimates": False,
            "is_upgrade": is_upgrade,
            "price_selection": "available_first" if prefer_available else "lowest_price",
        }

    minimum_remaining = [0] * (len(category_options) + 1)
    for index in range(len(category_options) - 1, -1, -1):
        minimum_remaining[index] = (
            minimum_remaining[index + 1]
            + category_options[index][0]["price_inr"]
        )

    best_key = None
    best_rows = None
    best_warnings = []

    def search(category_index, chosen, total_price):
        nonlocal best_key, best_rows, best_warnings
        if total_price + minimum_remaining[category_index] > budget_inr:
            return
        if (
            not prefer_available
            and best_key
            and best_key[:2] == (0, 0)
            and best_key[2] == minimum_remaining[0]
        ):
            return
        if category_index == len(category_options):
            evaluated_rows, check_warnings, compatibility_score = (
                _check_candidate_compatibility(chosen)
            )
            if prefer_available:
                recent_available_count = sum(
                    entry["price_type"] != "planning_estimate"
                    and entry["availability"] == "available"
                    and entry["availability_freshness"] == "recent"
                    for entry in evaluated_rows
                )
                candidate_key = (
                    *compatibility_score,
                    -recent_available_count,
                    total_price,
                )
            else:
                candidate_key = (*compatibility_score, total_price)
            if best_key is None or candidate_key < best_key:
                best_key = candidate_key
                best_rows = evaluated_rows
                best_warnings = check_warnings
            return
        for option in category_options[category_index]:
            if (
                not prefer_available
                and best_key
                and best_key[:2] == (0, 0)
                and best_key[2] == minimum_remaining[0]
            ):
                break
            option_total = total_price + option["price_inr"]
            if option_total > budget_inr:
                break
            partial_score = _check_candidate_compatibility(
                [*chosen, option]
            )[2]
            # Completed checks only accumulate, so a worse partial score cannot recover.
            if best_key and (
                partial_score[0] > best_key[0]
                or (
                    partial_score[0] == best_key[0]
                    and partial_score[1] > best_key[1]
                )
            ):
                continue
            search(
                category_index + 1,
                [*chosen, option],
                option_total,
            )

    search(0, [], 0)
    if best_rows is None:
        minimum_total = minimum_remaining[0]
        warnings.append(
            f"No combination of recorded prices fits within the {budget_inr:,} INR budget. "
            f"The lowest recorded-price total for the categories with priced options is {minimum_total:,} INR."
        )
        if includes_peripherals:
            warnings.append("Peripheral pricing is excluded because no peripheral price records exist in the catalog. This budget is interpreted as the build-only budget.")
        return [], warnings, {
            "total_price": 0,
            "remaining_budget": budget_inr,
            "build_status": "none",
            "missing_categories": missing_categories,
            "compatibility_status": "unknown",
            "includes_estimates": False,
            "is_upgrade": is_upgrade,
            "price_selection": "available_first" if prefer_available else "lowest_price",
        }

    selected_rows = best_rows
    warnings.extend(best_warnings)
    selected_by_category = {
        entry["category"].casefold(): entry for entry in selected_rows
    }
    missing_categories = list(dict.fromkeys([
        *missing_categories,
        *(category for category in required_categories if category not in selected_by_category),
    ]))

    if not is_upgrade and purpose in {"gaming", "content creation"} and "gpu" not in selected_by_category:
        warnings.append("No priced GPU is available in the catalog for the requested purpose.")
    if missing_categories:
        warnings.append(
            "This is a partial recommendation. Missing required categories: "
            + ", ".join(missing_categories)
            + ". Their prices were not treated as zero."
        )

    for entry in selected_rows:
        if not entry["compatibility_reason"].startswith("No documented"):
            continue
        warnings.append(
            f"Compatibility for {entry['category']} {entry['brand']} {entry['model']} "
            f"is unknown: {entry['compatibility_reason']}"
        )

    if includes_peripherals:
        warnings.append("Peripheral pricing is excluded because no peripheral price records exist in the catalog. This budget is interpreted as the build-only budget.")

    total_price = sum(item["price_inr"] for item in selected_rows)
    remaining_budget = budget_inr - total_price
    includes_estimates = any(
        item["price_type"] == "planning_estimate" for item in selected_rows
    )
    statuses = {entry["compatibility"] for entry in selected_rows}
    compatibility_status = (
        "incompatible" if "incompatible" in statuses
        else "unknown" if "unknown" in statuses
        else "compatible"
    )
    if is_upgrade:
        compatibility_status = "unknown"
        warnings.append(
            "Compatibility with your existing components is unknown because they were not provided; "
            "this recommendation covers only the selected upgrade categories."
        )
    elif compatibility_status == "unknown":
        warnings.append(
            "Overall build compatibility is unknown because one or more required checks or specifications are unknown."
        )
    elif compatibility_status == "incompatible":
        warnings.append("The selected build has one or more documented incompatibilities.")

    for entry in selected_rows:
        if entry.get("indian_market_presence") == "no_verified_indian_listing":
            warnings.append(
                f"No verified Indian retailer listing was found for {entry['category']} {entry['brand']} {entry['model']}; "
                "local-market presence is unverified. Treat this part as not confirmed available in India."
            )
        elif entry.get("indian_market_presence") == "unknown":
            warnings.append(
                f"Indian-market listing evidence for {entry['category']} {entry['brand']} {entry['model']} is unknown or missing."
            )
        specs = parse_specs(entry.get("specs_json"))
        if not specs:
            warnings.append(f"Missing specifications for {entry['category']} {entry['brand']} {entry['model']}; compatibility cannot be fully checked.")
        freshness_message = (
            f"checked {entry['observation_age_days']} days ago"
            if entry["observation_age_days"] is not None
            else "check age is unknown"
        )
        if (
            entry["price_type"] != "planning_estimate"
            and entry["availability_freshness"] == "stale"
        ):
            warnings.append(
                f"The {entry['category']} {entry['brand']} {entry['model']} price and availability observation "
                f"from {entry['checked_at']} is older than the {freshness_days}-day freshness window; "
                "treat its price and stock status as historical until checked again."
            )
        if entry["availability"] == "unavailable":
            warnings.append(
                f"{entry['category']} {entry['brand']} {entry['model']} was marked unavailable when checked "
                f"({entry['checked_at']}); this is recorded status, not a live stock check."
            )
        elif entry["availability"] == "available":
            if entry["availability_freshness"] == "recent":
                status_age = f"{freshness_message}, within the {freshness_days}-day freshness window"
            elif entry["availability_freshness"] == "stale":
                status_age = f"{freshness_message}, outside the {freshness_days}-day freshness window"
            else:
                status_age = "freshness could not be determined from the recorded check date"
            warnings.append(
                f"{entry['category']} {entry['brand']} {entry['model']} was marked available when checked "
                f"({entry['checked_at']}; {status_age}); this is not a live stock or delivery confirmation."
            )
        elif entry["availability"] == "unknown":
            warnings.append(
                f"Availability for {entry['category']} {entry['brand']} {entry['model']} is unknown "
                f"(price checked {entry['checked_at'] or 'on an unknown date'}); the recorded price is not a confirmation of current stock."
            )
        if entry["price_type"] == "planning_estimate":
            warnings.append(
                f"{entry['category']} {entry['brand']} {entry['model']} uses a user-provided planning estimate "
                f"of {entry['price_inr']:,} INR, not an independently verified seller price."
            )
        reason_bits = []
        if entry["category"] == "cpu":
            performance = specs.get("performance_tier")
            use_cases = specs.get("use_cases") or []
            if performance:
                reason_bits.append(f"performance tier: {performance}")
            if use_cases:
                reason_bits.append(f"use case match: {', '.join(use_cases[:2])}")
        elif entry["category"] == "gpu":
            performance = specs.get("performance_tier")
            if performance:
                reason_bits.append(f"graphical performance tier: {performance}")
            use_cases = specs.get("use_cases") or []
            if use_cases:
                reason_bits.append(f"use case match: {', '.join(use_cases[:2])}")
        elif entry["category"] == "ram":
            if specs.get("ram_type"):
                reason_bits.append(f"memory type: {specs.get('ram_type')}")
            if specs.get("speed_mtps"):
                reason_bits.append(f"speed: {specs.get('speed_mtps')} MT/s")
        elif entry["category"] == "motherboard":
            if specs.get("socket"):
                reason_bits.append(f"socket: {specs.get('socket')}")
            if specs.get("chipset"):
                reason_bits.append(f"chipset: {specs.get('chipset')}")
        elif entry["category"] == "cooler":
            if specs.get("height_mm"):
                reason_bits.append(f"height: {specs.get('height_mm')} mm")
            if specs.get("cooling_type"):
                reason_bits.append(f"type: {specs.get('cooling_type')}")
        else:
            reason_bits.append("recorded-price option")
        entry["reason"] = "Selected in the highest-ranked within-budget combination using recorded INR prices; " + "; ".join(reason_bits) if reason_bits else "Selected in the highest-ranked within-budget combination using recorded INR prices."

    warnings.append(
        "Indian retailer listings confirm documented local-market presence at the check date, "
        "not live stock, checkout price guarantees, or delivery eligibility."
    )
    return selected_rows, warnings, {
        "total_price": total_price,
        "remaining_budget": remaining_budget,
        "includes_estimates": includes_estimates,
        "build_status": "partial" if missing_categories else "complete",
        "missing_categories": missing_categories,
        "compatibility_status": compatibility_status,
        "is_upgrade": is_upgrade,
        "price_selection": "available_first" if prefer_available else "lowest_price",
    }


ROOT = Path(__file__).parent
st.set_page_config(page_title="BuildWise AI", page_icon="🖥️", layout="wide")
st.title("BuildWise AI")
st.caption("Rule-based PC compatibility and budget recommendations · India · INR")
st.caption("Availability and prices are historical observations recorded from sellers. Local-market presence is checked against verified Indian retailer listings. Hardware compatibility is evaluated separately.")

components, prices, issues = load_and_validate(ROOT / "data")
col1, col2, col3 = st.columns(3)
col1.metric("Catalog records", len(components))
col2.metric("Price observations", len(prices))
col3.metric("Validation issues", len(issues))

if components.empty:
    st.info("The data templates are intentionally empty. Add source-verified component records before asking the app to recommend a build.")
if prices.empty:
    st.info("No verified INR prices have been added yet. The app will not invent prices or convert USD values into Indian retail prices.")

st.subheader("Data readiness")
st.write("**Components:** specifications and provenance are stored separately from price observations.")
st.write("**Price history:** one component can have multiple dated seller observations.")
st.write("**Duplicate handling:** potential duplicates are flagged for review; records are never deleted automatically.")
st.write("**Compatibility:** missing facts will be treated as unknown, not as proof that parts are compatible.")

if issues:
    st.subheader("Validation report")
    st.warning("Review the issues below. No source records were changed or removed.")
    st.dataframe([{"Issue": item} for item in issues], use_container_width=True, hide_index=True)
else:
    st.success("CSV structure checks passed. This does not mean hardware compatibility has been verified.")

with st.expander("Required CSV columns"):
    st.markdown("**data/components.csv**: `component_id`, `category`, `brand`, `model`, `specs_json`, `source_name`, `source_url`, `source_license`, `identity_status`")
    st.markdown("**data/prices.csv**: `price_id`, `component_id`, `seller`, `price_inr`, `source_url`, `checked_at`, `availability`; optional `price_type`, `provenance` distinguish planning estimates from seller observations.")

st.subheader("Budget-based recommendation")
st.caption("Priced combinations are ranked by fewer documented incompatibilities, then fewer unknown compatibility checks, then lowest recorded price total. Local-market presence is checked against verified Indian retailer listings. Availability and prices are point-in-time observations and do not affect hardware compatibility.")
with st.form("budget_recommendation"):
    recommendation_scope = st.radio(
        "Recommendation type",
        ["Full PC build", "Upgrade (selected categories only)"],
        horizontal=True,
    )
    upgrade_categories = st.multiselect(
        "Categories to consider for upgrade (used only in upgrade mode)",
        sorted({category for layout in PURPOSE_LAYOUT.values() for category in layout}),
    )
    budget = st.number_input("Budget (INR)", min_value=0, step=1000, value=50000)
    purpose = st.selectbox("Purpose", ["study/office", "programming", "gaming", "content creation"])
    includes_peripherals = st.checkbox("Budget includes peripherals")
    submitted = st.form_submit_button("Generate recommendation")

if submitted:
    selected_categories = (
        upgrade_categories
        if recommendation_scope == "Upgrade (selected categories only)"
        else None
    )
    selected, warnings, summary = build_recommendation(
        components,
        prices,
        int(budget),
        purpose,
        includes_peripherals,
        selected_categories,
    )
    st.write(f"**Requested budget:** {budget:,.0f} INR")
    st.write(f"**Selected purpose:** {purpose}")
    if selected:
        total_price = summary["total_price"]
        remaining = summary["remaining_budget"]
        if summary["is_upgrade"]:
            st.write("**Recommendation status:** Upgrade options for selected categories only")
        elif summary["build_status"] == "complete":
            st.write(            "**Recommendation status:** Complete PC build recommendation — all required categories are included")
        else:
            st.write(
                "**Recommendation status:** Partial PC build — missing required categories: "
                + ", ".join(summary["missing_categories"])
            )
        compatibility_label = {
            "compatible": "Compatible",
            "incompatible": "Incompatible",
            "unknown": "Unknown — at least one required check is missing or inconclusive",
        }[summary["compatibility_status"]]
        st.write(f"**Overall compatibility:** {compatibility_label}")
        st.caption(
            "Selection uses the lowest recorded price per component regardless of availability, age, "
            "or estimate status; equal-price seller observations are preferred over estimates. "
            "Prices and retailer listings are historical observations, not live stock confirmations."
        )
        total_label = (
            "Budget total (includes planning estimate)"
            if summary["includes_estimates"] else "Recorded-price total"
        )
        st.write(f"**{total_label}:** {total_price:,.0f} INR")
        st.write(f"**Remaining budget:** {remaining:,.0f} INR")
        st.caption("The total includes valid seller observations and any explicitly labeled user planning estimates. Estimates are not verified market offers. Indian-market presence indicates verified local retailer evidence. Stock, current pricing, and delivery must be confirmed with the seller.")
        display_df = pd.DataFrame(selected)
        display_df["availability_freshness"] = display_df[
            "availability_freshness"
        ].map({
            "recent": f"Within {DEFAULT_AVAILABILITY_FRESHNESS_DAYS}-day window",
            "stale": "Potentially stale",
            "unknown": "Check date unavailable",
        })
        display_df["indian_market_presence"] = display_df[
            "indian_market_presence"
        ].map({
            "verified_indian_listing": "Verified Indian listing",
            "no_verified_indian_listing": "No verified Indian listing",
            "unknown": "Unknown",
        }).fillna(display_df.get("indian_market_presence", "Unknown"))
        display_df = display_df[["category", "brand", "model", "price_inr", "price_basis", "provenance", "seller", "checked_at", "indian_market_presence", "availability", "availability_freshness", "observation_age_days", "compatibility", "compatibility_reason", "source_url", "reason"]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No recommendation fits the current budget using the recorded prices. Review the warnings for missing categories or the minimum recorded total.")

    if warnings:
        st.subheader("Warnings")
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("No immediate warnings were raised for the selected candidate set.")
    st.caption("Recommendations are limited to the recorded catalog and price observations. Missing price data or incomplete compatibility information is reported instead of inferred.")

st.caption("Recommendations use recorded quotes and documented compatibility signals only. Missing price or specification data is not inferred.")
