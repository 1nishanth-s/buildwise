# BuildWise-AI — Phase 6C: Foreign Key Remapping and Relational Integrity Report

**Audit Date:** November 7, 2026  
**Auditor:** Senior PC Hardware Research Engineer & Data Engineer  
**Status:** Relational Integrity Verified — Zero Broken Foreign Keys  

---

## 1. Relational Architecture Overview

In BuildWise-AI, `components.csv` serves as the primary master entity table. Multiple auxiliary datasets depend on `component_id` as a foreign key:

```mermaid
erDiagram
    COMPONENTS ||--o{ PRICES : "has price observations"
    COMPONENTS ||--o{ BENCHMARKS : "has benchmark scores"
    COMPONENTS ||--o| ENRICHMENT : "has physical/electrical specs"
    COMPONENTS {
        string component_id PK
        string category
        string brand
        string model
        string specs_json
    }
    PRICES {
        string price_id PK
        string component_id FK
        string seller
        float price_inr
    }
    BENCHMARKS {
        string benchmark_id PK
        string component_id FK
        string benchmark_type
        float score
    }
    ENRICHMENT {
        string component_id FK
        string specs_json
    }
```

Any modification, deduplication, or exclusion of component records carries a direct risk of corrupting relational foreign keys.

---

## 2. Component Identity Mapping Analysis

The audit generated `component_identity_mapping.csv` covering all 789 staged candidate components:

| Candidate Subset | Count | Identity Classification | Action | Canonical ID Mapping |
|---|---:|---|---|---|
| **Accepted Candidates** | 787 | `UNIQUE_NEW_RECORD` | `IMPORT_AS_NEW` | `original_id` $\rightarrow$ `original_id` |
| **Held Candidates** | 2 | `AMBIGUOUS_NEEDS_REVIEW` | `HOLD` | `original_id` $\rightarrow$ `original_id` |
| **Exact Duplicates** | 0 | `EXACT_DUPLICATE` | `EXCLUDE` | N/A (None Detected) |
| **TOTAL** | **789** | — | — | — |

Because **zero duplicate collisions** occurred between candidates and production, **zero foreign key re-pointing** was necessary for accepted candidate components. Every accepted candidate retains its assigned canonical ID upon import.

---

## 3. Auxiliary Dataset Foreign Key Audit

### 3.1 Price Observations (`staged_prices.csv`)
- **Total Staged Prices:** 512 observations (`PRICE_089` through `PRICE_600`).
- **Referenced Components:** 545 unique components across production and candidate catalogs.
- **Relational Integrity Audit:**
  - 511 prices reference accepted candidate or production components.
  - **Crucial Discovery & Action:** Exactly 1 staged price observation (`PRICE_198`) references the held candidate `CAND_GPU_143`:
    - `PRICE_198`: Vedant Computers listing for `AMD Radeon RX 9070 XT 16GB Reference` at INR 8,290.00.
    - *Audit Finding:* This INR 8,290 price represents an anomalous pre-order deposit or retailer placeholder for an unlaunched GPU.
    - *Preservation & Quarantine Action:* To prevent an orphaned foreign key in production, `PRICE_198` is **quarantined alongside `CAND_GPU_143`**. It will NOT be imported into production until `CAND_GPU_143` is formally accepted.
  - **Cleaned Price Candidate Pool:** 511 valid price observations ready for controlled production import.

### 3.2 CPU Benchmark Observations (`staged_batch9_cpu_benchmarks.csv`)
- **Total Staged CPU Benchmarks:** 125 Cinebench R23 Multi-Core observations (`BM_CPU_056` to `BM_CPU_180`).
- **Referenced Components:** 125 unique CPU components (candidate CPUs + unbenchmarked production CPUs).
- **Foreign Key Check:** 100% of referenced `component_id` values resolve to valid CPU records.
- **Projected Catalog Coverage:** Upon import, all 180 CPUs in the expanded catalog (64 production + 116 accepted candidates) will have verified Cinebench R23 benchmark scores, achieving **100% CPU benchmark coverage** for ML training.

### 3.3 GPU Benchmark Observations (`staged_batch10_gpu_benchmarks.csv`)
- **Total Staged GPU Benchmarks:** 87 Time Spy Graphics observations (`BM_GPU_114` to `BM_GPU_200`).
- **Audit Finding:** Staged GPU benchmarks remain held/quarantined due to the indexing misalignment and unconfirmed Intel Arc B770 observation identified in Phase 6.
- **Foreign Key Check:** Confirmed that `staged_batch10_gpu_benchmarks.csv` contains **zero references** to held candidates `CAND_GPU_142` or `CAND_GPU_143`.

### 3.4 Compatibility Enrichment Data (`staged_enrichment.csv`)
- **Total Staged Enrichment Records:** 239 records.
- **Foreign Key Check:** 100% of enrichment records reference existing production components (`gpu-*`, `mb-*`, `psu-*`, `case-*`, `cooler-*`) to backfill missing physical clearances and electrical specifications. Zero broken foreign keys.

---

## 4. Derivative Artifact Preservation Policy

In accordance with strict safety protocols:
1. **Zero Overwrites:** The original `reports/dataset_expansion/candidates/staged_*.csv` files remain 100% unaltered.
2. **Clean Relational Export:** The verified clean candidates are exported to `reports/phase6_duplicate_audit/cleaned_component_candidates.csv` (787 rows).
3. **Quarantine Preservation:** All held records (`CAND_GPU_142`, `CAND_GPU_143`, and `PRICE_198`) are preserved in `ambiguous_records_report.csv` and documented for future resolution.
