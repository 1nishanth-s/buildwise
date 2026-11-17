# BuildWise-AI — Batch 8: Currently Available Budget Component Prices Audit Report

**Date of Audit:** November 2, 2026  
**Auditor:** BuildWise-AI Data Engineering & Verification Pipeline  
**Target Candidate Artifact:** `third_dataset_research/curated_import/batch8_inr_prices_candidates.csv`  
**Production Baseline:** `data/components.csv` (421 components) & `data/prices.csv` (78 observations across 60 unique components, 14.25% coverage; 93 passing tests)

---

## 1. Executive Summary & Objective

Following the Batch 7 import and the introduction of graphics output checking and purchasability classification, BuildWise-AI identified key bottlenecks in generating affordable PC configurations in the ₹35,000–₹60,000 price range:

1. **Case Availability Bottleneck**:
   Prior to Batch 8, every budget PC case in the database was recorded as `unavailable` (e.g., Cooler Master MasterBox Q300L at ₹3,725, Phanteks XT PRO at ₹5,500, Corsair 4000D at ₹6,680) or possessed only a stale observation (`case-nzxt-h5-flow-2024`). No active, purchasable Micro-ATX chassis was in stock.
2. **DDR4 RAM Dual-Channel Pricing**:
   The catalog previously contained only one active DDR4 RAM kit: `DS3_RAM_005` (Corsair Vengeance LPX 32GB DDR4-3600) priced at ₹27,500.00. While Batch 7 recorded `DS3_RAM_003` (Corsair LPX 16GB 2x8GB) at ₹7,000.00 (`unavailable`), unpriced catalog items such as `DS3_RAM_029` (G.Skill Ripjaws V 16GB DDR4-3200) lacked authentic Indian retail documentation.
3. **Power Supply Purchasability**:
   While `DS3_PSU_007` (MSI MAG A550BN) is available at ₹4,150.00, `DS3_PSU_014` (Corsair CX650 650W Bronze) was previously marked `unavailable` at ₹5,150.00, and `DS3_PSU_023` (Corsair CX550) lacked multi-vendor verification.
4. **Storage Multi-Vendor Verification**:
   500GB NVMe SSD options required verification across major authorized retailers to confirm local market pricing and in-stock status.

The objective of **Batch 8** is to research genuine, live retail offers across authorized Indian vendors (MD Computers, Vedant Computers, Computech Store, Prime ABGB) and formulate up to five (5) candidate observations prioritizing:
- Exact 16GB (2x8GB) DDR4 dual-channel memory kits
- 500GB NVMe SSDs
- Affordable Micro-ATX computer cases
- 450W–650W power supply units

All records were validated directly via HTTP GET requests against live storefront schema data. Zero production datasets or code files were modified.

---

## 2. Batch 8 Accepted Price Observations

Five (5) candidate price observations were authenticated and recorded into `third_dataset_research/curated_import/batch8_inr_prices_candidates.csv`:

| # | Price ID | Component ID | Brand & Model | Price (INR) | Availability | Price Type | Seller | Verified SKU / MPN |
|---|---|---|---|---|---|---|---|---|
| 1 | `price-case-lian-li-a3-matx-black-mdcomputers-20261102-191920` | `case-lian-li-a3-matx-black` | Lian Li A3-mATX (Black, A3X.US) | ₹7,300.0 | `available` | `seller_observation` | MD Computers | `G99-A3X-IN` / `LIAN-LI-A3-MATX-BLACK` |
| 2 | `price-psu-corsair-cx650-mdcomputers-20261102-192150` | `DS3_PSU_014` | Corsair CX (2023) 650W 80 Plus Bronze | ₹5,250.0 | `available` | `seller_observation` | MD Computers | `CP-9020278-IN` / `CORSAIR-CX650-80-PLUS-BRONZE` |
| 3 | `price-ram-gskill-ripjaws-v-16gb-ddr4-3200-mdcomputers-20261102-192740` | `DS3_RAM_029` | G.Skill Ripjaws V 16 GB (2x8GB) DDR4-3200 | ₹5,827.0 | `unavailable` | `seller_observation` | MD Computers | `F4-3200C16D-16GVKB` |
| 4 | `price-storage-kingston-nv3-500gb-mdcomputers-20261102-192250` | `DS3_STORAGE_038` | Kingston NV3 500GB PCIe 4.0 NVMe SSD | ₹10,450.0 | `available` | `seller_observation` | MD Computers | `SNV3S-500G` / `KINGSTON-NV3-500GB` |
| 5 | `price-psu-corsair-cx550-vedant-20261102-192540` | `DS3_PSU_023` | Corsair CX (2023) 550W 80 Plus Bronze | ₹3,900.0 | `unavailable` | `seller_observation` | Vedant Computers | `CP-9020277-IN` |

---

## 3. Detailed Retailer Evidence & Identity Verification

### Candidate 1: `case-lian-li-a3-matx-black` — Lian Li A3-mATX (Black)
- **Component ID:** `case-lian-li-a3-matx-black`
- **Catalog Identity:** Lian Li A3-mATX (Black, A3X.US), Micro-ATX chassis, supports mATX/ITX, max GPU length 415mm, max cooler height 165mm.
- **Seller:** MD Computers
- **Direct Product URL:** `https://mdcomputers.in/product/lian-li-a3-mini-tower-cabinet-g99-a3x-in`
- **Recorded Price:** ₹7,300.00 (Inclusive of GST)
- **Stock Availability:** `available` (`http://schema.org/InStock`)
- **Verified Manufacturer Model & SKU:** Model `G99-A3X-IN` (Store SKU: `LIAN-LI-A3-MATX-BLACK`, GTIN-8: `4718466015624`)
- **Inspection Timestamp:** `2026-11-02T19:19:20+05:30`
- **Catalog Impact:** Unlocks an active, in-stock Micro-ATX chassis in the catalog. Previously, every budget case was out of stock, preventing any budget build from achieving purchasability.

### Candidate 2: `DS3_PSU_014` — Corsair CX (2023) 650W 80 Plus Bronze
- **Component ID:** `DS3_PSU_014`
- **Catalog Identity:** Corsair CX (2023) 650W 80 Plus Bronze ATX Power Supply, Non-Modular.
- **Seller:** MD Computers
- **Direct Product URL:** `https://mdcomputers.in/product/corsair-cx650-bronze-smps-cp-9020278-na`
- **Recorded Price:** ₹5,250.00 (Inclusive of GST)
- **Stock Availability:** `available` (`http://schema.org/InStock`)
- **Verified Manufacturer Model & SKU:** Model `CP-9020278-IN` (Store SKU: `CORSAIR-CX650-80-PLUS-BRONZE`)
- **Inspection Timestamp:** `2026-11-02T19:21:50+05:30`
- **Catalog Impact:** Converts `DS3_PSU_014` from historical `unavailable` (previously seen only on Vedant Computers at ₹5,150.00 OutOfStock) into a live, currently purchasable power supply.

### Candidate 3: `DS3_RAM_029` — G.Skill Ripjaws V 16 GB (2x8GB) DDR4-3200
- **Component ID:** `DS3_RAM_029`
- **Catalog Identity:** G.Skill Ripjaws V 16 GB (2x8GB) DDR4-3200 CL16-18-18-38 1.35V Desktop Memory Kit.
- **Seller:** MD Computers
- **Direct Product URL:** `https://mdcomputers.in/product/gskill-ram-ripjaws-v-16gb-ddr4-3200mhz-f4-3200c16d-16gvkb`
- **Recorded Price:** ₹5,827.00 (Inclusive of GST)
- **Stock Availability:** `unavailable` (`http://schema.org/OutOfStock`)
- **Verified Manufacturer Model & SKU:** Model `F4-3200C16D-16GVKB` (Store SKU: `G.SKILL RIPJAWS V 16GB DDR4 3200MHz BLACK`)
- **Inspection Timestamp:** `2026-11-02T19:27:40+05:30`
- **Catalog Impact:** Previously unpriced. Establishes the most affordable 16GB dual-channel DDR4 memory benchmark in the dataset (₹5,827.00 vs ₹7,000.00 for Corsair LPX and ₹27,500.00 for 32GB LPX), significantly lowering theoretical build costs for AM4 configurations.

### Candidate 4: `DS3_STORAGE_038` — Kingston NV3 500GB PCIe 4.0 NVMe SSD
- **Component ID:** `DS3_STORAGE_038`
- **Catalog Identity:** Kingston NV3 500GB M.2 2280 NVMe PCIe 4.0 x4 Internal SSD.
- **Seller:** MD Computers
- **Direct Product URL:** `https://mdcomputers.in/product/kingston-nv3-500gb-ssd-snv3s-500g`
- **Recorded Price:** ₹10,450.00 (Inclusive of GST)
- **Stock Availability:** `available` (`http://schema.org/InStock`)
- **Verified Manufacturer Model & SKU:** Model `SNV3S-500G` (Store SKU: `KINGSTON-NV3-500GB`)
- **Inspection Timestamp:** `2026-11-02T19:22:50+05:30`
- **Catalog Impact:** Validates multi-vendor price consensus across independent Kolkata retailers (matching Vedant Computers' ₹10,450.00 offer) and provides a verified live in-stock 500GB NVMe storage option on MD Computers.

### Candidate 5: `DS3_PSU_023` — Corsair CX (2023) 550W 80 Plus Bronze
- **Component ID:** `DS3_PSU_023`
- **Catalog Identity:** Corsair CX (2023) 550W 80 Plus Bronze ATX Power Supply.
- **Seller:** Vedant Computers
- **Direct Product URL:** `https://www.vedantcomputers.com/corsair-cx-series-cx550-550-watt-80-plus-bronze-atx-power-supply-cp-9020277-in`
- **Recorded Price:** ₹3,900.00 (Inclusive of GST)
- **Stock Availability:** `unavailable` (`https://schema.org/OutOfStock`)
- **Verified Manufacturer Model & SKU:** Model `CP-9020277-IN`
- **Inspection Timestamp:** `2026-11-02T19:25:40+05:30`
- **Catalog Impact:** Lowers the reference price for budget 550W power supply from Prime ABGB's previous ₹4,049.00 to ₹3,900.00, improving feasibility for cost-constrained builds.

---

## 4. Rejection Log & Out-of-Stock Catalog Findings

During the research phase, multiple additional components and retailer listings were evaluated and triaged:

1. **Crucial P3 Plus 500GB (`DS3_STORAGE_013`) — Computech Store**:
   - URL: `https://computechstore.in/product/crucial-p3-plus-500gb-ssd/`
   - Price: ₹3,617.00
   - Status: `OutOfStock`
   - Disposition: Corroborates the ~₹3,500 historical price point for 500GB Gen4 SSDs, but held in favor of `DS3_STORAGE_038` to provide an in-stock storage candidate.
2. **WD Black SN770 1TB (`DS3_STORAGE_012`) — MD Computers**:
   - URL: `https://mdcomputers.in/product/wd-black-sn770-1tb-nvme-ssd-wds100t3x0e`
   - Price: ₹7,140.00 | Model `WDS100T3X0E`
   - Status: `OutOfStock`
   - Disposition: Verified authentic historical listing; held as secondary candidate.
3. **G.Skill Ripjaws V 16GB (`DS3_RAM_029`) — Vedant Computers**:
   - URL: `https://www.vedantcomputers.com/g-skill-ripjaws-v-16gb-8gbx2-ddr4-3200mhz-memory-f4-3200c16d-16gvkb`
   - Price: ₹9,400.00
   - Status: `OutOfStock`
   - Disposition: Confirmed identical SKU `F4-3200C16D-16GVKB`. MD Computers' ₹5,827.00 listing was selected as the more representative pricing.
4. **Corsair Vengeance LPX 16GB (`DS3_RAM_003`) — Vedant Computers**:
   - URL: `https://www.vedantcomputers.com/corsair-vengeance-lpx-16gb-8gbx2-ddr4-dram-3200mhz-c16-memory-kit-black-cmk16gx4m2z3200c16`
   - Price: ₹7,050.00
   - Status: `OutOfStock`
   - Disposition: Confirms the ~₹7,000 price point seen on MD Computers (₹7,000.00), verifying market consistency.
5. **G.Skill Flare X5 32GB DDR5-6000 CL30 (`DS3_RAM_016`) — MD Computers**:
   - URL: `https://mdcomputers.in/product/gskill-ram-flare-x5-32gb-ddr5-f5-6000j3038f16gh2-fx5`
   - Price: ₹62,738.00 | Status: `InStock`
   - Disposition: Genuine AMD EXPO DDR5-6000 CL30 dual kit, but held because high-end ₹60k+ DDR5 does not address the budget ₹35,000–₹60,000 build objective.
6. **Cooler Master MasterBox Q300L (`case-cooler-master-q300l`)**:
   - Status: Discontinued / OutOfStock across all queried primary distributors; SCL Gaming remains `unavailable`.

---

## 5. Build Feasibility & Simulation Analysis

Simulations were executed by layering the five Batch 8 candidates onto the production dataset (without altering production files):

### Scenario 1: ₹35,000 — Study/Office
- **Result:** `no_compatible_build_within_budget`
- **Root Cause Analysis:**
  Even with discrete GPU requirements removed for APUs (AMD Ryzen 5 5600GT Vega 7), the platform minimum cost is:
  - CPU: Ryzen 5 5600GT = ₹18,690.00
  - Motherboard: Gigabyte A520M K V2 = ₹5,240.00
  - RAM: G.Skill Ripjaws V 16GB DDR4 = ₹5,827.00
  - Storage: Crucial P3 Plus 500GB = ₹3,470.00
  - Case: Cooler Master Q300L = ₹3,725.00
  - PSU: Corsair CX550 = ₹3,900.00
  - **Minimum Platform Total:** ₹40,852.00
  - **Verdict:** ₹35,000 is mathematically infeasible in current Indian retail without artificial or sub-spec components. Honest reporting correctly flags this as infeasible.

### Scenario 2: ₹45,000 — Programming
- **Default (Lowest Price Search):**
  - CPU: AMD Ryzen 5 5600GT APU (₹18,690.00, `available`)
  - Motherboard: Gigabyte A520M K V2 (₹5,240.00, `available`)
  - RAM: G.Skill Ripjaws V 16GB DDR4-3200 (₹5,827.00, `unavailable`)
  - Storage: Crucial P3 Plus 500GB (₹3,470.00, `unavailable`)
  - Case: Cooler Master Q300L (₹3,725.00, `unavailable`)
  - PSU: Corsair CX550 (₹3,900.00, `unavailable`)
  - **Total:** ₹40,852.00 (Remaining Budget: ₹4,148.00)
  - **Status:** Complete build containing unavailable components.
- **In-Stock Search (`prefer_available=True`):**
  - CPU: AMD Ryzen 5 5600GT APU (₹18,690.00, `available`)
  - Motherboard: Gigabyte A520M K V2 (₹5,240.00, `available`)
  - Case: **Lian Li A3-mATX Black (₹7,300.00, `available`)** *(Batch 8 unlock)*
  - PSU: **MSI MAG A550BN (₹4,150.00, `available`)**
  - RAM: G.Skill Ripjaws V 16GB DDR4-3200 (₹5,827.00, `unavailable`)
  - Storage: Crucial P3 Plus 500GB (₹3,470.00, `unavailable`)
  - **Total:** ₹44,677.00 (Remaining Budget: ₹323.00)
  - **Status:** Complete build; unavailable components reduced from 4 to only 2 (RAM and Storage).

### Scenario 3: ₹60,000 — Gaming
- **Default (Lowest Price Search):**
  - CPU: AMD Ryzen 5 5500 (₹10,700.00, `available`)
  - Motherboard: Gigabyte A520M K V2 (₹5,240.00, `available`)
  - GPU: Gigabyte Radeon RX 6600 EAGLE 8GB (₹19,389.00, `unavailable`)
  - RAM: G.Skill Ripjaws V 16GB DDR4-3200 (₹5,827.00, `unavailable`)
  - Storage: Crucial P3 Plus 500GB (₹3,470.00, `unavailable`)
  - Case: Cooler Master Q300L (₹3,725.00, `unavailable`)
  - PSU: Corsair CX550 (₹3,900.00, `unavailable`)
  - Cooler: DeepCool AK400 (₹2,290.00, `available`)
  - **Total:** ₹54,541.00 (Remaining Budget: ₹5,459.00)
- **In-Stock Search (`prefer_available=True`):**
  - CPU: AMD Ryzen 5 5500 (₹10,700.00, `available`)
  - Motherboard: Gigabyte A520M K V2 (₹5,240.00, `available`)
  - Case: **Lian Li A3-mATX Black (₹7,300.00, `available`)** *(Batch 8 unlock)*
  - PSU: **MSI MAG A550BN (₹4,150.00, `available`)**
  - Cooler: DeepCool AK400 (₹2,290.00, `available`)
  - GPU: Gigabyte Radeon RX 6600 EAGLE (₹19,389.00, `unavailable`)
  - RAM: G.Skill Ripjaws V 16GB (₹5,827.00, `unavailable`)
  - Storage: Crucial P3 Plus 500GB (₹3,470.00, `unavailable`)
  - **Total:** ₹58,366.00 (Remaining Budget: ₹1,634.00)

### Summary of Market Realities
Across all audited Indian retailers (MD Computers, Vedant Computers, Computech Store, Prime ABGB), **16GB (2x8GB) dual-channel DDR4 retail kits are universally out of stock or superseded by single-module 16GB SKUs**. While single-DIMM modules exist, catalog integrity requires dual-channel kits to match the verified `2x8GB` specifications. The recommendation engine honestly identifies that while platform feasibility is achieved under ₹45k and ₹60k, RAM stock remains the primary physical supply-chain constraint in the Indian market.

---

## 6. Baseline Safety & Test Integrity Confirmation

- **Zero modifications** were made to production CSV files (`data/components.csv`, `data/prices.csv`).
- **Zero modifications** were made to source code (`app.py`, `src/compatibility.py`) or test files.
- The automated test suite ran and confirmed that all **93 existing tests continue to pass** cleanly.

