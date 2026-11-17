# Batch 9 Targeted Price Research Audit Report

**Date:** 2026-11-02  
**Targeted Products:** 5 Existing Catalog Components  
**Objective:** Research verified Indian retail pricing, merchant provenance, exact SKUs, and stock availability for high-priority budget catalog components to address purchasability bottlenecks.

---

## 1. Candidate Review & Audit Summary

| Target ID | Product Name | Target SKU | Retailer / Seller | Price (INR) | Availability | Audit Status | Audit Notes |
|---|---|---|---|---|---|---|---|
| `DS3_RAM_029` | G.Skill Ripjaws V 16GB (2x8GB) DDR4-3200 CL16 | `F4-3200C16D-16GVKB` | Vedant Computers | ₹9,400.0 | `unavailable` | **Accepted** | Exact part number verified. Listed on Vedant Computers; currently Out Of Stock. Provides secondary vendor observation alongside MD Computers. |
| `DS3_GPU_046` | Gigabyte EAGLE Radeon RX 6600 8GB | `GV-R66EAGLE-8GD` | SCL Gaming | ₹19,990.0 | `unavailable` | **Accepted** | Exact part number verified. Listed on authorized Indian storefront SCL Gaming; currently Out Of Stock. Close to genuine market baseline. |
| `DS3_STORAGE_013` | Crucial P3 Plus 500GB PCIe 4.0 NVMe SSD | `CT500P3PSSD8` | Computech Store | ₹3,617.0 | `unavailable` | **Accepted** | Exact part number verified. Listed on Computech Store; currently Out Of Stock. |
| `case-cooler-master-q300l` | Cooler Master MasterBox Q300L Micro-ATX Case | `MCB-Q300L-KANN-S00` | EliteHubs | ₹3,935.0 | `unavailable` | **Accepted** | Exact part number verified. Listed on EliteHubs; currently Out Of Stock. |
| `cooler-deepcool-ak400-black` | DeepCool AK400 Black High Performance Air Cooler | `R-AK400-BKNNMN-G-1` | Computech Store | ₹2,290.0 | `available` | **Accepted** | Exact part number verified. Live in-stock offer on Computech Store re-verified at ₹2,290 on 2026-11-02, refreshing the observation within the 7-day window. |

---

## 2. Alternatives & Rejected / Secondary Candidate Findings

1. **`DS3_RAM_029` Alternative Listings:**
   - **TPS Tech:** Listed at ₹9,400.0, Sold Out (`https://www.tpstech.in/products/g-skill-ripjaws-v-ram-16gb-2x8gb-ddr4-3200mhz-desktop-memory`). Valid secondary confirmation, held in reserve.
   - **EliteHubs:** Stale promo listing at ₹2,535.0, Out of Stock. Rejected due to unverified discounted placeholder status.

2. **`DS3_GPU_046` Alternative Listings:**
   - **MD Computers:** Listed at ₹23,999.0, Out Of Stock (`https://mdcomputers.in/product/gigabyte-rx-6600-eagle-8gb-gv-r66eagle-8gd`). Valid secondary confirmation; SCL Gaming preferred due to standard market pricing (₹19,990).
   - **Prime ABGB:** Product page exists (`https://www.primeabgb.com/online-price-india/gigabyte-radeon-rx-6600-eagle-8g-graphic-card-gv-r66eagle-8gd/`), but price is hidden/unlisted. Rejected as unverifiable price.

3. **`DS3_STORAGE_013` Alternative Listings:**
   - **EliteHubs:** Listed at ₹3,795.0, Out of Stock (`https://elitehubs.com/products/crucial-p3-plus-500gb-m-2-internal-solid-state-drive-ct500p3pssd8`). Valid secondary confirmation.
   - **MD Computers:** Listed at ₹5,090.0, Out of Stock (`https://mdcomputers.in/product/crucial-p3-plus-500gb-ssd-ct500p3pssd8`). Valid secondary confirmation.

4. **`cooler-deepcool-ak400-black` Alternative Listings:**
   - **Prime ABGB:** Listed at ₹2,488.0, Out of Stock (`https://www.primeabgb.com/online-price-india/deepcool-ak400-black-high-performance-cpu-cooler-r-ak400-bknnmn-g-1/`). Valid secondary check; Computech Store preferred as live available offer.
   - **Vedant Computers:** Listed at ₹2,695.0, Out of Stock (`https://www.vedantcomputers.com/deepcool-ak400-cpu-air-cooler-r-ak400-bknnmn-g-1`).
   - **MD Computers:** Listed at ₹2,730.0, Out of Stock (`https://mdcomputers.in/product/deepcool-ak400-black-r-ak400-bknnmn-g-1`).

---

## 3. Pre-Import Verification Checklist
- [x] All 5 target component IDs match existing rows in `data/components.csv`.
- [x] No duplicate component IDs are introduced.
- [x] Exact manufacturer SKUs match product specifications.
- [x] Unique `price_id` values generated following canonical naming rules.
- [x] Unique `(component_id, seller, checked_at)` tuples confirmed.
- [x] Strict adherence to raw CSV formatting rules to preserve integer string compatibility in validator tests.

