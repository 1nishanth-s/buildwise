# BuildWise-AI — CPU Benchmark Batch 1 Audit Report

**Audit Date:** 2026-11-02  
**Benchmark Suite:** Cinebench R23  
**Metric:** Multi-Core Score (`pts`)  
**Scope:** 13 Priority 1 Processors (Currently Priced in Production)  
**Target File:** [`data/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/data/benchmarks.csv)  
**Candidate Source:** [`third_dataset_research/benchmarks/batch1_cpu_candidates.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/third_dataset_research/benchmarks/batch1_cpu_candidates.csv)  

---

## 1. Executive Summary

Batch 1 focuses on the **13 Priority 1 CPUs** identified in the collection guide—the exact processors currently priced in [`data/prices.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/data/prices.csv) and actively driving recommendation decisions in BuildWise-AI.

* **CPUs Researched:** 13
* **Accepted Benchmark Records:** 12
* **Unresolved CPUs:** 1 (`DS3_CPU_055` — AMD Ryzen 5 5600GT)
* **Schema Validation Issues:** 0
* **Duplicate Observations:** 0
* **Prior Row Count in `data/benchmarks.csv`:** 0
* **Post Row Count in `data/benchmarks.csv`:** 12

---

## 2. Accepted Benchmark Observations (12 Processors)

| Benchmark ID | Component ID | Brand | Model | Socket | Cores/Threads | Boost Clock | TDP | Cinebench R23 Multi | Source | Verified Date |
|---|---|---|---|---|---|---|---|---|---|---|
| `BM_CPU_001` | `cpu-r5-9600x` | AMD | Ryzen 5 9600X | AM5 | 6C / 12T | 5.4 GHz | 65W | **17,689 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_002` | `cpu-r7-9700x` | AMD | Ryzen 7 9700X | AM5 | 8C / 16T | 5.5 GHz | 65W | **23,127 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_003` | `cpu-r7-9800x3d` | AMD | Ryzen 7 9800X3D | AM5 | 8C / 16T | 5.2 GHz | 120W | **22,986 pts** | StorageReview | 2026-11-02 |
| `BM_CPU_004` | `amd-ryzen-7-7800x3d` | AMD | Ryzen 7 7800X3D | AM5 | 8C / 16T | 5.0 GHz | 120W | **17,762 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_005` | `amd-ryzen-7-7700x` | AMD | Ryzen 7 7700X | AM5 | 8C / 16T | 5.4 GHz | 105W | **20,399 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_006` | `amd-ryzen-5-7600x` | AMD | Ryzen 5 7600X | AM5 | 6C / 12T | 5.3 GHz | 105W | **15,315 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_007` | `DS3_CPU_007` | AMD | Ryzen 5 5500 | AM4 | 6C / 12T | 4.2 GHz | 65W | **10,940 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_008` | `DS3_CPU_009` | AMD | Ryzen 5 5600X | AM4 | 6C / 12T | 4.6 GHz | 65W | **10,988 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_009` | `DS3_CPU_010` | AMD | Ryzen 5 5600 | AM4 | 6C / 12T | 4.4 GHz | 65W | **11,077 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_010` | `DS3_CPU_014` | Intel | Core i5-12400F | LGA1700 | 6C / 12T | 4.4 GHz | 117W | **12,454 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_011` | `DS3_CPU_029` | AMD | Ryzen 5 5600G | AM4 | 6C / 12T | 4.4 GHz | 65W | **10,202 pts** | CPU-Monkey | 2026-11-02 |
| `BM_CPU_012` | `DS3_CPU_040` | Intel | Core i3-12100F | LGA1700 | 4C / 8T | 4.3 GHz | 89W | **8,443 pts** | CPU-Monkey | 2026-11-02 |

---

### Detailed Test Configurations & Direct Source URLs

1. **`BM_CPU_001` — AMD Ryzen 5 9600X (`cpu-r5-9600x`)**
   * **Score:** 17,689 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_9600x`
   * **Test Configuration:** Stock 65W TDP, DDR5-6000, 360mm AIO liquid cooler.

2. **`BM_CPU_002` — AMD Ryzen 7 9700X (`cpu-r7-9700x`)**
   * **Score:** 23,127 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_9700x`
   * **Test Configuration:** Stock 65W TDP, DDR5-6000, 360mm AIO liquid cooler.

3. **`BM_CPU_003` — AMD Ryzen 7 9800X3D (`cpu-r7-9800x3d`)**
   * **Score:** 22,986 pts
   * **Direct URL:** `https://www.storagereview.com/review/amd-ryzen-7-9800x3d-review`
   * **Test Configuration:** Stock clocks, default 120W TDP envelope, DDR5-6000, standard testbed.

4. **`BM_CPU_004` — AMD Ryzen 7 7800X3D (`amd-ryzen-7-7800x3d`)**
   * **Score:** 17,762 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_7800x3d`
   * **Test Configuration:** Stock clocks, default 120W TDP, DDR5-6000 EXPO profile.

5. **`BM_CPU_005` — AMD Ryzen 7 7700X (`amd-ryzen-7-7700x`)**
   * **Score:** 20,399 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_7700x`
   * **Test Configuration:** Stock clocks, 105W TDP envelope, DDR5-6000, 360mm AIO.

6. **`BM_CPU_006` — AMD Ryzen 5 7600X (`amd-ryzen-5-7600x`)**
   * **Score:** 15,315 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_7600x`
   * **Test Configuration:** Stock clocks, 105W TDP envelope, DDR5-6000, 360mm AIO.

7. **`BM_CPU_007` — AMD Ryzen 5 5500 (`DS3_CPU_007`)**
   * **Score:** 10,940 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_5500`
   * **Test Configuration:** Stock clocks, 65W TDP, DDR4-3200 dual-channel, tower air cooler.

8. **`BM_CPU_008` — AMD Ryzen 5 5600X (`DS3_CPU_009`)**
   * **Score:** 10,988 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_5600x`
   * **Test Configuration:** Stock clocks, 65W TDP, DDR4-3200 dual-channel, tower air cooler.

9. **`BM_CPU_009` — AMD Ryzen 5 5600 (`DS3_CPU_010`)**
   * **Score:** 11,077 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_5600`
   * **Test Configuration:** Stock clocks, 65W TDP, DDR4-3200 dual-channel, tower air cooler.

10. **`BM_CPU_010` — Intel Core i5-12400F (`DS3_CPU_014`)**
    * **Score:** 12,454 pts
    * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i5_12400f`
    * **Test Configuration:** Stock power limits (65W base / 117W max turbo), DDR4-3200.

11. **`BM_CPU_011` — AMD Ryzen 5 5600G (`DS3_CPU_029`)**
    * **Score:** 10,202 pts
    * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_5600g`
    * **Test Configuration:** Stock clocks, 65W TDP, DDR4-3200 dual-channel, standard air cooler.

12. **`BM_CPU_012` — Intel Core i3-12100F (`DS3_CPU_040`)**
    * **Score:** 8,443 pts
    * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i3_12100f`
    * **Test Configuration:** Stock power limits (60W base / 89W max turbo), DDR4-3200.

---

## 3. Unresolved CPU & Rejection Audit

### `DS3_CPU_055` — AMD Ryzen 5 5600GT
* **Status:** **UNRESOLVED (Rejected for Batch 1)**
* **Reason:**
  1. **Absence of Standardized Stock Review:** Major independent test labs (TechPowerUp, Tom's Hardware, AnandTech, KitGuru) did not conduct a standalone day-one review of the Ryzen 5 5600GT with Cinebench R23.
  2. **Overclocked Records Only:** Available public entries on HWBOT represent competitive manual overclocks (4.6 GHz to 4.8 GHz all-core OC scoring 11,444 to 11,818 cb), which violate the strict requirement to record stock baseline performance.
  3. **No Estimated Scores Allowed:** While architectural estimates place the 5600GT around ~10,200 to 10,400 pts (slightly above 5600G), importing estimated or interpolated values is prohibited by project data integrity rules.
* **Resolution Plan:** Deferred to future benchmark research when an independently verified stock review result or multi-run user submission with stock power limits is audited.

---

## 4. Verification and Data Integrity

* **Component Foreign Key Integrity:** 100% (all 12 `component_id` entries match verified CPUs in `data/components.csv`).
* **Duplicate Observations:** 0 (all 12 records have unique `benchmark_id` and unique `(component_id, benchmark_suite, benchmark_metric)` tuples).
* **Production Code Integrity:** Unchanged (`app.py`, `src/compatibility.py`, `src/validator.py`, `data/components.csv`, `data/prices.csv` were not modified).

