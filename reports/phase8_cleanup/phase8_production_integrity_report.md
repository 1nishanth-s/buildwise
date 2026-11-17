# BuildWise-AI — Phase 8 Production Dataset Integrity Report

**Execution Timestamp:** 2026-11-08T14:59:00+05:30  
**Executing Role:** Senior PC Hardware Research Engineer, Data Engineer & Machine Learning Dataset Specialist  
**Dataset Scope:** Live Production Datasets in `data/`  
**Integrity Audit Status:** `100% PASSED — BIT-LEVEL CHECKSUM FIDELITY CONFIRMED`  

---

## 1. Executive Summary

This report provides cryptographic and referential verification of the live production datasets in `data/` at the conclusion of Phase 8.

Because zero confirmed duplicate records were identified during the duplicate audit, no destructive data operations were required. The production datasets retain 100% bit-for-bit checksum equality with the Phase 7 imported baseline.

---

## 2. Cryptographic Checksum & Row Count Verification

| Production Dataset File | Record Count | File Size (Bytes) | Phase 7 Imported Baseline SHA-256 | Post-Phase 8 Production SHA-256 | Fidelity Status |
|---|---:|---:|---|---|:---:|
| [data/components.csv](file:///E:/BuildWise-AI/BuildWise-AI1/data/components.csv) | 1,208 | 784,629 | `6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc` | `6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc` | **MATCH (100%)** |
| [data/prices.csv](file:///E:/BuildWise-AI/BuildWise-AI1/data/prices.csv) | 599 | 166,808 | `943e87ae76412d9ed37d442aafd7f079adb0344fede321c5989d37d97f929e7b` | `943e87ae76412d9ed37d442aafd7f079adb0344fede321c5989d37d97f929e7b` | **MATCH (100%)** |
| [data/benchmarks.csv](file:///E:/BuildWise-AI/BuildWise-AI1/data/benchmarks.csv) | 237 | 58,088 | `4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702` | `4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702` | **MATCH (100%)** |

---

## 3. Primary Key & Referential Integrity

- **Component IDs:** 1,208 / 1,208 unique primary keys (0 collisions).
- **Price IDs:** 599 / 599 unique primary keys (0 collisions).
- **Benchmark IDs:** 237 / 237 unique primary keys (0 collisions).
- **Price Referential Integrity:** 599 / 599 price records reference a valid component ID in `components.csv` (0 orphaned prices).
- **Benchmark Referential Integrity:** 237 / 237 benchmark records reference a valid component ID in `components.csv` (0 orphaned benchmarks).

---

## 4. Preservation of Legitimate Variants & Historical Observations

- **Hardware Variants:** Preserved both genuine manufacturer editions of the B650M GAMING PLUS WIFI motherboard:
  - Gigabyte `DS3_MB_028`
  - MSI `DS3_MB_074`
- **Historical Observations:** Preserved all 33 temporal price observations recorded across authorized Indian retailers on multiple check dates.
- **Quarantined Records Audit:**
  - `CAND_GPU_142`: 0 occurrences (Excluded).
  - `CAND_GPU_143`: 0 occurrences (Excluded).
  - `PRICE_198`: 0 occurrences (Excluded).
  - Candidate GPU benchmarks, gaming benchmarks, proposed categories: 0 occurrences (Quarantined).
