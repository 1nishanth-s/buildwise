# BuildWise-AI — Machine Learning Performance Prediction Module

This directory contains the prepared machine learning dataset generation, feature extraction, and group-aware validation infrastructure for Phase 10 and Phase 11.

## Structure

```
experiments/performance_prediction/
├── config.py                 # Feature allowlists, column schemas, filesystem paths
├── cpu_features.py           # CPU specification extraction and normalization
├── gpu_features.py           # GPU specification extraction and normalization
├── feature_extraction.py     # Unified leak-free feature extraction facade
├── dataset_preparation.py    # Production join, validation, and training dataset generator
├── validation.py             # GroupKFold and GroupShuffleSplit validation generators
├── README.md                 # Architecture documentation
└── data/
    ├── cpu_training_dataset.csv  # 180 verified Cinebench R23 Multi-Core samples
    └── gpu_training_dataset.csv  # 57 verified 3DMark Time Spy Graphics samples
```

## Datasets

### 1. CPU Regression Dataset (`data/cpu_training_dataset.csv`)
- **Rows:** 180
- **Target:** `cinebench_r23_multi_core_score` (Cinebench R23 Multi-Core Score in pts)
- **Predictive Numeric Features:** `cores`, `threads`, `boost_clock_ghz`, `base_clock_ghz`, `tdp_w`
- **Predictive Categorical Features:** `brand`, `socket`, `ram_type`
- **Grouping Column:** `group_id` (10 silicon platform families for GroupKFold)
- **Metadata (Traceability Only):** `component_id`, `benchmark_id`, `model`

### 2. GPU Regression Dataset (`data/gpu_training_dataset.csv`)
- **Rows:** 57
- **Target:** `timespy_graphics_score` (3DMark Time Spy Graphics Score in pts)
- **Predictive Numeric Features:** `vram_gb`, `memory_bus_width_bits`, `memory_bandwidth_gbps`, `base_clock_mhz`, `boost_clock_mhz`, `board_power_w`
- **Predictive Categorical Features:** `architecture`, `chipmaker`, `memory_type`
- **Grouping Column:** `group_id` / `base_die_group_id` (14 physical silicon die groups for GroupKFold)
- **Metadata (Traceability Only):** `component_id`, `benchmark_id`, `brand`, `model`, `sku_group_id`

## Strict Anti-Leakage Invariants
- Zero model fitting in Phase 10.
- No pricing, merchant, or URL features.
- No target variables in predictor feature sets.
- No identical hardware variants split across training and test folds.
