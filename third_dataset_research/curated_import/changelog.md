# BuildWise-AI: Third Dataset Curation Changelog

**Date:** 2026-10-26  
**Target Output Directory:** [`third_dataset_research/curated_import/`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/curated_import/)  
**Input Datasets:** `third_dataset_research/components.csv` (360 rows), `third_dataset_research/prices.csv` (357 rows)  
**Baseline Live Data:** `data/components.csv` (128 rows), `data/prices.csv` (29 rows)  

---

## 1. Scope and Objective
This changelog documents all transformations, deduplications, specification rectifications, model name disambiguations, and schema normalizations performed during the curation of the third dataset. All operations were executed without modifying live production files (`data/*`, `src/*`, `app.py`) or altering original downloads.

---

## 2. Deduplication and Collision Resolution (67 Rows Removed)

### 2.1 Production Catalog Duplicate Collisions (50 Rows Quarantined)
To prevent duplicate catalog entries and maintain production database integrity, 50 components that match existing live records were quarantined and excluded from import:
- **Desktop CPUs (25 Collisions):**
  - AMD Ryzen 7 9800X3D (`DS3_CPU_001` vs `cpu-r7-9800x3d`)
  - AMD Ryzen 7 7800X3D (`DS3_CPU_002` vs `amd-ryzen-7-7800x3d`)
  - AMD Ryzen 5 7600X (`DS3_CPU_003` vs `amd-ryzen-5-7600x`)
  - AMD Ryzen 5 9600X (`DS3_CPU_004` vs `cpu-r5-9600x`)
  - AMD Ryzen 7 7700X (`DS3_CPU_005` vs `amd-ryzen-7-7700x`)
  - AMD Ryzen 9 9950X3D (`DS3_CPU_006` vs `amd-ryzen-9-9950x3d`)
  - AMD Ryzen 7 9700X (`DS3_CPU_008` vs `cpu-r7-9700x`)
  - Intel Core i7-14700K (`DS3_CPU_012` vs `cpu-intel-core-i7-14700k`)
  - Intel Core i9-14900K (`DS3_CPU_013` vs `cpu-intel-core-i9-14900k`)
  - AMD Ryzen 5 7600 (`DS3_CPU_015` vs `amd-ryzen-5-7600`)
  - AMD Ryzen 9 7900X (`DS3_CPU_017` vs `amd-ryzen-9-7900x`)
  - AMD Ryzen 9 9900X (`DS3_CPU_018` vs `cpu-r9-9900x`)
  - Intel Core i5-14600K (`DS3_CPU_019` vs `cpu-i5-14600k`)
  - Intel Core Ultra 7 265K (`DS3_CPU_020` vs `cpu-cu7-265k`)
  - AMD Ryzen 9 9950X (`DS3_CPU_023` vs `amd-ryzen-9-9950x`)
  - Intel Core Ultra 9 285K (`DS3_CPU_026` vs `cpu-intel-core-ultra-9-285k`)
  - AMD Ryzen 9 7950X (`DS3_CPU_041` vs `amd-ryzen-9-7950x`)
  - AMD Ryzen 5 8600G (`DS3_CPU_043` vs `amd-ryzen-5-8600g`)
  - Intel Core i7-14700KF (`DS3_CPU_045` vs `cpu-intel-core-i7-14700kf`)
  - Intel Core Ultra 7 265KF (`DS3_CPU_047` vs `cpu-intel-core-ultra-7-265kf`)
  - AMD Ryzen 9 9900X3D (`DS3_CPU_048` vs `amd-ryzen-9-9900x3d`)
  - AMD Ryzen 9 7950X3D (`DS3_CPU_049` vs `amd-ryzen-9-7950x3d`)
  - AMD Ryzen 7 8700G (`DS3_CPU_050` vs `amd-ryzen-7-8700g`)
  - Intel Core i9-14900KF (`DS3_CPU_051` vs `cpu-intel-core-i9-14900kf`)
  - AMD Ryzen 9 7900 (`DS3_CPU_059` vs `amd-ryzen-9-7900`)
- **Motherboards (6 Collisions):**
  - MSI MAG B650 TOMAHAWK WIFI (`DS3_MB_003` vs `mb-b650-tomahawk`)
  - ASUS TUF GAMING B850-PLUS WIFI (`DS3_MB_007` vs `mb-asus-tuf-gaming-b850-plus-wifi`)
  - ASUS ROG STRIX B650-A GAMING WIFI (`DS3_MB_027` vs `mb-asus-rog-strix-b650-a-gaming-wifi`)
  - ASUS ROG CROSSHAIR X870E HERO (`DS3_MB_046` vs `mb-x870e-hero`)
  - ASUS ROG STRIX B850-I GAMING WIFI (`DS3_MB_059` vs `mb-asus-rog-strix-b850-i-gaming-wifi`)
  - ASUS TUF GAMING X870-PLUS WIFI (`DS3_MB_064` vs `mb-asus-tuf-gaming-x870-plus-wifi`)
- **RAM (1 Collision):**
  - G.Skill Flare X5 32GB DDR5-6000 CL36 (`DS3_RAM_002` vs `gskill-flare-x5-ddr5-6000-cl36-32gb`, identical MPN `F5-6000J3636F16GX2-FX5`)
- **Storage (10 Collisions across Model + Capacity):**
  - Samsung 990 Pro 4TB (`DS3_STORAGE_004` vs `samsung-990-pro-4tb`)
  - Samsung 990 Pro 1TB (`DS3_STORAGE_006` vs `samsung-990-pro-1tb`)
  - WD_Black SN850X 2TB (`DS3_STORAGE_008` vs `ssd-sn850x-2tb`)
  - Samsung 9100 PRO 4TB (`DS3_STORAGE_009` vs `samsung-9100-pro-4tb`)
  - WD_Black SN850X 8TB (`DS3_STORAGE_015` vs `wd-black-sn850x-8tb`)
  - WD_Black SN850X 4TB (`DS3_STORAGE_016` vs `ssd-sn850x-4tb`)
  - Samsung 9100 PRO 2TB (`DS3_STORAGE_017` vs `samsung-9100-pro-2tb`)
  - Samsung 990 EVO Plus 4TB (`DS3_STORAGE_022` vs `samsung-990-evo-plus-4tb`)
  - Samsung 9100 PRO 1TB (`DS3_STORAGE_034` vs `samsung-9100-pro-1tb`)
  - Crucial T705 2TB (`DS3_STORAGE_035` vs `ssd-t705-2tb`)
- **Power Supplies (2 Collisions):**
  - Corsair RM850x (2024) (`DS3_PSU_008` vs `psu-850w-gold`)
  - Corsair RM750x (2024) (`DS3_PSU_026` vs `psu-750w-gold`)
- **Cases (5 Collisions):**
  - Montech XR (`DS3_CASE_001` vs `case-montech-xr-black`)
  - NZXT H5 Flow (2024) (`DS3_CASE_003` vs `case-nzxt-h5-flow-2024`)
  - Lian Li A3-mATX (`DS3_CASE_012` vs `case-lian-li-a3-matx-black`)
  - Corsair FRAME 4000D RS ARGB (`DS3_CASE_025` vs `case-corsair-frame-4000d-rs-argb`)
  - Fractal Design Terra (`DS3_CASE_027` vs `case-fractal-design-terra-jade`)
- **CPU Coolers (1 Collision):**
  - Cooler Master Hyper 212 Black Edition (`DS3_COOLER_003` vs `cooler-cm-hyper-212-black`)

### 2.2 Redundant Internal Duplicates Purged (17 Rows Purged)
17 rows that were identical internal copies of other rows in the third dataset were purged, preserving a single unique primary instance:
- `DS3_CPU_032` (Redundant copy of `DS3_CPU_024` Ryzen 5 7500F)
- `DS3_RAM_011` (Redundant copy of `DS3_RAM_001` Corsair Vengeance RGB 32GB)
- `DS3_RAM_024` (Redundant copy of `DS3_RAM_006` Crucial Pro Overclocking 32GB)
- `DS3_RAM_036` (Redundant copy of `DS3_RAM_022` Corsair Dominator Titanium 64GB)
- `DS3_PSU_015` (Redundant copy of `DS3_PSU_002` MSI MAG A850GL)
- `DS3_PSU_024` (Redundant copy of `DS3_PSU_005` Corsair RM750e 2025)
- `DS3_PSU_030` (Redundant copy of `DS3_PSU_018` Corsair RM1000e 2025)
- `DS3_CASE_009` (Redundant copy of `DS3_CASE_004` Corsair 3500X ARGB)
- `DS3_CASE_015` (Redundant copy of `DS3_CASE_008` Lian Li O11 Vision Compact)
- `DS3_CASE_016` (Redundant copy of `DS3_CASE_003` NZXT H5 Flow 2024)
- `DS3_CASE_017` (Redundant copy of `DS3_CASE_012` Lian Li A3-mATX)
- `DS3_CASE_019` (Redundant copy of `DS3_CASE_007` NZXT H9 Flow 2023)
- `DS3_CASE_020` (Redundant copy of `DS3_CASE_001` Montech XR)
- `DS3_CASE_024` (Redundant copy of `DS3_CASE_022` NZXT H6 Flow)
- `DS3_COOLER_015` (Redundant copy of `DS3_COOLER_008` Arctic Liquid Freezer III 360)
- `DS3_COOLER_017` (Redundant copy of `DS3_COOLER_007` Corsair Nautilus 360 RS)
- `DS3_COOLER_018` (Redundant copy of `DS3_COOLER_011` Arctic Liquid Freezer III Pro 360)

---

## 3. Retained Distinct Physical SKUs

Four components sharing model substrings with live production entries were independently verified and retained as distinct physical hardware SKUs:
1. **AMD Ryzen 5 7600X3D (`DS3_CPU_028`):**  
   Distinct from `amd-ryzen-5-7600x`. Features 96MB L3 cache (32MB standard + 64MB 3D V-Cache), 65W TDP, 4.1 GHz base, 4.7 GHz boost.
2. **AMD Ryzen 7 7700 (`DS3_CPU_030`):**  
   Distinct from `amd-ryzen-7-7700x`. Operates at 65W TDP with bundled AMD Wraith Prism cooler, 3.8 GHz base, 5.3 GHz boost.
3. **Intel Core i5-14600KF (`DS3_CPU_042`):**  
   Distinct from `cpu-i5-14600k`. Omits integrated graphics (UHD 770); requires discrete graphics.
4. **Intel Core i9-14900KS (`DS3_CPU_054`):**  
   Distinct from `cpu-intel-core-i9-14900k`. Factory-binned special edition operating at 6.2 GHz TVB, 150W base power, up to 320W Extreme profile.

---

## 4. Specification Rectifications from Manufacturer Documentation

### 4.1 Intel Hybrid Architecture Thread & Power Rectifications
The upstream scraper doubled all core counts to calculate threads (`threads = cores * 2`), ignoring that Intel Gracemont / Crestmont / Skymont Efficient cores lack Hyper-Threading. Official Intel ARK specifications were applied:

| Component ID | Model | Raw Scraped Threads | Rectified Real Threads | Real Core Composition | Base Power (W) | Maximum Turbo Power / PL2 (W) |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| `DS3_CPU_022` | Core i5-14400F | 20 | **16** | 6P + 4E | 65 | 148 |
| `DS3_CPU_027` | Core i7-12700K | 24 | **20** | 8P + 4E | 125 | 190 |
| `DS3_CPU_031` | Core i5-13400F | 20 | **16** | 6P + 4E | 65 | 148 |
| `DS3_CPU_033` | Core i7-12700KF | 24 | **20** | 8P + 4E | 125 | 190 |
| `DS3_CPU_035` | Core i5-12600KF | 20 | **16** | 6P + 4E | 125 | 150 |
| `DS3_CPU_037` | Core i5-12600K | 20 | **16** | 6P + 4E | 125 | 150 |
| `DS3_CPU_042` | Core i5-14600KF | 28 | **20** | 6P + 8E | 125 | 181 |
| `DS3_CPU_046` | Core i9-12900K | 32 | **24** | 8P + 8E | 125 | 241 |
| `DS3_CPU_052` | Core i7-13700K | 32 | **24** | 8P + 8E | 125 | 253 |
| `DS3_CPU_054` | Core i9-14900KS | 48 | **32** | 8P + 16E | 150 | 253 |
| `DS3_CPU_056` | Core i5-13600KF | 28 | **20** | 6P + 8E | 125 | 181 |
| `DS3_CPU_058` | Core i7-14700F | 40 | **28** | 8P + 12E | 65 | 219 |
| `DS3_CPU_060` | Core i9-13900K | 48 | **32** | 8P + 16E | 125 | 253 |
| `DS3_CPU_014` | Core i5-12400F | 12 | **12** (Non-hybrid) | 6P + 0E | 65 | 117 |
| `DS3_CPU_040` | Core i3-12100F | 8 | **8** (Non-hybrid) | 4P + 0E | 58 | 89 |

*Clarification:* Out of the 15 listed Intel processors, **13 are hybrid architectures** with P+E cores whose thread counts were reduced. The 2 non-hybrid processors (12400F and 12100F) already had correct thread counts in the raw scrape; only their PL2 ratings were documented.

### 4.2 AMD Ryzen 5000 Socket Corrections
The upstream dataset erroneously classified 7 AMD Ryzen 5000 desktop processors as `Socket: AM5`. According to AMD official product documentation, all Ryzen 5000 series desktop processors belong to Socket AM4 (Zen 3) and DDR4 memory:
- `DS3_CPU_011`: AMD Ryzen 7 5800X $\to$ `socket: AM4`, `ram_type: DDR4`
- `DS3_CPU_025`: AMD Ryzen 7 5800XT $\to$ `socket: AM4`, `ram_type: DDR4`
- `DS3_CPU_034`: AMD Ryzen 9 5900X $\to$ `socket: AM4`, `ram_type: DDR4`
- `DS3_CPU_038`: AMD Ryzen 7 5700G $\to$ `socket: AM4`, `ram_type: DDR4`
- `DS3_CPU_039`: AMD Ryzen 7 5800X3D $\to$ `socket: AM4`, `ram_type: DDR4`
- `DS3_CPU_044`: AMD Ryzen 7 5700 $\to$ `socket: AM4`, `ram_type: DDR4`
- `DS3_CPU_057`: AMD Ryzen 9 5900XT $\to$ `socket: AM4`, `ram_type: DDR4`

---

## 5. Schema Alignment and Compatibility Field Mapping

1. **Column Normalization:**  
   Renamed `specifications_json` $\to$ `specs_json` across all curated component rows.
2. **Category Enum Normalization:**  
   Remapped `PC Case` $\to$ `Case` (18 rows) and `CPU Cooler` $\to$ `Cooler` (21 rows).
3. **Hardware Engine Key Mapping:**
   - **CPUs:** Injected `supported_chipsets` lists for AM5, AM4, and LGA1700 platforms; mapped `ram_type` to DDR5 or DDR4.
   - **Motherboards:** Normalized `form_factor` (`ATX`, `mATX`, `ITX`), mapped `memory_type` $\to$ `ram_type`, `max_memory_gb` $\to$ `ram_max_gb`, `memory_slots` $\to$ `ram_slots`, and populated `supported_storage_interfaces` (`['nvme', 'sata']`) and `supported_m2_form_factors` (`['M.2 2280', '2280']`).
   - **RAM:** Mapped `memory_type` $\to$ `ram_type`, `modules` $\to$ `kit`, `speed_mhz` $\to$ `speed_mtps`.
   - **GPUs:** Mapped `recommended_psu_w` $\to$ `recommended_system_psu_w`.
   - **Storage:** Normalized `interface` string to strictly match `src/compatibility.py` regex parser (`NVMe Gen4 x4`, `NVMe`, `SATA`).
   - **PSUs:** Mapped `efficiency_rating` $\to$ `efficiency`.
   - **Cases:** Mapped `supports_form_factors` list matching the primary form factor (`['ATX', 'mATX', 'ITX']`).

---

## 6. Price File Partitioning & Currency Isolation

1. **`curated_import/indian_prices.csv` (8 rows):**
   - Formatted to match production `PRICE_COLUMNS` (`price_id`, `component_id`, `seller`, `price_inr`, `source_url`, `checked_at`, `availability`, `price_type`, `provenance`).
   - Set `price_type = 'seller_observation'` and `availability = 'available'`.
2. **`curated_import/usd_reference_prices.csv` (349 rows):**
   - Isolated in a separate file with currency `USD` for external market analysis.
   - Quarantined from `data/prices.csv` to ensure 0 risk of INR currency corruption.

---

## 7. Model Name Disambiguation (69 Rows Rectified)

In response to the final audit findings, 69 non-unique model strings in `components.csv` were disambiguated using verified attributes already present in `specs_json` without guessing:
- **GPUs (33 rows):** Prepended GPU chipset name and appended VRAM capacity (e.g. `Gigabyte GAMING OC` $\to$ `Gigabyte GeForce RTX 4060 GAMING OC 8GB`, `Gigabyte Radeon RX 7800 XT GAMING OC 16GB`).
- **Storage (19 rows):** Appended capacity descriptor (e.g. `Crucial P3 Plus` $\to$ `Crucial P3 Plus 1TB`, `Crucial P3 Plus 2TB`, `Crucial P3 Plus 4TB`; `Kingston NV3` $\to$ `Kingston NV3 1TB`, `NV3 2TB`).
- **RAM (13 rows):** Appended kit configuration, DDR type, speed, and CAS latency (e.g. `Corsair Vengeance RGB 32 GB` $\to$ `Corsair Vengeance RGB 32 GB (2x16GB) DDR5-6000 CL36`, `Corsair Vengeance RGB 32 GB (2x16GB) DDR5-6000 CL30`).
- **PSUs (2 rows):** Appended wattage and efficiency (e.g. `Corsair CX (2023)` $\to$ `Corsair CX (2023) 650W 80 Plus Bronze`, `Corsair CX (2023) 550W 80 Plus Bronze`).
- **Coolers (2 rows):** Appended radiator size (e.g. `Thermalright Aqua Elite V3` $\to$ `Thermalright Aqua Elite V3 360mm`, `Thermalright Aqua Elite V3 240mm`).

**Result:** Duplicate normalized identities across `(category, brand, model)` in `components.csv` dropped from **69 to 0**. All 293 rows now possess unique, human-readable display identities.

---

## 8. Price Foreign Key Remapping & Duplication Check

In `curated_import/indian_prices.csv`, the 3 price records referencing CPU collision IDs were remapped to active production catalog IDs after verifying exact hardware identity:
- `PRC_INR_DS3_CPU_001`: `DS3_CPU_001` $\to$ `cpu-r7-9800x3d` (MD Computers, ₹49,500.0)
- `PRC_INR_DS3_CPU_002`: `DS3_CPU_002` $\to$ `amd-ryzen-7-7800x3d` (Vedant Computers, ₹36,900.0)
- `PRC_INR_DS3_CPU_003`: `DS3_CPU_003` $\to$ `amd-ryzen-5-7600x` (Prime ABGB, ₹19,499.0)

**Duplication Check:**  
Cross-referencing `data/prices.csv` confirmed that neither `amd-ryzen-7-7800x3d` nor `amd-ryzen-5-7600x` had existing prices. For `cpu-r7-9800x3d`, `data/prices.csv` only had an older Flipkart listing (₹75,000, 2026-10-17). The MD Computers observation (₹49,500, 2026-10-26) represents a distinct, fresh seller observation. Zero duplicate observations exist.

---

## 9. Remaining Unresolved Issues & Observations

1. **Standalone Category Deficits:**  
   Because duplicate rows were strictly removed, the curated import candidate set standalone contains 34 CPUs (deficit: -16 vs 50 target), 79 Motherboards (deficit: -1 vs 80 target), and 18 Cases (deficit: -7 vs 25 target). If combined with the live catalog, all targets are exceeded (64 CPUs, 95 Motherboards, 33 Cases).
2. **Scraped Data Redistribution Uncertainty:**  
   Although `docyx/pc-part-dataset` is distributed under an MIT license, its data was harvested from PCPartPicker.com. An MIT code repository license cannot legally override the terms of service of the scraped source website. Hardware data should be verified against first-party manufacturer specifications prior to commercial redistribution.
3. **CSV Source URLs:**  
   In `components.csv`, the `source_url` field preserves the upstream GitHub repository URL rather than direct Intel ARK / manufacturer product URLs.
