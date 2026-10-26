# BuildWise-AI: Third Dataset Integration Readiness Audit

**Audit Date:** 2026-10-26  
**Audited Target:** `third_dataset_research/` (360 staged components, 357 prices, 13 original source files, 60 quarantined legacy items)  
**Production Baseline:** `data/components.csv` (128 components), `data/prices.csv` (29 price observations)  
**Review Queue Deliverable:** [`third_dataset_research/integration_review_queue.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/integration_review_queue.csv) (104 flagged records)  
**Final Verdict:** **`needs corrections`** (Not ready for direct or automated ingestion; requires schema alignment, duplicate quarantine, and compatibility key enrichment prior to selective import).

---

## 1. Executive Summary

A comprehensive audit was performed on the staged third dataset (`third_dataset_research/`) to evaluate its technical readiness, schema conformity, licensing compliance, and hardware compatibility suitability for integration into the BuildWise-AI production catalog.

### Key Audit Findings
1. **Production Collisions (31 Components):**  
   31 components in the staged third dataset are exact duplicates of components already present in BuildWise-AI's production catalog (25 CPUs, 5 Motherboards, and 1 PC Case with brand-prefix duplication).
2. **Factual Specification Errors in Raw Scrape:**  
   Intel 14th Gen hybrid CPUs in the staged dataset contain serious specification errors. The scraper applied a naive 2x thread multiplier across all cores, incorrectly reporting **40 threads** for the Core i7-14700K (real hardware: 28 threads), **48 threads** for the Core i9-14900K (real hardware: 32 threads), and **28 threads** for the Core i5-14600K (real hardware: 20 threads). E-cores lack Hyper-Threading.
3. **Internal Dataset Redundancy (34 Rows):**  
   Within the 360 staged rows, 34 rows (17 duplicate pairs/triplets) are verbatim duplicates across category, brand, model, specifications, and source URL.
4. **Schema Incompatibilities:**  
   - `components.csv` uses `specifications_json` instead of production `specs_json`.
   - 55 rows use non-standard category names: `PC Case` (30 rows) and `CPU Cooler` (25 rows) instead of `Case` and `Cooler`.
   - `prices.csv` uses `price` and `currency` instead of production `price_inr`.
   - 349 prices in `prices.csv` are in **USD**, labeled `price_type = 'international_usd_reference'` and `availability = 'foreign_reference_only'`. Direct import into `data/prices.csv` would catastrophically corrupt the budget engine by evaluating $300 USD as ₹300 INR.
5. **Compatibility Engine Evidence Deficit (100% Failure Rate):**  
   Under BuildWise-AI's conservative compatibility rules (`src/compatibility.py`), **0 out of 10 checks evaluate as compatible** out-of-the-box. Key names mismatch (`tdp_w` vs `tdp`, `memory_type` vs `ram_type`, `wattage_w` vs `wattage`), and critical validation fields (`supported_chipsets`, `required_power_connectors`, `supports_form_factors` clearance dimensions) are absent from raw scraped JSON.

---

## 2. Dataset Overview and Staged Inventory

The staged third dataset successfully gathered 360 modern PC components across all 8 required hardware categories from open-source repositories (`docyx/pc-part-dataset` and `buildcores/buildcores-open-db`).

| Component Category | Target Expansion Goal | Staged in Third Dataset | Live Production Catalog | Distinct New Candidates (Before Scrubbing) |
| :--- | :---: | :---: | :---: | :---: |
| **Desktop CPUs** | 50 | 60 | 48 | 35 (25 exact duplicates with production) |
| **Motherboards** | 80 | 85 | 16 | 79 (6 exact duplicates with production) |
| **RAM Kits** | 32 | 40 | 12 | 37 (3 internal duplicate rows) |
| **GPUs** | 40 | 50 | 10 | 50 (0 duplicates with production) |
| **Storage (SSDs)** | 30 | 40 | 18 | 40 (0 duplicates with production) |
| **PSUs** | 25 | 30 | 8 | 27 (3 internal duplicate rows) |
| **Cases** | 25 | 30 | 9 | 22 (1 prod collision, 7 internal duplicates) |
| **Coolers** | 20 | 25 | 7 | 22 (3 internal duplicate rows) |
| **Total** | **302** | **360** | **128** | **312** |

---

## 3. Production Overlap and Conflict Analysis

Cross-referencing the 360 staged components against the 128 production components identified **31 direct collisions** and **4 distinct partial matches**.

### 3.1 Direct Collisions with Live Production Components (31 Items)

#### Desktop CPUs (25 Collisions)
All 25 of the following CPUs are already modeled with validated specs, TDP profiles, socket information, and BIOS requirements in `data/components.csv`:
- `DS3_CPU_001`: AMD Ryzen 7 9800X3D (`cpu-r7-9800x3d`)
- `DS3_CPU_002`: AMD Ryzen 7 7800X3D (`amd-ryzen-7-7800x3d`)
- `DS3_CPU_003`: AMD Ryzen 5 7600X (`amd-ryzen-5-7600x`)
- `DS3_CPU_004`: AMD Ryzen 5 9600X (`cpu-r5-9600x`)
- `DS3_CPU_005`: AMD Ryzen 7 7700X (`amd-ryzen-7-7700x`)
- `DS3_CPU_006`: AMD Ryzen 9 9950X3D (`amd-ryzen-9-9950x3d`)
- `DS3_CPU_008`: AMD Ryzen 7 9700X (`cpu-r7-9700x`)
- `DS3_CPU_012`: Intel Core i7-14700K (`cpu-intel-core-i7-14700k`) **[SPEC CONFLICT]**
- `DS3_CPU_013`: Intel Core i9-14900K (`cpu-intel-core-i9-14900k`) **[SPEC CONFLICT]**
- `DS3_CPU_015`: AMD Ryzen 5 7600 (`amd-ryzen-5-7600`)
- `DS3_CPU_017`: AMD Ryzen 9 7900X (`amd-ryzen-9-7900x`)
- `DS3_CPU_018`: AMD Ryzen 9 9900X (`cpu-r9-9900x`)
- `DS3_CPU_019`: Intel Core i5-14600K (`cpu-i5-14600k`) **[SPEC CONFLICT]**
- `DS3_CPU_020`: Intel Core Ultra 7 265K (`cpu-cu7-265k`) **[SPEC CONFLICT]**
- `DS3_CPU_023`: AMD Ryzen 9 9950X (`amd-ryzen-9-9950x`)
- `DS3_CPU_026`: Intel Core Ultra 9 285K (`cpu-intel-core-ultra-9-285k`) **[SPEC CONFLICT]**
- `DS3_CPU_041`: AMD Ryzen 9 7950X (`amd-ryzen-9-7950x`)
- `DS3_CPU_043`: AMD Ryzen 5 8600G (`amd-ryzen-5-8600g`)
- `DS3_CPU_045`: Intel Core i7-14700KF (`cpu-intel-core-i7-14700kf`) **[SPEC CONFLICT]**
- `DS3_CPU_047`: Intel Core Ultra 7 265KF (`cpu-intel-core-ultra-7-265kf`) **[SPEC CONFLICT]**
- `DS3_CPU_048`: AMD Ryzen 9 9900X3D (`amd-ryzen-9-9900x3d`)
- `DS3_CPU_049`: AMD Ryzen 9 7950X3D (`amd-ryzen-9-7950x3d`)
- `DS3_CPU_050`: AMD Ryzen 7 8700G (`amd-ryzen-7-8700g`)
- `DS3_CPU_051`: Intel Core i9-14900KF (`cpu-intel-core-i9-14900kf`) **[SPEC CONFLICT]**
- `DS3_CPU_059`: AMD Ryzen 9 7900 (`amd-ryzen-9-7900`)

#### Motherboards (5 Exact + 1 Naming Discrepancy Collision)
- `DS3_MB_007`: ASUS TUF GAMING B850-PLUS WIFI (`mb-asus-tuf-gaming-b850-plus-wifi`)
- `DS3_MB_014`: MSI MAG B650 TOMAHAWK WIFI (`mb-b650-tomahawk`, registered without "MAG" in prod)
- `DS3_MB_027`: ASUS ROG STRIX B650-A GAMING WIFI (`mb-asus-rog-strix-b650-a-gaming-wifi`)
- `DS3_MB_046`: ASUS ROG CROSSHAIR X870E HERO (`mb-x870e-hero`)
- `DS3_MB_059`: ASUS ROG STRIX B850-I GAMING WIFI (`mb-asus-rog-strix-b850-i-gaming-wifi`)
- `DS3_MB_064`: ASUS TUF GAMING X870-PLUS WIFI (`mb-asus-tuf-gaming-x870-plus-wifi`)

#### Cases (1 Brand-Prefix Duplication Collision)
- `DS3_CASE_027`: Corsair Corsair FRAME 4000D RS ARGB (`case-corsair-frame-4000d-rs-argb`)

### 3.2 Detailed Specification Conflicts

| Component | Staged DS3 Specification | Production Specification | Root Cause & Real Hardware Truth |
| :--- | :--- | :--- | :--- |
| **Intel Core i7-14700K** | Threads: **40**<br>TDP: **125W** | Threads: **28**<br>TDP: **253W** | **Factual error in scrape:** 14700K has 8 P-cores (16 threads) + 12 E-cores (12 threads) = 28 threads. Scraper doubled all 20 cores. Production uses 253W PL2 for power budgeting. |
| **Intel Core i9-14900K** | Threads: **48**<br>TDP: **125W** | Threads: **32**<br>TDP: **253W** | **Factual error in scrape:** 14900K has 8 P-cores (16 threads) + 16 E-cores (16 threads) = 32 threads. Scraper doubled all 24 cores. Production uses 253W PL2. |
| **Intel Core i5-14600K** | Threads: **28**<br>TDP: **125W** | Threads: **20**<br>TDP: **181W** | **Factual error in scrape:** 14600K has 6 P-cores (12 threads) + 8 E-cores (8 threads) = 20 threads. Scraper doubled all 14 cores. Production uses 181W PL2. |
| **Intel Core i7-14700KF** | Threads: **40**<br>TDP: **125W** | Threads: **28**<br>TDP: **253W** | Same E-core multiplier calculation error as 14700K. |
| **Intel Core i9-14900KF** | Threads: **48**<br>TDP: **125W** | Threads: **32**<br>TDP: **253W** | Same E-core multiplier calculation error as 14900K. |
| **Intel Arrow Lake CPUs**<br>(265K, 265KF, 285K) | TDP: **125W** | TDP: **250W** | Staged dataset only recorded Processor Base Power (125W); production records Maximum Turbo Power (250W) to prevent PSU under-sizing. |

### 3.3 Partial Matches (Legitimate Distinct SKUs)
The audit identified 4 components that share naming substrings with production components but represent legitimate distinct hardware SKUs:
1. `DS3_CPU_007`: **AMD Ryzen 5 7600X3D** (Prod: `amd-ryzen-5-7600x`) — Legitimate distinct SKU with 3D V-Cache (96MB L3) vs standard 32MB L3.
2. `DS3_CPU_014`: **AMD Ryzen 7 7700** (Prod: `amd-ryzen-7-7700x`) — Legitimate distinct 65W non-X SKU with bundled cooler.
3. `DS3_CPU_021`: **Intel Core i5-14600KF** (Prod: `cpu-i5-14600k`) — Legitimate distinct SKU without integrated graphics.
4. `DS3_CPU_025`: **Intel Core i9-14900KS** (Prod: `cpu-intel-core-i9-14900k`) — Legitimate distinct SKU (6.2 GHz special edition, 150W base).

### 3.4 Internal Redundant Duplicate Rows (34 Rows)
Within `third_dataset_research/components.csv`, 34 rows (17 duplicate sets) are exact duplicates of one another:
- **CPUs (2 rows):** `DS3_CPU_024` and `DS3_CPU_032` (AMD Ryzen 5 7500F)
- **RAM (6 rows):** `DS3_RAM_001` & `DS3_RAM_011`; `DS3_RAM_006` & `DS3_RAM_024`; `DS3_RAM_022` & `DS3_RAM_036`
- **PSUs (6 rows):** `DS3_PSU_002` & `DS3_PSU_015`; `DS3_PSU_005` & `DS3_PSU_024`; `DS3_PSU_018` & `DS3_PSU_030`
- **Cases (14 rows):** `DS3_CASE_001` & `020`; `003` & `016`; `004` & `009`; `007` & `019`; `008` & `015`; `012` & `017`; `022` & `024`
- **Coolers (6 rows):** `DS3_COOLER_007` & `017`; `008` & `015`; `011` & `018`

---

## 4. Schema and Field Validation

Running `src/validator.py` validation routines against the third dataset files revealed multiple schema non-conformities:

### 4.1 `components.csv` Schema Audit
- **Column Header Mismatch:** Staged dataset uses `specifications_json` instead of required column `specs_json`.
- **Category Enum Violations (55 rows):**
  - Production `VALID_CATEGORIES` expects `Case` and `Cooler`.
  - Staged dataset has 30 rows of `PC Case` and 25 rows of `CPU Cooler`.
- **Validator Internal Duplicate Alert:** `validate_components()` detects 34 matching rows across identity fields.
- **Identity Status:** All 360 rows have `identity_status = 'verified'`. However, given the factual thread errors and compatibility key deficits, these should be downgraded to `needs_review`.

### 4.2 `prices.csv` Schema and Currency Audit
- **Column Header Mismatch:** Staged dataset uses `price` and `currency` instead of required `price_inr`.
- **Invalid Enumerations:**
  - `price_type`: Staged dataset uses `international_usd_reference` (349 rows) and `indian_retail_observation` (8 rows). Production schema requires `seller_observation` or `planning_estimate`.
  - `availability`: Staged dataset uses `foreign_reference_only` (349 rows) and `available` (8 rows). Production schema requires `available`, `unavailable`, or `unknown`.
- **Currency Isolation & Safety:**  
  The 349 USD prices were properly separated by currency tag in research staging, but are completely unusable in production's INR-based recommendation calculations. If loaded as `price_inr`, a $399 GPU would be priced at ₹399, breaking all budget algorithms.

---

## 5. Licensing and Provenance Audit

- **Primary Source:** `docyx/pc-part-dataset` (GitHub)
  - **License:** MIT License (`third_dataset_research/original_downloads/docyx_pc_part_dataset/LICENSE.txt`)
  - **Attribution Requirement:** Doc Oliver (2021-2025)
  - **Redistribution Permitted:** Yes, full commercial and non-commercial reuse allowed with MIT notice.
- **Secondary Reference:** `buildcores/buildcores-open-db` (GitHub)
  - **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
  - **Integration Status:** Quarantined in `original_downloads/`. Not merged into staged components to maintain commercial flexibility and avoid ShareAlike constraints.
- **Source URLs:** All 360 component rows and 357 price rows contain valid, well-formed HTTP/HTTPS URLs.

---

## 6. Compatibility Engine Evidence Gap Analysis

BuildWise-AI's recommendation engine relies on conservative, deterministic compatibility checks implemented in `src/compatibility.py`. An automated check of staged JSON objects against all 11 compatibility rules revealed that **none of the checks succeed**:

```
Compatibility Check Evaluation on Staged Dataset:
1. check_cpu_motherboard:            UNKNOWN (missing 'supported_chipsets' on CPU)
2. check_cpu_motherboard_ram:        UNKNOWN (missing 'ram_type' on CPU/Motherboard/RAM)
3. check_motherboard_ram_capacity:   UNKNOWN (missing 'ram_max_gb' on Motherboard)
4. check_motherboard_case:           UNKNOWN (missing 'supports_form_factors' list on Case)
5. check_storage_motherboard:        UNKNOWN (unrecognized storage interface & missing M.2 sizes on MB)
6. check_gpu_case:                   UNKNOWN (missing 'max_gpu_length_mm' on Case)
7. check_psu:                        UNKNOWN (PSU uses 'wattage_w' instead of 'wattage'; missing connector inventory)
8. check_cooler_socket:              UNKNOWN (missing 'socket_support' list on Cooler)
9. check_cooler_case:                UNKNOWN (missing 'height_mm' on Cooler & 'max_cpu_cooler_mm' on Case)
10. check_cooler:                    UNKNOWN (missing 'tdp_rating' on Cooler)
```

### Required JSON Key Normalization Table

| Component Category | Staged Third Dataset Key | Required `src/compatibility.py` Key / Format | Missing Required Fields |
| :--- | :--- | :--- | :--- |
| **CPU** | `tdp_w` | `tdp` (numeric watts) | `supported_chipsets` (list), `ram_type` (e.g. "DDR5") |
| **Motherboard** | `memory_type`, `max_memory_gb` | `ram_type`, `ram_max_gb` | `supported_storage_interfaces`, `supported_m2_form_factors` |
| **RAM** | `memory_type` | `ram_type` | Standard JEDEC profile documentation |
| **GPU** | `length_mm` | `length_mm` | `tdp` (numeric watts), `required_power_connectors` (dict, e.g. `{"pcie_8pin": 2}`) |
| **Storage** | `interface: "M.2 PCIe 4.0 X4"` | `interface: "nvme"` or `"sata"` | Strict normalization required by regex |
| **PSU** | `wattage_w` | `wattage` (numeric watts) | `power_connectors` (dict inventory: `{"pcie_8pin": 4, "eps_8pin": 2, ...}`) |
| **Case** | `form_factor: "ATX Mid Tower"` | `supports_form_factors: ["atx", "matx", "itx"]` | `max_gpu_length_mm` (numeric), `max_cpu_cooler_mm` (numeric) |
| **Cooler** | `cooler_type` | `height_mm` (numeric) | `socket_support` (list of sockets), `tdp_rating` (numeric) |

---

## 7. Integration Review Queue Breakdown

The review queue [`third_dataset_research/integration_review_queue.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/integration_review_queue.csv) contains **104 flagged items**:

| Issue Classification | Item Count | Action Required |
| :--- | :---: | :--- |
| `schema_category_alias_mismatch` | 34 | Remap category strings (`PC Case` -> `Case`, `CPU Cooler` -> `Cooler`). |
| `exact_production_collision` | 26 | Quarantine; reject duplicate records to preserve live production data. |
| `internal_dataset_duplicate_primary` | 17 | Retain single primary record; flag for review. |
| `internal_dataset_duplicate_redundant` | 17 | Purge redundant duplicates during curation. |
| `spec_conflict_and_prod_collision` | 5 | Correct Intel E-core thread multiplier errors and TDP values before any reuse. |
| `partial_production_match_distinct_sku` | 4 | Retain as legitimate distinct candidate SKUs (7600X3D, 7700, 14600KF, 14900KS). |
| `naming_discrepancy_collision` | 1 | MSI MAG B650 Tomahawk WiFi; reject collision with `mb-b650-tomahawk`. |
| **Total Flagged Queue Rows** | **104** | |

---

## 8. Production System Health Verification

Prior to concluding the audit, the production environment was validated to ensure that all checks, recommendation pipelines, and unit tests remain operational:
1. `validate_data.py`: **Passed** (128 components, 29 price observations; 0 errors).
2. Unit Test Suite (`unittest discover -s tests -v`): **Passed** (85 tests ran in 51.039s; 0 failures, 0 errors).

---

## 9. Recommended Next Steps and Selective Ingestion Plan

To safely utilize the high-value candidates from `third_dataset_research/` without corrupting the production database, follow this staged roadmap:

1. **Step 1: Duplicate Quarantine & Discard**
   - Automatically drop the 31 production collisions from the import queue.
   - Drop the 17 redundant internal duplicate rows.
2. **Step 2: Schema Header and Category Normalization**
   - Rename `specifications_json` -> `specs_json`.
   - Remap `PC Case` -> `Case` and `CPU Cooler` -> `Cooler`.
   - Strip brand name repetitions from `model` fields (e.g., `Corsair Corsair 3500X` -> `3500X ARGB`).
3. **Step 3: Specification Correction**
   - Correct the Intel hybrid CPU thread counts: 14700K (28 threads), 14900K (32 threads), 14600K (20 threads).
   - Align CPU TDP values with PL2 / Maximum Turbo Power for PSU sizing.
4. **Step 4: Compatibility Engine Key Enrichment**
   - Enrich JSON keys: map `tdp_w` to `tdp`, `memory_type` to `ram_type`, `wattage_w` to `wattage`.
   - Add structured connector dictionaries for PSUs and GPUs (`power_connectors`, `required_power_connectors`).
   - Add supported form factors and clearance limits for Cases and Coolers.
5. **Step 5: Indian Price Ingestion vs USD Archive**
   - Isolate the 8 verified Indian retail observations (MD Computers, Prime ABGB, Vedant Computers) and format them into `data/prices.csv` with `price_type = 'seller_observation'`.
   - Archive the 349 USD scraped prices into a separate external reference file (`third_dataset_research/usd_reference_prices.csv`) for market research only. Never import USD prices into `data/prices.csv`.

---
*Report generated and validated autonomously for BuildWise-AI.*

