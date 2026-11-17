# BuildWise-AI — CPU Benchmark Batch 3 Audit Report

**Audit Date:** 2026-11-06  
**Benchmark Suite:** Cinebench R23  
**Metric:** Multi-Core Score (`pts`)  
**Scope:** 10 Priority 2 Processors (Mainstream & Budget Volume)  
**Target File:** [`data/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/data/benchmarks.csv)  
**Backup File:** [`backups/pre_cpu_benchmark_batch3_20261106_191200/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/backups/pre_cpu_benchmark_batch3_20261106_191200/benchmarks.csv)  
**Candidate Source:** [`third_dataset_research/benchmarks/batch3_cpu_candidates.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/third_dataset_research/benchmarks/batch3_cpu_candidates.csv)  

---

## 1. Executive Summary

Batch 3 continues research on **Priority 2** mainstream and budget processors from the CPU Benchmark Collection Guide, covering key AMD AM4/AM5 and Intel LGA1700 desktop processors.

* **Processors Researched:** 10
* **Accepted Benchmark Records:** 9
* **Unresolved / Deferred Processors:** 1 (`DS3_CPU_036` — AMD Ryzen 5 8500G)
* **Pre-Import Row Count in `data/benchmarks.csv`:** 22
* **Post-Import Row Count in `data/benchmarks.csv`:** 31
* **Schema Validation Issues:** 0
* **Duplicate Observations:** 0

---

## 2. Accepted Benchmark Observations (9 Processors)

| Benchmark ID | Component ID | Brand | Model | Socket | Cores/Threads | Boost Clock | TDP | Cinebench R23 Multi | Source | Verified Date | Configuration Disclosure |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `BM_CPU_023` | `DS3_CPU_022` | Intel | Core i5-14400F | LGA1700 | 10C / 16T | 4.7 GHz | 148W | **16,074 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 148W, DDR5-4800) |
| `BM_CPU_024` | `DS3_CPU_024` | AMD | Ryzen 5 7500F | AM5 | 6C / 12T | 5.0 GHz | 65W | **14,072 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR5-5200) |
| `BM_CPU_025` | `DS3_CPU_025` | AMD | Ryzen 7 5800XT | AM4 | 8C / 16T | 4.8 GHz | 105W | **15,036 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 105W, DDR4-3200) |
| `BM_CPU_026` | `DS3_CPU_027` | Intel | Core i7-12700K | LGA1700 | 12C / 20T | 5.0 GHz | 190W | **22,812 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 190W, DDR5-4800) |
| `BM_CPU_027` | `DS3_CPU_028` | AMD | Ryzen 5 7600X3D | AM5 | 6C / 12T | 4.7 GHz | 65W | **13,463 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR5-5200) |
| `BM_CPU_028` | `DS3_CPU_030` | AMD | Ryzen 7 7700 | AM5 | 8C / 16T | 5.3 GHz | 65W | **19,540 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR5-5200) |
| `BM_CPU_029` | `DS3_CPU_031` | Intel | Core i5-13400F | LGA1700 | 10C / 16T | 4.6 GHz | 148W | **15,890 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 148W, DDR5-4800) |
| `BM_CPU_030` | `DS3_CPU_033` | Intel | Core i7-12700KF | LGA1700 | 12C / 20T | 5.0 GHz | 190W | **22,812 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 190W, DDR5-4800) |
| `BM_CPU_031` | `DS3_CPU_035` | Intel | Core i5-12600KF | LGA1700 | 10C / 16T | 4.9 GHz | 150W | **17,660 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 150W, DDR5-4800) |

---

### Detailed Test Configurations & Direct Source URLs

1. **`BM_CPU_023` — Intel Core i5-14400F (`DS3_CPU_022`)**
   * **Score:** 16,074 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i5_14400f`
   * **Cross-Checking:** Corroborated with HWCooling review (15,858 pts B0 stepping).
   * **Test Configuration:** Stock power limits (65W base / 148W max turbo), DDR5-4800.

2. **`BM_CPU_024` — AMD Ryzen 5 7500F (`DS3_CPU_024`)**
   * **Score:** 14,072 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_7500f`
   * **Test Configuration:** Stock 65W TDP, DDR5-5200.

3. **`BM_CPU_025` — AMD Ryzen 7 5800XT (`DS3_CPU_025`)**
   * **Score:** 15,036 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_5800xt`
   * **Test Configuration:** Stock 105W TDP envelope, DDR4-3200 dual-channel.

4. **`BM_CPU_026` — Intel Core i7-12700K (`DS3_CPU_027`)**
   * **Score:** 22,812 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i7_12700k`
   * **Cross-Checking:** Corroborated with TechPowerUp review.
   * **Test Configuration:** Stock settings (125W base / 190W max turbo), DDR5-4800.

5. **`BM_CPU_027` — AMD Ryzen 5 7600X3D (`DS3_CPU_028`)**
   * **Score:** 13,463 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_7600x3d`
   * **Test Configuration:** Stock 65W TDP, DDR5-5200.

6. **`BM_CPU_028` — AMD Ryzen 7 7700 (`DS3_CPU_030`)**
   * **Score:** 19,540 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_7700`
   * **Cross-Checking:** Corroborated with TechPowerUp review (~19,300–19,550 pts).
   * **Test Configuration:** Stock 65W TDP, DDR5-5200.

7. **`BM_CPU_029` — Intel Core i5-13400F (`DS3_CPU_031`)**
   * **Score:** 15,890 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i5_13400f`
   * **Cross-Checking:** Corroborated with Tom's Hardware review (~16,000–16,130 pts).
   * **Test Configuration:** Stock power limits (65W base / 148W max turbo), DDR5-4800.

8. **`BM_CPU_030` — Intel Core i7-12700KF (`DS3_CPU_033`)**
   * **Score:** 22,812 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i7_12700kf`
   * **Test Configuration:** Stock settings (125W base / 190W max turbo), DDR5-4800.

9. **`BM_CPU_031` — Intel Core i5-12600KF (`DS3_CPU_035`)**
   * **Score:** 17,660 pts | **Verified:** 2026-11-06
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i5_12600kf`
   * **Test Configuration:** Stock settings (125W base / 150W max turbo), DDR5-4800.

---

## 3. Unresolved / Rejected CPU Audit

### `DS3_CPU_036` — AMD Ryzen 5 8500G
* **Status:** **UNRESOLVED (Rejected for Batch 3)**
* **Reason:**
  1. **Release Timing & Suite Transition:** The Ryzen 5 8500G launched in early 2024, by which point hardware review suites (TechPowerUp, Tom's Hardware, KitGuru, ComputerBase) had transitioned from Cinebench R23 to Cinebench 2024.
  2. **No Verifiable R23 Multi-Core Baseline:** The official CPU-Monkey profile lists Cinebench 2024 (742 pts multi-core) and Geekbench 6, but does not provide an audited stock Cinebench R23 Multi-Core score.
  3. **Strict Policy Compliance:** In accordance with project integrity guidelines prohibiting derivation from other benchmark suites or estimation, this processor remains excluded from the production benchmark dataset until an independently verified stock R23 measurement is documented.

---

## 4. Data Integrity & Validation

* **Foreign Key Check:** 100% (all 31 `component_id` values match verified CPUs in [`data/components.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/data/components.csv)).
* **Uniqueness:** All 31 `benchmark_id` records in `data/benchmarks.csv` are unique; 0 duplicate `(component_id, benchmark_suite, benchmark_metric)` pairs exist.
* **Controlled Isolation:** Unresolved processor `DS3_CPU_036` is preserved in the audit log and omitted from the production CSV.
* **Production Code Integrity:** Unchanged (`components.csv`, `prices.csv`, `app.py`, `src/compatibility.py`, and recommendation logic were not modified).

