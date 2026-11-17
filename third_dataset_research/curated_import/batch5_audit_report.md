# BuildWise-AI — Batch 5 INR Price Research & Verification Audit Report

**Date of Audit:** October 31, 2026  
**Auditor:** BuildWise-AI Automated Data Engineering & Verification Pipeline  
**Target Candidate Artifact:** `third_dataset_research/curated_import/batch5_inr_prices_candidates.csv`  
**Production Dataset Inspected:** `data/components.csv` (421 components) & `data/prices.csv` (60 observations across 43 unique components, 10.21% coverage)

---

## 1. Executive Summary & Objective

The primary objective of Batch 5 price research is to discover, authenticate, and document genuine Indian retail price observations for existing components in `data/components.csv` that currently possess zero recorded prices in `data/prices.csv`.

Priority was given to components essential for realistic budget PC builds (₹35,000–₹80,000 INR), specifically:
1. DDR4 and DDR5 RAM kits (high-capacity dual-channel).
2. Gen4 and Gen3 NVMe SSDs (500GB and 1TB).
3. Value AM4 and LGA1700 motherboards (sub-₹10,000 Micro-ATX options).
4. Mainstream ATX power supplies (650W Bronze).
5. Budget 1080p gaming graphics cards (Radeon RX 6600).
6. High-performance air coolers (flagship dual-tower).

All proposed observations were screened against strict identity, SKU, pricing, and live availability standards. Zero synthetic or hallucinated data were used.

---

## 2. Baseline Catalog Status (Pre-Batch 5)

- **Total Production Catalog Components:** 421
- **Total Production Price Observations:** 60
- **Unique Components Currently Priced:** 43
- **Baseline Price Coverage:** 10.21%
- **Unpriced Components Remaining:** 378

---

## 3. Batch 5 Accepted Price Observations

Ten (10) exact-match catalog components with zero prior price records were successfully verified with live Indian storefront evidence:

| # | Component ID | Category | Brand & Model | Price (INR) | Availability | Price Type | Seller | Verification Evidence / SKU |
|---|---|---|---|---|---|---|---|---|
| 1 | `wd-black-sn7100-1tb` | Storage | Western Digital WD_BLACK SN7100 1TB NVMe | ₹17,400.0 | `available` | `seller_observation` | Vedant Computers | SKU `WDS100T4X0E`; PCIe Gen4 M.2 NVMe SSD |
| 2 | `DS3_MB_036` | Motherboard | Gigabyte Z790 EAGLE AX | ₹22,293.0 | `available` | `seller_observation` | Vedant Computers | Model `Z790 EAGLE AX`; Intel LGA1700 ATX |
| 3 | `DS3_MB_037` | Motherboard | MSI B450M-A PRO MAX II | ₹6,050.0 | `available` | `seller_observation` | Vedant Computers | Model `B450M-A PRO MAX II`; AMD AM4 Micro-ATX |
| 4 | `DS3_MB_013` | Motherboard | Gigabyte B550M K | ₹8,590.0 | `available` | `seller_observation` | Vedant Computers | Model `B550M K`; AMD AM4 Micro-ATX |
| 5 | `DS3_RAM_005` | RAM | Corsair Vengeance LPX 32GB (2x16GB) DDR4-3600 | ₹27,500.0 | `available` | `seller_observation` | Vedant Computers | SKU `CMK32GX4M2D3600C18`; DDR4 3600MHz CL18 Kit |
| 6 | `DS3_MB_021` | Motherboard | MSI B550M PRO-VDH WIFI | ₹10,150.0 | `available` | `seller_observation` | Vedant Computers | Model `B550M PRO-VDH WIFI`; AMD AM4 Micro-ATX |
| 7 | `DS3_GPU_046` | GPU | Gigabyte EAGLE Radeon RX 6600 8GB | ₹19,389.0 | `unavailable` | `seller_observation` | Vedant Computers | SKU `GV-R66EAGLE-8GD`; Out of stock catalog listing |
| 8 | `DS3_PSU_014` | PSU | Corsair CX (2023) 650W Bronze ATX | ₹5,150.0 | `unavailable` | `seller_observation` | Vedant Computers | SKU `CP-9020278-IN`; Out of stock catalog listing |
| 9 | `DS3_COOLER_006` | Cooler | Noctua NH-D15 chromax.black | ₹10,780.0 | `available` | `seller_observation` | Vedant Computers | Model `NH-D15 chromax.black`; Dual-tower air cooler |
| 10 | `DS3_MB_029` | Motherboard | MSI MAG B550 TOMAHAWK MAX WIFI | ₹17,675.0 | `unavailable` | `seller_observation` | Vedant Computers | Model `MAG B550 TOMAHAWK MAX WIFI`; AM4 ATX |

### Stock Availability Breakdown:
- **Available (In Stock):** 7 / 10 (70%)
- **Unavailable (Catalog Listing / Out of Stock):** 3 / 10 (30%)

---

## 4. Screening and Rejection Log

During the research process, candidate components were rejected or excluded from Batch 5 for failing verification criteria:

| Candidate ID | Target Product | Source Attempted | Reason for Rejection |
|---|---|---|---|
| `DS3_RAM_018` | Corsair Vengeance RGB Pro 16GB DDR4-3200 | Vedant Computers | HTTP 404 (Broken / delisted product URL) |
| `DS3_RAM_029` | G.Skill Ripjaws V 16GB (2x8GB) DDR4-3600 | Vedant Computers | HTTP 404 (Obsolete listing slug) |
| `cooler-cm-hyper-212-black` | Cooler Master Hyper 212 Black Edition | Vedant Computers | HTTP 404 (Product page removed) |
| `DS3_STORAGE_013` | Crucial P3 Plus 500GB PCIe Gen4 NVMe | Vedant Computers | HTTP 404 (Direct SKU URL not resolved) |
| `DS3_STORAGE_002` | Crucial P3 Plus 1TB PCIe Gen4 NVMe | Vedant Computers | HTTP 404 (Direct SKU URL not resolved) |
| `DS3_STORAGE_010` | Samsung 990 EVO Plus 1TB PCIe Gen4 NVMe | Vedant Computers | HTTP 404 (Product listing inactive) |
| `DS3_CASE_006` | Lian Li Lancool 207 ATX Mid-Tower Case | Vedant Computers | HTTP 404 (Direct URL unavailable) |
| `DS3_CASE_022` | NZXT H6 Flow ATX Mid-Tower Case | Vedant Computers | HTTP 404 (Direct URL unavailable) |
| Multi-Component Batch | Various CPUs / Motherboards | MD Computers | HTTP 403 Forbidden (Cloudflare WAF bot-challenge prevented direct automated verification) |

---

## 5. Build Recommendation Impact

Adding Batch 5 candidate prices unlocks critical pathways for BuildWise-AI's recommendation engine:
1. **Entry-Level AMD AM4 Builds:** Motherboards like the MSI B450M-A PRO MAX II (₹6,050) and Gigabyte B550M K (₹8,590) allow fully functional sub-₹45,000 builds paired with Ryzen 5 5500/5600.
2. **Sub-₹20,000 Dedicated 1080p GPU:** The Gigabyte Radeon RX 6600 EAGLE (₹19,389) provides realistic pricing for pure 1080p esports and AAA gaming tier.
3. **High-Performance Memory & High-End Cooling:** Corsair 32GB DDR4-3600 kit (₹27,500) and Noctua NH-D15 chromax.black (₹10,780) provide realistic anchor points for enthusiast AM4/LGA1700 setups.
4. **Mainstream 650W Power Budget:** The Corsair CX650 (₹5,150) establishes realistic PSU pricing for mid-tier configurations.

---

## 6. Verification and Safety Compliance Checklist

- [x] `data/components.csv` untouched.
- [x] `data/prices.csv` untouched.
- [x] `app.py`, frontend, compatibility engine, and tests untouched.
- [x] Existing batch candidate files (`batch1` to `batch4`) preserved.
- [x] Zero duplicate `price_id` values across the entire repository.
- [x] Schema matches production standard (`price_id,component_id,seller,price_inr,source_url,checked_at,availability,price_type,provenance`).
- [x] Genuine timestamps recorded in ISO 8601 with local timezone offset (+05:30).
- [x] Out-of-stock items honestly marked `unavailable` rather than synthesized as available.

---

## 7. Recommended Next Batch (Batch 6) Priorities

1. **PC Cases:** Affordable Micro-ATX and ATX cases (e.g., Ant Esports, DeepCool, Galax) currently lack sufficient priced representation.
2. **Budget 500GB SSDs:** Sourcing verified live listings for sub-₹4,000 NVMe SSDs (Crucial P3, Kingston NV2/NV3) to support extreme-budget builds.
3. **8GB & 16GB Single-Stick RAM:** 1x8GB DDR4-3200 and 1x16GB DDR4-3200 modules for entry-level ₹35,000 builds.

