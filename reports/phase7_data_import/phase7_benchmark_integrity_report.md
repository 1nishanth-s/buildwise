# BuildWise-AI — Phase 7 Hardware Benchmark Integrity Report

**Execution Timestamp:** 2026-11-08T14:24:30+05:30  
**Executing Role:** Senior PC Hardware Research Engineer, Data Engineer & Machine Learning Dataset Specialist  
**Dataset Under Audit:** Live Production Hardware Benchmarks (`data/benchmarks.csv`)  
**Audit Status:** `100% PASSED — INTEGRITY VERIFIED`  

---

## 1. Overview & Metric Scope

The production benchmark dataset has been expanded from 112 baseline observations to **237 empirical benchmark observations**.

| Benchmark Suite | Benchmark Metric | Category | Baseline Observations | Added Candidate Observations | Total Production Observations | Target Hardware Population | Population Coverage |
|---|---|---|---:|---:|---:|---:|---:|
| Cinebench R23 | Multi-Core Score | CPU | 55 | 125 | 180 | 180 CPUs | **100.0% (180 / 180)** |
| 3DMark Time Spy | Graphics Score | GPU | 57 | 0 | 57 | 218 GPUs | 26.1% (57 / 218) |
| **Total** | — | — | **112** | **125** | **237** | — | — |

---

## 2. Referential Integrity & Primary Key Validation

- **Total Benchmark Rows:** 237
- **Unique `benchmark_id` Values:** 237 (0 collisions, 0 duplicates)
- **Foreign Key Validity:** 237 out of 237 `component_id` foreign keys resolve to a valid component in `data/components.csv` (0 orphaned benchmarks).
- **CPU 100% Coverage Verification:** Every single CPU in the 180-CPU catalog has an empirical Cinebench R23 Multi-Core score.

---

## 3. Score Validity & Metric Units

- **Null / NaN Score Values:** 0
- **Negative or Zero Scores:** 0
- **Score Unit:** All 237 records use standardized unit `"pts"`.
- **Cinebench R23 Multi-Core Range:**
  - Minimum Score: 3,420 pts (Entry-level quad-core CPU)
  - Maximum Score: 41,850 pts (High-end desktop flagship CPU)
- **3DMark Time Spy Graphics Range:**
  - Minimum Score: 2,650 pts (Entry-level discrete GPU)
  - Maximum Score: 36,450 pts (Ultra-enthusiast flagship GPU)

---

## 4. Strict Quarantine Adherence

In compliance with project architecture rules:
1. **Candidate GPU Benchmarks:** 143 candidate GPU benchmark observations from Phase 5 (`staged_batch10_gpu_benchmarks.csv`) were **STRICTLY QUARANTINED** (0 imported). GPU ML modeling will be conducted in a separate dedicated phase.
2. **System Gaming FPS Benchmarks:** 35 full-system gaming FPS observations from Phase 5 (`staged_batch11_gaming_benchmarks.csv`) were **STRICTLY QUARANTINED** (0 imported).
3. **Proposed Peripheral Benchmarks:** 9 proposed peripheral/monitor benchmarks from Phase 5 (`staged_batch12_proposed_categories.csv`) were **STRICTLY QUARANTINED** (0 imported).
