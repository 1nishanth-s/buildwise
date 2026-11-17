"""
BuildWise-AI — Catalog Data Access Layer

Loads and indexes production CSV datasets (components, prices, benchmarks)
without any Streamlit or UI dependencies for pure API and recommendation usage.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger("catalog_data")

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"

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


def parse_specs(raw_value: Any) -> Dict[str, Any]:
    """Safely decodes JSON specifications from catalog strings or dicts."""
    if isinstance(raw_value, dict):
        return raw_value
    if not raw_value or pd.isna(raw_value):
        return {}
    try:
        return json.loads(str(raw_value))
    except (json.JSONDecodeError, TypeError):
        return {}


def price_to_int(raw_value: Any) -> Optional[int]:
    """Converts price values safely to integer INR."""
    if pd.isna(raw_value) or raw_value is None or raw_value == "":
        return None
    try:
        val = float(raw_value)
        if pd.isna(val) or val <= 0:
            return None
        return int(round(val))
    except (ValueError, TypeError):
        return None


def observation_freshness(
    checked_at_str: Any, freshness_days: int = DEFAULT_AVAILABILITY_FRESHNESS_DAYS, now: Optional[datetime] = None
) -> Tuple[str, Optional[int]]:
    """Evaluates observation date freshness."""
    if not checked_at_str or pd.isna(checked_at_str):
        return "unknown", None
    val = str(checked_at_str).strip()
    if not val:
        return "unknown", None
    try:
        dt = datetime.fromisoformat(val)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        cur = now or datetime.now(timezone.utc)
        age = (cur - dt).days
        if age < 0:
            return "recent", 0
        status = "recent" if age <= freshness_days else "stale"
        return status, age
    except Exception:
        return "unknown", None


def build_prices_lookup(df_prices: pd.DataFrame, freshness_days: int = DEFAULT_AVAILABILITY_FRESHNESS_DAYS) -> Dict[str, List[Dict[str, Any]]]:
    """Builds a lookup mapping component_id -> list of price observations sorted by price."""
    lookup: Dict[str, List[Dict[str, Any]]] = {}
    now = datetime.now(timezone.utc)
    for _, row in df_prices.iterrows():
        component_id = str(row.get("component_id", "")).strip()
        if not component_id:
            continue
        price_val = price_to_int(row.get("price_inr"))
        if price_val is None:
            continue
        freshness, age_days = observation_freshness(row.get("checked_at"), freshness_days, now=now)
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


def build_benchmarks_lookup(df_benchmarks: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Builds a lookup mapping component_id -> benchmark information."""
    lookup: Dict[str, Dict[str, Any]] = {}
    for _, row in df_benchmarks.iterrows():
        cid = str(row.get("component_id", "")).strip()
        if not cid:
            continue
        lookup[cid] = {
            "component_id": cid,
            "benchmark_source": str(row.get("benchmark_source", "")).strip(),
            "cinebench_r23_single": row.get("cinebench_r23_single"),
            "cinebench_r23_multi": row.get("cinebench_r23_multi"),
            "timespy_graphics": row.get("timespy_graphics"),
            "recorded_at": str(row.get("recorded_at", "")).strip(),
        }
    return lookup


def choose_best_price(
    component_id: str, prices_lookup: Dict[str, List[Dict[str, Any]]], prefer_available: bool = True
) -> Optional[Dict[str, Any]]:
    """Picks the best price entry for a component."""
    entries = prices_lookup.get(component_id, [])
    if not entries:
        return None
    if not prefer_available:
        return min(entries, key=lambda item: (item["price_inr"], item["price_type"] == "planning_estimate"))

    def availability_priority(item: Dict[str, Any]) -> int:
        if item["price_type"] == "planning_estimate":
            return 4
        if item["availability"] == "available" and item["freshness"] == "recent":
            return 0
        if item["availability"] == "unknown" or item["freshness"] == "unknown":
            return 1
        if item["availability"] == "available":
            return 2
        return 3

    return min(entries, key=lambda item: (availability_priority(item), item["price_inr"]))


class CatalogService:
    """Singleton service to access production catalog DataFrames and lookups."""
    _instance: Optional[CatalogService] = None

    def __init__(self):
        self.components_path = DATA_DIR / "components.csv"
        self.prices_path = DATA_DIR / "prices.csv"
        self.benchmarks_path = DATA_DIR / "benchmarks.csv"

        self.df_components = pd.read_csv(self.components_path)
        self.df_prices = pd.read_csv(self.prices_path)
        self.df_benchmarks = pd.read_csv(self.benchmarks_path)

        self.prices_lookup = build_prices_lookup(self.df_prices)
        self.benchmarks_lookup = build_benchmarks_lookup(self.df_benchmarks)
        logger.info(
            "CatalogService loaded: %d components, %d prices, %d benchmarks",
            len(self.df_components), len(self.df_prices), len(self.df_benchmarks)
        )

    @classmethod
    def get_instance(cls) -> CatalogService:
        if cls._instance is None:
            cls._instance = CatalogService()
        return cls._instance

    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        rows = self.df_components[self.df_components["component_id"] == component_id]
        if rows.empty:
            return None
        return rows.iloc[0].to_dict()

    def get_components_by_category(self, category: str) -> List[Dict[str, Any]]:
        sub = self.df_components[self.df_components["category"].str.casefold() == category.casefold()]
        return sub.to_dict(orient="records")
