# BuildWise-AI — Indian Online Price Research Progress Report

**Generated:** 2026-11-10 13:00:50  
**Research Check Date:** 2026-11-08  
**Scope:** Comprehensive Indian retail price research for all 1,208 catalog components.

---

## 1. High-Level Research Metrics

| Metric | Count | Percentage |
|---|---:|---:|
| **Total Catalog Components** | 1208 | 100.0% |
| **Components Researched to Date** | **1208** | **100.0%** |
| Components with $\ge$1 Verified Retailer Price | **1054** | **87.3%** |
| — Single Verified Retailer Price | 960 | 79.5% |
| — Multiple Verified Retailer Prices | 94 | 7.8% |
| Components with Official Reference Price Only | 0 | 0.0% |
| Components with No Verifiable Retail Price (EOL/OEM/Unreleased) | 154 | 12.7% |
| Components with Ambiguous Product Matches (Excluded) | 0 | 0.0% |
| **Components Still Pending** | **0** | **0.0%** |
| **Total `data/prices.csv` Observation Rows** | **1084** | — |

---

## 2. Category-Level Price Coverage

| Category | Total Components | Verified Retail Priced | No Verifiable Price | Ambiguous Excluded | Pending |
|---|---:|---:|---:|---:|---:|
| CPU | 180 | 135 (75.0%) | 45 | 0 | 0 |
| GPU | 218 | 157 (72.0%) | 61 | 0 | 0 |
| MOTHERBOARD | 180 | 157 (87.2%) | 23 | 0 | 0 |
| RAM | 160 | 149 (93.1%) | 11 | 0 | 0 |
| STORAGE | 150 | 143 (95.3%) | 7 | 0 | 0 |
| PSU | 120 | 118 (98.3%) | 2 | 0 | 0 |
| CASE | 100 | 98 (98.0%) | 2 | 0 | 0 |
| COOLER | 100 | 97 (97.0%) | 3 | 0 | 0 |

---

## 3. Batch-by-Batch Research Execution Tracking

| Batch ID | Total Items | Verified Priced | Pending Items | Execution Status |
|---|---:|---:|---:|---|
| `BATCH_00_BASELINE_PRICED` | 544 | 544 | 0 | Completed |
| `BATCH_01_CPU` | 37 | 32 | 0 | Completed |
| `BATCH_02_CPU` | 36 | 11 | 0 | Completed |
| `BATCH_03_CPU` | 36 | 21 | 0 | Completed |
| `BATCH_04_GPU` | 34 | 22 | 0 | Completed |
| `BATCH_05_GPU` | 34 | 12 | 0 | Completed |
| `BATCH_06_GPU` | 33 | 15 | 0 | Completed |
| `BATCH_07_GPU` | 33 | 24 | 0 | Completed |
| `BATCH_08_MOTHERBOARD` | 35 | 35 | 0 | Completed |
| `BATCH_09_MOTHERBOARD` | 34 | 24 | 0 | Completed |
| `BATCH_10_MOTHERBOARD` | 34 | 21 | 0 | Completed |
| `BATCH_11_RAM` | 32 | 24 | 0 | Completed |
| `BATCH_12_RAM` | 32 | 29 | 0 | Completed |
| `BATCH_13_RAM` | 31 | 31 | 0 | Completed |
| `BATCH_14_STORAGE` | 42 | 41 | 0 | Completed |
| `BATCH_15_STORAGE` | 42 | 36 | 0 | Completed |
| `BATCH_16_PSU` | 30 | 30 | 0 | Completed |
| `BATCH_17_PSU` | 30 | 28 | 0 | Completed |
| `BATCH_18_CASE` | 40 | 38 | 0 | Completed |
| `BATCH_19_COOLER` | 39 | 36 | 0 | Completed |

---

## 4. Retail Sources & Provenance Policy

All verified retail prices strictly adhere to:
1. Direct product page URLs on reputable Indian hardware merchants:
   - MD Computers (`mdcomputers.in`)
   - Vedant Computers (`vedantcomputers.com`)
   - Prime ABGB (`primeabgb.com`)
   - PCStudio (`pcstudio.in`)
   - EliteHubs (`elitehubs.com`)
   - Computech Store (`computechstore.in`)
   - Clarion Computers (`clarioncomputers.in`)
   - SCL Gaming (`sclgaming.in`)
2. Numeric INR prices inclusive of standard 18% GST.
3. Strict isolation between live retailer pricing, official reference MSRPs, and historical planning estimates.
4. Preserved EOL / legacy documentation without artificial price fabrication.
