# BuildWise-AI — CPU Benchmark Batch 2 Audit Report

**Audit Date:** 2026-11-06  
**Benchmark Suite:** Cinebench R23  
**Metric:** Multi-Core Score (`pts`)  
**Scope:** 10 Priority 2 Processors (Mainstream & Budget Volume)  
**Target File:** [`data/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/data/benchmarks.csv)  
**Backup File:** [`backups/pre_cpu_benchmark_batch2_20261106_185200/benchmarks.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/backups/pre_cpu_benchmark_batch2_20261106_185200/benchmarks.csv)  
**Candidate Source:** [`third_dataset_research/benchmarks/batch2_cpu_candidates.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/third_dataset_research/benchmarks/batch2_cpu_candidates.csv)  

---

## 1. Executive Summary

Batch 2 targets the first **10 unrecorded processors from Priority 2** in the CPU Benchmark Collection Guide, covering mainstream and budget workhorse CPUs across Intel LGA1700, Intel LGA1851, AMD AM5, and AMD AM4.

* **CPUs Researched:** 10
* **Accepted Benchmark Records:** 10
* **Unresolved / Rejected Records:** 0
* **Pre-Import Row Count in `data/benchmarks.csv`:** 12
* **Post-Import Row Count in `data/benchmarks.csv`:** 22
* **Schema Validation Issues:** 0
* **Duplicate Observations:** 0

---

## 2. Accepted Benchmark Observations (10 Processors)

| Benchmark ID | Component ID | Brand | Model | Socket | Cores/Threads | Boost Clock | TDP | Cinebench R23 Multi | Source | Verified Date | Configuration Disclosure |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `BM_CPU_013` | `cpu-i5-14600k` | Intel | Core i5-14600K | LGA1700 | 14C / 20T | 5.3 GHz | 181W | **24,683 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 181W, DDR5-5600) |
| `BM_CPU_014` | `cpu-intel-core-ultra-5-245kf` | Intel | Core Ultra 5 245KF | LGA1851 | 14C / 14T | 5.2 GHz | 159W | **25,188 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 159W, DDR5-6400) |
| `BM_CPU_015` | `cpu-intel-core-i7-14700k` | Intel | Core i7-14700K | LGA1700 | 20C / 28T | 5.6 GHz | 253W | **36,245 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 253W, DDR5-5600) |
| `BM_CPU_016` | `cpu-intel-core-i7-14700kf` | Intel | Core i7-14700KF | LGA1700 | 20C / 28T | 5.6 GHz | 253W | **36,245 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock, 253W, DDR5-5600) |
| `BM_CPU_017` | `amd-ryzen-5-7600` | AMD | Ryzen 5 7600 | AM5 | 6C / 12T | 5.1 GHz | 65W | **14,540 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR5-5200) |
| `BM_CPU_018` | `amd-ryzen-7-8700g` | AMD | Ryzen 7 8700G | AM5 | 8C / 16T | 5.1 GHz | 65W | **18,040 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR5-5200) |
| `BM_CPU_019` | `amd-ryzen-5-8600g` | AMD | Ryzen 5 8600G | AM5 | 6C / 12T | 5.0 GHz | 65W | **14,067 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR5-5200) |
| `BM_CPU_020` | `DS3_CPU_011` | AMD | Ryzen 7 5800X | AM4 | 8C / 16T | 4.7 GHz | 105W | **15,228 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 105W, DDR4-3200) |
| `BM_CPU_021` | `DS3_CPU_016` | AMD | Ryzen 7 5700X | AM4 | 8C / 16T | 4.6 GHz | 65W | **14,309 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 65W, DDR4-3200) |
| `BM_CPU_022` | `DS3_CPU_021` | AMD | Ryzen 7 5700X3D | AM4 | 8C / 16T | 4.1 GHz | 105W | **13,786 pts** | CPU-Monkey | 2026-11-06 | Disclosed (Stock 105W, DDR4-3200) |

---

### Detailed Test Configurations & Direct Source URLs

1. **`BM_CPU_013` — Intel Core i5-14600K (`cpu-i5-14600k`)**
   * **Score:** 24,683 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i5_14600k`
   * **Test Configuration:** Stock settings, 181W turbo envelope, DDR5-5600.

2. **`BM_CPU_014` — Intel Core Ultra 5 245KF (`cpu-intel-core-ultra-5-245kf`)**
   * **Score:** 25,188 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_ultra_5_245kf`
   * **Test Configuration:** Stock settings, 159W turbo envelope, DDR5-6400.

3. **`BM_CPU_015` — Intel Core i7-14700K (`cpu-intel-core-i7-14700k`)**
   * **Score:** 36,245 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i7_14700k`
   * **Test Configuration:** Stock settings, 253W turbo envelope, DDR5-5600.

4. **`BM_CPU_016` — Intel Core i7-14700KF (`cpu-intel-core-i7-14700kf`)**
   * **Score:** 36,245 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-intel_core_i7_14700kf`
   * **Test Configuration:** Stock settings, 253W turbo envelope, DDR5-5600.

5. **`BM_CPU_017` — AMD Ryzen 5 7600 (`amd-ryzen-5-7600`)**
   * **Score:** 14,540 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_7600`
   * **Test Configuration:** Stock 65W TDP, DDR5-5200.

6. **`BM_CPU_018` — AMD Ryzen 7 8700G (`amd-ryzen-7-8700g`)**
   * **Score:** 18,040 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_8700g`
   * **Test Configuration:** Stock 65W TDP, DDR5-5200.

7. **`BM_CPU_019` — AMD Ryzen 5 8600G (`amd-ryzen-5-8600g`)**
   * **Score:** 14,067 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_5_8600g`
   * **Test Configuration:** Stock 65W TDP, DDR5-5200.

8. **`BM_CPU_020` — AMD Ryzen 7 5800X (`DS3_CPU_011`)**
   * **Score:** 15,228 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_5800x`
   * **Test Configuration:** Stock 105W TDP envelope, DDR4-3200 dual-channel.

9. **`BM_CPU_021` — AMD Ryzen 7 5700X (`DS3_CPU_016`)**
   * **Score:** 14,309 pts
   * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_5700x`
   * **Test Configuration:** Stock 65W TDP, DDR4-3200 dual-channel.

10. **`BM_CPU_022` — AMD Ryzen 7 5700X3D (`DS3_CPU_021`)**
    * **Score:** 13,786 pts
    * **Direct URL:** `https://www.cpu-monkey.com/en/cpu-amd_ryzen_7_5700x3d`
    * **Test Configuration:** Stock 105W TDP envelope, DDR4-3200 dual-channel.

---

## 3. Data Integrity & Validation

* **Foreign Key Check:** 100% (all 10 `component_id` values verified against `data/components.csv`).
* **Uniqueness:** All 22 `benchmark_id` records in `data/benchmarks.csv` are unique; no duplicate `(component_id, benchmark_suite, benchmark_metric)` pairs exist.
* **Controlled Isolation:** Unresolved CPUs remain 0 in Batch 2; all 10 candidates met verification criteria.
* **Production Code Integrity:** Unchanged (`components.csv`, `prices.csv`, `app.py`, `src/compatibility.py`, and recommendation logic were not modified).

