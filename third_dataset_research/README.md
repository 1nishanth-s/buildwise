# BuildWise-AI: Third PC Components Dataset Research

**Date:** 2026-10-26  
**Auditor:** Antigravity (Advanced Agentic Coding)  
**Status:** Staged & Audited (Isolated Research Directory — Not Merged Into Production)  
**Target Fulfillment:** 100% of Target Minimum Counts Met or Exceeded Across All 8 Categories  
**Directory Location:** [`third_dataset_research/`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/)  

---

## 1. Overview & Objective

Following the rejection and quarantine of `candidate_dataset_staging/` (which contained synthetic data, duplicate loops, and impossible hardware), this research initiative identified, downloaded, normalized, and audited a **real, reliable, and legally usable third PC components dataset**.

This dataset serves as an external candidate repository of **real desktop hardware**, completely decoupled from BuildWise-AI's production catalog (`data/components.csv` and `data/prices.csv`).

---

## 2. Source Repositories & Legal Licences

Two reputable open-source hardware repositories were evaluated, downloaded, and documented:

### Primary Dataset: `docyx/pc-part-dataset`
- **Repository URL:** [https://github.com/docyx/pc-part-dataset](https://github.com/docyx/pc-part-dataset)
- **Author:** Doc Oliver (Active 2021–2025)
- **License:** **MIT License** (Permissive open source)
- **Description:** Structured hardware specifications and pricing scraped directly from PCPartPicker, updated through early 2025. Covers 43,000+ PC components across all desktop categories.
- **Downloaded Files:** 8 category CSVs (`cpu.csv`, `motherboard.csv`, `memory.csv`, `video-card.csv`, `power-supply.csv`, `internal-hard-drive.csv`, `case.csv`, `cpu-cooler.csv`), along with `LICENSE.txt` and `README.md`.
- **Integrity Check:** Original raw downloads are archived in [`original_downloads/docyx_pc_part_dataset/`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/original_downloads/docyx_pc_part_dataset/) with SHA-256 checksums documented in [`source_manifest.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/source_manifest.csv).

### Secondary Reference: `buildcores/buildcores-open-db`
- **Repository URL:** [https://github.com/buildcores/buildcores-open-db](https://github.com/buildcores/buildcores-open-db)
- **Author:** BuildCores Community
- **License:** **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**
- **Description:** Open database of computer hardware containing UUID-indexed JSON records with Manufacturer Part Numbers (MPNs), EAN/UPC barcodes, and direct manufacturer datasheet links.
- **Downloaded Files:** `LICENSE.txt`, `NOTICE.md`, `README.md` archived in [`original_downloads/buildcores_open_db/`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/original_downloads/buildcores_open_db/).

### Legal & Fair Dealing Analysis
1. **Factual Hardware Specifications:** Under Section 52(1)(a) of the Indian Copyright Act, 1957, raw functional hardware specifications (clock speeds, TDP, sockets, memory configurations, dimensions) are non-copyrightable facts.
2. **Permissive MIT Licensing:** The primary source dataset (`docyx/pc-part-dataset`) is licensed under the MIT License, which explicitly allows modification, distribution, sublicensing, and inclusion in software projects.
3. **Attribution Baseline:** All source records retain full attribution to their upstream repositories, authors, and licenses.

---

## 3. Directory File Inventory

| Filename | Format | Records | Purpose & Contents |
|---|---|---:|---|
| [`components.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/components.csv) | CSV (`utf-8`) | **360** | Normalized, modern desktop PC components across all 8 hardware categories with structured JSON specifications. |
| [`prices.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/prices.csv) | CSV (`utf-8`) | **357** | Separately recorded price observations (349 international USD scrape references + 8 verified Indian retail INR observations). |
| [`review_queue.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/review_queue.csv) | CSV (`utf-8`) | **60** | Quarantined legacy components (LGA775, AM3+, DDR3, obsolete FX/Phenom CPUs) filtered out of the recommendation pool. |
| [`source_manifest.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/source_manifest.csv) | CSV (`utf-8`) | **13** | File-by-file provenance manifest with original URLs, SHA-256 hashes, file sizes, and license details. |
| [`dataset_audit.md`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/dataset_audit.md) | Markdown | -- | Comprehensive audit report analyzing category fulfillment, duplicate checks, validation, and limitations. |
| [`original_downloads/`](file:///e:/BuildWise-AI/BuildWise-AI1/third_dataset_research/original_downloads/) | Directory | 13 files | Pristine, unmodified raw source downloads with verification checksums. |

---

## 4. Target Fulfillment Summary

| Component Category | Target Requirement | Third Dataset Count | Status | Platform / Hardware Coverage |
|---|---:|---:|---|---|
| **Desktop CPUs** | $\ge 50$ | **60** | **MET (+10)** | AMD Ryzen 5000/7000/8000/9000; Intel 12th/13th/14th Gen, Core Ultra 200S |
| **Motherboards** | $\ge 80$ | **85** | **MET (+5)** | AM4 (B550/X570), AM5 (B650/X670/B850/X870), LGA1700 (B760/Z790), LGA1851 (Z890) |
| **Desktop RAM Kits** | $\ge 32$ | **40** | **MET (+8)** | DDR4-3200/3600 (16GB/32GB/64GB); DDR5-5200/5600/6000/6400 (32GB/64GB) |
| **Graphics Cards (GPUs)** | $\ge 40$ | **50** | **MET (+10)** | RTX 3050–3090, RTX 4060–4090, RX 6600–6950 XT, RX 7600–7900 XTX, Intel Arc A750/A770 |
| **Storage Drives (SSDs & HDDs)** | $\ge 30$ | **40** | **MET (+10)** | M.2 NVMe PCIe 4.0/5.0 SSDs (Samsung, WD, Crucial, Kingston) + 3.5" SATA HDDs (Seagate, WD) |
| **Power Supplies (PSUs)** | $\ge 25$ | **30** | **MET (+5)** | 550W–1000W 80 Plus Bronze/Gold/Platinum (Corsair, MSI, Cooler Master, Deepcool, Seasonic) |
| **PC Cases** | $\ge 25$ | **30** | **MET (+5)** | ATX Mid Tower, Micro-ATX Tempered Glass (Corsair, NZXT, Lian Li, Phanteks, Fractal, Montech) |
| **CPU Coolers** | $\ge 20$ | **25** | **MET (+5)** | Single/Dual Tower Air Coolers + 240mm/360mm AIO Liquid Coolers (Thermalright, DeepCool, Noctua) |
| **Total Components** | $\mathbf{\ge 302}$ | **360** | **ALL MET** | **Zero synthetic or fabricated components** |

---

## 5. Pricing Provenance & Currency Separation

In strict compliance with BuildWise-AI standards:
- **No Fabricated Indian Prices:** We do **not** convert USD to INR using arbitrary exchange rates.
- **Separation of Concerns:** Component technical specifications are completely decoupled from seller pricing.
- **US Retail Scrapes (349 records):** Explicitly tagged with `currency: USD`, `price_type: international_usd_reference`, and `availability: foreign_reference_only`.
- **Verified Indian Observations (8 records):** Recorded with `currency: INR`, `price_type: indian_retail_observation`, public retailer URLs, and dated observation timestamps.

---

## 6. How to Review This Dataset (Windows PowerShell)

Open Windows PowerShell in the project directory (`E:\BuildWise-AI\BuildWise-AI1`) and run:

```powershell
# 1. View summary counts of the third dataset
.\.venv\Scripts\python.exe -c "
import pandas as pd
df = pd.read_csv('third_dataset_research/components.csv')
print('=== Third Dataset Component Counts ===')
print(df['category'].value_counts())
print('Total Curated Components:', len(df))
"

# 2. Inspect pricing breakdown by currency and seller
.\.venv\Scripts\python.exe -c "
import pandas as pd
df = pd.read_csv('third_dataset_research/prices.csv')
print('=== Pricing Observations Breakdown ===')
print(df.groupby(['currency', 'price_type']).size())
"

# 3. View quarantined legacy records
.\.venv\Scripts\python.exe -c "
import pandas as pd
df = pd.read_csv('third_dataset_research/review_queue.csv')
print('=== Quarantined Legacy Hardware ===')
print(df['issue_type'].value_counts())
"
```
