# CPU Feature Enrichment Report (Phase 3C)

## 1. Executive Summary & Objective

Phase 3C investigates whether enriching the CPU specification dataset with verified architectural and cache metrics improves empirical Cinebench R23 Multi-Core benchmark predictions.

A supplemental verified specification dataset was collected for all **55 CPUs** currently benchmarked in `data/benchmarks.csv` without modifying the core production catalog (`data/components.csv`).

All data was sourced directly from official manufacturer documentation:
- **AMD Official Processor Specifications** (`amd.com`)
- **Intel ARK Processor Specifications** (`intel.com`)

Output dataset: [`data/ml/cpu_feature_enrichment_v1.csv`](file:///E:/BuildWise-AI/BuildWise-AI1/data/ml/cpu_feature_enrichment_v1.csv)  
Total verified records: **275 records** (5 verified attributes $\times$ 55 CPUs).

---

## 2. Enriched Feature Definitions & Standards

To ensure data integrity and prevent ambiguities in reporting conventions across manufacturers:

### A. Microarchitecture (`architecture`)
- **Definition:** The fundamental CPU core microarchitectural generation design.
- **Reporting Standard:**
  - **AMD:** `Zen 3` (5000-series), `Zen 4` (7000/8000-series), `Zen 5` (9000-series).
  - **Intel:** `Alder Lake` (12th Gen Golden Cove + Gracemont), `Raptor Lake` (13th Gen Raptor Cove + Gracemont), `Raptor Lake Refresh` (14th Gen), `Arrow Lake` (Core Ultra 200S Lion Cove + Skymont).
- **Distinction from Codename:** Codenames represent silicon fabrication dies or product segments (e.g., `Cezanne` vs `Vermeer` are both `Zen 3`; `Arrow Lake-S` compute tile is `Arrow Lake`).

### B. Level 3 Cache (`cache_l3_mb`)
- **Definition:** Total shared Level 3 cache capacity accessible by CPU cores, reported in Megabytes (MB).
- **Reporting Standard:**
  - **Standard Desktop Dies:** 16 MB (monolithic APUs like Cezanne, Phoenix), 32 MB (single CCD Vermeer, Raphael, Granite Ridge), 64 MB (dual CCDs Vermeer, Raphael, Granite Ridge).
  - **AMD 3D V-Cache SKUs:** Includes both on-die 2D L3 and stacked 3D SRAM. Total L3 is 96 MB for 8-core SKUs (32 MB + 64 MB) and 128 MB for 16-core SKUs (32 MB + 64 MB + 32 MB).
  - **Intel Smart Cache:** Intel's shared Last-Level Cache (LLC) dynamically shared across P-cores and E-core clusters (ranging from 12 MB on i3-12100F up to 36 MB on i9-13900K/14900K and Core Ultra 9 285K).
- **Conversion Rule:** Reported directly in Megabytes ($1 \text{ MB} = 1024 \text{ KB}$).

### C. Level 2 Cache (`cache_l2_mb`)
- **Definition:** Total aggregated Level 2 cache across all cores on the processor in Megabytes (MB).
- **Reporting Standard:**
  - **AMD Zen 3:** 512 KB per core (e.g., 6 cores = 3.0 MB, 8 cores = 4.0 MB, 12 cores = 6.0 MB, 16 cores = 8.0 MB).
  - **AMD Zen 4 & Zen 5:** 1 MB per core (e.g., 6 cores = 6.0 MB, 8 cores = 8.0 MB, 12 cores = 12.0 MB, 16 cores = 16.0 MB).
  - **Intel Hybrid:** Sum of dedicated P-core L2 caches (1.25 MB on Alder Lake, 2.0 MB on Raptor Lake, 3.0 MB on Arrow Lake) plus shared cluster L2 per 4-core E-core cluster (2.0 MB on Alder Lake, 4.0 MB on Raptor Lake / Arrow Lake).

### D. Base Frequency (`base_clock_ghz`)
- **Definition:** The guaranteed base operating frequency under baseline TDP envelope in Gigahertz (GHz).
- **Reporting Standard:**
  - For standard AMD CPUs: Advertised Base Clock.
  - For Intel Hybrid architectures (P-cores + E-cores): P-core Base Frequency (Performance-core base clock).

### E. Silicon Codename (`cpu_codename`)
- **Definition:** The internal semiconductor die family designation or design codename.
- **Reporting Standard:** `Cezanne`, `Vermeer`, `Phoenix`, `Raphael`, `Granite Ridge`, `Alder Lake-S`, `Raptor Lake-S`, `Raptor Lake Refresh`, `Arrow Lake-S`.

---

## 3. Feature Coverage & Provenance Table

| Feature Name | Coverage | Null / Missing | Min Value | Max Value | Primary Sources |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `architecture` | 55 / 55 (100%) | 0 (0%) | - | - | AMD Official Specifications, Intel ARK |
| `cache_l3_mb` | 55 / 55 (100%) | 0 (0%) | 12.0 MB | 128.0 MB | AMD Official Specifications, Intel ARK |
| `cache_l2_mb` | 55 / 55 (100%) | 0 (0%) | 3.0 MB | 40.0 MB | AMD Official Specifications, Intel ARK |
| `base_clock_ghz` | 55 / 55 (100%) | 0 (0%) | 2.1 GHz | 4.7 GHz | AMD Official Specifications, Intel ARK |
| `cpu_codename` | 55 / 55 (100%) | 0 (0%) | - | - | AMD Official Specifications, Intel ARK |

---

## 4. Distribution by Architecture & Cache

### Microarchitectures in Dataset
1. **Zen 3 (AM4):** 12 processors (5500, 5600, 5600G, 5600X, 5700G, 5700X, 5700X3D, 5800X, 5800XT, 5800X3D, 5900X, 5900XT).
2. **Zen 4 (AM5):** 14 processors (7500F, 7600, 7600X, 7600X3D, 7700, 7700X, 7800X3D, 7900, 7900X, 7950X, 7950X3D, 8600G, 8700G, 8700F).
3. **Zen 5 (AM5):** 5 processors (9600X, 9700X, 9800X3D, 9900X, 9950X).
4. **Alder Lake (LGA1700):** 7 processors (i3-12100F, i5-12400F, i5-12600K, i5-12600KF, i7-12700K, i7-12700KF, i9-12900K).
5. **Raptor Lake (LGA1700):** 4 processors (i5-13400F, i5-13600KF, i7-13700K, i9-13900K).
6. **Raptor Lake Refresh (LGA1700):** 9 processors (i5-14400F, i5-14600K, i5-14600KF, i7-14700F, i7-14700K, i7-14700KF, i9-14900K, i9-14900KF, i9-14900KS).
7. **Arrow Lake (LGA1851):** 4 processors (Ultra 5 245KF, Ultra 7 265K, Ultra 7 265KF, Ultra 9 285K).

---

## 5. Controlled Experimental Configurations (for Phase 3C)

To rigorously evaluate the predictive utility of these features without leakage or confounding effects, four experimental feature sets are formulated:

- **Feature Set A (Original V1 Baseline):** `cores`, `threads`, `boost_clock_ghz`, `tdp_w`, `brand`, `socket`.
- **Feature Set B (Architecture):** Original 6 features + `architecture`.
- **Feature Set C (Cache):** Original 6 features + `cache_l3_mb`.
- **Feature Set D (Combined):** Original 6 features + `architecture` + `cache_l3_mb`.
- **Feature Set E (Comprehensive):** Original 6 features + `architecture` + `cache_l3_mb` + `cache_l2_mb` + `base_clock_ghz`.
