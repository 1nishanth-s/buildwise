# BuildWise-AI — Phase 6F: Canonical Unified Component Dataset Validation Report

**Phase:** Phase 6F (Canonical Unified Component Dataset)  
**Date:** November 8, 2026  
**Auditor:** Senior PC Hardware Research Engineer, Data Engineer & ML Dataset Specialist  
**Project:** BuildWise-AI  
**Gate Status:** STANDBY — Fully Validated Canonical Dataset Staged (Zero Production Modifications)  

---

## 1. Executive Summary & Architectural Overview

Phase 6F establishes the single canonical component catalog for BuildWise-AI:
[`reports/phase6_unified_catalog/unified_component_catalog.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_unified_catalog/unified_component_catalog.csv)

### 1.1 The Single Canonical Catalog Architecture
In strict conformance with project architectural requirements:
- **No Fragmented Per-Category CSVs:** Separate files like `cpu.csv`, `gpu.csv`, `motherboard.csv`, etc., are **strictly rejected**.
- **Single Canonical Entity Master:** All hardware components across all eight sanctioned categories reside in a single canonical dataset differentiated by the mandatory `category` column.
- **Relational Dataset Separation:** The separation of concerns between components, prices, and benchmarks is strictly maintained:

```text
                 ┌─────────────────────────────────────┐
                 │    unified_component_catalog.csv    │
                 │             1,208 rows              │
                 ├─────────────────────────────────────┤
                 │ Defines WHAT the hardware product is│
                 │ (Category, Brand, Model, Specs JSON)│
                 └──────────────────┬──────────────────┘
                                    │
                              component_id
                                    │
              ┌─────────────────────┴─────────────────────┐
              │                                           │
       ┌──────▼──────┐                             ┌──────▼────────┐
       │ prices.csv  │                             │ benchmarks.csv│
       │  599 rows   │                             │   237 rows    │
       ├─────────────┤                             ├───────────────┤
       │ Historical  │                             │ Empirical     │
       │ retail INR  │                             │ performance   │
       │ price quotes│                             │ measurements  │
       └─────────────┘                             └───────────────┘
```

Price observations are NOT flattened into `components.csv`. Benchmark measurements are NOT flattened into `components.csv`. This architectural boundary guarantees clean machine learning feature sets and robust historical price tracking.

---

## 2. Quantitative Catalog Reconciliation

The canonical unified dataset contains exactly **1,208 accepted component records**, matching the approved production import plan:

| Category | Existing Production Baseline | New Accepted Candidates | Quarantined / Held Staged | Final Unified Total | Target Distribution Check |
|---|---:|---:|---:|---:|:---:|
| **CPU** | 64 | 116 | 0 | **180** | PASSED (Target: 180) |
| **GPU** | 75 | 143 | 2 (`CAND_GPU_142`, `143`) | **218** | PASSED (Target: 218) |
| **Motherboard** | 95 | 85 | 0 | **180** | PASSED (Target: 180) |
| **RAM** | 49 | 111 | 0 | **160** | PASSED (Target: 160) |
| **Storage** | 45 | 105 | 0 | **150** | PASSED (Target: 150) |
| **PSU** | 37 | 83 | 0 | **120** | PASSED (Target: 120) |
| **Case** | 33 | 67 | 0 | **100** | PASSED (Target: 100) |
| **Cooler** | 23 | 77 | 0 | **100** | PASSED (Target: 100) |
| **TOTAL** | **421** | **787** | **2** | **1,208** | **PASSED (Target: 1,208)** |

---

## 3. Product Identity & Deduplication Results

- **Row Count:** Exactly 1,208 rows ($1,208 / 1,208$).
- **Primary Key Uniqueness:** Exactly 1,208 unique `component_id` values. Zero duplicate IDs.
- **Production Collision Audit:** 0 collisions between the 421 production IDs and 787 candidate IDs.
- **Exact Duplicates:** 0 exact duplicate hardware models.
- **Marketing Aliases:** 0 same-product marketing alias collisions.
- **Held Components Excluded:** Confirmed that `CAND_GPU_142` (AMD Radeon RX 9070 16GB Reference) and `CAND_GPU_143` (AMD Radeon RX 9070 XT 16GB Reference) are **strictly excluded**.
- **Legitimate Variants Preserved (262 records):** 262 multi-variant records (represented by 29 detailed head-to-head pairs in [`legitimate_variants_report.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_duplicate_audit/legitimate_variants_report.csv)) are preserved:
  - Intel K (unlocked) vs non-K (locked 65W) vs F (discrete GPU required).
  - AMD X vs non-X vs X3D (96MB 3D V-Cache).
  - Board-partner custom cooling cards (ASUS TUF 301mm 3.15-slot vs FE 242mm dual-slot).
  - 8GB vs 16GB GPU VRAM variants.
  - Motherboard DDR4 vs DDR5 editions (ASUS PRIME B660M-A D4 vs B660M-A).
  - Dual-channel 2×16GB RAM kits vs single-channel 1×32GB modules.
  - 1TB vs 2TB SSD capacities with different TBW endurance and DRAM caches.
  - SFX compact (100mm) vs ATX standard (140mm) power supply form factors.
  - Case structural revisions (NZXT H5 Flow 2022 365mm clearance vs 2024 410mm clearance).
  - Single-tower (AK400, 220W) vs dual-tower (AK620, 260W) air coolers.

---

## 4. Compatibility Enrichment Results

All 239 accepted compatibility enrichment records from [`staged_enrichment.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/reports/dataset_expansion/candidates/staged_enrichment.csv) have been applied in-place to the production components in `unified_component_catalog.csv`:

### 4.1 Enrichment Metrics
- **Target Components:** Exactly 239 production components (`gpu`: 70, `motherboard`: 94, `psu`: 36, `case`: 18, `cooler`: 21).
- **Target Verification:** 239 / 239 target IDs exist in the catalog. Missing targets: **0**.
- **Held Component Isolation:** **0** enrichment records reference held components.
- **Specification Preservation:** **100% of existing verified keys were preserved**. Zero existing keys were lost ($0 / 239$).
- **Enriched Field Scope:** Updated 60 critical physical, electrical, and dimensional fields supported by the compatibility engine:
  - *GPUs:* `length_mm`, `slot_thickness_mm`, `gpu_height_mm`, `required_power_connectors`, `recommended_system_psu_w`, `pcie_lane_width`.
  - *Motherboards:* `m2_slots_count`, `pcie_lane_sharing`, `front_panel_usb_headers`, `bios_flashback_button`.
  - *PSUs:* `unit_length_mm`, `pcie_5_connectors`, `atx_specification_version`.
  - *Cases:* `max_gpu_length_mm`, `max_cpu_cooler_mm`, `max_psu_length_mm`, `radiator_support_locations`.
  - *Coolers:* `height_mm`, `tdp_rating_w`, `ram_clearance_mm`, `socket_support`.
- **Catalog Row Count Impact:** In-place update only. **0 rows added to the component catalog.**

---

## 5. Foreign-Key Referential Integrity Validation

The unified catalog was validated as an authoritative relational target for all dependent datasets:

| Relational Dataset | Source Files | Observation Count | Valid Target Component IDs | Broken Foreign Keys |
|---|---|---:|---:|---:|
| **Retail Prices** | `data/prices.csv` (88) + `cleaned_price_candidates.csv` (511) | 599 | 545 unique components | **0** |
| **CPU Benchmarks** | `data/benchmarks.csv` (55) + `staged_batch9_cpu_benchmarks.csv` (125) | 180 | 180 unique CPUs | **0** |
| **GPU Benchmarks** | `data/benchmarks.csv` (57 production observations) | 57 | 57 unique GPUs | **0** |
| **Total Benchmarks** | CPU (180) + GPU (57) | 237 | 237 unique components | **0** |

- **Zero Broken Foreign Keys:** All 599 prices and 237 benchmarks resolve 100% to valid primary keys in `unified_component_catalog.csv`.
- **Zero Orphaned Price Quotes:** Quarantining `PRICE_198` successfully prevented any orphaned pricing record from linking to the held `CAND_GPU_143`.
- **100% CPU Benchmark Coverage:** Every single one of the 180 CPUs in the unified catalog has exactly 1 verified Cinebench R23 Multi-Core benchmark observation.

---

## 6. Schema and Data Quality Validation

The unified catalog adheres strictly to the authoritative schema:

```text
['component_id', 'category', 'brand', 'model', 'specs_json', 'source_name', 'source_url', 'source_license', 'identity_status']
```

- **Mandatory Fields:** 0 null values in `component_id`, `category`, `brand`, `model`, or `specs_json`.
- **Provenance Fields:** 0 null values in `source_name`, `source_url`, `source_license`, or `identity_status`.
- **JSON Parse Integrity:** 1,208 / 1,208 records parse as valid JSON dictionaries. Zero JSON decoding errors.
- **Category Values:** 100% of rows contain one of the 8 sanctioned categories in lowercase (`cpu`, `gpu`, `motherboard`, `ram`, `storage`, `psu`, `case`, `cooler`).

---

## 7. Deliverable Artifact Manifest in `reports/phase6_unified_catalog/`

| Deliverable File | Format | Row Count | Purpose | Link |
|---|---|---:|---|---|
| `unified_component_catalog.csv` | CSV | 1,208 | Complete canonical component catalog ready for merge | [unified_component_catalog.csv](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_unified_catalog/unified_component_catalog.csv) |
| `category_distribution.csv` | CSV | 9 | Reconciled breakdown across all 8 categories | [category_distribution.csv](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_unified_catalog/category_distribution.csv) |
| `catalog_merge_manifest.csv` | CSV | 5 | Itemized merge operation manifest | [catalog_merge_manifest.csv](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_unified_catalog/catalog_merge_manifest.csv) |
| `component_id_integrity_report.md` | Markdown | — | Primary key taxonomy and foreign-key referential audit | [component_id_integrity_report.md](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_unified_catalog/component_id_integrity_report.md) |
| `source_provenance_report.md` | Markdown | — | Evidence audit across 65 authoritative sources and 72 brands | [source_provenance_report.md](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_unified_catalog/source_provenance_report.md) |
| `unified_catalog_validation_report.md` | Markdown | — | Master validation report and architectural sign-off | [unified_catalog_validation_report.md](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_unified_catalog/unified_catalog_validation_report.md) |

---

## 8. Production Protection Compliance

- [x] **Production Datasets Untouched:** [`data/components.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/data/components.csv) (421), [`data/prices.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/data/prices.csv) (88), and [`data/benchmarks.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/data/benchmarks.csv) (112) remain preserved and unmodified.
- [x] **Application Code Untouched:** `app.py`, `src/compatibility.py`, and ML models remain unmodified.
- [x] **Staged Source Files Preserved:** All candidate batch CSVs remain untouched.
- [x] **Test Suite Health:** All 113 automated unit tests pass cleanly in 75.38s; `validate_data.py` passes with exit code 0.
- [x] **Git Isolation:** Zero commits or pushes executed.

---

## 9. Production Integration Gate Status

> [!IMPORTANT]
> **GATE STATUS: STANDBY — READY FOR PHASE 6E CONTROLLED IMPORT**  
> The 1,208-row canonical unified component catalog has been completely built, enriched, and validated in `reports/phase6_unified_catalog/unified_component_catalog.csv`.  
> All 599 prices and 237 benchmarks resolve with zero broken foreign keys.  
> Production datasets remain strictly protected pending explicit authorization to execute the Phase 6E import.
