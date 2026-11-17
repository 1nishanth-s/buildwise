# BuildWise-AI — Phase 8 Code Audit & Redundancy Report

**Execution Timestamp:** 2026-11-08T14:48:00+05:30  
**Executing Role:** Senior PC Hardware Research Engineer, Data Engineer & Python Developer  
**Scope:** Repository-wide audit of `app.py`, `src/`, `tests/`, and `experiments/`  
**Status:** `CODE AUDIT COMPLETE — CLEANUP TARGETS IDENTIFIED`  

---

## 1. Executive Summary

A comprehensive codebase audit was conducted across all Python modules, test suites, and ML experiments in BuildWise-AI.

The audit sought to identify:
1. Duplicate or near-duplicate function/class definitions.
2. Dead or unreachable code.
3. Obsolete recommendation engine code scheduled for removal under Phase 8.
4. Hardcoded baseline test assumptions requiring modernization.
5. Reusable core libraries that must be strictly preserved.

---

## 2. Inventory of Audited Modules

| Module / Directory | Line Count / Files | Primary Responsibility | Audit Finding |
|---|---|---|---|
| `app.py` | 876 lines | Streamlit UI and legacy recommendation engine | Contains legacy unpruned DFS combination generator (`build_recommendation`) and associated helper `_check_candidate_compatibility` (lines 257–749). These 492 lines are obsolete and cause combinatorial timeouts on the 1,208-component catalog. |
| `src/compatibility.py` | 650 lines | Core deterministic hardware compatibility engine | **Clean & Non-Redundant.** Contains 11 dedicated compatibility checking functions (CPU/motherboard, RAM QVL, GPU clearance, PSU sizing, cooler mounting, storage lanes). Must be **100% preserved**. |
| `src/validator.py` | 196 lines | Data loader, schema checks, price integrity | **Clean & Non-Redundant.** Validates CSV headers, JSON syntax, price bounds, retailer domains. Must be **100% preserved**. |
| `experiments/performance_tier/train.py` | 420 lines | Feature extraction, stratified CV, classification models | **Clean & Non-Redundant.** Trains 5 ML classification models for CPU tiering. Must be **100% preserved**. |
| `experiments/cpu_benchmark_regression/` | Multiple files | CPU Cinebench R23 regression models (v1 and v2) | **Clean & Non-Redundant.** Preserved for ML modeling pipeline. |
| `tests/test_compatibility.py` | 47 tests | Unit tests for compatibility rules | **Clean & Passing.** 47 / 47 tests passing. |
| `tests/test_validator.py` | 14 tests | Unit tests for data loading and schema rules | **Clean & Passing.** 14 / 14 tests passing. |
| `tests/test_cpu_ml_regression.py` | 20 tests | Unit tests for CPU regression pipeline | **Clean & Passing.** 20 / 20 tests passing. |
| `tests/test_performance_tier.py` | 2 tests | Performance tier ML tests | Contains hardcoded assertions tied to the old 30-CPU baseline dataset (`len == 30`, `train == 21`). Needs update to dynamic dataset counts. |
| `tests/test_recommendation.py` | 29 tests | Legacy recommendation engine tests | Exclusively tests the retired exhaustive `build_recommendation()` engine via `AppTest`. Needs replacement with tests verifying catalog browsing, component filtering, and absence of legacy DFS. |

---

## 3. Duplicate and Obsolete Code Analysis

### 3.1 Obsolete Exhaustive Recommendation Engine in `app.py`
- **Symbols Identified for Removal:**
  - `_check_candidate_compatibility(selected_rows)`: Evaluated compatibility incrementally across combination sets during DFS traversal.
  - `build_recommendation(components, prices, budget_inr, ...)`: Unpruned recursive depth-first search that attempted to enumerate all complete PC builds from the Cartesian product of priced parts.
  - `PURPOSE_LAYOUT`: Mapping of build purpose to category sequence.
  - Streamlit form `st.form("budget_recommendation")`: Triggered exhaustive recommendation search.
- **Safety Assessment:** Safe to remove. These symbols are not imported by `src/` or any production service. Removing them eliminates the $8.4 \times 10^{10}$ Cartesian explosion.

### 3.2 Reusable Utilities Preserved in `app.py`
The following utilities are independent of the exhaustive search and are preserved to power the catalog browser and future guided workflow:
- `is_indian_retailer_url(url)`
- `evaluate_indian_market_presence(entries)`
- `parse_specs(raw_value)`
- `price_to_int(raw_value)`
- `observation_freshness(checked_at, freshness_days, now=None)`
- `price_lookup(prices_frame, freshness_days, now=None)`
- `choose_cheapest_price(component_id, prices_lookup, prefer_available=False)`
- `INDIAN_RETAILER_DOMAINS`
- `DEFAULT_AVAILABILITY_FRESHNESS_DAYS`

---

## 4. Code Cleanup Plan

1. **Refactor `app.py`:**
   - Remove `_check_candidate_compatibility`, `build_recommendation`, `PURPOSE_LAYOUT`, and the legacy recommendation form.
   - Implement the temporary interactive Streamlit interface:
     - Header & Introduction: "BuildWise-AI — PC Component Intelligence System"
     - Dataset Overview: Real-time metrics for components, prices, benchmarks, and category breakdown.
     - Component Catalog Browser: Category selector, brand/model filter, specs inspection, seller pricing display with freshness indicators, and Cinebench / Time Spy benchmark display.
     - Direct Hardware Compatibility Inspector: Interactive tool allowing users to select two components (e.g. CPU + Motherboard, or GPU + Case) to evaluate real-time compatibility using `src/compatibility.py`.
     - Future Workflow Notice: Explicit banner informing users of the retirement of exhaustive DFS and announcing upcoming guided Build Mode and ML predictions.
2. **Modernize `tests/test_performance_tier.py`:**
   - Update `len(live_features)` to calculate dynamically based on `prepare_cpu_dataset()`.
   - Update `first["preliminary_holdout"]["train_examples"]` to calculate based on the configured 70/30 split.
3. **Update `tests/test_recommendation.py`:**
   - Retire tests that exclusively invoke the retired `build_recommendation` function.
   - Replace with tests verifying:
     - Application loading and dataset rendering without errors.
     - Reusable pricing and freshness utilities.
     - Direct compatibility inspection.
     - Absence of any unpruned recursive DFS or `build_recommendation` execution.
