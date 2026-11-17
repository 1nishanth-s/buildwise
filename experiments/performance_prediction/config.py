"""
BuildWise-AI — Phase 10: Machine Learning Performance Prediction Configuration

Central configuration defining target variables, feature allowlists, metadata columns,
and filesystem paths for CPU and GPU regression datasets.
"""
from pathlib import Path

# Repository root resolution
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

# Production data paths (READ-ONLY)
COMPONENTS_CSV = PROJECT_ROOT / "data" / "components.csv"
PRICES_CSV = PROJECT_ROOT / "data" / "prices.csv"
BENCHMARKS_CSV = PROJECT_ROOT / "data" / "benchmarks.csv"

# Pre-existing ML metadata paths (READ-ONLY)
GPU_FAMILY_GROUPS_CSV = PROJECT_ROOT / "data" / "ml" / "gpu_family_groups_v1.csv"
GPU_ENRICHMENT_CSV = PROJECT_ROOT / "data" / "ml" / "gpu_feature_enrichment_v1.csv"

# Derived ML dataset output paths
DATA_DIR = CURRENT_DIR / "data"
CPU_TRAINING_CSV = DATA_DIR / "cpu_training_dataset.csv"
GPU_TRAINING_CSV = DATA_DIR / "gpu_training_dataset.csv"

# -----------------------------------------------------------------------------
# CPU Machine Learning Configuration
# -----------------------------------------------------------------------------
CPU_TARGET = "cinebench_r23_multi_core_score"
CPU_BENCHMARK_SUITE = "Cinebench R23"
CPU_BENCHMARK_METRIC = "Multi-Core Score"

CPU_NUMERIC_FEATURES = [
    "cores",
    "threads",
    "boost_clock_ghz",
    "base_clock_ghz",
    "tdp_w",
]

CPU_CATEGORICAL_FEATURES = [
    "brand",
    "socket",
    "ram_type",
]

CPU_PREDICTIVE_FEATURES = CPU_NUMERIC_FEATURES + CPU_CATEGORICAL_FEATURES
CPU_METADATA_COLUMNS = ["component_id", "benchmark_id", "model", "group_id"]
CPU_OUTPUT_COLUMNS = CPU_METADATA_COLUMNS + CPU_PREDICTIVE_FEATURES + [CPU_TARGET]

# -----------------------------------------------------------------------------
# GPU Machine Learning Configuration
# -----------------------------------------------------------------------------
GPU_TARGET = "timespy_graphics_score"
GPU_BENCHMARK_SUITE = "3DMark Time Spy"
GPU_BENCHMARK_METRIC = "Graphics Score"

GPU_NUMERIC_FEATURES = [
    "vram_gb",
    "memory_bus_width_bits",
    "memory_bandwidth_gbps",
    "base_clock_mhz",
    "boost_clock_mhz",
    "board_power_w",
]

GPU_CATEGORICAL_FEATURES = [
    "architecture",
    "chipmaker",
    "memory_type",
]

GPU_PREDICTIVE_FEATURES = GPU_NUMERIC_FEATURES + GPU_CATEGORICAL_FEATURES
GPU_METADATA_COLUMNS = [
    "component_id",
    "benchmark_id",
    "brand",
    "model",
    "base_die_group_id",
    "sku_group_id",
    "group_id",
]
GPU_OUTPUT_COLUMNS = GPU_METADATA_COLUMNS + GPU_PREDICTIVE_FEATURES + [GPU_TARGET]
