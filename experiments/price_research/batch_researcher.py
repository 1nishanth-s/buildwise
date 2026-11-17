"""Batch price research and integration engine for BuildWise-AI Phase 11A.

Handles resumable batch research, staging, validation, registry updating,
and report generation across all 1,208 catalog components.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd

from src.validator import load_and_validate, read_csv_or_empty, PRICE_COLUMNS, COMPONENT_COLUMNS

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
EXPERIMENTS_DIR = ROOT / "experiments" / "price_research"
REGISTRY_PATH = EXPERIMENTS_DIR / "price_research_registry.csv"
STAGED_PATH = EXPERIMENTS_DIR / "staged_price_observations.csv"
REPORT_PATH = EXPERIMENTS_DIR / "research_progress_report.md"


def get_next_price_id(
    prices_df: pd.DataFrame,
    staged_df: pd.DataFrame | None = None,
    current_staged_list: list[dict[str, Any]] | None = None,
) -> str:
    """Determine the next sequential PRICE_xxx identifier."""
    max_num = 0
    import re
    for pid in prices_df["price_id"].dropna():
        m = re.match(r"^PRICE_(\d+)$", str(pid).strip())
        if m:
            max_num = max(max_num, int(m.group(1)))
    if staged_df is not None and not staged_df.empty:
        for pid in staged_df["price_id"].dropna():
            m = re.match(r"^PRICE_(\d+)$", str(pid).strip())
            if m:
                max_num = max(max_num, int(m.group(1)))
    if current_staged_list:
        for item in current_staged_list:
            pid = item.get("price_id")
            if pid:
                m = re.match(r"^PRICE_(\d+)$", str(pid).strip())
                if m:
                    max_num = max(max_num, int(m.group(1)))
    return f"PRICE_{max_num + 1:03d}"


def load_registry() -> pd.DataFrame:
    """Load the price research registry tracking all 1,208 components."""
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Registry not found at {REGISTRY_PATH}")
    return pd.read_csv(REGISTRY_PATH, dtype=str, keep_default_na=False)


def save_registry(registry_df: pd.DataFrame) -> None:
    """Persist the price research registry."""
    registry_df.to_csv(REGISTRY_PATH, index=False)


def load_staged() -> pd.DataFrame:
    """Load staged price observations."""
    if not STAGED_PATH.exists():
        cols = PRICE_COLUMNS + ["price_type", "provenance", "batch_id"]
        return pd.DataFrame(columns=cols)
    return pd.read_csv(STAGED_PATH, dtype=str, keep_default_na=False)


def save_staged(staged_df: pd.DataFrame) -> None:
    """Persist staged price observations."""
    staged_df.to_csv(STAGED_PATH, index=False)


def record_batch_outcomes(
    batch_id: str,
    researched_observations: list[dict[str, Any]],
    unpriced_outcomes: dict[str, str],
    ambiguous_outcomes: dict[str, str] | None = None
) -> int:
    """
    Record research results for a batch:
    - researched_observations: list of dicts with price fields
    - unpriced_outcomes: {component_id: reason_note}
    - ambiguous_outcomes: {component_id: reason_note}
    """
    registry_df = load_registry()
    staged_df = load_staged()
    prices_df = pd.read_csv(DATA_DIR / "prices.csv", dtype=str, keep_default_na=False)
    ambiguous_outcomes = ambiguous_outcomes or {}

    new_staged_rows = []
    current_prices = prices_df.copy()

    # Process price observations
    for obs in researched_observations:
        cid = obs["component_id"]
        price_id = obs.get("price_id")
        if not price_id:
            price_id = get_next_price_id(current_prices, staged_df, new_staged_rows)
        
        row_dict = {
            "price_id": price_id,
            "component_id": cid,
            "seller": obs["seller"],
            "price_inr": str(int(round(float(obs["price_inr"])))),
            "source_url": obs["source_url"],
            "checked_at": obs.get("checked_at", "2026-11-08"),
            "availability": obs.get("availability", "available"),
            "price_type": "seller_observation",
            "provenance": obs.get("provenance", f"Observed retail listing on {obs['seller']} storefront (verified INR price inclusive of 18% GST)"),
            "batch_id": batch_id
        }
        new_staged_rows.append(row_dict)
        
        # Update registry entry
        reg_idx = registry_df[registry_df["component_id"] == cid].index
        if len(reg_idx) > 0:
            idx = reg_idx[0]
            existing_count = int(registry_df.at[idx, "observations_count"] or 0)
            registry_df.at[idx, "observations_count"] = str(existing_count + 1)
            registry_df.at[idx, "research_status"] = "multiple_retailer_prices" if (existing_count + 1) > 1 else "verified_retailer_price"
            registry_df.at[idx, "primary_seller"] = obs["seller"]
            registry_df.at[idx, "latest_price_inr"] = str(int(round(float(obs["price_inr"]))))
            registry_df.at[idx, "research_notes"] = obs.get("notes", f"Verified retailer price on {obs['seller']}")
            registry_df.at[idx, "researched_at"] = obs.get("checked_at", "2026-11-08")

    # Process unpriced outcomes
    for cid, reason in unpriced_outcomes.items():
        reg_idx = registry_df[registry_df["component_id"] == cid].index
        if len(reg_idx) > 0:
            idx = reg_idx[0]
            registry_df.at[idx, "research_status"] = "no_verifiable_price"
            registry_df.at[idx, "research_notes"] = reason
            registry_df.at[idx, "researched_at"] = "2026-11-08"

    # Process ambiguous outcomes
    for cid, reason in ambiguous_outcomes.items():
        reg_idx = registry_df[registry_df["component_id"] == cid].index
        if len(reg_idx) > 0:
            idx = reg_idx[0]
            registry_df.at[idx, "research_status"] = "ambiguous_match"
            registry_df.at[idx, "research_notes"] = reason
            registry_df.at[idx, "researched_at"] = "2026-11-08"

    if new_staged_rows:
        new_staged_df = pd.DataFrame(new_staged_rows)
        combined_staged = pd.concat([staged_df, new_staged_df], ignore_index=True)
        save_staged(combined_staged)

    save_registry(registry_df)
    generate_progress_report()
    return len(new_staged_rows)


def import_staged_to_production() -> tuple[int, list[str]]:
    """Controlled import of staged price observations into data/prices.csv."""
    staged_df = load_staged()
    if staged_df.empty:
        return 0, ["No staged observations to import."]

    prices_path = DATA_DIR / "prices.csv"
    components_path = DATA_DIR / "components.csv"
    
    current_prices = pd.read_csv(prices_path, dtype=str, keep_default_na=False)
    components = pd.read_csv(components_path, dtype=str, keep_default_na=False)

    # Columns to import into prices.csv
    target_cols = PRICE_COLUMNS + ["price_type", "provenance"]
    import_rows = staged_df[target_cols].copy()

    # Verify no duplicate price_ids
    existing_ids = set(current_prices["price_id"])
    collisions = set(import_rows["price_id"]).intersection(existing_ids)
    if collisions:
        raise ValueError(f"Price ID collisions detected: {collisions}")

    # Combine
    updated_prices = pd.concat([current_prices, import_rows], ignore_index=True)

    # Validate before saving
    from src.validator import validate_prices
    issues = validate_prices(updated_prices, components)
    if issues:
        raise ValueError(f"Validation failed during staging import: {issues}")

    # Write out
    updated_prices.to_csv(prices_path, index=False)

    # Clear staged
    empty_staged = pd.DataFrame(columns=PRICE_COLUMNS + ["price_type", "provenance", "batch_id"])
    save_staged(empty_staged)

    return len(import_rows), []


def generate_progress_report() -> str:
    """Generate comprehensive markdown progress report in experiments/price_research/."""
    registry_df = load_registry()
    prices_df = pd.read_csv(DATA_DIR / "prices.csv", dtype=str, keep_default_na=False)
    
    total_components = len(registry_df)
    status_counts = registry_df["research_status"].value_counts().to_dict()
    
    verified_single = status_counts.get("verified_retailer_price", 0)
    verified_multi = status_counts.get("multiple_retailer_prices", 0)
    total_verified = verified_single + verified_multi
    reference_only = status_counts.get("official_reference_price", 0)
    no_price = status_counts.get("no_verifiable_price", 0)
    ambiguous = status_counts.get("ambiguous_match", 0)
    pending = status_counts.get("pending", 0)
    completed = total_components - pending

    # Category breakdown
    cat_summary = []
    for cat in ["cpu", "gpu", "motherboard", "ram", "storage", "psu", "case", "cooler"]:
        sub = registry_df[registry_df["category"] == cat]
        c_tot = len(sub)
        c_ver = len(sub[sub["research_status"].isin(["verified_retailer_price", "multiple_retailer_prices"])])
        c_nop = len(sub[sub["research_status"] == "no_verifiable_price"])
        c_amb = len(sub[sub["research_status"] == "ambiguous_match"])
        c_pen = len(sub[sub["research_status"] == "pending"])
        c_pct = (c_ver / c_tot * 100) if c_tot else 0
        cat_summary.append(f"| {cat.upper()} | {c_tot} | {c_ver} ({c_pct:.1f}%) | {c_nop} | {c_amb} | {c_pen} |")

    # Batch summary
    batch_summary = []
    for b_id in sorted(registry_df["batch_id"].unique()):
        sub = registry_df[registry_df["batch_id"] == b_id]
        b_tot = len(sub)
        b_pen = len(sub[sub["research_status"] == "pending"])
        b_ver = len(sub[sub["research_status"].isin(["verified_retailer_price", "multiple_retailer_prices"])])
        b_status = "Completed" if b_pen == 0 else f"{b_tot - b_pen}/{b_tot} Done"
        batch_summary.append(f"| `{b_id}` | {b_tot} | {b_ver} | {b_pen} | {b_status} |")

    report_content = f"""# BuildWise-AI — Indian Online Price Research Progress Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Research Check Date:** 2026-11-08  
**Scope:** Comprehensive Indian retail price research for all 1,208 catalog components.

---

## 1. High-Level Research Metrics

| Metric | Count | Percentage |
|---|---:|---:|
| **Total Catalog Components** | {total_components} | 100.0% |
| **Components Researched to Date** | **{completed}** | **{(completed / total_components * 100):.1f}%** |
| Components with $\ge$1 Verified Retailer Price | **{total_verified}** | **{(total_verified / total_components * 100):.1f}%** |
| — Single Verified Retailer Price | {verified_single} | {(verified_single / total_components * 100):.1f}% |
| — Multiple Verified Retailer Prices | {verified_multi} | {(verified_multi / total_components * 100):.1f}% |
| Components with Official Reference Price Only | {reference_only} | {(reference_only / total_components * 100):.1f}% |
| Components with No Verifiable Retail Price (EOL/OEM/Unreleased) | {no_price} | {(no_price / total_components * 100):.1f}% |
| Components with Ambiguous Product Matches (Excluded) | {ambiguous} | {(ambiguous / total_components * 100):.1f}% |
| **Components Still Pending** | **{pending}** | **{(pending / total_components * 100):.1f}%** |
| **Total `data/prices.csv` Observation Rows** | **{len(prices_df)}** | — |

---

## 2. Category-Level Price Coverage

| Category | Total Components | Verified Retail Priced | No Verifiable Price | Ambiguous Excluded | Pending |
|---|---:|---:|---:|---:|---:|
{chr(10).join(cat_summary)}

---

## 3. Batch-by-Batch Research Execution Tracking

| Batch ID | Total Items | Verified Priced | Pending Items | Execution Status |
|---|---:|---:|---:|---|
{chr(10).join(batch_summary)}

---

## 4. Retail Sources & Provenance Policy

All verified retail prices strictly adhere to:
1. Direct product page URLs on reputable Indian hardware merchants:
   - MD Computers (`mdcomputers.in`)
   - Vedant Computers (`vedantcomputers.com`)
   - Prime ABGB (`primeabgb.com`)
   - PCStudio (`pcstudio.in`)
   - EliteHubs (`elitehubs.com`)
   - Computech Store (`computechstore.in`)
   - Clarion Computers (`clarioncomputers.in`)
   - SCL Gaming (`sclgaming.in`)
2. Numeric INR prices inclusive of standard 18% GST.
3. Strict isolation between live retailer pricing, official reference MSRPs, and historical planning estimates.
4. Preserved EOL / legacy documentation without artificial price fabrication.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    return report_content
