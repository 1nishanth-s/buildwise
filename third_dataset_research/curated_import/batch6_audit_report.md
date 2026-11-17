# BuildWise-AI — Batch 6 INR Price Research & Verification Audit Report

**Date of Audit:** October 31, 2026  
**Auditor:** BuildWise-AI Automated Data Engineering & Verification Pipeline  
**Target Candidate Artifact:** `third_dataset_research/curated_import/batch6_inr_prices_candidates.csv`  
**Production Baseline:** `data/components.csv` (421 components) & `data/prices.csv` (70 observations across 53 unique components, 12.59% coverage)

---

## 1. Executive Summary & Objective

The objective of Batch 6 targeted price research is to discover, authenticate, and document genuine Indian retail price observations for five (5) key catalog components identified during the post-Batch 5 recommendation coverage audit. These components directly address the critical pricing bottlenecks preventing BuildWise-AI from generating realistic ₹35,000–₹60,000 budget PC builds:

1. **`DS3_RAM_003`** — Corsair Vengeance LPX 16GB (2x8GB) DDR4-3200 (Dual-channel budget DDR4 kit)
2. **`DS3_RAM_028`** — Kingston FURY Beast 16GB (2x8GB) DDR4-3200 (Dual-channel budget DDR4 kit)
3. **`DS3_STORAGE_013`** — Crucial P3 Plus 500GB NVMe SSD (Budget Gen4 NVMe storage)
4. **`DS3_STORAGE_021`** — WD Blue SN580 1TB NVMe SSD (Mainstream Gen4 NVMe storage)
5. **`case-cooler-master-q300l`** — Cooler Master MasterBox Q300L (Affordable Micro-ATX enclosure)

Strict verification standards were enforced:
- Exact part numbers and SKUs were validated against catalog records.
- Single-DIMM RAM modules were strictly disqualified from matching dual-channel kit specifications.
- Live vendor product pages were examined for explicit displayed INR prices and stock statuses.
- Zero price estimation, extrapolation, or synthetic data generation was permitted.

---

## 2. Baseline Catalog Status (Pre-Batch 6)

- **Total Production Catalog Components:** 421
- **Total Production Price Observations:** 70
- **Unique Components Currently Priced:** 53
- **Current Price Coverage:** 12.59%
- **Unpriced Components Remaining:** 368

---

## 3. Batch 6 Accepted Price Observations

Four (4) target catalog components were successfully verified with documented Indian storefront evidence and recorded into `batch6_inr_prices_candidates.csv`:

| # | Component ID | Category | Brand & Model | Price (INR) | Availability | Price Type | Seller | Verified SKU & Evidence |
|---|---|---|---|---|---|---|---|---|
| 1 | `DS3_RAM_003` | RAM | Corsair Vengeance LPX 16GB (2x8GB) DDR4-3200 | ₹7,000.0 | `available` | `seller_observation` | MD Computers | SKU `CMK16GX4M2Z3200C16`; Live in-stock 2x8GB DDR4 dual-channel kit |
| 2 | `DS3_STORAGE_013` | Storage | Crucial P3 Plus 500GB | ₹3,470.0 | `unavailable` | `seller_observation` | Vedant Computers | SKU `CT500P3PSSD8`; PCIe Gen4 M.2 2280 NVMe SSD catalog listing |
| 3 | `DS3_STORAGE_021` | Storage | Western Digital Blue SN580 1TB | ₹5,439.0 | `unavailable` | `seller_observation` | Ezpz Solutions | SKU `WDS100T3B0E`; PCIe Gen4 M.2 2280 NVMe SSD catalog listing |
| 4 | `case-cooler-master-q300l` | Case | Cooler Master MasterBox Q300L | ₹3,725.0 | `unavailable` | `seller_observation` | SCL Gaming | SKU `MCB-Q300L-KANN-S00`; Micro-ATX Mini-Tower PC cabinet catalog listing |

### Direct Retailer Evidence:
1. **`DS3_RAM_003` (Corsair Vengeance LPX 16GB 2x8GB DDR4-3200):**
   - **Seller:** MD Computers
   - **URL:** `https://mdcomputers.in/corsair-vengeance-lpx-16gb-8gbx2-ddr4-3200mhz-black-cmk16gx4m2z3200c16.html`
   - **SKU:** `CMK16GX4M2Z3200C16`
   - **Price:** ₹7,000.0 (Inclusive of GST)
   - **Availability:** In Stock (`available`)
   - **Provenance:** Observed live in-stock retail offer on authorized Indian hardware vendor storefront (MD Computers; SKU CMK16GX4M2Z3200C16; Corsair Vengeance LPX 16GB (2x8GB) DDR4-3200 CL16 Desktop Memory Kit)

2. **`DS3_STORAGE_013` (Crucial P3 Plus 500GB NVMe SSD):**
   - **Seller:** Vedant Computers
   - **URL:** `https://www.vedantcomputers.com/crucial-p3-plus-500gb-pcie-gen4-nvme-m2-ssd-ct500p3pssd8`
   - **SKU:** `CT500P3PSSD8`
   - **Price:** ₹3,470.0 (Markdown from list price ₹6,800.0)
   - **Availability:** Out of Stock (`unavailable`)
   - **Provenance:** Observed out-of-stock retail catalog listing on authorized Indian hardware vendor storefront (Vedant Computers; SKU CT500P3PSSD8; Crucial P3 Plus 500GB PCIe Gen4 NVMe M.2 SSD)

3. **`DS3_STORAGE_021` (Western Digital Blue SN580 1TB NVMe SSD):**
   - **Seller:** Ezpz Solutions
   - **URL:** `https://www.ezpzsolutions.in/western-digital-wd-blue-sn580-1tb-gen4-ssd/`
   - **SKU:** `WDS100T3B0E`
   - **Price:** ₹5,439.0 (Inclusive of GST)
   - **Availability:** Out of Stock (`unavailable`)
   - **Provenance:** Observed out-of-stock retail catalog listing on authorized Indian hardware vendor storefront (Ezpz Solutions; SKU WDS100T3B0E; Western Digital WD Blue SN580 1TB PCIe Gen4 NVMe M.2 SSD)

4. **`case-cooler-master-q300l` (Cooler Master MasterBox Q300L):**
   - **Seller:** SCL Gaming
   - **URL:** `https://sclgaming.in/product/cooler-master-masterbox-q300l-m-atx-mini-tower-cabinet-black-mcb-q300l-kann-s00/`
   - **SKU:** `MCB-Q300L-KANN-S00`
   - **Price:** ₹3,725.0
   - **Availability:** Out of Stock (`unavailable`)
   - **Provenance:** Observed out-of-stock retail catalog listing on authorized Indian hardware vendor storefront (SCL Gaming; SKU MCB-Q300L-KANN-S00; Cooler Master MasterBox Q300L Micro-ATX Mini Tower Cabinet)

---

## 4. Screening and Rejection Log

### Rejected Candidate: `DS3_RAM_028`
- **Catalog Identity:** Kingston FURY Beast 16 GB (2x8GB) DDR4 DDR4-3200 CL16 (`DS3_RAM_028`)
- **Target Manufacturer SKU:** `KF432C16BBK2/16` (Dual-channel kit, 2x8GB)
- **Stores Investigated:** MD Computers, Vedant Computers, Prime ABGB, The IT Depot, PC Studio, Computech Store, Ezpz Solutions, Clarion Computers.
- **Audit Findings:**
  1. Indian authorized distribution channels overwhelmingly list individual single-module SKUs (`KF432C16BB/16` for 1x16GB, or `KF432C16BB/8` for 1x8GB) rather than the boxed dual-channel kit `KF432C16BBK2/16`.
  2. While third-party cross-border import platforms (e.g. Ubuy, Desertcart) list the dual kit at inflated international freight pricing (₹4,300–₹5,700 + import duties), no authorized Indian retailer storefront currently maintains a live or evidenced direct catalog page for `KF432C16BBK2/16`.
  3. Single-DIMM modules cannot be substituted for dual-channel kits in the database per safety protocol ("Do not confuse single-DIMM RAM with a dual-channel kit").
- **Final Determination:** **REJECTED**. Excluded from candidate CSV to uphold zero-hallucination policy.

---

## 5. Impact Analysis on Budget PC Builds

The introduction of these four accepted price observations dramatically improves BuildWise-AI's recommendation engine capabilities in the budget tier:

1. **DDR4 Memory Floor Drop:**
   - Pre-Batch 6 DDR4 floor: **₹27,500** (`DS3_RAM_005` 32GB kit).
   - Post-Batch 6 DDR4 floor: **₹7,000** (`DS3_RAM_003` 16GB kit).
   - **Net reduction:** **-₹20,500** across all DDR4/AM4 builds!

2. **Storage Floor Drop:**
   - Pre-Batch 6 storage floor: **₹10,450** (`DS3_STORAGE_038` Kingston NV3 500GB).
   - Post-Batch 6 500GB storage floor: **₹3,470** (`DS3_STORAGE_013` Crucial P3 Plus 500GB).
   - Post-Batch 6 1TB storage floor: **₹5,439** (`DS3_STORAGE_021` WD Blue SN580 1TB).
   - **Net reduction:** **-₹6,980** on 500GB builds and **-₹10,601** on 1TB builds!

3. **Case Floor Drop:**
   - Pre-Batch 6 case floor: **₹5,500** (`DS3_CASE_002` Phanteks XT PRO).
   - Post-Batch 6 case floor: **₹3,725** (`case-cooler-master-q300l` MasterBox Q300L).
   - **Net reduction:** **-₹1,775**!

### Revised Budget Feasibility Projection:
- **Cheapest AM4 Base Build (CPU + Motherboard + RAM + Storage + Case + PSU):**
  - Ryzen 5 5500 (`DS3_CPU_007`): ₹10,700
  - Gigabyte A520M K V2 (`DS3_MB_010`): ₹5,240
  - Corsair LPX 16GB DDR4 (`DS3_RAM_003`): ₹7,000
  - Crucial P3 Plus 500GB (`DS3_STORAGE_013`): ₹3,470
  - Cooler Master Q300L (`case-cooler-master-q300l`): ₹3,725
  - Corsair CX 550W (`DS3_PSU_023`): ₹4,049
  - **Total Minimum Cost:** **₹34,184** (Down from ₹63,439!)
  - **Verdict:** Valid within the ₹35,000 Study/Office and ₹45,000 Programming budgets!

---

## 6. Recommendations for Batch 7 Research

To build upon Batch 6 and further reinforce the budget catalog, Batch 7 should target:
1. **`DS3_RAM_029`** — G.Skill Ripjaws V 16GB (2x8GB) DDR4-3200 (Popular Indian DDR4 alternative to Kingston Fury)
2. **`corsair-vengeance-ddr5-6000-cl36-16gb`** — Corsair Vengeance DDR5 16GB (Entry-level DDR5 to lower the DDR5 barrier)
3. **`DS3_MB_085`** — MSI PRO H610M-G DDR4 (Enables sub-₹30,000 Intel LGA1700 DDR4 builds with i3-12100F)
4. **`DS3_GPU_005`** — XFX Speedster SWFT 210 Radeon RX 6600 8GB (In-stock 1080p gaming alternative)
5. **`DS3_PSU_025`** — Corsair CX650M (2021) 650W Bronze (High-value mid-wattage PSU option)

