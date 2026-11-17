# BuildWise-AI — CPU Benchmark Batch 6 Audit Report

**Audit Date:** 2026-11-07  
**Benchmark Suite:** Cinebench R23  
**Metric:** Multi-Core Score (`pts`)  
**Scope:** 8 Priority 3 Intel High-End & Flagship Processors  
**Target File:** [`data/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/data/benchmarks.csv)  
**Backup File:** [`backups/pre_cpu_benchmark_batch6_20261107_095000/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/backups/pre_cpu_benchmark_batch6_20261107_095000/benchmarks.csv)  
**Candidate Source:** [`third_dataset_research/benchmarks/batch6_cpu_candidates.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/third_dataset_research/benchmarks/batch6_cpu_candidates.csv)  

---

## 1. Executive Summary

Batch 6 concludes the research and collection of all **Priority 3 Intel High-End & Workstation Processors** from the [CPU Benchmark Collection Guide](file:///E:/BuildWise-AI/BuildWise-AI1/docs/cpu_benchmark_collection_guide.md). This covers Intel's most demanding compute architectures: Arrow Lake-S (LGA1851), Raptor Lake Refresh (LGA1700), Raptor Lake (LGA1700), and Alder Lake (LGA1700) flagships.

* **Processors Researched:** 8
* **Accepted Benchmark Records:** 8
* **Unresolved / Deferred Processors:** 0
* **Pre-Import Row Count in `data/benchmarks.csv`:** 47
* **Post-Import Row Count in `data/benchmarks.csv`:** 55
* **Schema Validation Issues:** 0
* **Duplicate Observations:** 0
* **Priority 3 Intel Coverage:** 100% complete (8 of 8 processors recorded).
* **Workstation Regression Capability:** With Batch 6 complete, high-core count workstation compute behavior (up to 24 cores / 32 threads, and up to 42,620 pts) is comprehensively mapped on the Intel platform.

---

## 2. Accepted Benchmark Observations (8 Processors)

| Benchmark ID | Component ID | Brand | Model | Socket | Cores/Threads | Boost Clock | TDP | Cinebench R23 Multi | Primary Source | Verified Date | Configuration Disclosure |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `BM_CPU_048` | `cpu-cu7-265k` | Intel | Core Ultra 7 265K | LGA1851 | 20C / 20T | 5.5 GHz | 250W | **35,315 pts** | CPU-Monkey | 2026-11-07 | Disclosed (Stock 125W/250W, DDR5-6400) |
| `BM_CPU_049` | `cpu-intel-core-ultra-9-285k` | Intel | Core Ultra 9 285K | LGA1851 | 24C / 24T | 5.7 GHz | 250W | **42,620 pts** | CPU-Monkey | 2026-11-07 | Disclosed (Stock 125W/250W, DDR5-6400) |
| `BM_CPU_050` | `cpu-intel-core-ultra-7-265kf` | Intel | Core Ultra 7 265KF | LGA1851 | 20C / 20T | 5.5 GHz | 250W | **35,315 pts** | CPU-Monkey | 2026-11-07 | Disclosed (Stock 125W/250W, DDR5-6400) |
| `BM_CPU_051` | `cpu-intel-core-i9-14900k` | Intel | Core i9-14900K | LGA1700 | 24C / 32T | 6.0 GHz | 253W | **38,712 pts** | CPU-Monkey | 2026-11-07 | Disclosed (Stock 125W/253W, DDR5-5600) |
| `BM_CPU_052` | `cpu-intel-core-i9-14900kf` | Intel | Core i9-14900KF | LGA1700 | 24C / 32T | 6.0 GHz | 253W | **38,712 pts** | CPU-Monkey | 2026-11-07 | Disclosed (Stock 125W/253W, DDR5-5600) |
| `BM_CPU_053` | `DS3_CPU_046` | Intel | Core i9-12900K | LGA1700 | 16C / 24T | 5.2 GHz | 241W | **27,472 pts** | CPU-Monkey | 2026-11-07 | Disclosed (Stock 125W/241W, DDR5-4800) |
| `BM_CPU_054` | `DS3_CPU_054` | Intel | Core i9-14900KS | LGA1700 | 24C / 32T | 6.2 GHz | 253W | **40,976 pts** | CPU-Monkey | 2026-11-07 | Disclosed (Stock 150W/253W, DDR5-5600) |
| `BM_CPU_055` | `DS3_CPU_060` | Intel | Core i9-13900K | LGA1700 | 24C / 32T | 5.8 GHz | 253W | **39,652 pts** | CPU-Monkey | 2026-11-07 | Disclosed (Stock 125W/253W, DDR5-5600) |

---

## 3. Detailed Test Configurations & Independent Cross-Checks

1. **`BM_CPU_048` — Intel Core Ultra 7 265K (`cpu-cu7-265k`)**
   * **Primary Measurement:** **35,315 pts** | CPU-Monkey
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_ultra_7_265k`
   * **Test Configuration:** Stock settings (125W base PL1 / 250W turbo PL2), DDR5-6400 memory.
   * **Secondary Cross-Check:** Corroborated with independent Arrow Lake reviews and database tracking (~35,000–35,500 pts).

2. **`BM_CPU_049` — Intel Core Ultra 9 285K (`cpu-intel-core-ultra-9-285k`)**
   * **Primary Measurement:** **42,620 pts** | CPU-Monkey
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_ultra_9_285k`
   * **Test Configuration:** Stock settings (125W base / 250W max turbo), DDR5-6400.
   * **Secondary Cross-Check:** Corroborated with Tom's Hardware 250W stock measurements (~42,500–43,100 pts).

3. **`BM_CPU_050` — Intel Core Ultra 7 265KF (`cpu-intel-core-ultra-7-265kf`)**
   * **Primary Measurement:** **35,315 pts** | CPU-Monkey
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_ultra_7_265kf`
   * **Test Configuration:** Stock settings (125W base / 250W max turbo), DDR5-6400.
   * **Secondary Cross-Check:** Silicon is identical to Core Ultra 7 265K without integrated GPU, matching `BM_CPU_048` (35,315 pts).

4. **`BM_CPU_051` — Intel Core i9-14900K (`cpu-intel-core-i9-14900k`)**
   * **Primary Measurement:** **38,712 pts** | CPU-Monkey
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i9_14900k`
   * **Test Configuration:** Stock settings (125W base / 253W max turbo), DDR5-5600.
   * **Secondary Cross-Check:** Corroborated with Tom's Hardware, TechPowerUp, and KitGuru baseline review runs under Intel baseline profile (~38,000–39,500 pts).

5. **`BM_CPU_052` — Intel Core i9-14900KF (`cpu-intel-core-i9-14900kf`)**
   * **Primary Measurement:** **38,712 pts** | CPU-Monkey
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i9_14900kf`
   * **Test Configuration:** Stock settings (125W base / 253W max turbo), DDR5-5600.
   * **Secondary Cross-Check:** Silicon is identical to Core i9-14900K, matching `BM_CPU_051` (38,712 pts).

6. **`BM_CPU_053` — Intel Core i9-12900K (`DS3_CPU_046`)**
   * **Primary Measurement:** **27,472 pts** | CPU-Monkey
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i9_12900k`
   * **Test Configuration:** Stock settings (125W base / 241W max turbo), DDR5-4800.
   * **Secondary Cross-Check:** Corroborated with TechPowerUp and Tom's Hardware review baselines (27,000–27,500 pts at manufacturer default power limits).

7. **`BM_CPU_054` — Intel Core i9-14900KS (`DS3_CPU_054`)**
   * **Primary Measurement:** **40,976 pts** | CPU-Monkey
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i9_14900ks`
   * **Test Configuration:** Stock settings (150W base / 253W turbo, Extreme 320W profile), DDR5-5600.
   * **Secondary Cross-Check:** Corroborated with independent reviews showing ~40,500–41,200 pts under high-end AIO cooling.

8. **`BM_CPU_055` — Intel Core i9-13900K (`DS3_CPU_060`)**
   * **Primary Measurement:** **39,652 pts** | CPU-Monkey
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i9_13900k`
   * **Test Configuration:** Stock settings (125W base / 253W max turbo), DDR5-5600.
   * **Secondary Cross-Check:** Corroborated with Tom's Hardware and TechPowerUp reviews (~39,000–40,000 pts under unlocked multi-core rendering loops).

---

## 4. Previously Unresolved Processors

In accordance with strict project guidelines, the three previously audited unresolved processors were **not revisited or altered** in Batch 6:
* `DS3_CPU_055` — AMD Ryzen 5 5600GT (Unresolved in Batch 1)
* `DS3_CPU_036` — AMD Ryzen 5 8500G (Unresolved in Batch 3)
* `DS3_CPU_044` — AMD Ryzen 7 5700 (Unresolved in Batch 4)

These three processors remain safely isolated outside `data/benchmarks.csv`.

---

## 5. Dataset Integrity & Consolidated Validation Status

* **Pre-Import Backup:** [`backups/pre_cpu_benchmark_batch6_20261107_095000/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/backups/pre_cpu_benchmark_batch6_20261107_095000/benchmarks.csv) (47 records).
* **Pre-Import Row Count:** 47 records.
* **Batch 6 Appended Records:** 8 records (`BM_CPU_048` through `BM_CPU_055`).
* **Post-Import Row Count:** 55 records.
* **Foreign Key Integrity:** 100% (all 55 `component_id` values verified against `data/components.csv` with `category == 'cpu'`).
* **Primary Key Uniqueness:** All 55 `benchmark_id` records are strictly unique (`BM_CPU_001` to `BM_CPU_055`).
* **Composite Uniqueness:** Zero duplicate `(component_id, benchmark_suite, benchmark_metric)` tuples.
* **Score Validity:** 100% positive, non-empty numerical scores (Range: 8,443 pts to 42,871 pts).
* **Validator Output:** `validate_data.py` exited with return code 0 (421 components, 88 price observations).
* **Automated Test Suite:** Full suite passed with **93/93 tests OK**.
* **Production Code Integrity:** Unchanged (`components.csv`, `prices.csv`, `app.py`, `src/compatibility.py`, and tests were untouched).
