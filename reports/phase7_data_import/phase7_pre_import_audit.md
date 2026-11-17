# BuildWise-AI — Phase 7 Pre-Import Dataset Audit

**Audit Date:** 2026-11-08T14:20:00+05:30  
**Executing Role:** Senior PC Hardware Research Engineer, Data Engineer & Machine Learning Dataset Specialist  
**Operation Scope:** Pre-Import Audit for Controlled Production Integration of Expanded Hardware Datasets  
**Pre-Import Backup Directory:** `backups/phase7_pre_import_20261108_142000`  

---

## 1. Executive Summary

Phase 7 executes a controlled, data-only import of the independently audited, deduplicated, and validated Phase 6F expanded datasets into the BuildWise-AI production environment.

The previous Phase 6E import was automatically rolled back in compliance with safety policy because the legacy exhaustive recommendation engine (`build_recommendation()` in `app.py`) could not process the expanded search space within Streamlit's default 10-second `AppTest` timeout. In this phase, the production datasets are imported and validated independently of the recommendation engine.

All source datasets have been audited, referential integrity has been confirmed, and immutable backups have been cryptographically verified prior to data transfer.

---

## 2. Production Baseline vs. Staged Expanded Datasets

### 2.1 File Inventory and Cryptographic Checksums

| Dataset Role | File Path | Row Count | File Size (Bytes) | SHA-256 Checksum |
|---|---|---:|---:|---|
| **Baseline Production** | `data/components.csv` | 421 | 216,780 | `ca4f2735ec475715ecc2551ab2358377327f28bc89a9603ac91f56b587ad4b60` |
| **Baseline Production** | `data/prices.csv` | 88 | 30,795 | `978808024239d3bea1b595311f4bed30390b13c8b3252774f97877d83095ac79` |
| **Baseline Production** | `data/benchmarks.csv` | 112 | 27,383 | `0885fd94cb3b00e4985fab0fd58e9129a03c12cdf4df99c818cf15dbc10e92c6` |
| **Staged Target Catalog** | `reports/phase6e_import/staged_production/components.csv` | 1,208 | 784,629 | `6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc` |
| **Staged Target Prices** | `reports/phase6e_import/staged_production/prices.csv` | 599 | 166,808 | `943e87ae76412d9ed37d442aafd7f079adb0344fede321c5989d37d97f929e7b` |
| **Staged Target Benchmarks** | `reports/phase6e_import/staged_production/benchmarks.csv` | 237 | 58,088 | `4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702` |
| **Phase 6F Unified Source** | `reports/phase6_unified_catalog/unified_component_catalog.csv` | 1,208 | 784,629 | `6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc` |

### 2.2 Pre-Import Backup Verification

All three baseline production files were copied to `backups/phase7_pre_import_20261108_142000/`. Checksum equality confirms 100% bit-level fidelity between the live production baseline and the backup:
- `components.csv`: `ca4f2735ec475715ecc2551ab2358377327f28bc89a9603ac91f56b587ad4b60` (**MATCH**)
- `prices.csv`: `978808024239d3bea1b595311f4bed30390b13c8b3252774f97877d83095ac79` (**MATCH**)
- `benchmarks.csv`: `0885fd94cb3b00e4985fab0fd58e9129a03c12cdf4df99c818cf15dbc10e92c6` (**MATCH**)

---

## 3. Dataset Schemas and Field Definitions

### 3.1 Component Catalog Schema (`components.csv`)
1. `component_id` (string, primary key, non-null, unique)
2. `category` (string, sanctioned 8 categories: cpu, gpu, motherboard, ram, storage, psu, case, cooler)
3. `brand` (string, non-null)
4. `model` (string, non-null)
5. `specs_json` (valid JSON dictionary string, non-null)
6. `source_name` (string, non-null)
7. `source_url` (string, valid HTTP/HTTPS URL, non-null)
8. `source_license` (string, non-null)
9. `identity_status` (string, enum: "verified", non-null)

### 3.2 Retail Prices Schema (`prices.csv`)
1. `price_id` (string, primary key, non-null, unique)
2. `component_id` (string, foreign key -> components.component_id, non-null)
3. `seller` (string, authorized Indian retailer storefront or catalog provider, non-null)
4. `price_inr` (integer, positive INR value, non-null)
5. `source_url` (string, valid HTTP/HTTPS URL, non-null)
6. `checked_at` (ISO 8601 timestamp string, non-null)
7. `availability` (string, enum: "available", "unavailable", "unknown", non-null)
8. `price_type` (string, enum: "seller_observation", "planning_estimate")
9. `provenance` (string, explanatory provenance notes)

### 3.3 Hardware Benchmarks Schema (`benchmarks.csv`)
1. `benchmark_id` (string, primary key, non-null, unique)
2. `component_id` (string, foreign key -> components.component_id, non-null)
3. `category` (string, enum: "cpu", "gpu", non-null)
4. `benchmark_suite` (string, enum: "Cinebench R23", "3DMark Time Spy", non-null)
5. `benchmark_metric` (string, enum: "Multi-Core Score", "Graphics Score", non-null)
6. `score` (float/int, positive numeric value, non-null)
7. `score_unit` (string, enum: "pts", non-null)
8. `source_name` (string, verified benchmark source or database, non-null)
9. `source_url` (string, valid HTTP/HTTPS URL, non-null)
10. `verified_date` (ISO 8601 date string, non-null)
11. `test_configuration` (string, hardware configuration metadata, non-null)

---

## 4. Expected Production Targets and Category Allocations

### 4.1 Component Distribution

| Category | Baseline Rows | Accepted Candidate Additions | Final Production Target | Target Parity |
|---|---:|---:|---:|:---:|
| CPU | 64 | 116 | 180 | EXACT MATCH |
| GPU | 75 | 143 | 218 | EXACT MATCH |
| Motherboard | 95 | 85 | 180 | EXACT MATCH |
| RAM | 49 | 111 | 160 | EXACT MATCH |
| Storage | 45 | 105 | 150 | EXACT MATCH |
| PSU | 42 | 78 | 120 | EXACT MATCH |
| Case | 26 | 74 | 100 | EXACT MATCH |
| Cooler | 25 | 75 | 100 | EXACT MATCH |
| **Total Components** | **421** | **787** | **1,208** | **100% APPROVED** |

### 4.2 Retail Price Observations

| Metric | Baseline | Accepted Candidates | Final Production Target |
|---|---:|---:|---:|
| Total Observations | 88 | 511 | 599 |
| Available Offers | 55 | 441 | 496 |
| Unavailable Catalog Listings | 30 | 70 | 100 |
| Unknown Availability | 3 | 0 | 3 |
| Seller Observations | 79 | 511 | 590 |
| Planning Estimates | 1 | 0 | 1 |
| Preserved Unlabeled Estimates | 8 | 0 | 8 |

### 4.3 Hardware Benchmarks

| Metric / Suite | Baseline | Accepted Candidates | Final Production Target | Target Hardware Population | Population Coverage |
|---|---:|---:|---:|---:|---:|
| Cinebench R23 Multi-Core (CPU) | 55 | 125 | 180 | 180 CPUs | 100.0% |
| 3DMark Time Spy Graphics (GPU) | 57 | 0 | 57 | 218 GPUs | 26.1% |
| **Total Benchmark Observations** | **112** | **125** | **237** | — | — |

---

## 5. Excluded and Quarantined Records

In strict accordance with project architecture policies, the following staged records are explicitly quarantined and will **NOT** be imported:

1. **Held GPU Candidates (2 records):**
   - `CAND_GPU_142` (Sapphire Pulse Radeon RX 7600 XT 16GB) — Held due to near-duplicate model verification.
   - `CAND_GPU_143` (Zotac Gaming GeForce GTX 1650 OC 4GB GDDR6) — Held due to duplicate verification.
2. **Quarantined Price Observations (1 record):**
   - `PRICE_198` (Vedant Computers offer of ₹8,290 referencing held candidate `CAND_GPU_143`).
3. **Quarantined Candidate GPU Benchmarks (143 records):**
   - Staged in `reports/dataset_expansion/candidates/staged_batch10_gpu_benchmarks.csv` — Quarantined pending formal GPU ML model training phases.
4. **Quarantined Full-System Gaming FPS Benchmarks (35 records):**
   - Staged in `reports/dataset_expansion/candidates/staged_batch11_gaming_benchmarks.csv` — Quarantined reference data.
5. **Quarantined Proposed Peripheral/Accessory Benchmarks (9 records):**
   - Staged in `reports/dataset_expansion/candidates/staged_batch12_proposed_categories.csv` — Quarantined out-of-scope categories.

---

## 6. Merge and Integration Strategy

1. **Full Replacement with Pre-Validated Unified Artifacts:**
   Because the unified catalog in `reports/phase6e_import/staged_production/components.csv` is already the authoritative, deduplicated merge of the 421 baseline components and 787 accepted candidate components, the file represents the complete target dataset. Appending candidates to the baseline file would create duplicate entries.
2. **Atomic Write through Temporary Staging:**
   New production datasets will be written to temporary files (`data/components.csv.tmp`, etc.), audited for row counts and schema compliance, and atomically renamed to replace `data/components.csv`, `data/prices.csv`, and `data/benchmarks.csv`.
3. **Post-Import Validation:**
   Immediately following replacement, `python validate_data.py` and dedicated unit tests will be executed to guarantee production health.
