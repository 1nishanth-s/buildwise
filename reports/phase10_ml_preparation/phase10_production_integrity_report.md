# BuildWise-AI — Phase 10 Production Integrity & Immutability Report

## 1. Executive Summary

Phase 10 (*Machine Learning Dataset Audit, Feature Engineering and Training Data Preparation*) operated under a strict safety mandate:
**Under no circumstances may the production datasets (`data/components.csv`, `data/prices.csv`, `data/benchmarks.csv`) be modified, re-sorted, overwritten, or appended to.**

All training datasets, feature tables, and experiment artifacts were generated strictly as downstream, read-only derived assets located in `experiments/performance_prediction/data/` and `reports/phase10_ml_preparation/`.

This report provides cryptographic proof of the immutability of all production datasets before, during, and after Phase 10 execution.

---

## 2. Cryptographic Checksum Verification (SHA-256)

Calculated via Windows PowerShell `Get-FileHash -Algorithm SHA256`:

| Dataset Path | Row Count | Phase 8/9 Baseline SHA-256 | Post-Phase 10 SHA-256 | Verification Result |
|---|---|---|---|---|
| `data/components.csv` | 1,208 | `6753F468DEC05ADC2CCB4C2582BF798C922A70474AAC8FFB8508541A19A67ECC` | `6753F468DEC05ADC2CCB4C2582BF798C922A70474AAC8FFB8508541A19A67ECC` | **IDENTICAL (100% Match)** |
| `data/prices.csv` | 599 | `943E87AE76412D9ED37D442AAFD7F079ADB0344FEDE321C5989D37D97F929E7B` | `943E87AE76412D9ED37D442AAFD7F079ADB0344FEDE321C5989D37D97F929E7B` | **IDENTICAL (100% Match)** |
| `data/benchmarks.csv` | 237 | `4187F577BB064F429F12CB644FFED343246B98E56F2122AEA9F095714A564702` | `4187F577BB064F429F12CB644FFED343246B98E56F2122AEA9F095714A564702` | **IDENTICAL (100% Match)** |

---

## 3. Production Catalog Integrity Analysis

### A. Component Catalog (`data/components.csv`)
- **Row count:** Exactly 1,208 hardware component rows.
- **Category distribution:**
  - Case: 110
  - Cooler: 110
  - CPU: 180
  - GPU: 218
  - Motherboard: 180
  - PSU: 100
  - RAM: 160
  - Storage: 150
- **Modification status:** Zero rows altered, zero columns added, zero whitespace modified.

### B. Retail Price Observations (`data/prices.csv`)
- **Row count:** Exactly 599 price records.
- **Sourcing integrity:** Indian retail pricing observations from MDComputers, Vedant Computers, PrimeABGB, EliteHubs, Amazon India, and verified baseline planning estimates.
- **Modification status:** Zero rows altered.

### C. Empirical Benchmark Observations (`data/benchmarks.csv`)
- **Row count:** Exactly 237 empirical benchmark observations.
  - Cinebench R23 Multi-Core: 180 observations (CPUs).
  - 3DMark Time Spy Graphics: 57 observations (GPUs).
- **Modification status:** Zero rows altered.

---

## 4. Location of Derived Experiment Artifacts

All files created or derived in Phase 10 are strictly isolated in designated experiment directories:

- **Derived Datasets:**
  - `experiments/performance_prediction/data/cpu_training_dataset.csv`
  - `experiments/performance_prediction/data/gpu_training_dataset.csv`
- **Feature Modules:**
  - `experiments/performance_prediction/config.py`
  - `experiments/performance_prediction/cpu_features.py`
  - `experiments/performance_prediction/gpu_features.py`
  - `experiments/performance_prediction/feature_extraction.py`
  - `experiments/performance_prediction/dataset_preparation.py`
  - `experiments/performance_prediction/validation.py`
  - `experiments/performance_prediction/README.md`
- **Tests:**
  - `tests/test_ml_dataset_preparation.py`
- **Audit Reports:**
  - `reports/phase10_ml_preparation/*`

---

## 5. Production Validator Confirmation

The project's authoritative validation script was executed to ensure end-to-end schema compliance:

```powershell
.\.venv\Scripts\python.exe validate_data.py
```

Result:
```text
Component rows: 1208
Price observations: 599
Validation passed. Note: an empty template is valid, but it cannot generate recommendations yet.
```

Exit code: `0`.

---

## 6. Certification

I certify that Phase 10 maintained complete data separation and strictly read-only access to all production data stores. No production files were compromised, altered, or overwritten.
