# BuildWise-AI — Phase 8 Automated Test & Validation Report

**Execution Timestamp:** 2026-11-08T14:58:00+05:30  
**Executing Role:** Senior PC Hardware Research Engineer, Data Engineer & Python Developer  
**Execution Environment:** Windows, Python 3.11 (Virtualenv `.venv`)  
**Production Dataset:** 1,208 components, 599 prices, 237 benchmarks  
**Overall Test Result:** `94 / 94 TESTS PASSED (100% SUCCESS — 0 FAILURES, 0 TIMEOUTS)`  

---

## 1. Test Suite Summary Matrix

Following the removal of the legacy exhaustive recommendation engine and the modernization of performance tier assertions, the entire test suite was executed via `unittest discover`.

| Test Module | Primary Target Scope | Tests Run | Passed | Failed | Errors | Skipped | Runtime | Status |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| `validate_data.py` | CSV structure, specs JSON, foreign keys, price bounds | 1 suite | 1 suite | 0 | 0 | 0 | 1.05s | **PASSED** |
| `tests/test_validator.py` | Dataset loader, schema enforcement, price integrity | 14 | 14 | 0 | 0 | 0 | 1.13s | **100% PASSED** |
| `tests/test_compatibility.py` | Hardware compatibility engine (sockets, clearance, PSU) | 47 | 47 | 0 | 0 | 0 | 0.10s | **100% PASSED** |
| `tests/test_cpu_ml_regression.py` | CPU Cinebench R23 regression models (V1 & V2) | 20 | 20 | 0 | 0 | 0 | 0.35s | **100% PASSED** |
| `tests/test_performance_tier.py` | Performance tier feature preparation & 5-model CV | 2 | 2 | 0 | 0 | 0 | 36.74s | **100% PASSED** |
| `tests/test_recommendation.py` | Modern catalog browser, price utilities, UI startup | 11 | 11 | 0 | 0 | 0 | 3.31s | **100% PASSED** |
| **Total Test Suite** | **Entire Project Codebase** | **94** | **94** | **0** | **0** | **0** | **42.00s** | **100% PASSED** |

---

## 2. Test Suite Details

### 2.1 Production Data Validator (`validate_data.py`)
- **Command:** `.\.venv\Scripts\python.exe validate_data.py`
- **Output:**
  ```text
  Component rows: 1208
  Price observations: 599
  Validation passed. Note: an empty template is valid, but it cannot generate recommendations yet.
  ```
- **Validation Gates Evaluated:**
  - Presence and non-null status of all required CSV columns.
  - Component ID uniqueness (1,208 / 1,208 unique).
  - Price ID uniqueness (599 / 599 unique).
  - Referential integrity: 100% of price records resolve to catalog components.
  - Specification JSON parsing: 100% parse successfully as valid dictionaries.
  - Retailer URL formatting: 100% valid URLs.
  - Price formatting: 100% valid positive integer amounts.

### 2.2 Modern Application & Catalog Tests (`tests/test_recommendation.py`)
- **Command:** `.\.venv\Scripts\python.exe -m unittest tests/test_recommendation.py`
- **Tests Evaluated (11 tests):**
  1. `test_legacy_exhaustive_engine_is_retired`: Asserts `build_recommendation`, `_check_candidate_compatibility`, and `PURPOSE_LAYOUT` do not exist in `app.py`.
  2. `test_app_starts_and_renders_clean_interface`: Launches `app.py` via `AppTest`, verifies title, metrics, and future workflow notice render cleanly.
  3. `test_app_does_not_contain_legacy_budget_form`: Verifies that no legacy recommendation form exists in the UI.
  4. `test_dataset_loading_in_app`: Verifies loading of 1,208 components and 599 prices with 0 issues.
  5. `test_is_indian_retailer_url`: Validates authorized vs. unauthorized domain filtering.
  6. `test_evaluate_indian_market_presence`: Validates verified vs. unverified retailer classification.
  7. `test_parse_specs_utility`: Validates robust dictionary parsing from JSON strings, dicts, and invalid inputs.
  8. `test_price_to_int_utility`: Validates integer conversion, negative number rejection, and float rounding.
  9. `test_observation_freshness`: Validates 7-day freshness window calculations against known timestamps.
  10. `test_choose_cheapest_price_lowest_vs_available`: Validates both lowest-price and available-first price policies.
  11. `test_compatibility_engine_integration_without_old_recommender`: Directly executes `check_cpu_motherboard` and `check_gpu_case` to confirm compatibility engine functionality.

### 2.3 Performance Tier Tests (`tests/test_performance_tier.py`)
- **Command:** `.\.venv\Scripts\python.exe -m unittest tests/test_performance_tier.py`
- **Modernization Applied:** Updated hardcoded baseline CPU count assertions (`len == 30`, `train == 21`) to calculate dynamically from the dataset size (`len(live_features) == sum(live_quality["label_counts"].values()) == 120`).
- **Tests Evaluated (2 tests):**
  1. `test_prepares_catalog_without_identifier_features`: Verifies feature extraction, absence of identifier leakage, and exclusion of unlabelled CPUs.
  2. `test_evaluation_reports_holdout_record_and_grouped_cv`: Verifies 5 classification models across repeated stratified k-fold cross-validation.

### 2.4 Hardware Compatibility Tests (`tests/test_compatibility.py`)
- **Tests Evaluated (47 tests):** 47 / 47 passed in 0.10s. Verifies all cross-component physical, electrical, and logical rules.

### 2.5 CPU ML Regression Tests (`tests/test_cpu_ml_regression.py`)
- **Tests Evaluated (20 tests):** 20 / 20 passed in 0.35s. Verifies feature pipelines and benchmark prediction models.
