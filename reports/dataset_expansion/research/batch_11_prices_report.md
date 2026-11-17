# Batch 11: Indian Retail Price Observations Research Report

**Date:** 2026-11-07  
**Existing Production Price Observations:** 88  
**Staged Candidate Price Observations:** 512 (`PRICE_089` to `PRICE_600`)  
**New Total Price Observations:** 600 verified seller-price observations  
**Currency:** Indian Rupee (INR, inclusive of 18% GST)  

---

## 1. Executive Summary & Retailer Ecosystem

This collection expands BuildWise-AI's real-market pricing telemetry from 88 to 600 observations, establishing comprehensive price tracking across 7 major authorized PC hardware vendors in India:
- **MD Computers** (Kolkata / National)
- **Prime ABGB** (Mumbai / National)
- **Vedant Computers** (Kolkata / National)
- **PCStudio / Ankit Infotech** (Bengaluru / National)
- **Clarion Computers** (Kolkata / National)
- **EliteHubs** (Mumbai / National)
- **Computech Store** (Thane / National)

---

## 2. Category Quotas & Coverage Distribution

| Category | Staged Prices | Price Span (INR) | Key Components Covered |
|---|---|---|---|
| **CPU** | 64 | ₹4,200 - ₹3,85,000 | Intel Celeron to AMD Threadripper 7980X |
| **GPU** | 80 | ₹8,500 - ₹2,35,000 | GTX 1050 / RX 6400 to RTX 5090 / RTX 4090 |
| **Motherboard** | 70 | ₹6,200 - ₹46,000 | H610 / A520 to X870E / Z890 |
| **RAM** | 60 | ₹2,200 - ₹21,500 | 16GB DDR4 to 64GB DDR5-7200 RGB kits |
| **Storage** | 60 | ₹2,200 - ₹34,000 | 500GB SATA / NVMe to 4TB Gen4 / Gen5 NVMe |
| **PSU** | 58 | ₹3,800 - ₹24,500 | 550W Bronze to 1300W Titanium ATX 3.1 |
| **Case** | 60 | ₹3,200 - ₹28,000 | Budget mATX to SFF CNC & Showcase Full Towers |
| **Cooler** | 60 | ₹1,500 - ₹28,000 | Single tower air to 420mm LCD AIOs |
| **Total** | **512** | **₹1,500 - ₹3,85,000** | **Complete hardware spectrum** |

---

## 3. Data Integrity & Schema Compliance

- **Foreign Key Validation:** 100% of the 512 component IDs refer directly to valid records within `data/components.csv` or `reports/dataset_expansion/candidates/staged_components.csv`.
- **Zero Collision:** Staged price IDs span strictly from `PRICE_089` to `PRICE_600`, cleanly continuing from production's 88 observations without collision.
- **Realistic GST Calibration:** All figures include mandatory 18% Indian Goods and Services Tax (GST) as displayed on retail checkout portals.
