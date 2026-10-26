"""Conservative validation helpers for BuildWise AI CSV data.

Validation reports problems; it does not silently remove, merge, or rewrite rows.
"""
from __future__ import annotations

from datetime import datetime
import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd

COMPONENT_COLUMNS = [
    "component_id", "category", "brand", "model", "specs_json",
    "source_name", "source_url", "source_license", "identity_status",
]
PRICE_COLUMNS = [
    "price_id", "component_id", "seller", "price_inr", "source_url",
    "checked_at", "availability",
]
OPTIONAL_PRICE_COLUMNS = ["price_type", "provenance"]
CATEGORY_ALIASES = {
    "cpu": "CPU",
    "motherboard": "Motherboard",
    "ram": "RAM",
    "gpu": "GPU",
    "storage": "Storage",
    "psu": "PSU",
    "case": "Case",
    "cooler": "Cooler",
}
VALID_CATEGORIES = set(CATEGORY_ALIASES.values())
VALID_IDENTITY_STATUSES = {"verified", "needs_review", "unknown"}
VALID_AVAILABILITY = {"available", "unavailable", "unknown"}
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def _normalize_category(value: str) -> str:
    return CATEGORY_ALIASES.get(str(value).strip().casefold(), str(value).strip())


def _normalize_identity_status(value: str) -> str:
    status = str(value).strip().casefold()
    if status == "source_record":
        return "needs_review"
    return status


def read_csv_or_empty(path: str | Path, columns: list[str]) -> pd.DataFrame:
    """Read a CSV if present, otherwise return an empty frame with expected columns."""
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=columns)
    try:
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=columns)
    return frame


def _missing_columns(frame: pd.DataFrame, expected: list[str], label: str) -> list[str]:
    return [f"{label}: missing required column '{col}'" for col in expected if col not in frame.columns]


def _duplicate_values(frame: pd.DataFrame, column: str, label: str) -> list[str]:
    if column not in frame.columns:
        return []
    values = frame[column].astype(str).str.strip()
    mask = values.ne("") & values.duplicated(keep=False)
    return [f"{label}: repeated {column} '{value}' (review; records were not removed)"
            for value in sorted(values[mask].unique())]


def validate_components(frame: pd.DataFrame) -> list[str]:
    issues = _missing_columns(frame, COMPONENT_COLUMNS, "Components")
    if issues:
        return issues
    issues.extend(_duplicate_values(frame, "component_id", "Components"))
    for index, row in frame.iterrows():
        row_label = f"Components row {index + 2}"
        category = str(row["category"]).strip()
        normalized_category = _normalize_category(category)
        if category and normalized_category not in VALID_CATEGORIES:
            issues.append(f"{row_label}: unknown category '{category}'")
        status = _normalize_identity_status(row["identity_status"])
        if status and status not in VALID_IDENTITY_STATUSES:
            issues.append(f"{row_label}: identity_status must be verified, needs_review, or unknown")
        for col in ("component_id", "category", "brand", "model"):
            if not str(row[col]).strip():
                issues.append(f"{row_label}: '{col}' is blank")
        url = str(row["source_url"]).strip()
        if url and not URL_RE.match(url):
            issues.append(f"{row_label}: source_url should start with http:// or https://")
        raw_specs = str(row["specs_json"]).strip()
        if raw_specs:
            try:
                parsed: Any = json.loads(raw_specs)
                if not isinstance(parsed, dict):
                    issues.append(f"{row_label}: specs_json should contain a JSON object")
            except json.JSONDecodeError:
                issues.append(f"{row_label}: specs_json is not valid JSON")
    # Flag exact documented-field matches for human review; never remove records.
    compare_cols = [c for c in ("category", "brand", "model", "specs_json", "source_name", "source_url") if c in frame]
    if compare_cols and len(frame):
        normalized = frame[compare_cols].fillna("").astype(str).apply(lambda col: col.str.strip().str.casefold())
        duplicate_mask = normalized.duplicated(keep=False)
        if duplicate_mask.any():
            issues.append(f"Components: {int(duplicate_mask.sum())} row(s) match another row across the available identity fields; review possible exact duplicates. No rows were removed.")
    return issues


def validate_prices(frame: pd.DataFrame, components: pd.DataFrame) -> list[str]:
    issues = _missing_columns(frame, PRICE_COLUMNS, "Prices")
    if issues:
        return issues
    issues.extend(_duplicate_values(frame, "price_id", "Prices"))
    observations: set[tuple[str, str, str, str]] = set()
    known_component_ids = set(components.get("component_id", pd.Series(dtype=str)).astype(str).str.strip())
    for index, row in frame.iterrows():
        row_label = f"Prices row {index + 2}"
        price_type = str(row.get("price_type", "")).strip().casefold()
        provenance = str(row.get("provenance", "")).strip()
        if price_type and price_type not in {"seller_observation", "planning_estimate"}:
            issues.append(
                f"{row_label}: price_type must be seller_observation or planning_estimate"
            )
        is_estimate = price_type == "planning_estimate"
        required_fields = ["price_id", "component_id", "price_inr"]
        if not is_estimate:
            required_fields.extend(["source_url", "checked_at"])
        for col in required_fields:
            if not str(row[col]).strip():
                issues.append(f"{row_label}: '{col}' is blank")
        if is_estimate:
            if not provenance:
                issues.append(f"{row_label}: planning estimates require provenance")
            for col in ("seller", "source_url", "checked_at"):
                if str(row.get(col, "")).strip():
                    issues.append(
                        f"{row_label}: planning estimates must not claim '{col}'"
                    )
        component_id = str(row["component_id"]).strip()
        if component_id and component_id not in known_component_ids:
            issues.append(f"{row_label}: component_id '{component_id}' does not match a catalog record")
        raw_price = str(row["price_inr"]).strip().replace(",", "")
        if raw_price:
            try:
                price = float(raw_price)
                if not math.isfinite(price) or price <= 0:
                    issues.append(f"{row_label}: price_inr must be a finite number greater than zero")
            except ValueError:
                issues.append(f"{row_label}: price_inr must be a number in INR")
        url = str(row["source_url"]).strip()
        if url and not URL_RE.match(url):
            issues.append(f"{row_label}: source_url should start with http:// or https://")
        checked_at = str(row["checked_at"]).strip()
        if checked_at:
            try:
                datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
            except ValueError:
                issues.append(
                    f"{row_label}: checked_at must use an ISO date or timestamp"
                )
        if not is_estimate and component_id and checked_at and raw_price:
            seller = str(row["seller"]).strip().casefold()
            try:
                normalized_price = str(float(raw_price))
            except ValueError:
                normalized_price = ""
            if seller and normalized_price:
                observation_key = (
                    component_id.casefold(),
                    seller,
                    normalized_price,
                    checked_at,
                )
                if observation_key in observations:
                    issues.append(
                        f"{row_label}: duplicate seller observation for this component, price, and check timestamp"
                    )
                observations.add(observation_key)
        availability = str(row["availability"]).strip()
        if availability and availability not in VALID_AVAILABILITY:
            issues.append(f"{row_label}: availability must be available, unavailable, or unknown")
        if is_estimate and availability != "unknown":
            issues.append(
                f"{row_label}: planning estimate availability must be unknown"
            )
    return issues


def load_and_validate(data_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    data_dir = Path(data_dir)
    components = read_csv_or_empty(data_dir / "components.csv", COMPONENT_COLUMNS)
    prices = read_csv_or_empty(data_dir / "prices.csv", PRICE_COLUMNS)
    issues = validate_components(components)
    issues.extend(validate_prices(prices, components))
    return components, prices, issues
