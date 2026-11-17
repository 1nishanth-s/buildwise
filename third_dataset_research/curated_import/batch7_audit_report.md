# BuildWise-AI — Batch 7: Affordable APU & DDR4 Price Research Audit Report

**Date of Audit:** November 1, 2026  
**Auditor:** BuildWise-AI Automated Data Engineering & Verification Pipeline  
**Target Candidate Artifact:** `third_dataset_research/curated_import/batch7_inr_prices_candidates.csv`  
**Production Baseline:** `data/components.csv` (421 components) & `data/prices.csv` (73 observations across 56 unique components, 13.30% coverage; 93 passing tests)

---

## 1. Executive Summary & Objective

Following the Batch 6 feasibility audit and the recent integration of display requirements checking (`check_graphics_output`) and honest purchase availability reporting, BuildWise-AI identified two critical data gaps:

1. **APU Absence (Study/Office & Programming Bottleneck)**:
   The catalog previously contained zero price observations for CPUs with documented integrated graphics (such as AMD Ryzen 5000G-series APUs). Consequently, systems for Study/Office workloads with budgets under ₹50,000 could not be generated because discrete GPUs (~₹19,389 for RX 6600) were required to guarantee video display output for CPUs lacking an iGPU (e.g., Ryzen 5 5500, Core i3-12100F).
2. **Affordable DDR4 RAM Bottleneck (AM4 Budget Systems)**:
   The only priced DDR4 RAM kit in the database was `DS3_RAM_005` (Corsair Vengeance LPX 32GB DDR4-3600) at ₹27,500.0. Budget AM4 builds were forced into either over-budget failures or incompatibility errors (attempting to pair DDR5 with AM4 motherboards).

The objective of **Batch 7** is to discover, authenticate, and document verified Indian retail prices for existing catalog components:
- **Target 1**: AMD Ryzen 5 5600G (`DS3_CPU_029`)
- **Target 2**: AMD Ryzen 5 5600GT (`DS3_CPU_055`)
- **Target 3**: Affordable DDR4 RAM kits (focusing on dual-channel 16GB 2x8GB configurations represented in `data/components.csv`)

Strict guidelines were enforced:
- Maximum 5 candidate observations recorded in `batch7_inr_prices_candidates.csv`.
- Direct product page verification on authorized Indian hardware retailers (no aggregators, marketplace scrapers, or synthetic estimations).
- Exact SKU and package verification (single-module DIMMs strictly disqualified from dual-channel catalog records).
- Full separation between live in-stock offers (`available`) and out-of-stock catalog listings (`unavailable`).

---

## 2. Batch 7 Accepted Price Observations

Five (5) candidate price observations were verified through live HTTP inspections on authorized Indian hardware storefronts and recorded into `batch7_inr_prices_candidates.csv`:

| # | Price ID | Component ID | Brand & Model | Price (INR) | Availability | Price Type | Seller | Verified SKU / MPN |
|---|---|---|---|---|---|---|---|---|
| 1 | `price-cpu-amd-ryzen5-5600g-vedant-20261101-182801` | `DS3_CPU_029` | AMD Ryzen 5 5600G (Vega 7) | ₹18,800.0 | `available` | `seller_observation` | Vedant Computers | `100-100000252BOX` |
| 2 | `price-cpu-amd-ryzen5-5600gt-vedant-20261101-182802` | `DS3_CPU_055` | AMD Ryzen 5 5600GT (Vega 7) | ₹18,690.0 | `available` | `seller_observation` | Vedant Computers | `100-100001488BOX` |
| 3 | `price-cpu-amd-ryzen5-5600gt-mdcomputers-20261101-182803` | `DS3_CPU_055` | AMD Ryzen 5 5600GT (Vega 7) | ₹19,300.0 | `available` | `seller_observation` | MD Computers | `100-100001488BOX` |
| 4 | `price-ram-corsair-vengeance-lpx-16gb-ddr4-3200-mdcomputers-20261101-182804` | `DS3_RAM_003` | Corsair Vengeance LPX 16GB (2x8GB) DDR4-3200 | ₹7,000.0 | `unavailable` | `seller_observation` | MD Computers | `CMK16GX4M2Z3200C16` |
| 5 | `price-ram-corsair-vengeance-rgb-pro-16gb-ddr4-3200-vedant-20261101-182805` | `DS3_RAM_018` | Corsair Vengeance RGB Pro 16GB (2x8GB) DDR4-3200 | ₹7,150.0 | `unavailable` | `seller_observation` | Vedant Computers | `CMW16GX4M2C3200C16` |

---

## 3. Detailed Retailer Evidence & Identity Verification

### Candidate 1: `DS3_CPU_029` — AMD Ryzen 5 5600G
- **Component ID:** `DS3_CPU_029`
- **Catalog Identity:** AMD Ryzen 5 5600G, 6 Cores, 12 Threads, Base 3.9 GHz, Boost 4.4 GHz, Radeon Vega 7 integrated graphics, Socket AM4, 65W TDP.
- **Seller:** Vedant Computers
- **Direct Product URL:** `https://www.vedantcomputers.com/amd-ryzen-5-5600g-processor-100-100000252box`
- **Recorded Price:** ₹18,800.0 (Inclusive of GST; markdown from list price ₹37,000.0)
- **Stock Availability:** `available` (`http://schema.org/InStock`)
- **Verified Manufacturer Part Number (MPN):** `100-100000252BOX` (Seller SKU: `AMD-R5-5600G`)
- **Inspection Timestamp:** `2026-11-01T18:28:01+05:30`
- **Observation Provenance:** Live in-stock retail offer on authorized Indian hardware vendor storefront (Vedant Computers; SKU AMD-R5-5600G / 100-100000252BOX; AMD Ryzen 5 5600G 6-Core APU with Radeon Vega 7 Graphics).

### Candidate 2: `DS3_CPU_055` — AMD Ryzen 5 5600GT
- **Component ID:** `DS3_CPU_055`
- **Catalog Identity:** AMD Ryzen 5 5600GT, 6 Cores, 12 Threads, Base 3.6 GHz, Boost 4.6 GHz, Radeon Vega 7 integrated graphics, Socket AM4, 65W TDP.
- **Seller:** Vedant Computers
- **Direct Product URL:** `https://www.vedantcomputers.com/amd-ryzen-5-5600gt-processor-100-100001488box`
- **Recorded Price:** ₹18,690.0 (Inclusive of GST; markdown from list price ₹22,000.0)
- **Stock Availability:** `available` (`http://schema.org/InStock`)
- **Verified Manufacturer Part Number (MPN):** `100-100001488BOX`
- **Inspection Timestamp:** `2026-11-01T18:28:02+05:30`
- **Observation Provenance:** Live in-stock retail offer on authorized Indian hardware vendor storefront (Vedant Computers; Model 100-100001488BOX; AMD Ryzen 5 5600GT 6-Core APU with Radeon Vega 7 Graphics).

### Candidate 3: `DS3_CPU_055` — AMD Ryzen 5 5600GT
- **Component ID:** `DS3_CPU_055`
- **Catalog Identity:** AMD Ryzen 5 5600GT, 6 Cores, 12 Threads, Radeon Vega 7 integrated graphics, Socket AM4.
- **Seller:** MD Computers
- **Direct Product URL:** `https://mdcomputers.in/product/amd-ryzen-5-5600gt-100-100001488box-desktop-processor`
- **Recorded Price:** ₹19,300.0 (Inclusive of GST)
- **Stock Availability:** `available` (`http://schema.org/InStock`)
- **Verified Manufacturer Part Number (MPN):** `100-100001488BOX` (Store SKU: `AMD-RYZEN-5-5600GT-100-100001488BOX`)
- **Inspection Timestamp:** `2026-11-01T18:28:03+05:30`
- **Observation Provenance:** Live in-stock retail offer on authorized Indian hardware vendor storefront (MD Computers; SKU AMD-RYZEN-5-5600GT-100-100001488BOX / 100-100001488BOX; AMD Ryzen 5 5600GT 6-Core APU with Radeon Vega 7 Graphics).

### Candidate 4: `DS3_RAM_003` — Corsair Vengeance LPX 16GB (2x8GB) DDR4-3200
- **Component ID:** `DS3_RAM_003`
- **Catalog Identity:** Corsair Vengeance LPX 16GB (2x8GB), DDR4-3200 CL16, 1.35V.
- **Seller:** MD Computers
- **Direct Product URL:** `https://mdcomputers.in/product/corsair-ram-vengeance-lpx-cmk16gx4m2z3200c16`
- **Recorded Price:** ₹7,000.0 (Inclusive of GST)
- **Stock Availability:** `unavailable` (`http://schema.org/OutOfStock`)
- **Verified Manufacturer Part Number (MPN):** `CMK16GX4M2Z3200C16` (Ryzen-tuned 2x8GB DDR4-3200 CL16 dual-channel kit)
- **Inspection Timestamp:** `2026-11-01T18:28:04+05:30`
- **Observation Provenance:** Observed out-of-stock retail catalog listing on authorized Indian hardware vendor storefront (MD Computers; SKU CMK16GX4M2Z3200C16; Corsair Vengeance LPX 16GB (2x8GB) DDR4-3200 CL16 Desktop Memory Kit).
- **Audit Note & Resolution:** In Batch 6, this component was held due to an archived `.html` URL that redirected to the home page, and a tentative `available` flag. Inspection of MD Computers' live catalog revealed the active product endpoint `https://mdcomputers.in/product/corsair-ram-vengeance-lpx-cmk16gx4m2z3200c16` listing the genuine historical price of ₹7,000.0 with availability accurately recorded as `unavailable`.

### Candidate 5: `DS3_RAM_018` — Corsair Vengeance RGB Pro 16GB (2x8GB) DDR4-3200
- **Component ID:** `DS3_RAM_018`
- **Catalog Identity:** Corsair Vengeance RGB Pro 16GB (2x8GB), DDR4-3200 CL16.
- **Seller:** Vedant Computers
- **Direct Product URL:** `https://www.vedantcomputers.com/corsair-vengeance-rgb-pro-16gb-8gbx2-ddr4-dram-3200mhz-c16-memory-black-cmw16gx4m2c3200c16`
- **Recorded Price:** ₹7,150.0 (Inclusive of GST)
- **Stock Availability:** `unavailable` (`https://schema.org/OutOfStock`)
- **Verified Manufacturer Part Number (MPN):** `CMW16GX4M2C3200C16` (Black 2x8GB DDR4-3200 CL16 dual-channel RGB kit)
- **Inspection Timestamp:** `2026-11-01T18:28:05+05:30`
- **Observation Provenance:** Observed out-of-stock retail catalog listing on authorized Indian hardware vendor storefront (Vedant Computers; SKU CMW16GX4M2C3200C16; Corsair Vengeance RGB Pro 16GB (2x8GB) DDR4-3200 CL16 Black Desktop Memory Kit).

---

## 4. Corroborating Price Evidence Researched

To cross-verify authenticity and market pricing consistency, additional retailer product pages were examined:

| Component ID | Model | Store | Direct URL | Price (INR) | Availability | SKU / MPN |
|---|---|---|---|---|---|---|
| `DS3_CPU_029` | Ryzen 5 5600G | Prime ABGB | `https://www.primeabgb.com/online-price-reviews-india/amd-ryzen-5-5600g-desktop-processor-integrated-radeon-graphics-100-100000252box/` | ₹19,220.0 | `available` | `100-100000252BOX` |
| `DS3_CPU_029` | Ryzen 5 5600G | MD Computers | `https://mdcomputers.in/amd-ryzen-5-5600g-100-100000252box.html` | ₹14,000.0 | `unavailable` | `100-100000252BOX` |
| `DS3_CPU_055` | Ryzen 5 5600GT | Prime ABGB | `https://www.primeabgb.com/online-price-reviews-india/amd-ryzen-5-5600gt-ryzen-5-5000-series-6-core-3-6-ghz-socket-am4-65w-amd-radeon-graphics-processor-100-100001488box/` | ₹19,689.0 | `available` | `100-100001488BOX` |
| `DS3_RAM_003` | Corsair LPX 16GB | Vedant Computers | `https://www.vedantcomputers.com/corsair-vengeance-lpx-16gb-8gbx2-ddr4-dram-3200mhz-c16-memory-kit-black-cmk16gx4m2z3200c16` | ₹7,050.0 | `unavailable` | `CMK16GX4M2Z3200C16` |
| `DS3_RAM_018` | Corsair RGB Pro 16GB | MD Computers | `https://mdcomputers.in/product/corsair-ram-vengeance-rgb-pro-cmw16gx4m2c3200c16` | ₹9,953.0 | `unavailable` | `CMW16GX4M2C3200C16` |
| `DS3_RAM_037` | Crucial Pro 32GB Kit | MD Computers | `https://mdcomputers.in/product/crucial-ram-pro-cp2k16g4dfra32a` | ₹9,350.0 | `unavailable` | `CP2K16G4DFRA32A` |

---

## 5. Screening and Rejection Log

### Disqualified / Rejected: `DS3_RAM_028` (Kingston FURY Beast 16GB 2x8GB DDR4-3200)
- **Target SKU:** `KF432C16BBK2/16` (2x8GB dual kit)
- **Stores Checked:** MD Computers, Vedant Computers, Prime ABGB, PCStudio, Computech Store, EliteHubs.
- **Findings:** Indian retail channels stock individual single-module SKUs (`KF432C16BB/8` for 1x8GB, `KF432C16BB/16` for 1x16GB). The boxed dual-channel kit `KF432C16BBK2/16` is only listed on international dropshipping sites (Desertcart, Ubuy) with inflated customs/shipping overhead. Per database integrity rules, single modules must not be substituted for dual-channel kit records.
- **Determination:** **REJECTED** (Preserved rejection from Batch 6).

### Disqualified / Unresolved: `DS3_RAM_029` (G.Skill Ripjaws V 16GB 2x8GB DDR4-3200)
- **Target SKU:** `F4-3200C16D-16GVKB`
- **Stores Checked:** MD Computers, Vedant Computers, Prime ABGB.
- **Findings:** MD Computers legacy page `g-skill-ripjaws-v-ddr4-f4-3200c16d-16gvkb.html` redirects to the generic home page, and Vedant Computers returns HTTP 404. All current retail stock in India for Ripjaws V 16GB is single-stick `F4-3200C16S-16GVK`.
- **Determination:** **UNRESOLVED / REJECTED** (Excluded due to lack of an active direct product page).

### Deprecated URL Reconciliation: Corsair Vengeance LPX Batch 6 Listing
- **Previous Held URL:** `https://mdcomputers.in/corsair-vengeance-lpx-16gb-8gbx2-ddr4-3200mhz-black-cmk16gx4m2z3200c16.html`
- **Findings:** MD Computers transitioned their platform URLs from root `.html` files to `/product/<slug>`. The old URL soft-redirected to the store homepage. The active live endpoint `https://mdcomputers.in/product/corsair-ram-vengeance-lpx-cmk16gx4m2z3200c16` was discovered, verified, and correctly identified as `unavailable` at ₹7,000.0.

---

## 6. Expected Impact on PC Recommendation Feasibility

When these 5 observations are imported in a subsequent controlled batch:

1. **Unlocking Office / Programming APU Builds**:
   With `DS3_CPU_029` (Ryzen 5 5600G at ₹18,800) and `DS3_CPU_055` (Ryzen 5 5600GT at ₹18,690), BuildWise-AI can assemble complete 6-component systems without a discrete GPU. An office build comprising:
   - CPU: AMD Ryzen 5 5600GT (₹18,690.0)
   - Motherboard: MSI B450M-A PRO MAX II (₹6,050.0)
   - RAM: Corsair Vengeance LPX 16GB (₹7,000.0)
   - Storage: Crucial P3 Plus 500GB (₹3,470.0)
   - Case: Cooler Master Q300L (₹3,725.0)
   - PSU: Corsair CX550 (₹4,049.0)
   **Total System Cost: ~₹42,984.00**.  
   This immediately solves the ₹45,000 Programming and sub-₹50,000 Office build failure modes.

2. **Fixing AM4 DDR4 RAM Pricing**:
   Replacing the sole ₹27,500 DDR4 kit (`DS3_RAM_005`) with `DS3_RAM_003` (₹7,000.0) and `DS3_RAM_018` (₹7,150.0) reduces memory platform cost by over ₹20,000, allowing realistic entry-level AM4 gaming builds (pairing Ryzen 5 5500 + RX 6600) to fall within the ₹55,000–₹60,000 budget window.

3. **Purchase Availability Truthfulness**:
   Because `DS3_RAM_003` and `DS3_RAM_018` are correctly marked `unavailable`, any system incorporating them will transparently display:  
   `**Build classification:** Complete build containing unavailable or stale-price components`  
   `**Purchase availability:** Not purchasable (historical / out of stock)`  
   This ensures complete alignment with our zero-hallucination and purchasability honesty policies.

