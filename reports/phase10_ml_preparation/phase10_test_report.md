# BuildWise-AI — Phase 10 Test Suite Execution Report

## 1. Executive Summary

As part of Phase 10 (*Machine Learning Dataset Audit, Feature Engineering and Training Data Preparation*), a dedicated unit test suite was developed to guarantee dataset cleanliness, leak-free feature engineering, group-aware cross-validation, strict empirical benchmark target handling, and production dataset immutability.

Both the specialized Phase 10 test suite and the complete system regression test suite were executed in the project virtual environment (`E:\BuildWise-AI\BuildWise-AI1\.venv\Scripts\python.exe`).

| Test Suite | Total Tests | Passed | Failed | Errors | Status | Duration |
|---|---|---|---|---|---|---|
| **Phase 10 Dataset Preparation Tests** | 18 | 18 | 0 | 0 | **PASS** | 0.623s |
| **Full System Regression Suite** | 127 | 127 | 0 | 0 | **PASS** | 52.733s |
| **Production Data Validator (`validate_data.py`)** | N/A | N/A | 0 | 0 | **PASS** | 1.812s |

---

## 2. Phase 10 Dedicated Unit Test Suite (`tests/test_ml_dataset_preparation.py`)

The test suite contains 18 comprehensive tests structured across data filtering, target isolation, specification parsing, leakage prevention, reproducible derivation, and production safety.

### Test Case Verification Breakdown

| Test ID | Test Method | Scope & Assertion | Result |
|---|---|---|---|
| 01 | `test_01_cpu_benchmark_filtering` | Verifies that CPU training data strictly filters Cinebench R23 records and excludes other test types. | **PASS** |
| 02 | `test_02_gpu_benchmark_filtering` | Verifies that GPU training data strictly filters 3DMark Time Spy records and excludes other benchmark runs. | **PASS** |
| 03 | `test_03_correct_benchmark_metric_selection` | Verifies CPU target is strictly Cinebench R23 Multi-Core and GPU target is strictly Time Spy Graphics Score. | **PASS** |
| 04 | `test_04_correct_target_extraction` | Verifies continuous positive numeric values across all target records ($y > 0$). | **PASS** |
| 05 | `test_05_valid_component_id_mapping` | Verifies every dataset record links to an existing component in `data/components.csv`. | **PASS** |
| 06 | `test_06_valid_specification_json_parsing` | Confirms resilient JSON parsing for valid strings, pre-parsed dicts, and invalid/malformed JSON. | **PASS** |
| 07 | `test_07_correct_numerical_unit_conversion` | Confirms CPU clocks in GHz, GPU clocks in MHz, TDP/TBP in Watts, bus width in bits, bandwidth in GB/s. | **PASS** |
| 08 | `test_08_correct_categorical_feature_extraction` | Confirms categorical normalization (brands, architectures, sockets, memory types) without empty strings. | **PASS** |
| 09 | `test_09_missing_feature_handling` | Confirms base clock missingness in 30 CPUs is properly surfaced as NaN and not synthetic imputed values. | **PASS** |
| 10 | `test_10_invalid_feature_handling` | Confirms feature extractors reject non-positive cores, invalid specs, or corrupt specification payloads. | **PASS** |
| 11 | `test_11_missing_benchmark_target_exclusion` | Confirms unbenchmarked GPUs (161 components) are strictly excluded from the GPU training dataset. | **PASS** |
| 12 | `test_12_no_benchmark_target_leakage_into_features` | Confirms that feature matrices exclude target scores and benchmark columns to prevent target leakage. | **PASS** |
| 13 | `test_13_no_component_id_used_as_predictor` | Confirms identifiers (`component_id`, `name`, `group_id`, `url`) are excluded from feature allowlists. | **PASS** |
| 14 | `test_14_dataset_creation_reproducibility` | Confirms calling preparation scripts multiple times produces bit-for-bit identical DataFrames. | **PASS** |
| 15 | `test_15_group_aware_splitting_behavior` | Confirms GroupKFold and GroupShuffleSplit enforce 100% group isolation between train and validation folds. | **PASS** |
| 16 | `test_16_cpu_and_gpu_dataset_separation` | Confirms CPU and GPU datasets remain completely isolated with zero schema overlap or shared records. | **PASS** |
| 17 | `test_17_traceability_to_original_records` | Confirms every training row can be mapped back to verified component and benchmark IDs. | **PASS** |
| 18 | `test_18_no_modification_of_production_csv_files` | Confirms that production datasets retain identical SHA-256 hashes before and after ML preparation. | **PASS** |

---

## 3. Full System Regression Test Suite Execution

To confirm zero regression across the application, guided workflow, validator, and compatibility engine, the full project test suite was executed:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Module Summary

- `tests/test_compatibility_engine.py`: 18 tests passed.
- `tests/test_guided_workflow.py`: 24 tests passed.
- `tests/test_modern_catalog_and_app.py`: 12 tests passed.
- `tests/test_validator.py`: 14 tests passed.
- `tests/test_performance_tier.py`: 2 tests passed.
- `tests/test_cpu_ml_regression.py`: 16 tests passed.
- `tests/test_recommendation.py`: 23 tests passed.
- `tests/test_ml_dataset_preparation.py`: 18 tests passed.

**Total:** 127 tests executed.  
**Result:** `Ran 127 tests in 52.733s — OK` (0 failures, 0 errors, 0 skipped).

---

## 4. Production Data Validator Execution

The existing standalone production validator was executed:

```powershell
.\.venv\Scripts\python.exe validate_data.py
```

### Validator Output

```text
Component rows: 1208
Price observations: 599
Validation passed. Note: an empty template is valid, but it cannot generate recommendations yet.
```

Exit code: `0`.

---

## 5. Conclusion

All 18 Phase 10 ML dataset preparation tests passed with zero errors or warnings. The complete suite of 127 system tests confirmed that the derived ML datasets, feature engineering modules, and validation splitters operate in total isolation without compromising production application stability or data integrity.
