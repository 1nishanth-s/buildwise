# BuildWise-AI — Phase 9: Test Execution Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 9 — Guided PC Build Mode and Upgrade Mode  
**Test Runner:** `python -m unittest discover -s tests -v`  
**Overall Status:** **109 / 109 Tests Passed (100% Success)**  

---

## 1. Test Suite Architecture and Inventory

To validate Phase 9 without weakening any historical regression coverage, a dedicated test file `tests/test_guided_workflow.py` was introduced alongside existing project test suites:

| Test File | Test Class | Focus Area | Tests Count | Status |
|---|---|---|---:|---|
| `tests/test_guided_workflow.py` | `GuidedWorkflowBuildModeTests` | Sequential category selection, compatibility revalidation, budget tracking, missing prices | 8 | **Passed** |
| `tests/test_guided_workflow.py` | `GuidedWorkflowUpgradeModeTests` | Retained hardware evaluation, empirical CPU/GPU benchmark comparisons, missing data | 5 | **Passed** |
| `tests/test_guided_workflow.py` | `GuidedWorkflowSafeguardsTests` | Anti-combinatorial guarantees, SHA-256 dataset protection | 2 | **Passed** |
| `tests/test_recommendation.py` | `ModernApplicationAndCatalogTests` | App startup, catalog loading, price lookup, engine retirement verification | 11 | **Passed** |
| `tests/test_compatibility.py` | `CompatibilityRuleTests` | Deterministic socket, form-factor, RAM, PSU, cooler, and storage rules | 47 | **Passed** |
| `tests/test_validator.py` | `ValidatorTests` | CSV schemas, foreign keys, price formats, JSON integrity | 14 | **Passed** |
| `tests/test_cpu_ml_regression.py` | `CpuMlRegressionPipelineTests` | Holdout evaluation, pipeline invariants, experiment regression tests | 20 | **Passed** |
| `tests/test_performance_tier.py` | `PerformanceTierExperimentTests` | Tiering datasets, grouped cross-validation | 2 | **Passed** |
| **Total** | | | **109** | **109 / 109 Passed** |

---

## 2. Detailed Results for `tests/test_guided_workflow.py`

| Test Method | Category | Verified Requirement | Result |
|---|---|---|---|
| `test_build_categories_order_and_labels` | Build Mode | Exact 8-step sequential selection order: CPU $\rightarrow$ Motherboard $\rightarrow$ RAM $\rightarrow$ Case $\rightarrow$ GPU $\rightarrow$ PSU $\rightarrow$ Cooler $\rightarrow$ Storage. | **PASS** |
| `test_component_filtering_by_category` | Build Mode | All 8 hardware categories filter cleanly with $>10$ catalog records each. | **PASS** |
| `test_cpu_motherboard_compatibility_check` | Build Mode | Motherboard socket matches CPU socket (AM5 vs AM5 $\rightarrow$ compatible/unknown; AM5 vs LGA1700 $\rightarrow$ incompatible). | **PASS** |
| `test_motherboard_ram_compatibility_check` | Build Mode | RAM generation match against Motherboard (DDR5 on DDR5 $\rightarrow$ compatible; DDR4 on DDR5 $\rightarrow$ incompatible). | **PASS** |
| `test_multiple_component_selections_retention` | Build Mode | Complete 8-component build configuration is retained in state simultaneously. | **PASS** |
| `test_changing_earlier_component_triggers_revalidation` | Build Mode | Changing earlier CPU from AM5 to LGA1700 dynamically flags conflict with selected AM5 motherboard. | **PASS** |
| `test_budget_totals_and_missing_price_handling` | Build Mode | Sums available prices accurately; unpriced items are flagged and never treated as ₹0; seller obs vs estimates distinguished. | **PASS** |
| `test_unknown_compatibility_preserved` | Build Mode | Empty/incomplete specifications produce `unknown`, never falling back to `compatible`. | **PASS** |
| `test_cpu_benchmark_comparison_same_metric` | Upgrade Mode | Cinebench R23 Multi-Core score delta (+2,637 pts / +14.8%) calculated correctly between comparable CPUs. | **PASS** |
| `test_gpu_benchmark_comparison_same_metric` | Upgrade Mode | 3DMark Time Spy Graphics Score delta (-8,100 pts / -22.0%) calculated correctly between comparable GPUs. | **PASS** |
| `test_cross_category_and_missing_benchmark_handling` | Upgrade Mode | Cross-category (CPU vs GPU) comparison rejected; missing benchmarks report unavailable. | **PASS** |
| `test_upgrade_candidate_compatibility_against_retained_hardware` | Upgrade Mode | Candidate GPU clearance evaluated against retained case; wattage checked against retained PSU. | **PASS** |
| `test_upgrade_mode_with_unknown_retained_hardware` | Upgrade Mode | Unknown retained motherboard safely produces `unknown` status for CPU upgrade without exceptions. | **PASS** |
| `test_anti_combinatorial_guarantees` | Safeguards | Confirms `build_recommendation`, DFS, and Cartesian product generators do not exist. | **PASS** |
| `test_dataset_checksums_remain_unmodified` | Safeguards | Confirms `components.csv`, `prices.csv`, `benchmarks.csv` match exact Phase 7/8 SHA-256 hashes. | **PASS** |

---

## 3. Full Test Suite Execution Summary

```
======================================================================
Ran 109 tests in 42.888s

OK
```

- **Passed:** 109
- **Failed:** 0
- **Errors:** 0
- **Skipped:** 0
- **Regression Check:** All 94 pre-existing Phase 8 unit tests passed without regression.
