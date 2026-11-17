# BuildWise-AI — Phase 10: GPU Benchmark Target Audit

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 10 — Machine Learning Dataset Audit, Feature Engineering and Training Data Preparation  
**Target Variable:** `timespy_graphics_score`  
**Source Dataset:** `data/benchmarks.csv` (57 GPU records)  
**Catalog Reference:** `data/components.csv` (218 GPU records)  

---

## 1. Executive Summary & Verification Findings

An exhaustive data integrity audit was conducted on the GPU benchmark records in `data/benchmarks.csv`. The production catalog contains 218 graphics card models, of which 57 possess verified empirical benchmark observations for **3DMark Time Spy Graphics Score**, representing **26.15% catalog coverage**.

| Audit Metric | Expected Requirement | Actual Audit Result | Status |
|---|---|---|---|
| **Catalog GPU Records** | 218 components | 218 components | **VERIFIED** |
| **GPU Benchmark Observations** | 57 records | 57 records | **VERIFIED** |
| **Catalog Coverage** | 26.15% | 26.15% (57 / 218) | **VERIFIED** |
| **Suite Consistency** | `3DMark Time Spy` | 57 / 57 records match `3DMark Time Spy` | **VERIFIED** |
| **Metric Consistency** | `Graphics Score` | 57 / 57 records match `Graphics Score` | **VERIFIED** |
| **Unit Consistency** | `pts` | 57 / 57 records specify `pts` | **VERIFIED** |
| **Missing / Null Scores** | 0 nulls | 0 nulls, 0 NaNs | **VERIFIED** |
| **Negative / Zero Scores** | 0 non-positive | 0 non-positive | **VERIFIED** |
| **Duplicate Benchmark IDs** | 0 duplicates | 57 unique IDs across 57 rows | **VERIFIED** |
| **Duplicate Component IDs** | 0 duplicates | 57 unique CIDs across 57 rows | **VERIFIED** |
| **Referential Integrity** | All CIDs in catalog | 57 / 57 exist in `components.csv` (category: `gpu`) | **VERIFIED** |

---

## 2. Metric Isolation & Anti-Contamination Safeguards

A critical audit check verified that `timespy_graphics_score` is strictly isolated from incompatible performance metrics:
1. **No Time Spy Overall / CPU Score Contamination:** 3DMark Time Spy outputs an Overall Score (which weights CPU physics heavily) and a Graphics Score (which isolates rasterization and shader throughput). All 57 records strictly report the **Graphics Score**, isolating GPU silicon capabilities from host CPU variance.
2. **No Gaming FPS Mixing:** Synthetic benchmark points are never conflated with game-specific frame rates (FPS).
3. **No Target Synthesis:** The 161 catalog GPUs lacking benchmark records are not filled with artificial scores or interpolated values. They are retained in `data/components.csv` for catalog browsing, compatibility inspection, and future model inference, but are strictly excluded from the supervised training dataset.

---

## 3. Descriptive Statistical Distribution

The target variable `timespy_graphics_score` reflects genuine empirical testing across mainstream and enthusiast desktop GPU generations:

$$\text{Count} = 57 \quad|\quad \mu = 15,902.37 \text{ pts} \quad|\quad \sigma = 7,091.62 \text{ pts}$$

| Statistical Percentile | Score Value (pts) | Representative GPU Silicon |
|---|---:|---|
| **Minimum (0%)** | 4,780 | Entry-level silicon (e.g. RTX 3050 6GB / RX 6500 XT) |
| **First Quartile (25%)** | 10,687 | Budget 1080p graphics cards (e.g. RTX 3060 12GB, RX 6600) |
| **Median (50%)** | 13,820 | Mainstream 1440p graphics cards (e.g. RTX 4060, RX 7600 XT, Arc B580) |
| **Third Quartile (75%)** | 19,420 | High-end 1440p / Entry 4K graphics cards (e.g. RTX 4070, RX 7800 XT) |
| **Maximum (100%)** | 36,742 | Enthusiast 4K halo silicon (NVIDIA GeForce RTX 4090) |

---

## 4. Benchmark Provenance & Review Sources

All 57 observations are sourced from established independent hardware review publications with verified empirical testing rigs:
- **Guru3D Direct / Lab Benchmarks:** 34 observations (59.6%)
- **VideoCardz / Guru3D Database:** 8 observations (14.0%)
- **Guru3D / TechPowerUp Cross-Verified:** 3 observations (5.3%)
- **TweakTown / Guru3D Database:** 3 observations (5.3%)
- **TechPowerUp Direct:** 3 observations (5.3%)
- **ComputerBase / TechPowerUp Database:** 2 observations (3.5%)
- **Other Verified Laboratories (LanOC, Overclock3D, PurePC):** 4 observations (7.0%)

Every record includes a direct URL and documented driver/environment metadata.

---

## 5. Mapping into Derived ML Target

In the prepared ML regression dataset (`experiments/performance_prediction/data/gpu_training_dataset.csv`), the target variable is mapped as:

```python
TARGET_COLUMN = "timespy_graphics_score"
```

- **Traceability Reference:** Preserves `component_id` and `benchmark_id` as metadata (excluded from feature matrix $X$).
- **Sample Size Consideration:** With $N = 57$ observations, GPU regression will be evaluated with careful group-aware validation and documented limitations in Phase 11.
