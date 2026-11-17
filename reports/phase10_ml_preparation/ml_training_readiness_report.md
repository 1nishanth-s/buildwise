# BuildWise-AI — Phase 10: Machine Learning Training Readiness Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 10 — Machine Learning Dataset Audit, Feature Engineering and Training Data Preparation  
**Scope:** Independent Readiness Assessment for CPU and GPU Supervised Regression Pipelines  

---

## 1. Readiness Framework & Criteria

Each hardware domain is evaluated against six standardized criteria to determine its readiness for Phase 11 supervised model training:
1. **Target Completeness & Provenance:** Empirical target availability, absence of nulls, and verifiable methodology.
2. **Feature Coverage & Integrity:** Completeness of physical and electrical predictor features.
3. **Silicon Diversity & Grouping:** Number of distinct microarchitectural / die groups available for group-aware validation.
4. **Data Leakage Risk Mitigation:** Structural guarantees preventing identical hardware from appearing in train and test splits.
5. **Sample Size & Statistical Power:** Sufficiency of observations to fit linear and non-linear estimators without severe overfitting.
6. **Generalization Scope:** Defined boundaries within which model inferences will be valid.

Classification Tiers:
- `ready_for_experimentation`: Dataset meets all statistical and architectural criteria for benchmark modeling and model comparison.
- `ready_with_limitations`: Dataset supports exploratory regression within represented hardware families, but sample size or coverage imposes defined operational constraints.
- `insufficient_data`: Data volume, target coverage, or feature quality is inadequate for supervised modeling.

---

## 2. CPU Dataset Readiness Assessment

### 2.1 Criteria Evaluation
- **Target Completeness:** **100.0% (180 / 180 records)** in `data/benchmarks.csv` have verified empirical Cinebench R23 Multi-Core scores. 0 missing, 0 duplicates, 0 synthetic values.
- **Feature Coverage:**
  - `cores`, `threads`, `boost_clock_ghz`, `tdp_w`, `brand`, `socket`, `ram_type`: 100.0% complete (180 / 180).
  - `base_clock_ghz`: 83.33% complete (150 / 180; 30 missing). Handled via median imputation in Phase 11.
- **Independent Groups:** **10 platform generation groups** (`amd_am4`, `intel_lga1700`, `amd_am5`, `intel_lga1200`, `intel_lga1151`, `intel_lga1851`, `amd_str5`, `amd_str4`, `amd_strx4`, `intel_lga2066`).
- **Data Leakage Mitigation:** 5-Fold `GroupKFold` strictly isolates platform families.
- **Sample Size:** $N = 180$ provides adequate degrees of freedom for evaluating Dummy, Ridge, Random Forest, Extra Trees, and Gradient Boosting regressors.
- **Generalization Scope:** Generalizes well across mainstream desktop CPUs spanning AMD Zen through Zen 5 and Intel 6th through 14th Gen / Core Ultra platforms.

### 2.2 Classification: `ready_for_experimentation`
The CPU dataset satisfies all data governance, sample size, and feature quality requirements. It is fully approved for multi-algorithm regression experiments in Phase 11.

---

## 3. GPU Dataset Readiness Assessment

### 3.1 Criteria Evaluation
- **Target Completeness:** **26.15% (57 / 218 records)** in `data/components.csv` have verified 3DMark Time Spy Graphics scores. All 57 are empirical lab observations. The remaining 161 catalog GPUs lack benchmark targets and are excluded from supervised training.
- **Feature Coverage:** Universal features (`vram_gb`, `memory_bus_width_bits`, `memory_bandwidth_gbps`, `base_clock_mhz`, `boost_clock_mhz`, `board_power_w`, `architecture`, `chipmaker`, `memory_type`) are 100.0% complete across all 57 benchmarked GPUs.
- **Silicon Diversity:** 5 distinct architectures (AMD RDNA 3, AMD RDNA 2, NVIDIA Ada Lovelace, NVIDIA Ampere, Intel Xe2-HPG) across **14 physical silicon die groups** and **27 SKU groups**.
- **Data Leakage Mitigation:** Die-level grouping (`base_die_group_id`) prevents board-partner variant leakage across folds.
- **Sample Size Constraint:** $N = 57$ is relatively small. Cross-validation folds must be limited to 4 splits ($~14$ samples per fold) to preserve training set stability ($~43$ samples). Non-linear models with high capacity (e.g. deep trees) risk overfitting.
- **Generalization Scope:** Models will be valid for interpolating within known die families and architectures. They **cannot** generalize to unrepresented architectures (e.g., NVIDIA Blackwell, AMD RDNA 4, or legacy pre-Ampere/pre-RDNA cards).

### 3.2 Classification: `ready_with_limitations`
The GPU dataset is approved for exploratory model comparison and baseline regression in Phase 11, subject to explicit architectural boundaries:
1. Model comparisons must emphasize regularized linear baselines (Ridge) and shallow ensemble estimators with heavy regularization.
2. Inferences on unbenchmarked catalog GPUs belonging to unrepresented die groups must be flagged with a wide uncertainty margin.
3. Production claims must clearly distinguish empirical measurements from model predictions.

---

## 4. Summary Readiness Scorecard

| Domain | Target Metric | Samples ($N$) | Groups | Coverage | Missing Features | Classification |
|---|---|---:|---:|---:|---:|---|
| **CPU Pipeline** | Cinebench R23 Multi-Core | 180 | 10 | 100.0% | 0% primary / 16.7% base clock | **`ready_for_experimentation`** |
| **GPU Pipeline** | 3DMark Time Spy Graphics | 57 | 14 | 26.15% | 0% on universal features | **`ready_with_limitations`** |
