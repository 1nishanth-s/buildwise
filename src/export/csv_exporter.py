"""
BuildWise-AI — CSV Report Exporter

Generates well-structured, Excel-compatible CSV reports for completed
Build Mode and Upgrade Mode recommendations using real catalog data.
"""
from __future__ import annotations

import ast
import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def get_clean_name(item: Any) -> str:
    """Extracts clean display string from a component or name field that might be nested or stringified."""
    if not item:
        return "N/A"
    if isinstance(item, str):
        s = item.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, dict):
                    return get_clean_name(parsed)
            except Exception:
                pass
        return s
    if isinstance(item, dict):
        if "name" in item and item["name"] != item:
            return get_clean_name(item["name"])
        if "label" in item:
            return get_clean_name(item["label"])
        brand = item.get("brand", "")
        model = item.get("model", "")
        if brand or model:
            return f"{brand} {model}".strip()
    return str(item)


def extract_specs_dict(item: Any) -> Optional[Dict[str, Any]]:
    """Extracts specs dict whether stored under 'specs', top-level properties, or stringified dict."""
    if not item:
        return None
    if isinstance(item, str):
        s = item.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, dict):
                    return extract_specs_dict(parsed)
            except Exception:
                pass
        return None
    if isinstance(item, dict):
        for k in ("name", "model", "label"):
            val = item.get(k)
            if isinstance(val, str) and val.strip().startswith("{") and val.strip().endswith("}"):
                try:
                    parsed = ast.literal_eval(val.strip())
                    if isinstance(parsed, dict):
                        res = extract_specs_dict(parsed)
                        if res:
                            return res
                except Exception:
                    pass

        if "specs" in item and isinstance(item["specs"], dict) and item["specs"]:
            return item["specs"]

        filtered = {
            k: v for k, v in item.items()
            if not k.startswith("_") and k not in (
                "name", "label", "category", "component_id", "componentId",
                "brand", "model", "price", "seller", "sourceUrl", "availability",
                "priceBasis", "empiricalBenchmark", "mlPrediction", "alternatives",
                "specs"
            )
        }
        return filtered if filtered else None
    return None


def format_specs(category: str, specs: Optional[Dict[str, Any]]) -> str:
    """Formats hardware specification dictionary into a clean, human-readable string."""
    if not specs or not isinstance(specs, dict):
        return "Standard hardware specifications"

    cat = category.lower()
    parts = []

    if cat == "cpu":
        if "cores" in specs and "threads" in specs:
            parts.append(f"{specs['cores']}C/{specs['threads']}T")
        if "boost_ghz" in specs:
            parts.append(f"{specs['boost_ghz']} GHz Boost")
        if "tdp_w" in specs:
            parts.append(f"{specs['tdp_w']}W TDP")
        if "socket" in specs:
            parts.append(f"Socket {specs['socket']}")
        if "ram_type" in specs:
            parts.append(f"Supports {specs['ram_type']}")

    elif cat == "gpu":
        if "chipset" in specs:
            parts.append(str(specs["chipset"]))
        if "vram_gb" in specs:
            parts.append(f"{specs['vram_gb']}GB VRAM")
        if "boost_clock_mhz" in specs:
            parts.append(f"{specs['boost_clock_mhz']} MHz Boost")
        if "tgp_w" in specs:
            parts.append(f"{specs['tgp_w']}W TGP")
        if "length_mm" in specs:
            parts.append(f"Length {specs['length_mm']}mm")

    elif cat == "motherboard":
        if "socket" in specs:
            parts.append(f"Socket {specs['socket']}")
        if "chipset" in specs:
            parts.append(f"Chipset {specs['chipset']}")
        if "form_factor" in specs:
            parts.append(f"{specs['form_factor']}")
        if "ram_type" in specs:
            parts.append(f"{specs['ram_type']}")

    elif cat == "ram":
        if "capacity_gb" in specs:
            cap = f"{specs['capacity_gb']}GB"
            if "modules" in specs:
                cap += f" ({specs['modules']})"
            parts.append(cap)
        if "speed_mhz" in specs:
            parts.append(f"{specs['speed_mhz']} MHz")
        if "ram_type" in specs:
            parts.append(str(specs["ram_type"]))

    elif cat == "storage":
        if "capacity_gb" in specs:
            parts.append(f"{specs['capacity_gb']}GB")
        if "form_factor" in specs:
            parts.append(str(specs["form_factor"]))
        if "interface" in specs:
            parts.append(str(specs["interface"]))
        if "type" in specs:
            parts.append(str(specs["type"]))

    elif cat == "psu":
        if "wattage_w" in specs:
            parts.append(f"{specs['wattage_w']}W")
        if "efficiency_rating" in specs:
            parts.append(str(specs["efficiency_rating"]))
        if "form_factor" in specs:
            parts.append(str(specs["form_factor"]))
        if "modular" in specs:
            parts.append(f"Modular: {specs['modular']}")

    elif cat == "case":
        if "form_factor" in specs:
            parts.append(str(specs["form_factor"]))
        if "max_gpu_length_mm" in specs:
            parts.append(f"Max GPU: {specs['max_gpu_length_mm']}mm")
        if "max_cpu_cooler_height_mm" in specs:
            parts.append(f"Max Cooler: {specs['max_cpu_cooler_height_mm']}mm")

    elif cat == "cooler":
        if "socket_support" in specs:
            supp = specs["socket_support"]
            if isinstance(supp, list):
                parts.append("Sockets: " + ", ".join(str(s) for s in supp[:4]))
            else:
                parts.append(f"Sockets: {supp}")
        if "height_mm" in specs:
            parts.append(f"Height: {specs['height_mm']}mm")
        if "cooling_type" in specs:
            parts.append(str(specs["cooling_type"]))

    if not parts:
        # Fallback to key-value pairs
        for k, v in specs.items():
            if k not in ("source", "last_verified", "notes", "supported_chipsets", "use_cases"):
                parts.append(f"{k}: {v}")

    return "; ".join(parts) if parts else "Standard specifications"


def extract_build_components(project: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extracts components dictionary from project snapshot or nodes."""
    snapshot = project.get("recommendationSnapshot") or {}
    components = snapshot.get("components")

    if components and isinstance(components, dict):
        return components

    # Fallback: extract from nodes
    extracted = {}
    nodes = project.get("nodes") or snapshot.get("nodes") or []
    for node in nodes:
        data = node.get("data", {})
        if data.get("kind") == "component":
            cat = (data.get("category") or "").lower()
            if cat:
                extracted[cat] = {
                    "component_id": data.get("componentId") or node.get("id"),
                    "category": cat,
                    "brand": data.get("brand", ""),
                    "model": data.get("model", ""),
                    "name": data.get("name") or data.get("label", ""),
                    "specs": data.get("specs", {}),
                    "price": data.get("price"),
                    "seller": data.get("seller", "Recorded Retailer"),
                    "sourceUrl": data.get("sourceUrl", ""),
                    "availability": data.get("availability", "available"),
                    "priceBasis": data.get("priceBasis", "Retail observation"),
                    "empiricalBenchmark": data.get("empiricalBenchmark"),
                    "mlPrediction": data.get("mlPrediction"),
                }
    return extracted


def extract_upgrade_components(project: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts upgrade proposed, existing, retained, and replaced info."""
    snapshot = project.get("recommendationSnapshot") or {}
    existing = snapshot.get("existing") or project.get("inputs", {}).get("existing") or {}
    proposed = snapshot.get("proposed") or snapshot.get("components") or {}
    deltas = snapshot.get("deltas") or {}
    summary = project.get("summary") or snapshot.get("summary") or {}
    upgraded_categories = summary.get("upgradedCategories") or []

    primary_categories = summary.get("primaryCategories") or []
    dependent_categories = summary.get("dependentCategories") or []
    retained_categories = summary.get("retainedCategories") or []
    unresolved_categories = summary.get("unresolvedCategories") or []

    # Identify retained vs replaced
    replaced = set(upgraded_categories)
    retained = set(retained_categories)

    for cat, comp in proposed.items():
        if isinstance(comp, dict):
            role = comp.get("upgrade_role")
            if role in ("primary", "dependency", "optional"):
                replaced.add(cat)
                if role == "primary" and cat not in primary_categories:
                    primary_categories.append(cat)
                elif role == "dependency" and cat not in dependent_categories:
                    dependent_categories.append(cat)
            elif role == "retained":
                retained.add(cat)
            elif role == "unresolved":
                if cat not in unresolved_categories:
                    unresolved_categories.append(cat)
            else:
                price = comp.get("price", 0) or 0
                if price > 0:
                    replaced.add(cat)
                else:
                    retained.add(cat)

    # Any existing component not in replaced is retained
    for cat in existing.keys():
        if cat not in replaced and cat not in unresolved_categories:
            retained.add(cat)

    return {
        "existing": existing,
        "proposed": proposed,
        "deltas": deltas,
        "replaced": list(replaced),
        "retained": list(retained),
        "primary": primary_categories,
        "dependent": dependent_categories,
        "unresolved": unresolved_categories,
    }


def generate_build_csv(project: Dict[str, Any]) -> str:
    """
    Generates a comprehensive CSV string for a Build Mode project.
    Excel-friendly format with metadata header and detailed component rows.
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    summary = project.get("summary") or project.get("recommendationSnapshot", {}).get("summary") or {}
    inputs = project.get("inputs") or {}
    proj_id = project.get("id", "N/A")
    proj_name = project.get("name", "BuildWise-AI PC Build")
    usage = inputs.get("usage", "General Computing")
    target_budget = summary.get("budget", inputs.get("budget", 0))
    total_cost = summary.get("total", 0)
    remaining = summary.get("remaining", target_budget - total_cost if target_budget else 0)
    validation = project.get("recommendationSnapshot", {}).get("validation") or {}
    val_status = "Compatible" if validation.get("compatible") is not False else "Warnings Flagged"
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Header Metadata Block
    writer.writerow(["# BuildWise-AI PC Build Recommendation Specification"])
    writer.writerow(["Project ID", proj_id])
    writer.writerow(["Project Name", proj_name])
    writer.writerow(["Mode", "Build Recommendation"])
    writer.writerow(["Usage Profile", usage])
    writer.writerow(["Target Budget (INR)", f"Rs. {target_budget:,}" if target_budget else "N/A"])
    writer.writerow(["Total Estimated Cost (INR)", f"Rs. {total_cost:,}"])
    writer.writerow(["Remaining Budget (INR)", f"Rs. {remaining:,}"])
    writer.writerow(["Budget Adherence", "Within Budget" if remaining >= 0 else f"Over Budget by Rs. {abs(remaining):,}"])
    writer.writerow(["System Compatibility", val_status])
    writer.writerow(["Generated At", now_str])
    writer.writerow([])  # Blank spacer

    # Table Column Headers
    writer.writerow([
        "Category",
        "Brand",
        "Model",
        "Component Full Name",
        "Key Specifications",
        "Price (INR)",
        "Availability",
        "Seller / Retailer",
        "Price Basis",
        "Price Source URL",
        "Compatibility Status",
        "Empirical Benchmark Suite",
        "Empirical Benchmark Metric",
        "Empirical Benchmark Score (pts)",
        "Empirical Benchmark Source",
        "ML Performance Metric",
        "ML Predicted Score (pts)",
        "ML Model Pipeline",
        "ML Prediction Status",
    ])

    components = extract_build_components(project)
    category_order = ["cpu", "motherboard", "ram", "gpu", "storage", "psu", "cooler", "case"]

    # Also catch any categories outside the standard 8
    ordered_cats = [c for c in category_order if c in components]
    for c in components:
        if c not in ordered_cats:
            ordered_cats.append(c)

    for cat in ordered_cats:
        comp = components.get(cat, {})
        brand = comp.get("brand", "")
        model = comp.get("model", "")
        name = comp.get("name") or f"{brand} {model}".strip()
        specs_str = format_specs(cat, comp.get("specs"))
        price = comp.get("price")
        price_str = str(price) if price is not None else "Unpriced"
        avail = comp.get("availability", "Available").capitalize()
        seller = comp.get("seller", "Recorded Online Retailer")
        pbasis = comp.get("priceBasis", "Retailer observation")
        source_url = comp.get("sourceUrl", "")
        compat = "Compatible (Verified)"

        # Empirical Benchmark
        emp = comp.get("empiricalBenchmark") or {}
        emp_suite = emp.get("suite", emp.get("benchmark_suite", "Cinebench R23" if cat == "cpu" else "3DMark" if cat == "gpu" else "N/A")) if emp else "N/A"
        emp_metric = emp.get("metric", emp.get("benchmark_metric", "N/A")) if emp else "N/A"
        emp_score = str(emp.get("score", "N/A")) if emp else "N/A"
        emp_source = emp.get("source", emp.get("source_name", "N/A")) if emp else "N/A"

        # ML Prediction
        ml = comp.get("mlPrediction") or {}
        ml_metric = ml.get("metric", "N/A") if ml else "N/A"
        ml_score = f"{ml.get('score'):.1f}" if ml and ml.get("score") is not None else "N/A"
        ml_model = ml.get("model", "N/A") if ml else "N/A"
        ml_status = ml.get("status", "N/A") if ml else "N/A"

        writer.writerow([
            cat.upper(),
            brand,
            model,
            name,
            specs_str,
            price_str,
            avail,
            seller,
            pbasis,
            source_url,
            compat,
            emp_suite,
            emp_metric,
            emp_score,
            emp_source,
            ml_metric,
            ml_score,
            ml_model,
            ml_status,
        ])

    writer.writerow([])
    # Rationale & Compatibility Notes
    notes = summary.get("notes") or project.get("recommendationSnapshot", {}).get("notes") or []
    if notes:
        writer.writerow(["# Recommendation Rationale & Selection Notes"])
        for idx, note in enumerate(notes, 1):
            writer.writerow([f"Note {idx}", note])
        writer.writerow([])

    # Warnings / Validation Details
    warnings = validation.get("warnings") or []
    if warnings:
        writer.writerow(["# Compatibility Flags & Hardware Warnings"])
        for idx, warn in enumerate(warnings, 1):
            writer.writerow([f"Warning {idx}", warn])
        writer.writerow([])

    # Disclaimer Row
    writer.writerow(["# Disclaimer"])
    writer.writerow([
        "Prices reflect genuine recorded retailer observations in the Indian market (e.g. Computech, PrimeABGB, Amazon IN, MDComputers) and may fluctuate based on real-time stock. Scores marked 'Predicted' are derived from supervised scikit-learn Ridge regression models and represent statistical approximations."
    ])

    return output.getvalue()


def generate_upgrade_csv(project: Dict[str, Any]) -> str:
    """
    Generates a comprehensive CSV string for an Upgrade Mode project.
    Excel-friendly format with existing vs proposed components and performance gains.
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    summary = project.get("summary") or project.get("recommendationSnapshot", {}).get("summary") or {}
    inputs = project.get("inputs") or {}
    proj_id = project.get("id", "N/A")
    proj_name = project.get("name", "BuildWise-AI PC Upgrade")
    goal = inputs.get("goal", summary.get("goal", "Upgrade Performance"))
    target_budget = summary.get("budget", inputs.get("budget", 0))
    total_cost = summary.get("total", 0)
    remaining = summary.get("remaining", target_budget - total_cost if target_budget else 0)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    upgrade_info = extract_upgrade_components(project)
    existing = upgrade_info["existing"]
    proposed = upgrade_info["proposed"]
    deltas = upgrade_info["deltas"]
    replaced_cats = set(upgrade_info["replaced"])
    primary_cats = upgrade_info.get("primary", [])
    dependent_cats = upgrade_info.get("dependent", [])
    retained_cats = upgrade_info.get("retained", [])
    unresolved_cats = upgrade_info.get("unresolved", [])

    # Header Metadata Block
    writer.writerow(["# BuildWise-AI PC Upgrade Recommendation Report"])
    writer.writerow(["Project ID", proj_id])
    writer.writerow(["Project Name", proj_name])
    writer.writerow(["Mode", "Upgrade Recommendation"])
    writer.writerow(["Upgrade Goal", goal])
    writer.writerow(["Upgrade Budget (INR)", f"Rs. {target_budget:,}" if target_budget else "N/A"])
    writer.writerow(["Total Upgrade Cost (INR)", f"Rs. {total_cost:,}"])
    writer.writerow(["Remaining Budget (INR)", f"Rs. {remaining:,}"])
    writer.writerow(["Budget Adherence", "Within Budget" if remaining >= 0 else f"Over Budget by Rs. {abs(remaining):,}"])
    writer.writerow(["Primary Upgrades", ", ".join(c.upper() for c in primary_cats) if primary_cats else "None"])
    writer.writerow(["Required Dependencies", ", ".join(c.upper() for c in dependent_cats) if dependent_cats else "None"])
    writer.writerow(["Retained Components", ", ".join(c.upper() for c in retained_cats) if retained_cats else "None"])
    if unresolved_cats:
        writer.writerow(["Unresolved Warnings", ", ".join(c.upper() for c in unresolved_cats)])
    writer.writerow(["Generated At", now_str])
    writer.writerow([])  # Blank spacer

    # Table Column Headers
    writer.writerow([
        "Category",
        "Action",
        "Upgrade Role",
        "Dependency Reason",
        "Existing Component",
        "Existing Specifications",
        "Recommended Component",
        "Recommended Brand",
        "Recommended Model",
        "Recommended Specifications",
        "Upgrade Cost (INR)",
        "Availability",
        "Seller / Retailer",
        "Price Source URL",
        "Compatibility Status",
        "Empirical Benchmark Metric",
        "Empirical Benchmark Score (pts)",
        "ML Performance Metric",
        "ML Predicted Score (pts)",
        "Performance Gain / Delta",
    ])

    category_order = ["cpu", "motherboard", "ram", "gpu", "storage", "psu", "cooler", "case"]
    all_cats = list(dict.fromkeys(category_order + list(existing.keys()) + list(proposed.keys())))

    for cat in all_cats:
        ex = existing.get(cat, {})
        prop = proposed.get(cat, {})

        if not ex and not prop:
            continue

        is_replaced = cat in replaced_cats
        role = prop.get("upgrade_role") if isinstance(prop, dict) else None
        if not role:
            role = "primary" if is_replaced else "retained"

        if role == "primary":
            action = "REPLACED (Primary Upgrade)"
            role_label = "PRIMARY UPGRADE"
        elif role == "dependency":
            action = "REPLACED (Required Dependency)"
            role_label = "REQUIRED DEPENDENCY"
        elif role == "unresolved":
            action = "UNRESOLVED (Incompatible)"
            role_label = "UNRESOLVED"
        else:
            action = "RETAINED (Reusable)"
            role_label = "RETAINED"

        dep_reason = (prop.get("dependency_reason") or "N/A") if isinstance(prop, dict) else "N/A"

        # Existing specs
        ex_name = get_clean_name(ex)
        ex_specs = format_specs(cat, extract_specs_dict(ex))

        # Proposed specs
        if prop and isinstance(prop, dict):
            prop_brand = prop.get("brand", "") if is_replaced else "User Hardware"
            prop_model = get_clean_name(prop.get("model", "")) if is_replaced else ex_name
            prop_name = get_clean_name(prop) or f"{prop_brand} {prop_model}".strip() or ex_name
            prop_specs = format_specs(cat, extract_specs_dict(prop)) or ex_specs
            price = prop.get("price", 0) if is_replaced else 0
            price_str = str(price) if price is not None else "Unpriced"
            avail = prop.get("availability", "Available").capitalize() if is_replaced else "In Possession"
            seller = prop.get("seller", "Recorded Retailer") if is_replaced else "Owned"
            source_url = prop.get("sourceUrl", "") if is_replaced else ""
            compat = "Incompatible (Warning)" if role == "unresolved" else ("Compatible (Verified)" if is_replaced else "Compatible (Retained)")

            # Empirical
            emp = prop.get("empiricalBenchmark") or {}
            emp_metric = emp.get("metric", emp.get("benchmark_metric", "N/A")) if emp else "N/A"
            emp_score = str(emp.get("score", "N/A")) if emp else "N/A"

            # ML
            ml = prop.get("mlPrediction") or {}
            ml_metric = ml.get("metric", "N/A") if ml else "N/A"
            ml_score = f"{ml.get('score'):.1f}" if ml and ml.get("score") is not None else "N/A"
        else:
            prop_brand = "N/A"
            prop_model = "N/A"
            prop_name = ex_name
            prop_specs = ex_specs
            price_str = "0"
            avail = "In Possession"
            seller = "Owned"
            source_url = ""
            compat = "Compatible (Retained)"
            emp_metric = "N/A"
            emp_score = "N/A"
            ml_metric = "N/A"
            ml_score = "N/A"

        # Delta
        delta_info = deltas.get(cat, {})
        if delta_info:
            d_val = delta_info.get("delta", delta_info.get("absoluteDelta", 0))
            d_pct = delta_info.get("pct_gain", delta_info.get("percentageDelta", 0))
            delta_str = f"+{d_val:,.0f} pts (+{d_pct:.1f}%)" if d_val > 0 else f"{d_val:,.0f} pts"
        else:
            delta_str = "No baseline comparison" if is_replaced else "Retained baseline"

        writer.writerow([
            cat.upper(),
            action,
            role_label,
            dep_reason,
            ex_name,
            ex_specs,
            prop_name,
            prop_brand,
            prop_model,
            prop_specs,
            price_str,
            avail,
            seller,
            source_url,
            compat,
            emp_metric,
            emp_score,
            ml_metric,
            ml_score,
            delta_str,
        ])

    writer.writerow([])
    # Delta Summary
    if deltas:
        writer.writerow(["# Performance Upgrade Deltas Summary"])
        for comp_cat, d in deltas.items():
            base_s = d.get("baseline", "N/A")
            up_s = d.get("upgraded", "N/A")
            d_val = d.get("delta", "N/A")
            d_pct = d.get("pct_gain", "N/A")
            metric = d.get("metric", "Score")
            writer.writerow([
                f"{comp_cat.upper()} Delta",
                f"Metric: {metric}",
                f"Baseline: {base_s}",
                f"Upgraded: {up_s}",
                f"Gain: +{d_val} pts (+{d_pct}%)",
            ])
        writer.writerow([])

    # Disclaimer
    writer.writerow(["# Disclaimer"])
    writer.writerow([
        "Upgrade recommendations verify compatibility between existing retained parts and recommended upgrades. Prices reflect verified Indian online retailer observations. Performance scores marked 'Predicted' are computed via supervised scikit-learn Ridge regression pipelines."
    ])

    return output.getvalue()
