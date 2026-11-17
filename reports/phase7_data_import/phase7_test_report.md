# BuildWise-AI — Phase 7 Automated Test & Validation Report

**Execution Timestamp:** 2026-11-08T14:27:30+05:30  
**Executing Role:** Senior PC Hardware Research Engineer, Data Engineer & Machine Learning Dataset Specialist  
**Execution Environment:** Windows, Python 3.11 (Virtualenv `.venv`)  
**Live Production Data:** 1,208 components, 599 prices, 237 benchmarks  

---

## 1. Test Suite Execution Summary

In accordance with Phase 7 instructions, the expanded datasets were imported into production and validated independently of the legacy recommendation engine. Existing test files and application code were kept completely untouched (no test rewrites to force passing).

| Test Module / Script | Scope / Target Area | Total Tests | Passed | Failed | Skipped | Status / Note |
|---|---|---:|---:|---:|---:|:---:|
| `validate_data.py` | CSV schema, JSON specs, ID integrity, null checks | 1 suite | 1 suite | 0 | 0 | **PASSED (0 errors)** |
| `tests/test_validator.py` | Data loader, schema constraints, price rules | 14 | 14 | 0 | 0 | **100% PASSED** |
| `tests/test_compatibility.py` | Cross-component compatibility engine rules | 47 | 47 | 0 | 0 | **100% PASSED** |
| `tests/test_cpu_ml_regression.py` | CPU Cinebench R23 regression models & ML pipeline | 20 | 20 | 0 | 0 | **100% PASSED** |
| `tests/test_performance_tier.py` | Performance tier classification on live catalog | 2 | 0 | 2 | 0 | **FAILED (Hardcoded Baseline CPU Count)** |
| `tests/test_recommendation.py` | Legacy exhaustive DFS recommendation engine | 29 | — | — | — | **KNOWN LIMITATION (AppTest Timeout)** |
| **Total Automated Tests Evaluated** | — | **83** | **81** | **2** | **0** | **97.6% (Excl. Legacy Recommender)** |

---

## 2. Detailed Test Results by Module

### 2.1 `validate_data.py`
- **Command:** `.\.venv\Scripts\python.exe validate_data.py`
- **Output:**
  ```text
  Component rows: 1208
  Price observations: 599
  Validation passed. Note: an empty template is valid, but it cannot generate recommendations yet.
  ```
- **Execution Time:** 1.05s
- **Result:** PASSED (0 errors).

### 2.2 `tests/test_validator.py`
- **Command:** `.\.venv\Scripts\python.exe -m unittest tests/test_validator.py`
- **Execution Time:** 1.129s
- **Tests Evaluated:** 14 tests
  - Schema column structure validation
  - Empty catalog handling
  - Valid component category enforcement
  - Component ID uniqueness enforcement
  - specs_json dictionary parsing
  - Valid integer price parsing
  - Retailer URL validation
  - Availability status enforcement
  - Provenance tracking verification
- **Result:** OK (14 / 14 passed).

### 2.3 `tests/test_compatibility.py`
- **Command:** `.\.venv\Scripts\python.exe -m unittest tests/test_compatibility.py`
- **Execution Time:** 0.098s
- **Tests Evaluated:** 47 tests
  - Socket matching (AM4, AM5, LGA1700, LGA1200, LGA1851)
  - Motherboard RAM generation (DDR4 vs DDR5)
  - Motherboard RAM capacity and slot count limits
  - RAM speed and QVL matching
  - Motherboard to Case form factor compatibility (ATX, mATX, ITX)
  - Storage interface and form factor matching (M.2 NVMe, SATA)
  - GPU physical length vs case maximum clearance
  - GPU power connectors and recommended PSU wattage
  - PSU dimensions and chassis clearance
  - CPU cooler height vs case maximum cooler clearance
  - CPU cooler mounting bracket socket support
  - Three-state evaluation (`compatible`, `incompatible`, `unknown`)
- **Result:** OK (47 / 47 passed).

### 2.4 `tests/test_cpu_ml_regression.py`
- **Command:** `.\.venv\Scripts\python.exe -m unittest tests/test_cpu_ml_regression.py`
- **Execution Time:** 0.353s
- **Tests Evaluated:** 20 tests
  - Feature extraction and normalization pipeline
  - Benchmark score regression targets
  - Model cross-validation and evaluation metrics
  - Multi-core score prediction fidelity
  - ML dataset integrity and absence of data leakage
- **Result:** OK (20 / 20 passed).

### 2.5 `tests/test_performance_tier.py`
- **Command:** `.\.venv\Scripts\python.exe -m unittest tests/test_performance_tier.py`
- **Execution Time:** 47.390s
- **Tests Evaluated:** 2 tests
- **Failures Recorded:**
  1. `test_prepares_catalog_without_identifier_features`:
     ```text
     AssertionError: 120 != 30
     ```
     *Root Cause:* Line 86 asserts `self.assertEqual(len(live_features), 30)`. In the baseline 64-CPU catalog, exactly 30 CPUs possessed performance tier labels. In the expanded 180-CPU catalog, 120 CPUs possess performance tier labels.
  2. `test_evaluation_reports_holdout_record_and_grouped_cv`:
     ```text
     AssertionError: 84 != 21
     ```
     *Root Cause:* Line 97 asserts `self.assertEqual(first["preliminary_holdout"]["train_examples"], 21)`. The 70% train split on 30 baseline labeled CPUs was 21; on the expanded 120 labeled CPUs, 70% of 120 is 84.
- **Result:** 2 test failures due to hardcoded baseline count assertions against `data/components.csv`. In strict compliance with instructions, the test assertions were **not rewritten** to force passing.

---

## 3. Documentation of Legacy Recommendation Engine Limitation

As explicitly anticipated in the Phase 7 task directive:
> *"The previous Phase 6E import was rolled back because the existing exhaustive recommendation engine could not handle the expanded dataset efficiently. This time, import and validate the data independently of that engine... Do not launch the complete Streamlit recommendation workflow as part of this phase if it triggers the known exhaustive search and becomes unresponsive. Do not mistake that existing limitation for a dataset import failure."*

### Root Cause Analysis of `test_recommendation.py` Limitation:
1. **Combinatorial Complexity:** `build_recommendation()` in `app.py` implements an unpruned depth-first search across the Cartesian product of priced components. With 599 prices ($60 - 84$ priced items per category), the theoretical combinations exceed $8.4 \times 10^{10}$ for 6-part builds and $4.3 \times 10^{14}$ for 8-part gaming builds.
2. **Streamlit AppTest Timeout:** Streamlit's `AppTest` framework imposes a hard 10-second timeout. Because the unpruned search cannot complete on high-budget builds within 10 seconds, AppTest terminates execution.
3. **Hardcoded Legacy Fixtures:** Tests such as `test_rm750x_estimate_counts_toward_budget_and_is_labeled` asserted specific legacy planning estimates (₹29,370) that are replaced by genuine verified retail offers (Computech Store ₹8,550).
4. **Resolution Roadmap:** This legacy recommendation search will be reviewed, optimized, or replaced with a scalable guided recommendation workflow in a subsequent dedicated phase.
