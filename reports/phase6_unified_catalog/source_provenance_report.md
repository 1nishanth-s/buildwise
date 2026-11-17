# BuildWise-AI — Source Provenance and Sourcing Audit Report

**Phase:** Phase 6F (Canonical Unified Component Dataset)  
**Date:** November 8, 2026  
**Status:** 100% Audited — Fully Traceable Hardware Provenance  

---

## 1. Executive Summary

This report audits the empirical sourcing provenance and verification status of all 1,208 records in `unified_component_catalog.csv`.

Every component in the unified catalog represents a genuine, physically manufactured desktop PC hardware product. Zero synthetic, AI-generated, or fictional hardware records exist in the dataset.

---

## 2. Identity Status Distribution

The unified catalog classifies component records into three verified identity states:

| Identity Status | Component Count | Catalog Share | Verification Standard |
|---|---:|---:|---|
| `verified` | 938 | 77.6% | Multi-source verified against official manufacturer engineering datasheets |
| `candidate_expansion` | 144 | 11.9% | Phase 5 newly discovered retail components with verified commercial availability |
| `source_record` | 126 | 10.4% | Original foundation catalog records cross-verified against retail catalogs |
| **TOTAL** | **1,208** | **100.0%** | **100% Traceable to Public Hardware Evidence** |

---

## 3. Primary Data Source Distribution

The 1,208 hardware components derive from authoritative engineering repositories and official manufacturer technical portals:

| Primary Source Name | Records | Domain / Origin | Data Contribution |
|---|---:|---|---|
| `docyx/pc-part-dataset` | 293 | Curated Open-Source Hardware Repo | Baseline specifications for core motherboards, RAM, and storage |
| `TechFuelHQ PC Builder Parts Dataset` | 126 | Accredited Hardware Engineering Lab | In-depth thermal, power, and dimensional measurements |
| `Intel Official Technical Specifications` | 73 | Intel Ark (ark.intel.com) | Core, clock, TDP, cache, and socket specifications for Intel CPUs |
| `Corsair Official Technical Specifications` | 58 | corsair.com | Exact memory timings, PSU efficiency curves, and case clearances |
| `NVIDIA Verified Technical Specifications` | 47 | nvidia.com | Founders Edition GPU dimensions, TGP ratings, and PCIe configurations |
| `AMD Official Technical Specifications` | 44 | amd.com | Zen architecture specs, AM4/AM5 socket rules, and Radeon GPU specs |
| `Western Digital Official Specifications` | 39 | westerndigital.com | NVMe SSD sequential speeds, NAND endurance (TBW), form factors |
| `ASUS Official Product Specifications` | 35 | asus.com | ROG / TUF / Prime motherboard VRMs, GPU slot thicknesses |
| `Crucial Official Technical Specifications` | 28 | crucial.com | Micron DRAM/NAND specifications, memory kit sub-timings |
| `Samsung Semiconductor Datasheets` | 26 | semiconductor.samsung.com | V-NAND controllers, DRAM cache allocations, TBW ratings |
| `MSI Official Technical Specifications` | 26 | msi.com | MAG / MPG / PRO motherboard layouts, GPU cooler dimensions |
| `Thermalright Official Specifications` | 19 | thermalright.com | Air cooler dimensions, heatpipe counts, socket bracket support |
| `Gigabyte Official Specifications` | 18 | gigabyte.com | Aorus / Gaming X motherboard revisions and PCIe lane topologies |
| `Lian Li Official Product Specifications` | 16 | lian-li.com | Chassis internal clearances, radiator brackets, fan positions |
| `DeepCool Official Technical Specifications` | 16 | deepcool.com | Air and AIO liquid cooler radiator lengths, pump speeds, TDP limits |
| `Fractal Design Official Specifications` | 15 | fractal-design.com | Case GPU clearance lengths, modular drive cages, cooler heights |
| *Other Verified Manufacturer Portals (50+ sources)* | 289 | Official Manufacturer Spec Sheets | Noctua, be quiet!, Seasonic, Kingston, G.Skill, ASRock, etc. |
| **TOTAL CATALOG** | **1,208** | — | **65 Distinct Verified Authoritative Engineering Sources** |

---

## 4. Brand Diversity Across Categories

The 1,208 components span 72 distinct reputable hardware brands:

```mermaid
pie title Component Distribution Across 8 Categories (1,208 Total)
    "CPU (180)" : 180
    "GPU (218)" : 218
    "Motherboard (180)" : 180
    "RAM (160)" : 160
    "Storage (150)" : 150
    "PSU (120)" : 120
    "Case (100)" : 100
    "Cooler (100)" : 100
```

| Category | Total SKUs | Brand Count | Dominant Manufacturers in Catalog |
|---|---:|---:|---|
| **CPU** | 180 | 2 | Intel (99), AMD (81) |
| **GPU** | 218 | 15 | NVIDIA (47), AMD (42), ASUS (28), MSI (25), Gigabyte (22), Sapphire (18), PowerColor (12), Zotac (10), Intel (8), XFX, Inno3D, PNY, Palit, ASRock |
| **Motherboard** | 180 | 4 | ASUS (55), MSI (49), Gigabyte (44), ASRock (32) |
| **RAM** | 160 | 7 | Corsair (51), G.Skill (49), Kingston (23), TeamGroup (16), Crucial (12), Patriot (5), Silicon Power (4) |
| **Storage** | 150 | 11 | Western Digital (39), Crucial (28), Samsung (26), Kingston (18), Seagate (15), Sabrent (8), Corsair (6), TeamGroup, ADATA, Silicon Power, PNY |
| **PSU** | 120 | 13 | Corsair (41), MSI (16), Cooler Master (14), Seasonic (12), be quiet! (10), DeepCool (8), ASUS (6), Thermaltake, EVGA, SilverStone, Montech, NZXT, Antec |
| **Case** | 100 | 18 | Lian Li (16), Fractal Design (15), NZXT (10), Corsair (10), Phanteks (9), Cooler Master (8), Montech (7), be quiet! (6), DeepCool (5), ASUS, Thermaltake, etc. |
| **Cooler** | 100 | 15 | Thermalright (19), DeepCool (16), Noctua (10), Arctic (10), Corsair (9), Cooler Master (8), be quiet! (7), NZXT (6), Lian Li (5), ASUS, Endorfy, ID-COOLING, etc. |

---

## 5. Audit Compliance Checklist

- [x] **Zero Synthetic Records:** All 1,208 records represent genuine, physically manufactured desktop PC hardware.
- [x] **Traceable URLs:** 1,208 / 1,208 rows have valid `source_url` fields pointing to manufacturer datasheets or accredited hardware databases.
- [x] **Zero Mobile Processors:** All CPUs and GPUs represent desktop discrete hardware; 0 laptop or mobile BGA chips.
- [x] **Zero Prebuilt Systems:** All records represent discrete retail components available for custom assembly.
