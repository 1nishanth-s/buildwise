# BuildWise-AI — Phase 10: Machine Learning Dataset Preparation Plan

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 10 — Machine Learning Dataset Audit, Feature Engineering and Training Data Preparation  
**Objective:** Prepare clean, reproducible, leak-free CPU and GPU supervised regression training datasets from production components and verified empirical benchmark observations.

---

## 1. Context and Architectural Scope

In BuildWise-AI, machine learning will provide empirical performance predictions to assist users in evaluating component choices. Two independent regression models are planned for Phase 11:
1. **CPU Performance Model:** Predicts Cinebench R23 Multi-Core scores from CPU architectural and physical specifications.
2. **GPU Performance Model:** Predicts 3DMark Time Spy Graphics scores from GPU memory subsystem, frequency, power, and architectural specifications.

### Strict Phase 10 Mandates:
- **No Model Training in Phase 10:** Actual training, algorithm comparison (Dummy, Ridge, Random Forest, Extra Trees, Gradient Boosting), hyperparameter tuning, and model persistence (`.joblib`) are deferred to Phase 11.
- **Strict Target Provenance:** Targets must be 100% empirical observations recorded in `data/benchmarks.csv`. No LLM-generated predictions, interpolated values, or synthetic targets may be used.
- **Production Data Protection:** `data/components.csv`, `data/prices.csv`, and `data/benchmarks.csv` must remain byte-for-byte unmodified (identical SHA-256 hashes).
- **Separation of Derived Data:** All prepared ML datasets must reside under `experiments/performance_prediction/data/` and must never be merged into the production catalog.

---

## 2. Review of Existing ML Infrastructure

The repository contains historical ML experiments from earlier phases:
- `experiments/cpu_benchmark_regression/`: Contains early Phase 3B code (`prepare_dataset.py`, `train.py`) designed for an initial 55-CPU dataset. Tested by `tests/test_cpu_ml_regression.py`.
- `experiments/performance_tier/`: Performance tiering experiment tested by `tests/test_performance_tier.py`.
- `data/ml/`: Houses historical dataset artifacts (`cpu_benchmark_training_v1.csv` [55 rows], `cpu_family_groups.csv` [55 rows], `gpu_family_groups_v1.csv` [57 rows], `gpu_feature_enrichment_v1.csv` [1141 rows]).

**Preservation Principle:** To guarantee zero regression on the existing 109 unit tests, existing files in `experiments/cpu_benchmark_regression/` and `data/ml/` will be preserved untouched. New Phase 10 work will be organized in a modular package under `experiments/performance_prediction/`.

---

## 3. Benchmark Target Audit Plan

### 3.1 CPU Benchmark Dataset
- **Suite:** Cinebench R23
- **Metric:** Multi-Core Score
- **Unit:** `pts`
- **Target Variable Name:** `cinebench_r23_multi_core_score`
- **Catalog Size:** 180 CPUs
- **Expected Benchmark Records:** 180 (100% coverage)
- **Integrity Criteria:** Unique benchmark IDs, 1-to-1 component ID alignment, positive non-null integers/floats, valid source URLs, absence of duplicates.

### 3.2 GPU Benchmark Dataset
- **Suite:** 3DMark Time Spy
- **Metric:** Graphics Score
- **Unit:** `pts`
- **Target Variable Name:** `timespy_graphics_score`
- **Catalog Size:** 218 GPUs
- **Expected Benchmark Records:** 57 (~26.1% coverage)
- **Integrity Criteria:** Unique benchmark IDs, alignment to genuine catalog GPUs, no mixing with Time Spy Overall or CPU scores, positive non-null numeric scores, traceable source URLs.

---

## 4. Hardware Feature Engineering Plan

### 4.1 CPU Predictor Features
From the catalog specifications (`specs_json` in `data/components.csv`), the following features are audited:
- **Numerical Features:**
  - `cores` (int, 100% coverage): Physical CPU core count.
  - `threads` (int, 100% coverage): Logical CPU thread count.
  - `boost_clock_ghz` (float, 100% coverage): Maximum single-core boost clock frequency.
  - `base_clock_ghz` (float, 83.3% coverage): Base clock frequency (150/180 documented).
  - `tdp_w` (float, 100% coverage): Thermal Design Power / base power in Watts.
- **Categorical Features:**
  - `brand` (str, 100% coverage): Silicon manufacturer (`AMD`, `Intel`).
  - `socket` (str, 100% coverage): Motherboard socket interface (`AM4`, `AM5`, `LGA1700`, `LGA1851`, `LGA1200`, `LGA1151`, `sTR4`, `sTRX4`, `sTR5`, `LGA2066`).
  - `ram_type` (str, 100% coverage): Memory standard (`DDR4`, `DDR5`, `DDR4/DDR5`).
- **Excluded Features:**
  - `l3_cache_mb`, `l2_cache_mb`, `process_nm`: Missing in the production catalog for the majority of the expanded records ($>80\%$ missing). Excluded to prevent fabricated inputs.
  - `component_id`, `model`, `price_inr`, URLs: Excluded to prevent label memorization and price bias.

### 4.2 GPU Predictor Features
From catalog specifications and verified hardware enrichment (`data/ml/gpu_feature_enrichment_v1.csv`), the following features are audited:
- **Universal Numerical Features (100% coverage across 57 benchmarked GPUs):**
  - `vram_gb` (int): Video RAM capacity.
  - `memory_bus_width_bits` (int): Memory bus interface width.
  - `memory_bandwidth_gbps` (float): Theoretical memory bandwidth in GB/s.
  - `base_clock_mhz` (float): Base GPU core frequency.
  - `boost_clock_mhz` (float): Boost GPU core frequency.
  - `board_power_w` (float): Total board power / TGP in Watts.
- **Universal Categorical Features (100% coverage):**
  - `architecture` (str): GPU microarchitecture (`RDNA 3`, `Ada Lovelace`, `Ampere`, `RDNA 2`, `Xe2-HPG`).
  - `chipmaker` (str): GPU vendor (`AMD`, `NVIDIA`, `Intel`).
  - `memory_type` (str): VRAM standard (`GDDR6`, `GDDR6X`).
- **Architecture-Specific Exclusions:**
  - `cuda_cores` (NVIDIA only, 26/57), `stream_processors` (AMD only, 29/57), `xe_cores` (Intel only, 2/57). These cannot be directly pooled into a single numerical column without introducing architectural distortions; they are audited and documented separately.

---

## 5. Data Leakage Prevention and Validation Strategy

### 5.1 Leakage Risks
- **Variant Leakage:** Different vendor SKUs sharing identical underlying silicon (e.g. ASUS Dual RTX 4070 vs Gigabyte Windforce RTX 4070) share near-identical performance. Splitting randomly by row puts identical hardware in both training and test sets, inflating validation accuracy.
- **Platform Leakage:** Related CPU models within the same generation/stepping share architectural IPC characteristics.

### 5.2 Group-Aware Validation Design
- **CPU Grouping:** Platform/silicon generation grouping using `group_id` based on brand, socket, and generation family (10 distinct platform groups: `amd_am4`, `amd_am5`, `intel_lga1700`, `intel_lga1200`, `intel_lga1151`, `intel_lga1851`, `amd_str4`, `amd_strx4`, `amd_str5`, `intel_lga2066`).
  - Validation method: `GroupKFold(n_splits=5)` and `GroupShuffleSplit(test_size=0.20)`.
- **GPU Grouping:** Grouping by underlying silicon die using `base_die_group_id` from `gpu_family_groups_v1.csv` (14 distinct die groups: `amd_rdna3_navi32`, `nvidia_ada_ad107`, `nvidia_ampere_ga106`, etc.).
  - Validation method: Group-aware split to ensure physical dies do not leak across folds.

---

## 6. Target Dataset Artifacts and Directory Layout

```
experiments/performance_prediction/
├── config.py                 (Feature allowlists, column mappings, paths)
├── cpu_features.py           (CPU specification parsing and feature extraction)
├── gpu_features.py           (GPU specification parsing and feature extraction)
├── feature_extraction.py     (Unified feature extraction facade)
├── dataset_preparation.py    (Generates and validates final training CSVs)
├── validation.py             (Group-aware splitters and CV generators)
├── README.md                 (Module documentation and usage)
└── data/
    ├── cpu_training_dataset.csv  (180 rows, Cinebench R23 Multi-Core target)
    └── gpu_training_dataset.csv  (57 rows, 3DMark Time Spy Graphics target)
```

---

## 7. Testing and Safety Verification

1. **Unit Testing:** Implement `tests/test_ml_dataset_preparation.py` covering:
   - Target filtering, metric selection, ID mapping, JSON specs parsing.
   - Numerical unit conversion, categorical encoding prep, missing data handling.
   - Exclusion of targets/IDs from predictors, reproducibility, group separation.
   - Data protection: production CSV checksum immutability.
2. **Regression Testing:** Ensure all 109 existing unit tests continue to pass with 0 failures.
3. **Data Protection:** SHA-256 hashes of `components.csv`, `prices.csv`, and `benchmarks.csv` must be audited before and after execution.
