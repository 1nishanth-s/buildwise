"""
BuildWise-AI — Phase 10: Supervised ML Training Dataset Preparation

Loads production hardware components and empirical benchmark observations,
performs leak-free feature extraction and validation, and outputs separate,
reproducible CPU and GPU regression training datasets.
"""
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from experiments.performance_prediction.config import (
    BENCHMARKS_CSV,
    COMPONENTS_CSV,
    CPU_BENCHMARK_METRIC,
    CPU_BENCHMARK_SUITE,
    CPU_OUTPUT_COLUMNS,
    CPU_TARGET,
    CPU_TRAINING_CSV,
    GPU_BENCHMARK_METRIC,
    GPU_BENCHMARK_SUITE,
    GPU_ENRICHMENT_CSV,
    GPU_FAMILY_GROUPS_CSV,
    GPU_OUTPUT_COLUMNS,
    GPU_TARGET,
    GPU_TRAINING_CSV,
)
from experiments.performance_prediction.cpu_features import extract_cpu_record_features
from experiments.performance_prediction.gpu_features import extract_gpu_record_features


def prepare_cpu_dataset(
    components_path: Path = COMPONENTS_CSV,
    benchmarks_path: Path = BENCHMARKS_CSV,
    output_path: Optional[Path] = CPU_TRAINING_CSV,
) -> pd.DataFrame:
    """
    Constructs and saves the derived CPU Cinebench R23 regression training dataset.
    
    Returns:
        pd.DataFrame containing 180 validated CPU training samples.
    """
    components_df = pd.read_csv(components_path)
    benchmarks_df = pd.read_csv(benchmarks_path)

    # 1. Filter CPU catalog components
    cpu_comp = components_df[components_df["category"].str.casefold() == "cpu"].copy()
    if cpu_comp.empty:
        raise ValueError("No CPU records found in components catalog")

    # 2. Filter Cinebench R23 Multi-Core benchmark observations
    cpu_bench = benchmarks_df[
        (benchmarks_df["benchmark_suite"].str.strip() == CPU_BENCHMARK_SUITE)
        & (benchmarks_df["benchmark_metric"].str.strip() == CPU_BENCHMARK_METRIC)
    ].copy()

    if cpu_bench.empty:
        raise ValueError(f"No benchmark records found for {CPU_BENCHMARK_SUITE} ({CPU_BENCHMARK_METRIC})")

    # Map benchmarks by component_id
    bench_by_cid = {}
    for _, b in cpu_bench.iterrows():
        cid = str(b["component_id"]).strip()
        bench_by_cid[cid] = b

    # 3. Construct records
    records: List[Dict] = []
    for _, comp_row in cpu_comp.iterrows():
        cid = str(comp_row["component_id"]).strip()
        if cid not in bench_by_cid:
            # Skip components lacking empirical benchmark targets
            continue

        bench_row = bench_by_cid[cid]
        score_val = float(bench_row["score"])
        if score_val <= 0 or pd.isna(score_val):
            raise ValueError(f"Invalid non-positive benchmark score for {cid}: {score_val}")

        # Extract features
        feat = extract_cpu_record_features(comp_row)

        record = {
            "component_id": cid,
            "benchmark_id": str(bench_row["benchmark_id"]).strip(),
            "model": str(comp_row.get("model", "")).strip(),
            "group_id": feat["group_id"],
            "cores": feat["cores"],
            "threads": feat["threads"],
            "boost_clock_ghz": feat["boost_clock_ghz"],
            "base_clock_ghz": feat["base_clock_ghz"],
            "tdp_w": feat["tdp_w"],
            "brand": feat["brand"],
            "socket": feat["socket"],
            "ram_type": feat["ram_type"],
            CPU_TARGET: score_val,
        }
        records.append(record)

    df_cpu = pd.DataFrame(records)[CPU_OUTPUT_COLUMNS]

    # Verification assertions
    assert len(df_cpu) == 180, f"Expected 180 CPU samples, got {len(df_cpu)}"
    assert df_cpu[CPU_TARGET].isnull().sum() == 0, "Null targets detected in CPU dataset"
    assert df_cpu["component_id"].nunique() == len(df_cpu), "Duplicate component_ids in CPU dataset"
    assert df_cpu["benchmark_id"].nunique() == len(df_cpu), "Duplicate benchmark_ids in CPU dataset"

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_cpu.to_csv(output_path, index=False)
        print(f"[dataset_preparation] Successfully prepared CPU dataset ({len(df_cpu)} rows) -> {output_path}")

    return df_cpu


def prepare_gpu_dataset(
    components_path: Path = COMPONENTS_CSV,
    benchmarks_path: Path = BENCHMARKS_CSV,
    enrichment_path: Path = GPU_ENRICHMENT_CSV,
    family_groups_path: Path = GPU_FAMILY_GROUPS_CSV,
    output_path: Optional[Path] = GPU_TRAINING_CSV,
) -> pd.DataFrame:
    """
    Constructs and saves the derived GPU 3DMark Time Spy regression training dataset.
    
    Returns:
        pd.DataFrame containing 57 validated GPU training samples.
    """
    components_df = pd.read_csv(components_path)
    benchmarks_df = pd.read_csv(benchmarks_path)
    enrichment_df = pd.read_csv(enrichment_path)
    family_groups_df = pd.read_csv(family_groups_path)

    # 1. Filter GPU components
    gpu_comp = components_df[components_df["category"].str.casefold() == "gpu"].copy()
    if gpu_comp.empty:
        raise ValueError("No GPU records found in components catalog")

    # 2. Filter 3DMark Time Spy Graphics observations
    gpu_bench = benchmarks_df[
        (benchmarks_df["benchmark_suite"].str.strip() == GPU_BENCHMARK_SUITE)
        & (benchmarks_df["benchmark_metric"].str.strip() == GPU_BENCHMARK_METRIC)
    ].copy()

    if gpu_bench.empty:
        raise ValueError(f"No benchmark records found for {GPU_BENCHMARK_SUITE} ({GPU_BENCHMARK_METRIC})")

    # Map benchmarks by component_id
    bench_by_cid = {str(b["component_id"]).strip(): b for _, b in gpu_bench.iterrows()}

    # Map enrichment values (consolidating verified_value and value)
    enrichment_df["val"] = enrichment_df["verified_value"].combine_first(enrichment_df["value"])
    enrich_pivot = enrichment_df.pivot(index="component_id", columns="feature_name", values="val")

    # Map family groups
    family_by_cid = {str(f["component_id"]).strip(): f for _, f in family_groups_df.iterrows()}

    # 3. Construct records
    records: List[Dict] = []
    comp_by_cid = {str(c["component_id"]).strip(): c for _, c in gpu_comp.iterrows()}

    for cid, bench_row in bench_by_cid.items():
        if cid not in comp_by_cid:
            raise KeyError(f"GPU benchmark references unknown catalog component_id: {cid}")

        comp_row = comp_by_cid[cid]
        enrich_vals = enrich_pivot.loc[cid].to_dict() if cid in enrich_pivot.index else {}
        fam_row_raw = family_by_cid.get(cid, {})
        fam_row = fam_row_raw.to_dict() if hasattr(fam_row_raw, "to_dict") else (fam_row_raw or {})

        score_val = float(bench_row["score"])
        if score_val <= 0 or pd.isna(score_val):
            raise ValueError(f"Invalid non-positive benchmark score for {cid}: {score_val}")

        # Extract features
        feat = extract_gpu_record_features(
            component_row=comp_row,
            enrichment_map=enrich_vals,
            family_group_row=fam_row,
        )

        record = {
            "component_id": cid,
            "benchmark_id": str(bench_row["benchmark_id"]).strip(),
            "brand": str(comp_row.get("brand", "")).strip(),
            "model": str(comp_row.get("model", "")).strip(),
            "base_die_group_id": feat["base_die_group_id"],
            "sku_group_id": feat["sku_group_id"],
            "group_id": feat["group_id"],
            "vram_gb": feat["vram_gb"],
            "memory_bus_width_bits": feat["memory_bus_width_bits"],
            "memory_bandwidth_gbps": feat["memory_bandwidth_gbps"],
            "base_clock_mhz": feat["base_clock_mhz"],
            "boost_clock_mhz": feat["boost_clock_mhz"],
            "board_power_w": feat["board_power_w"],
            "architecture": feat["architecture"],
            "chipmaker": feat["chipmaker"],
            "memory_type": feat["memory_type"],
            GPU_TARGET: score_val,
        }
        records.append(record)

    df_gpu = pd.DataFrame(records)[GPU_OUTPUT_COLUMNS]

    # Verification assertions
    assert len(df_gpu) == 57, f"Expected 57 GPU samples, got {len(df_gpu)}"
    assert df_gpu[GPU_TARGET].isnull().sum() == 0, "Null targets detected in GPU dataset"
    assert df_gpu["component_id"].nunique() == len(df_gpu), "Duplicate component_ids in GPU dataset"
    assert df_gpu["benchmark_id"].nunique() == len(df_gpu), "Duplicate benchmark_ids in GPU dataset"

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_gpu.to_csv(output_path, index=False)
        print(f"[dataset_preparation] Successfully prepared GPU dataset ({len(df_gpu)} rows) -> {output_path}")

    return df_gpu


def prepare_all_datasets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepares and saves both CPU and GPU regression datasets."""
    df_cpu = prepare_cpu_dataset()
    df_gpu = prepare_gpu_dataset()
    return df_cpu, df_gpu


if __name__ == "__main__":
    df_c, df_g = prepare_all_datasets()
    print("CPU Dataset Info:")
    print(df_c.info())
    print("\nGPU Dataset Info:")
    print(df_g.info())
