# BuildWise-AI — Phase 10: CPU Benchmark Target Audit

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 10 — Machine Learning Dataset Audit, Feature Engineering and Training Data Preparation  
**Target Variable:** `cinebench_r23_multi_core_score`  
**Source Dataset:** `data/benchmarks.csv` (180 CPU records)  
**Catalog Reference:** `data/components.csv` (180 CPU records)  

---

## 1. Executive Summary & Verification Findings

An exhaustive data integrity audit was performed on the CPU benchmark observations stored in `data/benchmarks.csv`. All 180 desktop CPU components present in the production catalog have verified empirical benchmark observations, achieving **100.0% catalog coverage**.

| Audit Metric | Expected Requirement | Actual Audit Result | Status |
|---|---|---|---|
| **Catalog CPU Records** | 180 components | 180 components | **VERIFIED** |
| **CPU Benchmark Observations** | 180 records | 180 records | **VERIFIED** |
| **Catalog Coverage** | 100.0% | 100.0% (180 / 180) | **VERIFIED** |
| **Suite Consistency** | `Cinebench R23` | 180 / 180 records match `Cinebench R23` | **VERIFIED** |
| **Metric Consistency** | `Multi-Core Score` | 180 / 180 records match `Multi-Core Score` | **VERIFIED** |
| **Unit Consistency** | `pts` | 180 / 180 records specify `pts` | **VERIFIED** |
| **Missing / Null Scores** | 0 nulls | 0 nulls, 0 NaNs | **VERIFIED** |
| **Negative / Zero Scores** | 0 non-positive | 0 non-positive | **VERIFIED** |
| **Duplicate Benchmark IDs** | 0 duplicates | 180 unique IDs across 180 rows | **VERIFIED** |
| **Duplicate Component IDs** | 0 duplicates | 180 unique CIDs across 180 rows | **VERIFIED** |
| **Referential Integrity** | All CIDs in catalog | 180 / 180 exist in `components.csv` (category: `cpu`) | **VERIFIED** |

---

## 2. Descriptive Statistical Distribution

The target variable `cinebench_r23_multi_core_score` exhibits a realistic, empirically sound distribution reflecting the wide spectrum of desktop computing hardware (from entry-level dual/quad cores to multi-threaded workstation processors):

$$\text{Count} = 180 \quad|\quad \mu = 17,890.23 \text{ pts} \quad|\quad \sigma = 13,322.32 \text{ pts}$$

| Statistical Percentile | Score Value (pts) | Representative Hardware Exemplar |
|---|---:|---|
| **Minimum (0%)** | 1,380 | Legacy / Entry dual-core processors |
| **First Quartile (25%)** | 8,825 | Mid-range older quad-cores / 6-core budget processors |
| **Median (50%)** | 14,113 | Modern 6-core / 8-core mainstream desktop CPUs (e.g. Ryzen 5 7600X, Core i5-12600K) |
| **Third Quartile (75%)** | 24,200 | Modern 8-core / 12-core performance processors (e.g. Ryzen 7 9700X, Core i7-14700K) |
| **Maximum (100%)** | 98,500 | High-core-count workstation silicon (AMD Ryzen Threadripper Pro) |

---

## 3. Data Provenance & Methodology

Every benchmark record is traceable to verifiable public benchmark repositories and empirical hardware review labs:
- **CPU-Monkey / TechPowerUp Database:** 125 observations (69.4%)
- **CPU-Monkey Direct:** 54 observations (30.0%)
- **StorageReview / Enterprise Labs:** 1 observation (0.6%)

Every observation specifies:
- Full source URL linking to original test results.
- Published review date / verification date.
- Standardized test methodology (Cinebench R23 10-minute thermal throttling loop).

---

## 4. Mapping into Derived ML Target

In the prepared ML regression dataset (`experiments/performance_prediction/data/cpu_training_dataset.csv`), the target variable is mapped as:

```python
TARGET_COLUMN = "cinebench_r23_multi_core_score"
```

- **No Synthetic Values:** Zero imputation or synthetic target interpolation was performed.
- **Traceability Reference:** Each row preserves `component_id` and `benchmark_id` for auditing purposes, strictly excluded from the feature matrix $X$.
- **Readiness:** The CPU benchmark target dataset satisfies all preconditions for supervised regression training in Phase 11.
