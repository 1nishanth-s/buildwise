# BuildWise-AI — Phase 8 Pre-Cleanup Baseline Report

**Execution Timestamp:** 2026-11-08T14:45:00+05:30  
**Executing Role:** Senior PC Hardware Research Engineer, Data Engineer & Python Developer  
**Operation Scope:** Pre-Cleanup Baseline Documentation & Strategy for Phase 8  
**Backup Repository:** `backups/phase8_pre_cleanup_20261108_144500`  

---

## 1. Executive Summary

Phase 8 follows the successful Phase 7 production dataset import. The objective of Phase 8 is threefold:
1. Conduct a comprehensive dataset duplicate audit across `data/components.csv`, `data/prices.csv`, and `data/benchmarks.csv` to identify genuine exact duplicates while strictly preserving legitimate hardware variants and historical observations.
2. Audit the codebase (`app.py`, `src/`, `tests/`, `experiments/`) for duplicate, dead, or obsolete code.
3. Completely remove the legacy exhaustive recommendation engine (`build_recommendation()` and associated unpruned DFS helpers) from `app.py` and replace it with a clean, responsive component catalog browser and compatibility inspection interface.
4. Correct the hardcoded baseline dataset count assertions in `tests/test_performance_tier.py` so they dynamically adapt to the live catalog.

---

## 2. Pre-Cleanup Production Datasets & Checksums

| Dataset File | Live Row Count | File Size (Bytes) | Phase 7 Verified SHA-256 Checksum | Status |
|---|---:|---:|---|:---:|
| `data/components.csv` | 1,208 | 784,629 | `6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc` | **MATCH (100%)** |
| `data/prices.csv` | 599 | 166,808 | `943e87ae76412d9ed37d442aafd7f079adb0344fede321c5989d37d97f929e7b` | **MATCH (100%)** |
| `data/benchmarks.csv` | 237 | 58,088 | `4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702` | **MATCH (100%)** |

---

## 3. Pre-Cleanup Protected Code Files & Checksums

| File Path | File Size (Bytes) | SHA-256 Checksum | Role / Modification Scope |
|---|---:|---|---|
| `app.py` | 38,660 | `b6cb351a6622c413b01901e3afc600a9cd10adc0d22abb7d327f67470042d31f` | Legacy exhaustive recommendation engine to be removed; temporary catalog browser interface to be added |
| `tests/test_performance_tier.py` | 8,147 | `ec00beadc44cc27785b75ecc0de23aaf727caf3ac6725a17409ec4a63e78c6aa` | Update hardcoded baseline CPU count assertions to dynamic dataset counts |
| `tests/test_recommendation.py` | 49,298 | `7f939ebcef166232c5105c3bae6ea454937c573266d5737629fd1e75a88ac728` | Retire tests exclusively asserting the legacy exhaustive recommendation engine |
| `src/compatibility.py` | 32,040 | `3161689994113d02f5e7b583fb93ffad272a0839b455ef81ef114476f9ec42af` | **100% PRESERVED** (No modifications permitted) |
| `src/validator.py` | 9,006 | `8eac18b1f7597f3bea1ae2710ad4f68b78866aa034fb3f933cbedaa4e18a504d` | **100% PRESERVED** (No modifications permitted) |

---

## 4. Git Repository & Working-Tree Status

- **Branch:** `main` (tracking `origin/main`)
- **Git Restrictions:** No git commit, no git push, no branch resets. All operations are local.
- **Untracked Directories:** `reports/`, `backups/`, `experiments/`, `models/`, `docs/`.

---

## 5. Phase 8 Execution Strategy

1. **Part A (Dataset Duplicate Audit):**
   - Execute programmatic duplicate scans on `data/components.csv`, `data/prices.csv`, and `data/benchmarks.csv`.
   - Check exact duplicate rows, duplicate primary keys, duplicate model identities, duplicate prices, and duplicate benchmark measurements.
   - Classify all suspicious records: `confirmed_duplicate`, `possible_duplicate`, `legitimate_variant`, `legitimate_historical_observation`, `conflicting_identity`, `not_duplicate`.
   - Apply removal ONLY if `confirmed_duplicate` records are found with full foreign-key reconciliation. If no confirmed duplicates exist, retain datasets byte-for-byte.

2. **Part B (Code Audit):**
   - Scan `app.py`, `src/`, `tests/`, and `experiments/` for duplicate function definitions, unused imports, dead helpers, and obsolete UI code.
   - Document all findings in `code_duplicate_audit.md` and `code_cleanup_manifest.csv`.

3. **Part C (Removal of Legacy Exhaustive Recommendation Engine):**
   - Remove `build_recommendation()` and engine-specific DFS helpers (`_check_candidate_compatibility`, Cartesian generation, exhaustive PC configuration enumeration).
   - Keep all core compatibility checking in `src/compatibility.py`.
   - Keep dataset loaders, price lookup, freshness, and Indian retailer evaluation utilities.
   - Deploy temporary Streamlit catalog browser in `app.py` with category filtering, specification inspection, pricing and benchmark display, and future workflow notice.

4. **Part D (Test Suite Modernization & Validation):**
   - Update `tests/test_performance_tier.py` assertions to adapt dynamically to the expanded CPU catalog size.
   - Replace tests in `tests/test_recommendation.py` that tested the legacy exhaustive engine with tests verifying the new clean catalog browser, component filtering, and absence of legacy DFS search.
   - Run `validate_data.py`, `unittest discover`, and Streamlit headless smoke test.
