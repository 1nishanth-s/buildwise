# BuildWise-AI — Phase 9: Benchmark Comparison Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 9 — Guided PC Build Mode and Upgrade Mode  
**Scope:** Empirical Benchmark Records, Comparison Rules, Performance Delta Calculations, and Machine Learning Boundaries  

---

## 1. Production Benchmark Dataset Baseline

`data/benchmarks.csv` contains 237 empirical hardware performance observations across two sanctioned, industry-standard benchmark suites:

| Benchmark Suite | Hardware Category | Target Benchmark Metric | Records Count | Typical Sources |
|---|---|---|---:|---|
| **Cinebench R23** | CPU | `Multi-Core Score` (pts) | 180 | CPU-Monkey, Notebookcheck, TechPowerUp |
| **3DMark Time Spy** | GPU | `Graphics Score` (pts) | 57 | Guru3D, TechPowerUp, 3DMark Leaderboard |

---

## 2. Comparison Methodology & Rules

The `compare_benchmarks(comp_a_id, comp_b_id, benchmarks_df)` function implements 6 strict comparison rules mandated by the BuildWise-AI architecture:

1. **Suite and Metric Consistency:** Comparisons are only permitted between records with identical `benchmark_suite` and `benchmark_metric`.
2. **Category Isolation:** CPU benchmarks are never compared with GPU benchmarks. Cross-category queries immediately return:  
   `"Incompatible benchmark suites/metrics: Cinebench R23 (Multi-Core Score) vs 3DMark Time Spy (Graphics Score)"`.
3. **Transparent Score Provenance:** All comparison outputs report the raw empirical score (points), unit, and publishing source name for both baseline and upgrade hardware.
4. **Valid Mathematical Delta:** The percentage difference is calculated strictly when both scores are valid and positive:
   $$\Delta = \text{Score}_B - \text{Score}_A$$
   $$\%\Delta = \left( \frac{\text{Score}_B - \text{Score}_A}{\text{Score}_A} \right) \times 100$$
5. **Missing Benchmark Transparency:** If either component lacks an empirical benchmark record in `data/benchmarks.csv`, the function returns:  
   `{"status": "unavailable", "message": "Benchmark data unavailable"}`.
6. **No Speculative FPS Projections:** Synthetic benchmark points are presented as standardized computational measurements; they are never falsely converted into real-world gaming frame rate (FPS) promises.

---

## 3. Verified Empirical Benchmark Comparison Examples

### 3.1 CPU Multi-Core Comparison
- **Baseline Component:** AMD Ryzen 7 7800X3D (`amd-ryzen-7-7800x3d`)
  - Suite: Cinebench R23
  - Metric: Multi-Core Score
  - Score: `17,762 pts`
  - Source: CPU-Monkey
- **Upgrade Component:** AMD Ryzen 7 7700X (`amd-ryzen-7-7700x`)
  - Score: `20,399 pts`
  - Source: CPU-Monkey
- **Calculated Results:**
  - Delta: `+2,637 pts`
  - Percentage: `+14.8%`
  - Summary: `20,399 vs 17,762 pts (+14.8%)`

### 3.2 GPU Graphics Score Comparison
- **Baseline Component:** NVIDIA GeForce RTX 4070 Ti (`DS3_GPU_036`)
  - Suite: 3DMark Time Spy
  - Metric: Graphics Score
  - Score: `36,742 pts`
  - Source: Guru3D
- **Upgrade Component:** NVIDIA GeForce RTX 4070 (`DS3_GPU_035`)
  - Score: `28,642 pts`
  - Source: Guru3D
- **Calculated Results:**
  - Delta: `-8,100 pts`
  - Percentage: `-22.0%`
  - Summary: `28,642 vs 36,742 pts (-22.0%)`

---

## 4. Machine Learning Boundaries & Future Model Integration

Phase 9 strictly prohibits training ML models or claiming that empirical benchmark scores represent machine learning predictions:
- All benchmark values displayed in BuildWise-AI are empirical observations recorded in `data/benchmarks.csv`.
- Untrained or mock ML models have not been deployed.
- **User Notice:** In all benchmark inspection areas, the application displays:  
  > *"ML-based performance predictions will be available after the project's CPU and GPU models have been trained and evaluated."*
- Future phases will train supervised regression models on hardware architectural features and benchmark targets; Phase 9 establishes the clean presentation interface into which those models will be integrated.

---

## 5. Verification & Test Evidence

Tested in `tests/test_guided_workflow.py`:
- `test_cpu_benchmark_comparison_same_metric`: Passed.
- `test_gpu_benchmark_comparison_same_metric`: Passed.
- `test_cross_category_and_missing_benchmark_handling`: Passed.
