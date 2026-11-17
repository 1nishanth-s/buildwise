"""
BuildWise-AI — Phase 3B: CPU Benchmark Regression Dataset Preparation

Extracts, validates, and prepares the CPU Cinebench R23 Multi-Core regression dataset
from production hardware catalog and benchmark records.

Strict Data Governance:
- Joins data/components.csv and data/benchmarks.csv.
- Enforces strict 6-feature allowlist: cores, threads, boost_clock_ghz, tdp_w, brand, socket.
- Attaches silicon family group_id from data/ml/cpu_family_groups.csv for GroupKFold validation.
- Strictly excludes any pricing data, vendor information, tier labels, or benchmark sources.
- Never estimates, imputes, or synthesizes benchmark scores.
"""

import csv
import json
import os
import sys
from pathlib import Path
import pandas as pd


# Expected feature allowlist
PREDICTIVE_NUMERIC_FEATURES = ["cores", "threads", "boost_clock_ghz", "tdp_w"]
PREDICTIVE_CATEGORICAL_FEATURES = ["brand", "socket"]
PREDICTIVE_FEATURES = PREDICTIVE_NUMERIC_FEATURES + PREDICTIVE_CATEGORICAL_FEATURES
TARGET_COLUMN = "score"
METADATA_COLUMNS = ["component_id", "benchmark_id", "model", "group_id"]
OUTPUT_COLUMNS = METADATA_COLUMNS[:2] + PREDICTIVE_CATEGORICAL_FEATURES[:1] + METADATA_COLUMNS[2:3] + PREDICTIVE_CATEGORICAL_FEATURES[1:] + PREDICTIVE_NUMERIC_FEATURES + METADATA_COLUMNS[3:] + [TARGET_COLUMN]


def get_project_root() -> Path:
    """Resolve repository root directory."""
    # This script is at experiments/cpu_benchmark_regression/prepare_dataset.py
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "data" / "components.csv").is_file() and (parent / "data" / "benchmarks.csv").is_file():
            return parent
    raise FileNotFoundError("Could not locate project root containing data/components.csv and data/benchmarks.csv")


def prepare_cpu_benchmark_dataset(project_root: Path = None, output_path: Path = None) -> pd.DataFrame:
    """
    Validate, join, and produce the CPU Cinebench R23 regression training dataset.
    
    Returns:
        pd.DataFrame containing 55 validated rows.
    """
    if project_root is None:
        project_root = get_project_root()
    
    components_file = project_root / "data" / "components.csv"
    benchmarks_file = project_root / "data" / "benchmarks.csv"
    family_groups_file = project_root / "data" / "ml" / "cpu_family_groups.csv"
    
    if output_path is None:
        output_path = project_root / "data" / "ml" / "cpu_benchmark_training_v1.csv"
    
    # 1. Verify existence of required source files
    for req_file in [components_file, benchmarks_file, family_groups_file]:
        if not req_file.is_file():
            raise FileNotFoundError(f"Required dataset preparation file not found: {req_file}")
    
    # 2. Load catalog components (filter CPUs)
    catalog_cpus = {}
    with open(components_file, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("category") == "cpu":
                catalog_cpus[row["component_id"]] = row
    
    if not catalog_cpus:
        raise ValueError("No CPU records found in data/components.csv")
    
    # 3. Load silicon family groupings
    family_groups = {}
    with open(family_groups_file, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            family_groups[row["component_id"]] = row["group_id"]
    
    # 4. Load and validate benchmark observations
    valid_records = []
    seen_benchmark_ids = set()
    seen_component_ids = set()
    
    with open(benchmarks_file, "r", encoding="utf-8") as f:
        benchmarks = list(csv.DictReader(f))
    
    for idx, b in enumerate(benchmarks, 1):
        bm_id = b.get("benchmark_id", "").strip()
        cid = b.get("component_id", "").strip()
        suite = b.get("benchmark_suite", "").strip()
        metric = b.get("benchmark_metric", "").strip()
        unit = (b.get("score_unit") or b.get("benchmark_unit", "")).strip()
        score_raw = b.get("score", "").strip()
        
        # Validation checks
        if not bm_id:
            raise ValueError(f"Row {idx}: Missing benchmark_id")
        if bm_id in seen_benchmark_ids:
            raise ValueError(f"Duplicate benchmark_id detected: {bm_id}")
        seen_benchmark_ids.add(bm_id)
        
        if not cid:
            raise ValueError(f"Row {idx} ({bm_id}): Missing component_id")
        if cid in seen_component_ids:
            raise ValueError(f"Duplicate component_id observation in single-suite dataset: {cid}")
        seen_component_ids.add(cid)
        
        if cid not in catalog_cpus:
            raise KeyError(f"Benchmark {bm_id} references unknown CPU component_id: {cid}")
        
        if suite != "Cinebench R23":
            raise ValueError(f"Benchmark {bm_id} has invalid suite '{suite}', expected 'Cinebench R23'")
        if metric != "Multi-Core Score":
            raise ValueError(f"Benchmark {bm_id} has invalid metric '{metric}', expected 'Multi-Core Score'")
        if unit != "pts":
            raise ValueError(f"Benchmark {bm_id} has invalid unit '{unit}', expected 'pts'")
        
        try:
            score = float(score_raw)
            if score <= 0:
                raise ValueError(f"Score must be positive, got {score}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Benchmark {bm_id} has invalid numerical score '{score_raw}': {e}")
        
        # Check family group mapping
        if cid not in family_groups:
            raise KeyError(f"Component {cid} lacks silicon family group assignment in cpu_family_groups.csv")
        group_id = family_groups[cid]
        
        # Extract features from components catalog
        c = catalog_cpus[cid]
        brand = c.get("brand", "").strip()
        model = c.get("model", "").strip()
        
        if not brand:
            raise ValueError(f"Component {cid} has missing brand")
        if not model:
            raise ValueError(f"Component {cid} has missing model")
        
        specs_raw = c.get("specs_json", "")
        try:
            specs = json.loads(specs_raw)
        except Exception as e:
            raise ValueError(f"Component {cid} has invalid specs_json: {e}")
        
        socket = str(specs.get("socket", "")).strip()
        if not socket:
            raise ValueError(f"Component {cid} specs_json missing socket")
        
        try:
            cores = int(specs["cores"])
            if cores <= 0:
                raise ValueError("cores must be > 0")
        except Exception as e:
            raise ValueError(f"Component {cid} specs_json invalid cores: {e}")
        
        try:
            threads = int(specs["threads"])
            if threads <= 0 or threads < cores:
                raise ValueError(f"threads ({threads}) must be >= cores ({cores})")
        except Exception as e:
            raise ValueError(f"Component {cid} specs_json invalid threads: {e}")
        
        boost_val = specs.get("boost_ghz") or specs.get("boost_clock_ghz")
        try:
            boost_clock_ghz = float(boost_val)
            if boost_clock_ghz <= 0:
                raise ValueError("boost_clock_ghz must be > 0")
        except Exception as e:
            raise ValueError(f"Component {cid} specs_json invalid boost clock: {e}")
        
        tdp_val = specs.get("tdp_w") or specs.get("tdp")
        try:
            tdp_w = float(tdp_val)
            if tdp_w <= 0:
                raise ValueError("tdp_w must be > 0")
        except Exception as e:
            raise ValueError(f"Component {cid} specs_json invalid tdp: {e}")
        
        valid_records.append({
            "component_id": cid,
            "benchmark_id": bm_id,
            "brand": brand,
            "model": model,
            "socket": socket,
            "cores": cores,
            "threads": threads,
            "boost_clock_ghz": boost_clock_ghz,
            "tdp_w": tdp_w,
            "group_id": group_id,
            "score": score
        })
    
    # Construct DataFrame
    df = pd.DataFrame(valid_records)
    
    # Ensure correct column ordering
    ordered_cols = [
        "component_id", "benchmark_id", "brand", "model", "socket",
        "cores", "threads", "boost_clock_ghz", "tdp_w", "group_id", "score"
    ]
    df = df[ordered_cols]
    
    # Save output CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[prepare_dataset] Successfully prepared {len(df)} validated CPU benchmark samples.")
    print(f"[prepare_dataset] Dataset written to: {output_path}")
    
    return df


if __name__ == "__main__":
    df = prepare_cpu_benchmark_dataset()
    print(df.info())
