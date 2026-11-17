# BuildWise-AI — Phase 8 Preserved Functionality Report

**Execution Timestamp:** 2026-11-08T14:57:30+05:30  
**Executing Role:** Senior PC Hardware Research Engineer, Data Engineer & Python Developer  
**Status:** `VERIFIED — 100% ESSENTIAL CAPABILITIES PRESERVED`  

---

## 1. Executive Summary

Phase 8 removed only the legacy exhaustive PC combination search and its exclusive UI bindings. All reusable domain logic, hardware compatibility checking, dataset processing, price utilities, and machine learning infrastructure remain completely intact and functional.

---

## 2. Preserved Functional Systems

### 2.1 Hardware Compatibility Engine (`src/compatibility.py`)
- **Status:** **100% PRESERVED (Byte-for-byte unchanged)**
- **File Checksum:** `3161689994113d02f5e7b583fb93ffad272a0839b455ef81ef114476f9ec42af`
- **Active Public Interfaces:**
  - `check_cpu_motherboard(cpu_specs, mb_specs, cpu_component_id=None)`
  - `check_cpu_motherboard_ram(cpu_specs, mb_specs, ram_specs)`
  - `check_motherboard_ram_capacity(mb_specs, ram_specs)`
  - `check_ram_speed_qvl(ram_specs, mb_specs, ram_component_id=None, cpu_specs=None)`
  - `check_motherboard_case(mb_specs, case_specs)`
  - `check_storage_motherboard(storage_specs, mb_specs)`
  - `check_gpu_case(gpu_specs, case_specs)`
  - `check_psu(psu_specs, cpu_specs, gpu_specs)`
  - `check_cooler_socket(cooler_specs, cpu_specs, mb_specs=None)`
  - `check_cooler_case(cooler_specs, case_specs)`
- **Three-State Invariant:** Strictly maintains `compatible`, `incompatible`, and `unknown` evaluations. Missing specifications remain `unknown`, never inferred.
- **Test Coverage:** All 47 unit tests in `tests/test_compatibility.py` pass.

### 2.2 Dataset Loading and Validation Pipeline (`src/validator.py`)
- **Status:** **100% PRESERVED (Byte-for-byte unchanged)**
- **File Checksum:** `8eac18b1f7597f3bea1ae2710ad4f68b78866aa034fb3f933cbedaa4e18a504d`
- **Active Capabilities:**
  - `load_and_validate(data_dir)`: Loads `components.csv` and `prices.csv`, performs full schema validation, enforces unique keys, validates JSON specification dictionaries, and tracks provenance.
  - Test Coverage: All 14 unit tests in `tests/test_validator.py` pass.

### 2.3 Retail Price, Provenance & Availability Utilities (`app.py`)
- **Status:** **PRESERVED & TESTED**
- **Preserved Functions:**
  - `is_indian_retailer_url(url)`: Domain-based authentication of authorized Indian hardware vendors.
  - `evaluate_indian_market_presence(entries)`: Classifies verified Indian retailer listings vs. unverified foreign observations.
  - `parse_specs(raw_value)`: Safe dictionary parser for JSON specification strings.
  - `price_to_int(raw_value)`: Validates positive integer INR amounts.
  - `observation_freshness(checked_at, freshness_days, now=None)`: Classifies point-in-time observations into `recent`, `stale`, or `unknown`.
  - `price_lookup(prices_frame, freshness_days, now=None)`: Component price indexer tracking age and freshness.
  - `choose_cheapest_price(component_id, prices_lookup, prefer_available=False)`: Flexible price selection supporting both lowest-price and available-first policies.

### 2.4 Machine Learning Infrastructure (`experiments/`)
- **Status:** **100% PRESERVED**
- **Preserved Experiments:**
  - `experiments/performance_tier/train.py`: CPU performance tier classification models (Decision Tree, Class-Balanced Decision Tree, Random Forest, Scaled Logistic Regression) with Repeated Stratified K-Fold CV.
  - `experiments/cpu_benchmark_regression/`: V1 Baseline and V2 Comprehensive CPU Cinebench R23 regression models, feature pipelines, and OOF evaluation reports.
  - `experiments/gpu_benchmark_regression/`: GPU benchmark collection reports, readiness audits, and architectural staging.
- **Test Coverage:** 20 / 20 tests in `tests/test_cpu_ml_regression.py` and 2 / 2 tests in `tests/test_performance_tier.py` pass.
