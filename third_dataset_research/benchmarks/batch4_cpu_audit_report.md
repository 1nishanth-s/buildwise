# BuildWise-AI — CPU Benchmark Batch 4 Audit Report

**Audit Date:** 2026-11-06  
**Benchmark Suite:** Cinebench R23  
**Metric:** Multi-Core Score (`pts`)  
**Scope:** 9 Priority 2 Processors (Remaining Mainstream & High-Performance Processors)  
**Target File:** [`data/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/data/benchmarks.csv)  
**Backup File:** [`backups/pre_cpu_benchmark_batch4_20261106_193800/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/backups/pre_cpu_benchmark_batch4_20261106_193800/benchmarks.csv)  
**Candidate Source:** [`third_dataset_research/benchmarks/batch4_cpu_candidates.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/third_dataset_research/benchmarks/batch4_cpu_candidates.csv)  

---

## 1. Executive Summary

Batch 4 concludes the collection of **Priority 2** mainstream and performance desktop processors from the [CPU Benchmark Collection Guide](file:///E:/BuildWise-AI/BuildWise-AI1/docs/cpu_benchmark_collection_guide.md), evaluating the final 9 unrecorded processors across AMD AM4, AMD AM5, and Intel LGA1700 platforms.

* **Processors Researched:** 9
* **Accepted Benchmark Records:** 8
* **Unresolved / Deferred Processors:** 1 (`DS3_CPU_044` — AMD Ryzen 7 5700)
* **Pre-Import Row Count in `data/benchmarks.csv`:** 31
* **Post-Import Row Count in `data/benchmarks.csv`:** 39
* **Schema Validation Issues:** 0
* **Duplicate Observations:** 0

With Batch 4 completed, **all 42 processors across Priority 1 and Priority 2** have been thoroughly researched. 39 processors have verified, empirical Cinebench R23 Multi-Core measurements recorded in production, while 3 specialized chips (`DS3_CPU_055` Ryzen 5 5600GT, `DS3_CPU_036` Ryzen 5 8500G, and `DS3_CPU_044` Ryzen 7 5700) have been audited and properly deferred due to lack of independent Cinebench R23 multi-core lab publications.

---

## 2. Accepted Benchmark Observations (8 Processors)

| Benchmark ID | Component ID | Brand | Model | Socket | Cores/Threads | Boost Clock | TDP | Cinebench R23 Multi | Source | Verified Date | Configuration Disclosure |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `BM_CPU_032` | `DS3_CPU_037` | Intel | Core i5-12600K | LGA1700 | 10C / 16T | 4.9 GHz | 150W | **17,660 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 125W/150W, DDR5-4800) |
| `BM_CPU_033` | `DS3_CPU_038` | AMD | Ryzen 7 5700G | AM4 | 8C / 16T | 4.6 GHz | 65W | **14,075 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR4-3200) |
| `BM_CPU_034` | `DS3_CPU_039` | AMD | Ryzen 7 5800X3D | AM4 | 8C / 16T | 4.5 GHz | 105W | **15,125 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 105W, DDR4-3200) |
| `BM_CPU_035` | `DS3_CPU_042` | Intel | Core i5-14600KF | LGA1700 | 14C / 20T | 5.3 GHz | 181W | **24,683 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 125W/181W, DDR5-5600) |
| `BM_CPU_036` | `DS3_CPU_052` | Intel | Core i7-13700K | LGA1700 | 16C / 24T | 5.4 GHz | 253W | **30,766 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 125W/253W, DDR5-5600) |
| `BM_CPU_037` | `DS3_CPU_053` | AMD | Ryzen 7 8700F | AM5 | 8C / 16T | 5.0 GHz | 65W | **18,040 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR5-5200) |
| `BM_CPU_038` | `DS3_CPU_056` | Intel | Core i5-13600KF | LGA1700 | 14C / 20T | 5.1 GHz | 181W | **23,960 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 125W/181W, DDR5-5600) |
| `BM_CPU_039` | `DS3_CPU_058` | Intel | Core i7-14700F | LGA1700 | 20C / 28T | 5.4 GHz | 219W | **33,441 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W/219W, DDR5-5600) |

---

### Detailed Test Configurations & Direct Source URLs

1. **`BM_CPU_032` — Intel Core i5-12600K (`DS3_CPU_037`)**
   * **Score:** 17,660 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i5_12600k`
   * **Cross-Checking:** Corroborated with TechPowerUp review (~17,500–17,700 pts) and aligns identically with `BM_CPU_031` (Core i5-12600KF, 17,660 pts).
   * **Test Configuration:** Stock settings (125W PL1 base / 150W PL2 max turbo), DDR5-4800.

2. **`BM_CPU_033` — AMD Ryzen 7 5700G (`DS3_CPU_038`)**
   * **Score:** 14,075 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_5700g`
   * **Cross-Checking:** Corroborated with Tom's Hardware and NotebookCheck review baselines (~13,800–14,100 pts under stock 65W envelope).
   * **Test Configuration:** Stock 65W TDP, DDR4-3200 dual-channel.

3. **`BM_CPU_034` — AMD Ryzen 7 5800X3D (`DS3_CPU_039`)**
   * **Score:** 15,125 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_5800x3d`
   * **Cross-Checking:** Corroborated with Tom's Hardware, KitGuru, and TechPowerUp reviews (~14,800–15,150 pts).
   * **Test Configuration:** Stock 105W TDP envelope, DDR4-3200 dual-channel.

4. **`BM_CPU_035` — Intel Core i5-14600KF (`DS3_CPU_042`)**
   * **Score:** 24,683 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i5_14600kf`
   * **Cross-Checking:** Silicon is identical to Core i5-14600K without iGPU; matches `BM_CPU_014` (`cpu-i5-14600k`, 24,683 pts).
   * **Test Configuration:** Stock settings (125W base / 181W max turbo), DDR5-5600.

5. **`BM_CPU_036` — Intel Core i7-13700K (`DS3_CPU_052`)**
   * **Score:** 30,766 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i7_13700k`
   * **Cross-Checking:** Corroborated with Tom's Hardware, KitGuru, and TechPowerUp reviews (~30,500–31,000 pts under standard 253W turbo limits).
   * **Test Configuration:** Stock settings (125W base / 253W max turbo), DDR5-5600.

6. **`BM_CPU_037` — AMD Ryzen 7 8700F (`DS3_CPU_053`)**
   * **Score:** 18,040 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_8700f`
   * **Cross-Checking:** Phoenix 8C/16T silicon without iGPU. Clocks slightly below Ryzen 7 8700G (18,348 pts in `BM_CPU_020`) due to 5.0 GHz vs 5.1 GHz boost limit, consistent with architecture scaling.
   * **Test Configuration:** Stock 65W TDP, DDR5-5200.

7. **`BM_CPU_038` — Intel Core i5-13600KF (`DS3_CPU_056`)**
   * **Score:** 23,960 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i5_13600kf`
   * **Cross-Checking:** Corroborated with TechPowerUp Core i5-13600K review (24,010 pts).
   * **Test Configuration:** Stock settings (125W base / 181W max turbo), DDR5-5600.

8. **`BM_CPU_039` — Intel Core i7-14700F (`DS3_CPU_058`)**
   * **Score:** 33,441 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i7_14700f`
   * **Cross-Checking:** Corroborated with independent tests showing stock 219W turbo operation scaling between 31,000 and 33,800 pts; aligns logically below unlocked 14700K (34,763 pts in `BM_CPU_017`).
   * **Test Configuration:** Stock power limits (65W base / 219W max turbo), DDR5-5600.

---

## 3. Unresolved / Deferred CPU Audit

### `DS3_CPU_044` — AMD Ryzen 7 5700
* **Status:** **UNRESOLVED (Deferred from Batch 4)**
* **Catalog Details:** AMD Ryzen 7 5700 | Socket AM4 | 8 Cores / 16 Threads | 3.7 GHz Base / 4.6 GHz Boost | 65W TDP
* **Architecture & Background:** The Ryzen 7 5700 (non-X, non-G) is a repackaged desktop Cezanne APU silicon with disabled integrated graphics, released in early 2024. Unlike the Vermeer-based Ryzen 7 5700X, it features a halved L3 cache (16MB) and is restricted to PCIe 3.0.
* **Audit Finding:**
  1. Major review outlets (Hardware Unboxed / TechSpot) evaluated this CPU primarily for its architectural differences and gaming deficits against the 5700X, but did not publish standardized Cinebench R23 Multi-Core runs.
  2. Aggregated databases (such as CPU-Monkey) list Geekbench 6 and Cinebench 2024 scores for this processor, but omit empirical Cinebench R23 Multi-Core measurements.
  3. Under BuildWise-AI's zero-tolerance policy against cross-suite formula conversion (e.g. converting Cinebench 2024 to R23) or synthetic approximation, `DS3_CPU_044` cannot be assigned an unverified number.
* **Action Taken:** Excluded from `data/benchmarks.csv` until an authoritative, verified Cinebench R23 Multi-Core lab measurement is published.

---

## 4. Dataset Integrity & Validation Status

* **Pre-Import Backup:** [`backups/pre_cpu_benchmark_batch4_20261106_193800/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/backups/pre_cpu_benchmark_batch4_20261106_193800/benchmarks.csv) created and verified before any modifications.
* **Pre-Import Benchmarks Count:** 31
* **Batch 4 Appended Records:** 8
* **Post-Import Benchmarks Count:** 39
* **Foreign Key Integrity:** 100% of `component_id` values exist in `data/components.csv` with `category == 'cpu'`.
* **Primary Key Uniqueness:** All `benchmark_id` values (`BM_CPU_001` through `BM_CPU_039`) are strictly unique.
* **Composite Uniqueness:** No duplicate `(component_id, benchmark_suite, benchmark_metric)` exists across the dataset.
* **Data Validator:** `validate_data.py` exited with return code 0.
* **Automated Test Suite:** 93 passed.

