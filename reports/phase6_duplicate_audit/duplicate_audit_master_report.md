# BuildWise-AI — Phase 6C: Comprehensive Component Duplicate, Near-Duplicate and Product Identity Audit Report (Corrected Master)

**Audit Date:** November 7, 2026 (Reconciled & Corrected: November 8, 2026)  
**Auditor:** Senior PC Hardware Research Engineer, Data Engineer & ML Dataset Specialist  
**Project:** BuildWise-AI  
**Status:** Completed — Audit & Staging-Cleanup Only (Zero Production Modifications)  

---

## 1. Executive Summary & Audit Mandate

Phase 5 executed large-scale internet-based dataset expansion, staging candidate hardware components across 8 categories alongside retail prices, empirical benchmarks, and compatibility enrichment data. Phase 6 conducted an independent quality audit, verifying product identities, sources, and baseline integrity.

Phase 6C was commissioned as an independent, comprehensive, conservative component identity audit with a primary mandate:
> **Primary Objective:** Identify and eliminate genuine duplicate component records while preserving all legitimate hardware models, product variants, manufacturer-specific designs, and compatibility-relevant differences.

This audit was conducted strictly under conservative, evidence-based identity principles:
1. **Never conflate legitimate product variants with duplicates:** Different board-partner cooling designs, memory channel configurations, VRAM capacities, motherboard DDR generations, or chassis revisions are functional hardware distinctions vital for compatibility and performance modeling.
2. **Multi-Signal Hardware Verification:** Products were evaluated using manufacturer identifiers, hardware architecture, socket/interface, core configurations, clock rates, physical dimensions, electrical power connectors, and verified manufacturer datasheets.
3. **Foreign Key Integrity:** All relationships across prices, benchmarks, and compatibility enrichment were audited to prevent orphaned foreign keys or corrupted linkages.
4. **Strict Isolation:** Zero modifications were made to production data (`data/components.csv`, `data/prices.csv`, `data/benchmarks.csv`), application code, or the compatibility engine.

### Key Audit Metrics
- **Existing Production Components:** 421 components
- **Original Candidate Components:** 789 components
- **Exact Duplicates Detected Within Candidates:** 0 records
- **Exact Duplicates Detected Against Production:** 0 records
- **Same-Product Aliases Identified:** 0 records
- **Legitimate Product Variant Records Identified & Preserved:** 262 records across all 8 categories (illustrated by 29 representative head-to-head pairs)
- **Ambiguous / Unconfirmed Records Held:** 2 records (`CAND_GPU_142`, `CAND_GPU_143`)
- **Phase 5 Pre-Filtered Redundant Records:** 39 records (14 CPUs, 24 Motherboards, 1 RAM kit)
- **Final Cleaned Unique Candidate Components:** 787 components
- **Final Projected Production Catalog Total:** 1,208 components

---

## 2. Dataset Scope & Audit Methodology

The audit systematically examined all 1,210 total component records across production and candidate staging:

| Dataset | Scope | Component Records | Status |
|---|---|---:|---|
| Production Catalog | `data/components.csv` | 421 | Active Production (Protected) |
| Batch 1 Staged CPUs | `staged_batch1_cpu.csv` | 116 | Candidate Staging |
| Batch 2 Staged GPUs | `staged_batch2_gpu.csv` | 145 | Candidate Staging |
| Batch 3 Staged Motherboards | `staged_batch3_mb.csv` | 85 | Candidate Staging |
| Batch 4 Staged RAM | `staged_batch4_ram.csv` | 111 | Candidate Staging |
| Batch 5 Staged Storage | `staged_batch5_storage.csv` | 105 | Candidate Staging |
| Batch 6 Staged PSUs | `staged_batch6_psu.csv` | 83 | Candidate Staging |
| Batch 7 Staged Cases | `staged_batch7_case.csv` | 67 | Candidate Staging |
| Batch 8 Staged Coolers | `staged_batch8_cooler.csv` | 77 | Candidate Staging |
| Consolidated Candidates | `staged_components.csv` | 789 | Consolidated Staging |
| Phase 5 Rejected Records | `rejected_records.csv` | 39 | Pre-Filtered Duplicates |
| Staged Prices | `staged_prices.csv` | 512 | Price Observations |
| Staged CPU Benchmarks | `staged_batch9_cpu_benchmarks.csv` | 125 | Cinebench R23 Observations |
| Staged GPU Benchmarks | `staged_batch10_gpu_benchmarks.csv` | 143 | Time Spy Observations (Held) |
| Staged System Benchmarks | `staged_system_benchmarks.csv` | 35 | Reference FPS Observations |
| Staged Enrichment | `staged_enrichment.csv` | 239 | Compatibility Metadata |
| Proposed Hardware Categories | `staged_proposed_categories.csv` | 9 | Schema Expansion (Held) |

### Three-Stage Normalization & Comparison Pipeline
To detect potential duplicates, near-duplicates, and naming collisions, every component model string was processed through a 3-tier normalization engine:
- **Tier 1 (Literal Exact Match):** Lowercase, trimmed exact string match.
- **Tier 2 (Stripped Brand Match):** Manufacturer prefix stripped, common punctuation removed (`/`, `-`, `_`, `.` normalized).
- **Tier 3 (Phonetic & Levenshtein Token Match):** Token set ratio analysis with hardware-aware stop words (`edition`, `series`, `gaming`, `oc`, `wifi`).

Pairs exhibiting high token similarity (>0.85) were audited against manufacturer technical datasheets across 10 physical and electrical dimensions.

---

## 3. Four Identity Classifications & Audit Results

Every candidate record was audited against four strict identity classifications:

### A. EXACT_DUPLICATE (0 Records Found)
- **Definition:** The exact same manufacturer hardware SKU represented more than once under different formatting.
- **Audit Result:** **0 exact duplicates** detected. Phase 5 had already applied strict pre-filtering (rejecting 39 redundant SKUs documented in `rejected_records.csv`), leaving zero duplicate inflation in the candidate pool.

### B. SAME_PRODUCT_ALIAS (0 Records Found)
- **Definition:** Two records representing identical physical products where one is merely a marketing abbreviation or localized naming variant.
- **Audit Result:** **0 marketing aliases** detected. All candidate naming formats adhere to standardized manufacturer nomenclature.

### C. LEGITIMATE_VARIANT (262 Records Identified & Preserved)
- **Definition:** Hardware products sharing a core brand or architecture but possessing distinct physical, electrical, memory, or thermal characteristics.
- **Audit Result:** **All preserved!** Distinct SKUs (e.g. DDR4 vs DDR5 motherboards, 8GB vs 16GB GPUs, AIB custom coolers, SFX vs ATX PSUs, and revision updates) were strictly preserved to guarantee compatibility engine precision.

### D. AMBIGUOUS_NEEDS_REVIEW (2 Records Held)
- **Definition:** Records lacking retail board-partner SKUs, verified physical dimensions, or pricing stability.
- **Audit Result:** **2 records held** (`CAND_GPU_142` and `CAND_GPU_143`, AMD Radeon RX 9070 and RX 9070 XT Reference cards). Held from production import pending official retail AIB partner availability.

---

## 4. Category-by-Category Identity Audit Findings

### 4.1 CPUs / Processors
- **Baseline:** 64 production CPUs | **Candidates:** 116 CPUs | **Accepted:** 116 | **Projected Total:** 180 CPUs
- **Duplicate & Alias Findings:** 0 duplicates, 0 aliases.
- **Legitimate Variants Preserved (35 records):**
  - *Intel K vs Non-K vs F Editions:* `Core i7-12700` (65W Base, 180W Turbo, UHD 770) vs `Core i7-12700K` (125W Base, 190W Turbo, unlocked multiplier) vs `Core i5-13400F` (discrete GPU strictly required).
  - *AMD X vs Non-X vs X3D Editions:* `Ryzen 5 7600` (65W TDP with bundled Wraith Stealth cooler) vs `Ryzen 5 7600X` (105W TDP without cooler); `Ryzen 7 7800X3D` (96MB 3D V-Cache for gaming) vs `Ryzen 7 7700X` (32MB standard L3 cache).
- **Desktop vs Mobile Validation:** 100% of candidate CPUs are verified desktop socket processors (AM4, AM5, LGA1700, LGA1200, LGA1851). 0 mobile BGA processors, 0 server SP3/LGA4677 processors, 0 complete desktop systems.

### 4.2 GPUs / Graphics Cards
- **Baseline:** 75 production GPUs | **Candidates:** 145 GPUs | **Held:** 2 | **Accepted:** 143 | **Projected Total:** 218 GPUs
- **Duplicate & Alias Findings:** 0 duplicates, 0 aliases.
- **Legitimate Variants Preserved (52 records):**
  - *VRAM Configurations:* `GeForce RTX 4060 Ti 8GB` vs `GeForce RTX 4060 Ti 16GB` (clamshell memory layout, critical for large language model inference).
  - *Board-Partner Custom Designs:* `NVIDIA GeForce RTX 4070 Founders Edition` (242mm dual-slot) vs `ASUS TUF Gaming RTX 4070 OC` (301mm 3.15-slot triple-fan) vs `Sapphire NITRO+ Radeon RX 7800 XT` (320mm 3-slot).
- **Ambiguous Records Held:**
  - `CAND_GPU_142` (AMD Radeon RX 9070 16GB Reference) & `CAND_GPU_143` (AMD Radeon RX 9070 XT 16GB Reference) held pending retail partner availability.

### 4.3 Motherboards
- **Baseline:** 95 production MBs | **Candidates:** 85 MBs | **Accepted:** 85 | **Projected Total:** 180 MBs
- **Duplicate & Alias Findings:** 0 duplicates, 0 aliases. Phase 5 pre-filtered 24 redundant SKUs.
- **Legitimate Variants Preserved (40 records):**
  - *DDR4 vs DDR5:* `ASUS PRIME B660M-A D4` (DDR4 memory slots) vs `ASUS PRIME B660M-A` (DDR5 memory slots) — physical memory incompatibility.
  - *Revision Updates:* `Gigabyte B650 AORUS ELITE AX` vs `B650 AORUS ELITE AX V2` (enhanced memory trace routing and VRM controllers).

### 4.4 RAM / Memory Kits
- **Baseline:** 49 production RAM | **Candidates:** 111 RAM | **Accepted:** 111 | **Projected Total:** 160 RAM
- **Duplicate & Alias Findings:** 0 duplicates, 0 aliases.
- **Legitimate Variants Preserved (38 records):**
  - *Channel Topologies:* `Corsair Vengeance 32GB (2x16GB) DDR5-6000` (dual-channel 128-bit bus) vs `Corsair Vengeance 32GB (1x32GB) DDR5-5600` (single-channel 64-bit bus).
  - *XMP 3.0 vs AMD EXPO:* `G.Skill Trident Z5 RGB` (Intel XMP) vs `G.Skill Trident Z5 Neo RGB` (AMD EXPO optimized sub-timings).

### 4.5 Storage Devices
- **Baseline:** 45 production Storage | **Candidates:** 105 Storage | **Accepted:** 105 | **Projected Total:** 150 Storage
- **Duplicate & Alias Findings:** 0 duplicates, 0 aliases.
- **Legitimate Variants Preserved (32 records):**
  - *Capacities & Caches:* `Samsung 980 Pro 1TB` (600 TBW, 1GB DRAM) vs `Samsung 980 Pro 2TB` (1200 TBW, 2GB DRAM).
  - *Architecture:* `WD Black SN850X 1TB` (DRAM cache, 7300 MB/s) vs `WD Black SN770 1TB` (DRAM-less HMB, 5150 MB/s).

### 4.6 Power Supply Units
- **Baseline:** 37 production PSUs | **Candidates:** 83 PSUs | **Accepted:** 83 | **Projected Total:** 120 PSUs
- **Duplicate & Alias Findings:** 0 duplicates, 0 aliases.
- **Legitimate Variants Preserved (25 records):**
  - *Wattage Ratings:* `Corsair RM750e` (62.5A on +12V) vs `Corsair RM850e` (70.8A on +12V).
  - *Form Factors:* `Cooler Master V750 SFX Gold` (100mm depth SFX) vs `Corsair RM750e` (140mm depth ATX) — chassis mounting physical incompatibility.

### 4.7 PC Cases
- **Baseline:** 33 production Cases | **Candidates:** 67 Cases | **Accepted:** 67 | **Projected Total:** 100 Cases
- **Duplicate & Alias Findings:** 0 duplicates, 0 aliases.
- **Detailed Variant Audit Case Study (18 records):**
  - `case-nzxt-h5-flow-2024` vs `CAND_CASE_028` (NZXT H5 Flow 2022 Matte Black):
    - Both share the "NZXT H5 Flow" name, but represent distinct chassis generations.
    - 2024 Edition (SKU CC-H52FB-01): 410mm GPU clearance, 170mm cooler clearance, top 360mm radiator support.
    - 2022 Edition (SKU CC-H51FB-01): 365mm GPU clearance, 165mm cooler clearance, angled bottom intake fan duct.
    - Long GPUs (>365mm) fit in 2024 but collide in 2022. Both records are legitimately preserved!

### 4.8 CPU Coolers / Thermal Systems
- **Baseline:** 23 production Coolers | **Candidates:** 77 Coolers | **Accepted:** 77 | **Projected Total:** 100 Coolers
- **Duplicate & Alias Findings:** 0 duplicates, 0 aliases.
- **Legitimate Variants Preserved (22 records):**
  - *Radiator Sizes:* `Arctic Liquid Freezer III 240` (277mm) vs `Arctic Liquid Freezer III 360` (398mm).
  - *Tower Configurations:* `DeepCool AK400` (single-tower 4-heatpipe, 220W) vs `DeepCool AK620` (dual-tower 6-heatpipe, 260W).

---

## 5. Quantitative Reconciliation Matrix

Every component record across all eight categories reconciles with 100% mathematical precision:

| Category | Production Baseline | Original Candidates | Exact Dups | Aliases | Legitimate Variants Identified | Ambiguous Held | Phase 5 Pre-Filtered | Accepted Candidates | Projected Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **case** | 33 | 67 | 0 | 0 | 18 | 0 | 0 | 67 | **100** |
| **cooler** | 23 | 77 | 0 | 0 | 22 | 0 | 0 | 77 | **100** |
| **cpu** | 64 | 116 | 0 | 0 | 35 | 0 | 14 | 116 | **180** |
| **gpu** | 75 | 145 | 0 | 0 | 52 | 2 | 0 | 143 | **218** |
| **motherboard** | 95 | 85 | 0 | 0 | 40 | 0 | 24 | 85 | **180** |
| **psu** | 37 | 83 | 0 | 0 | 25 | 0 | 0 | 83 | **120** |
| **ram** | 49 | 111 | 0 | 0 | 38 | 0 | 1 | 111 | **160** |
| **storage** | 45 | 105 | 0 | 0 | 32 | 0 | 0 | 105 | **150** |
| **TOTAL** | **421** | **789** | **0** | **0** | **262** | **2** | **39** | **787** | **1,208** |

---

## 6. Resolution of Phase 6 Audit Arithmetic Discrepancy

An independent re-audit of the Phase 6 reports identified an arithmetic discrepancy between the reported global summary totals and the underlying record-level manifests.

### Root Cause Analysis
In `reports/phase6_audit/accepted_records_report.md` and `phase6_independent_audit_report.md`, the summary text stated:
- *Reported Accepted:* 1,638 records
- *Reported Held:* 89 records
- *Reported Total Evaluated:* 1,727 records

However, when summing the actual rows of the itemized evaluation tables and CSV files:
- Components Accepted: 787
- CPU Benchmarks Accepted: 125
- GPU Benchmarks Accepted: 65
- System Gaming Benchmarks Accepted: 35
- Indian Retail Prices Accepted: 512
- Compatibility Enrichment Records Accepted: 239
- **Actual Sum of Accepted Staged Records:** **1,763 records**

The difference is:
$$1,763 - 1,638 = 125$$

This discrepancy of **exactly 125 records** corresponds to the **125 CPU Cinebench R23 benchmark observations** (`BM_CPU_056` to `BM_CPU_180` in `staged_batch9_cpu_benchmarks.csv`). The author included CPU benchmarks as an itemized line item in the table, but omitted their count from the bottom summation cell ($1,638$ instead of $1,763$).

Furthermore, the total evaluated records calculation ($1,638 + 89 = 1,727$) propagated this 125-record omission. The true total staged records evaluated across all candidate datasets is:
$$1,763 \text{ (Accepted)} + 89 \text{ (Held)} = 1,852 \text{ records}$$

### Complete Staging Reconciliation Table

| Staging File | Entity / Scope | Total Records | Accepted Records | Held Records | Discrepancy Cause |
|---|---|---:|---:|---:|---|
| `staged_components.csv` | Candidate Hardware Components | 789 | 787 | 2 | 2 reference GPUs held (`CAND_GPU_142`, `143`) |
| `staged_batch9_cpu_benchmarks.csv` | CPU Cinebench R23 Multi-Core | 125 | 125 | 0 | **Omitted from Phase 6 summary sum (125)** |
| `staged_batch10_gpu_benchmarks.csv` | GPU Time Spy Graphics | 143 | 65 | 78 | 1 unconfirmed Arc B770 + 66 misaligned + 11 unconfirmed prod |
| `staged_system_benchmarks.csv` | System Gaming FPS Benchmarks | 35 | 35 | 0 | Reference ground truth; held from general ML |
| `staged_prices.csv` | Indian Retail Price Observations | 512 | 511 | 1 | `PRICE_198` quarantined due to link with `CAND_GPU_143` |
| `staged_enrichment.csv` | Compatibility Specification Backfill | 239 | 239 | 0 | 100% verified production component backfill |
| `staged_proposed_categories.csv` | Proposed Hardware Categories | 9 | 0 | 9 | Held pending formal architectural schema update |
| **TOTAL EVALUATED** | **All Candidate Datasets** | **1,852** | **1,762** | **90** | **Fully reconciled against actual CSV records** |

*(Note: In Phase 6D, price record `PRICE_198` was moved from accepted to quarantined/held, shifting accepted from 1,763 to 1,762 and held from 89 to 90).*

---

## 7. Legitimate Variant Accounting Methodology

To eliminate ambiguity regarding variant counting:

1. **262 Legitimate Variant Records:**  
   This number represents the count of **individual component records** in the catalog that belong to multi-variant hardware families (e.g., locked vs unlocked CPUs, 8GB vs 16GB GPU memory configs, AIB board partner cooling variants, DDR4 vs DDR5 motherboards, SFX vs ATX PSUs, and chassis revisions). Every one of these 262 records represents a distinct physical hardware product that was audited and preserved.
2. **29 Representative Head-to-Head Variant Pairs:**  
   Documented in [`legitimate_variants_report.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_duplicate_audit/legitimate_variants_report.csv). To avoid hundreds of combinatoric rows, the audit selected 29 representative cross-category pairs (4 cases, 4 coolers, 4 CPUs, 4 GPUs, 4 motherboards, 3 RAM kits, 3 storage drives, 3 PSUs) to demonstrate the exact technical distinctions (dimensional clearances, power limits, memory channels, DDR types) that dictate why merging them would degrade compatibility precision.
3. **39 Pre-Filtered Redundant Records:**  
   Documented in [`rejected_records.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/reports/dataset_expansion/rejected/rejected_records.csv). These were true redundant duplicates (14 CPUs, 24 motherboards, 1 RAM kit) identified and discarded during Phase 5 candidate triage. They were never admitted into the candidate staging files.

---

## 8. Deliverable Artifact Manifest

All 12 audit deliverables are located in [`reports/phase6_duplicate_audit/`](file:///e:/BuildWise-AI/BuildWise-AI1/reports/phase6_duplicate_audit):

1. `duplicate_audit_master_report.md` — Corrected master audit report.
2. `exact_duplicates_report.csv` — Verified 0 exact duplicate records across candidate and production pools.
3. `same_product_aliases_report.csv` — Verified 0 marketing alias collisions.
4. `legitimate_variants_report.csv` — Comprehensive audit register documenting 29 key legitimate variant pairs.
5. `ambiguous_records_report.csv` — Quarantine register for held candidates `CAND_GPU_142` and `CAND_GPU_143`.
6. `component_identity_mapping.csv` — Full 1-to-1 relational mapping for all 789 candidates.
7. `category_wise_duplicate_summary.csv` — Formal quantitative category reconciliation CSV.
8. `cleaned_component_candidates.csv` — Cleaned candidate dataset containing exactly 787 accepted unique component records.
9. `cleaned_price_candidates.csv` — 511 validated price observations ready for merge.
10. `quarantined_price_records.csv` — Quarantined price record `PRICE_198`.
11. `foreign_key_remapping_report.md` — Relational audit across prices, benchmarks, and compatibility enrichment.
12. `final_import_readiness_report.md` — Production integration readiness assessment and approval gate protocol.

---

## 9. Strict Protection & Isolation Compliance

- [x] `data/components.csv` strictly unmodified (421 components preserved).
- [x] `data/prices.csv` strictly unmodified (88 price observations preserved).
- [x] `data/benchmarks.csv` strictly unmodified (112 benchmark observations preserved).
- [x] Phase 5 original staged files strictly unmodified and preserved.
- [x] Application code (`app.py`, `src/`) untouched.
- [x] Compatibility engine untouched.
- [x] Automated test suite passing 100% (113 unit tests pass cleanly).
- [x] Zero Git commits or pushes executed.
- [x] All candidate hardware identities verified against genuine retail datasheets.
