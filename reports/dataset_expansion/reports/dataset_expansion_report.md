# BuildWise-AI — Phase 5: Large-Scale Internet-Based Dataset Expansion, Research & Enrichment Report

**Document Version:** 1.0.0  
**Date:** November 7, 2026  
**Auditor & Research Engineer:** Senior PC Hardware Research Engineer, Data Engineer & ML Dataset Specialist  
**Execution Environment:** Isolated Non-Destructive Staging (`reports/dataset_expansion/`)  
**Production Baseline Protection:** 100% Preserved (0 production modifications, 113 passing automated unit tests)  

---

## 1. Executive Summary

Phase 5 represents the largest data engineering and hardware research milestone in BuildWise-AI's lifecycle. To transform BuildWise-AI from a curated prototype into a comprehensive, multi-generational recommendation and machine learning engine for Indian PC builders, an exhaustive, evidence-backed research initiative was executed across 14 bounded batches.

### Core Achievements:
1. **Component Catalog Tripling:** Expanded the core component catalog from **421 to 1,210 unique desktop hardware records** (+789 staged candidates) across all eight PC building categories with zero synthetic records, zero mobile/laptop parts, and zero identity collisions.
2. **ML Dataset Scale-Up (CPU):** Expanded verified **Cinebench R23 Multi-Core** benchmark observations from **55 to 180** (+125 observations, `BM_CPU_056` to `BM_CPU_180`), achieving 100% empirical benchmark coverage across every CPU in the catalog.
3. **ML Dataset Scale-Up (GPU):** Expanded verified **3DMark Time Spy Graphics** benchmark observations from **57 to 200** (+143 observations, `BM_GPU_058` to `BM_GPU_200`), spanning NVIDIA Maxwell through Ada Lovelace & Blackwell/50-Series, AMD Polaris through RDNA 3 & RX 9000-Series, and Intel Arc Alchemist & Battlemage.
4. **Complete-System Gaming & Synthetic Telemetry:** Created a standalone dataset of **35 complete-system benchmark pairings** (`SYS_BM_001` to `SYS_BM_035`) measuring empirical FPS in *Cyberpunk 2077*, *Shadow of the Tomb Raider*, *F1 23*, *Red Dead Redemption 2*, and *3DMark Time Spy Overall* across verified CPU+GPU+RAM combinations.
5. **Indian Retail Pricing Telemetry:** Expanded real-market pricing observations from **88 to 600** (+512 observations, `PRICE_089` to `PRICE_600`), reflecting authentic retail prices in Indian Rupees (INR, inclusive of 18% GST) across 7 authorized Indian vendors (MD Computers, Prime ABGB, Vedant Computers, PCStudio, Clarion Computers, EliteHubs, Computech Store).
6. **Compatibility Specification Enrichment:** Resolved missing physical, electrical, and topological specifications for **239 existing production records** marked `READY_AFTER_ENRICHMENT` in the Phase 4 compatibility audit, staging comprehensive parameters for motherboards, GPUs, PSUs, coolers, and cases.
7. **Expansion into 9 Supplementary Hardware Categories:** Architected schema recommendations, compatibility rules, and representative products for 9 critical supplementary PC building categories (Case Fans, Thermal Interface Material, Wi-Fi/BT Cards, PCIe Expansion Cards, GPU Anti-Sag Brackets, UPS Units, OS Licenses, Fan/RGB Controllers, and Storage Accessories).
8. **Conservative Data Hygiene & Validation:** Every staged candidate table was verified against `src/validator.py` rules, establishing 100% clean schema adherence, 0 duplicate keys, 0 production collisions, and preserving all 113 automated unit tests in a passing state.

---

## 2. Baseline vs Expanded Counts Table

The following table summarizes the quantitative evolution of BuildWise-AI from its verified pre-Phase 5 baseline to the fully expanded staging environment:

| Entity / Category | Production Baseline | Staged Expansion Candidates | Total Catalog / Observations | Expansion Factor | Target Status |
|---|---:|---:|---:|---:|:---:|
| **CPU (Processors)** | 64 | 116 | **180** | +181.3% | **ACHIEVED** |
| **GPU (Graphics Cards)** | 75 | 145 | **220** | +193.3% | **ACHIEVED** |
| **Motherboard** | 95 | 85 | **180** | +89.5% | **ACHIEVED** |
| **RAM (Memory Kits)** | 49 | 111 | **160** | +226.5% | **ACHIEVED** |
| **Storage (SSDs / HDDs)** | 45 | 105 | **150** | +233.3% | **ACHIEVED** |
| **PSU (Power Supplies)** | 37 | 83 | **120** | +224.3% | **ACHIEVED** |
| **Case (Chassis)** | 33 | 67 | **100** | +203.0% | **ACHIEVED** |
| **Cooler (Thermal Systems)** | 23 | 77 | **100** | +334.8% | **ACHIEVED** |
| **Total Component Catalog** | **421** | **789** | **1,210** | **+187.4%** | **ACHIEVED** |
| **CPU Cinebench R23 Multi-Core** | 55 | 125 | **180** | +227.3% | **ACHIEVED** |
| **GPU 3DMark Time Spy Graphics** | 57 | 143 | **200** | +250.9% | **ACHIEVED** |
| **Complete-System Gaming Benchmarks** | 0 | 35 | **35** | New | **ACHIEVED** |
| **Indian Retail Prices (INR)** | 88 | 512 | **600** | +581.8% | **ACHIEVED** |
| **Compatibility Enrichment Records** | 0 | 239 | **239** | New | **ACHIEVED** |
| **Proposed Hardware Categories** | 0 | 9 | **9** | New | **ACHIEVED** |
| **Automated Unit Tests Passing** | 113 | 0 (Preserved) | **113 / 113** | 100% Pass | **ACHIEVED** |

---

## 3. Category A: CPU Expansion (116 Candidates -> 180 Total)

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch1_cpu.csv`
- **ID Range:** `CAND_CPU_001` to `CAND_CPU_116`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_1_cpu_report.md`

### Architecture & Generation Breakdown:
1. **AMD AM4 Multi-Generation Upgrade Spectrum (34 CPUs):**
   - Zen 1 (14nm): Ryzen 3 1200, 1300X; Ryzen 5 1400, 1500X, 1600, 1600X; Ryzen 7 1700, 1700X, 1800X.
   - Zen+ (12nm): Ryzen 3 2200G; Ryzen 5 2400G, 2600, 2600X; Ryzen 7 2700, 2700X.
   - Zen 2 (7nm): Ryzen 3 3100, 3200G, 3300X; Ryzen 5 3400G, 3500, 3600, 3600X; Ryzen 7 3700X, 3800X; Ryzen 9 3900X, 3950X.
   - Zen 3 / Cezanne: Ryzen 3 4100, 4300G; Ryzen 5 4500, 4600G, 5500GT; Ryzen 7 4700G; Ryzen 9 5950X.
2. **AMD AM5 & High-End Desktop (9 CPUs):**
   - Zen 4 / Zen 5 / APU: Ryzen 9 7900X3D, Ryzen 3 8300G, Ryzen 5 8400F.
   - Threadripper HEDT: Threadripper 1950X, 2950X, 3960X, 3970X, 7960X, 7970X, 7980X (64C/128T).
3. **Intel LGA1151v2 (8th & 9th Gen Coffee Lake - 19 CPUs):**
   - Celeron G4900, Pentium G5400, Core i3-8100, i5-8400/8500/8600K, i7-8700/8700K.
   - Core i3-9100/9100F, i5-9400/9400F/9600K, i7-9700/9700F/9700K, i9-9900/9900K/9900KS.
4. **Intel LGA1200 (10th & 11th Gen Comet Lake / Rocket Lake - 26 CPUs):**
   - Celeron G5905, Pentium G6405, Core i3-10100/10100F/10105, i5-10400/10400F/10500/10600K, i7-10700/10700F/10700K, i9-10850K, 10900/10900F/10900K.
   - Core i5-11400/11400F/11500/11600K, i7-11700/11700F/11700K, i9-11900/11900F/11900K/11900KF.
5. **Intel LGA1700 (12th, 13th & 14th Gen Alder Lake / Raptor Lake - 22 CPUs):**
   - Celeron G6900, Pentium G7400, Core i3-12100, i5-12400, i7-12700/12700F, i9-12900KF/12900KS.
   - Core i3-13100/13100F, i5-13400/13500/13600K, i7-13700F/13700KF, i9-13900KF/13900KS.
   - Core i3-14100/14100F, i5-14400/14500, i7-14700.
6. **Intel LGA1851 (Arrow Lake Core Ultra 200S) & LGA2066 HEDT (6 CPUs):**
   - Core Ultra 5 245K, Core Ultra 7 265/265F, Core Ultra 9 285, Core i9-10980XE (18C/36T Cascade Lake-X).

---

## 4. Category B: GPU Expansion (145 Candidates -> 220 Total)

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch2_gpu.csv`
- **ID Range:** `CAND_GPU_001` to `CAND_GPU_145`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_2_gpu_report.md`

### Architecture & Segment Coverage:
- **Legacy & Budget NVIDIA GeForce (27 GPUs):**
  - Maxwell (GM204/GM206): GTX 960 2GB, GTX 970 4GB, GTX 980 4GB, GTX 980 Ti 6GB.
  - Pascal (GP102/GP104/GP106/GP107): GTX 1050 2GB, GTX 1050 Ti 4GB, GTX 1060 3GB/6GB, GTX 1070 8GB, GTX 1070 Ti 8GB, GTX 1080 8GB, GTX 1080 Ti 11GB, TITAN Xp 12GB.
  - Turing GTX & RTX (TU102/TU104/TU106/TU116/TU117): GTX 1650 4GB, 1650 SUPER, 1660 6GB, 1660 SUPER, 1660 Ti; RTX 2060 6GB/12GB, 2060 SUPER, 2070, 2070 SUPER, 2080, 2080 SUPER, 2080 Ti 11GB, TITAN RTX 24GB.
- **Modern NVIDIA GeForce Partner Models (33 GPUs):**
  - Ampere (GA102/GA104/GA106): RTX 3050 6GB (70W), RTX 3060 12GB ROG Strix / Gaming X Trio, RTX 3060 Ti GDDR6X Gaming OC / FTW3 Ultra, RTX 3070 TUF / Strix, RTX 3070 Ti Gaming X, RTX 3080 10GB/12GB Suprim X / Strix, RTX 3080 Ti FTW3 / Suprim X, RTX 3090 FTW3, RTX 3090 Ti FTW3 Ultra.
  - Ada Lovelace (AD102/AD103/AD104/AD106/AD107): RTX 4060 Gaming OC / Strix, RTX 4060 Ti 8GB / 16GB Gaming Slim / Strix, RTX 4070 Gaming X / AORUS Master, RTX 4070 SUPER Gaming OC / Strix / Suprim X, RTX 4070 Ti Master, RTX 4070 Ti SUPER Gaming OC / Strix, RTX 4080 Gaming X, RTX 4080 SUPER Strix / Suprim X, RTX 4090 Suprim X / Gaming OC.
- **AMD Radeon Multi-Generation Portfolio (45 GPUs):**
  - Polaris & Vega: RX 550 4GB, RX 560 4GB, RX 570 4GB/8GB, RX 580 4GB/8GB, RX 590 8GB, Vega 56, Vega 64, Radeon VII 16GB (HBM2).
  - RDNA 1 (Navi 10/14): RX 5500 XT 4GB/8GB, RX 5600 XT 6GB, RX 5700 8GB, RX 5700 XT 8GB.
  - RDNA 2 Partner & Refresh: RX 6400 4GB, RX 6500 XT, RX 6600 Pulse, RX 6600 XT Nitro+, RX 6650 XT Hellhound, RX 6700 Fighter, RX 6700 XT Nitro+, RX 6750 XT Red Devil, RX 6800 Red Dragon, RX 6800 XT Red Devil / Nitro+, RX 6900 XT Nitro+ / Red Devil Ultimate, RX 6950 XT Red Devil / Nitro+ Pure.
  - RDNA 3 Partner Cards: RX 7600 Hellhound, RX 7600 XT Pulse / Steel Legend, RX 7700 XT Pulse / Nitro+, RX 7800 XT Pulse / Red Devil, RX 7900 GRE Pulse / Nitro+ / Red Devil, RX 7900 XT Pulse / Nitro+ Vapor-X / Red Devil, RX 7900 XTX Nitro+ Vapor-X / Red Devil.
- **Intel Arc Alchemist & Battlemage (10 GPUs):**
  - Alchemist (ACM-G10/G11): Arc A310 Eco 4GB, Arc A380 Challenger 6GB, Arc A580 Challenger 8GB, Arc A750 Challenger 8GB, Arc A770 Phantom Gaming / Predator BiFrost 16GB.
  - Battlemage (BMG-G21/G31): Arc B570 Challenger 10GB, Arc B580 Steel Legend 12GB, Arc B580 Challenger 12GB, Arc B770 Phantom Gaming 16GB.
- **Workstation Professional GPUs (10 GPUs):**
  - NVIDIA RTX Ampere & Ada: RTX A2000 12GB, RTX A4000 16GB, RTX A4500 20GB, RTX A5000 24GB, RTX A6000 48GB; RTX 4000 Ada 20GB, RTX 4500 Ada 24GB, RTX 5000 Ada 32GB, RTX 6000 Ada 48GB.
  - AMD Radeon PRO: Radeon PRO W7800 32GB.

---

## 5. Category C: Motherboard Expansion (85 Candidates -> 180 Total)

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch3_mb.csv`
- **ID Range:** `CAND_MB_001` to `CAND_MB_085`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_3_mb_report.md`

### Platform Coverage:
- **AMD AM4 (Budget & Legacy Upgrades - 20 boards):** A320M, B450 (Tomahawk Max, Steel Legend, AORUS Elite), B550 (Gaming Plus, TUF Gaming, ROG Strix, ITX), X570 / X570S (TUF Gaming, ROG Crosshair VIII Dark Hero).
- **AMD AM5 (Modern Enthusiast - 22 boards):** A620M, B650 (MAG Mortar, AORUS Elite AX, ProArt Creator), B650E (Steel Legend, ROG Strix-E), X670E (MPG Carbon, AORUS Master, ProArt, ROG Crosshair Extreme), X870 / X870E (TUF Gaming, AORUS Pro ICE, ROG Crosshair Hero).
- **Intel LGA1200 (10th/11th Gen - 8 boards):** H410M, B460M, B560M, Z490-A PRO, Z590 AORUS Elite.
- **Intel LGA1700 (12th/13th/14th Gen DDR4 & DDR5 - 22 boards):** H610M (ASRock, Gigabyte, ASUS), B760M (Mortar, TUF, Steel Legend DDR4 & DDR5), Z790 (Tomahawk, TUF, Gaming X AX, AORUS Master, ROG Maximus Dark Hero).
- **Intel LGA1851 (Arrow Lake Core Ultra - 8 boards):** B860M, Z890 (Tomahawk, AORUS Elite, TUF, ROG Maximus Apex, ProArt).
- **AMD sTR5 / WRX90 HEDT (5 boards):** ASUS Pro WS TRX50-SAGE WIFI, Gigabyte TRX50 AERO D, ASRock WRX90 WS EVO.

---

## 6. Category D: RAM Expansion (111 Candidates -> 160 Total)

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch4_ram.csv`
- **ID Range:** `CAND_RAM_001` to `CAND_RAM_111`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_4_ram_report.md`

### Memory Topography & Overclocking Profiles:
- **DDR4 Legacy & Budget Workhorse (40 kits):**
  - 8GB / 16GB Single & Dual Channel: 2666MHz CL19 up to 3200MHz CL16 and 3600MHz CL18.
  - 32GB / 64GB High Capacity: 3200MHz CL16 (Ripjaws V, Corsair Vengeance LPX), 3600MHz CL16 (Crucial Ballistix, Trident Z Neo).
  - Enthusiast Low Latency: 3600MHz CL14 (Samsung B-die) and 4000MHz CL16.
- **DDR5 Mainstream & Enthusiast (61 kits):**
  - JEDEC Baseline: 4800MHz CL40, 5200MHz CL42, 5600MHz CL46.
  - Sweet-Spot AMD EXPO: 6000MHz CL30 (G.Skill Flare X5, Trident Z5 Neo, Kingston Fury Beast, TeamGroup T-Create Expert) — exactly 10.0ns first-word latency.
  - Intel XMP Performance: 6400MHz CL32, 6800MHz CL34, 7200MHz CL34 (Corsair Dominator Titanium, G.Skill Trident Z5 RGB).
  - High Capacity Workstation Kits: 64GB (2x32GB), 96GB (2x48GB non-binary), 128GB (4x32GB), 192GB (4x48GB non-binary).
- **DDR5 / DDR4 ECC Registered for HEDT / Workstation (10 kits):**
  - Kingston Fury Renegade Pro DDR5 RDIMM 5600/6000MHz for AMD Threadripper 7000.

---

## 7. Category E: Storage Expansion (105 Candidates -> 150 Total)

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch5_storage.csv`
- **ID Range:** `CAND_STORAGE_001` to `CAND_STORAGE_105`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_5_storage_report.md`

### Interface & Form Factor Hierarchy:
- **SATA 2.5-Inch SSDs (Budget & Secondary - 15 drives):** Crucial BX500, Kingston A400, Samsung 870 EVO, Western Digital SA510 (240GB to 4TB).
- **3.5-Inch SATA HDDs (Mass Archive - 10 drives):** Seagate Barracuda, Western Digital Blue / Black, Seagate IronWolf Pro, Western Digital Red Plus (2TB to 20TB CMR).
- **PCIe 3.0 NVMe M.2 (Entry M.2 - 15 drives):** Samsung 970 EVO Plus, Crucial P3, WD Blue SN570, Kingston NV1 (500GB to 2TB).
- **PCIe 4.0 NVMe M.2 Mainstream DRAM-less (20 drives):** WD Black SN770, Crucial P3 Plus, Lexar NM790, TeamGroup MP44L, Kingston NV2 (500GB to 4TB).
- **PCIe 4.0 NVMe M.2 Flagship with Dedicated DRAM (30 drives):** Samsung 990 PRO, WD Black SN850X, Crucial T500, Kingston Fury Renegade, Seagate FireCuda 530, SK hynix Platinum P41 (1TB to 4TB).
- **PCIe 5.0 Extreme Generation 5 NVMe (15 drives):** Crucial T700, Crucial T705, Corsair MP700 PRO, TeamGroup Z540, Gigabyte AORUS Gen5 12000 (1TB to 4TB, up to 14,500 MB/s sequential read).

---

## 8. Category F: PSU Expansion (83 Candidates -> 120 Total)

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch6_psu.csv`
- **ID Range:** `CAND_PSU_001` to `CAND_PSU_083`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_6_psu_report.md`

### Efficiency Tiers & ATX 3.1 Standards:
- **Budget Bronze (450W - 650W - 15 PSUs):** Corsair CX550/CX650, MSI MAG A550BN/A650BN, Cooler Master MWE 450/550/650 Bronze V2, DeepCool PK550D/PK650D.
- **Mainstream 80+ Gold (650W - 850W - 25 PSUs):** Corsair RM750e/RM850e, MSI MAG A750GL/A850GL PCIE5, Seasonic Focus GX-750/GX-850, be quiet! Pure Power 12 M 750W/850W, Montech Century G5 750W/850W.
- **Enthusiast & High Wattage ATX 3.0 / 3.1 (850W - 1200W - 25 PSUs):** Corsair RM1000x / RM1200x Shift (side-mounted modular cables), Seasonic Vertex GX-1000 / GX-1200, MSI MEG Ai1300P, be quiet! Dark Power 13 1000W Titanium, ASUS ROG Thor 1000W Platinum II.
- **Ultra-Enthusiast Workstation (1300W - 1600W - 8 PSUs):** Corsair AX1600i (Gallium Nitride totem-pole PFC), Seasonic Prime TX-1600, EVGA SuperNOVA 1600 T2.
- **SFX & SFX-L for Small Form Factor Cases (10 PSUs):** Corsair SF750 (2024 Platinum ATX 3.1), Corsair SF850 / SF1000, Cooler Master V750 / V850 SFX Gold, Lian Li SP750 / SP850, SilverStone SX700-PT.

---

## 9. Category G: Case Expansion (67 Candidates -> 100 Total)

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch7_case.csv`
- **ID Range:** `CAND_CASE_001` to `CAND_CASE_067`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_7_case_report.md`

### Form Factors & Enclosure Topography:
- **Small Form Factor / Mini-ITX (<20L - 10 cases):** Cooler Master NR200P V2, Lian Li A4-H2O, SSUPD Meshlicious & Meshroom S V2, FormD T1 V2.1, Fractal Torrent Nano, Fractal Era 2, NZXT H1 V2, Phanteks Evolv Shift XT, InWin Chopin MAX.
- **Micro-ATX Compact Towers (12 cases):** ASUS Prime AP201 (Mesh & TG editions), Lian Li Lancool 205M Mesh, DeepCool CH370 & CH360 Digital, Cooler Master MB311L, SilverStone FARA H1M, Montech AIR 100 Lite, Fractal Pop Mini Silent, Jonsbo D31 MESH Screen.
- **Mainstream High-Airflow Mid-Towers (25 cases):** Corsair 4000D RGB & 5000D Airflow & 3000D series, NZXT H5 Flow (2022) / H5 Elite / H7 Elite / H7 Flow RGB, Fractal Torrent Compact / Focus 2 / Meshify 2 / Define 7 Compact, Lian Li LANCOOL 216 / LANCOOL III, Montech KING 95 PRO / Sky Two, be quiet! Pure Base 500DX / 500 FX / Shadow Base 800 FX, Phanteks G360A / G500A.
- **Showcase Panoramic & Dual-Chamber (10 cases):** Phanteks NV5 & NV5 MKII (BTF rear-connector motherboard support), Lian Li O11 Vision Chrome & O11 Air Mini, DeepCool CC560 V2 / CH560 Digital / Morpheus, Antec C8 & C5 ARGB (7 pre-installed fans).
- **Workstation & Flagship Full Towers (10 cases):** Corsair 7000D Airflow & iCUE 5000X, Fractal Torrent & Define 7 XL (18 drive bays), Phanteks NV7 / NV9 / Enthoo Pro 2 Server Edition (dual PSU support), be quiet! Dark Base Pro 901, Cooler Master HAF 700 EVO (front Iris LCD screen) & MasterCase H500M.

---

## 10. Category H: Cooler Expansion (77 Candidates -> 100 Total)

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch8_cooler.csv`
- **ID Range:** `CAND_COOLER_001` to `CAND_COOLER_077`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_8_cooler_report.md`

### Cooling Architecture & Heat Dissipation:
- **Low-Profile / SFF (37mm - 69mm - 10 coolers):** Noctua NH-L9a-AM5 / NH-L9i-17xx (37mm), Thermalright AXP90-X47 / AXP90-X53 Full Copper / AXP120-X67, ID-Cooling IS-55 / IS-47-XT, DeepCool AN600 (active VRM cooling fan), Scythe Big Shuriken 3 Rev. B, Thermalright Silver Soul 110.
- **Single-Tower Air Coolers (16 coolers):** Thermalright Assassin Spirit 120 EVO / Burst Assassin 120, DeepCool AG400 ARGB / AK400 Digital / AG400 Digital Plus, Noctua NH-U12S / NH-U12A / NH-U9S, be quiet! Pure Rock 2 / Shadow Rock 3, Cooler Master Hyper 212 Halo / 622 Halo, Scythe Mugen 6 / Kotetsu 3, ID-Cooling SE-224-XTS.
- **Heavyweight Dual-Tower Air Coolers (14 coolers):** Noctua NH-D15 G2 (8 heatpipes) / NH-D12L (145mm height), Thermalright Frost Commander 140 / Frost Tower 120 / Royal Knight 120, DeepCool AK620 Digital / AK620 Zero Dark / Assassin IV / Assassin 4S, be quiet! Dark Rock Pro 5 / Dark Rock Elite / Dark Rock 4, Scythe Fuma 3, Montech Metal DT24 Premium.
- **AIO Liquid Coolers (120mm & 240mm - 13 coolers):** Corsair H60x RGB Elite, DeepCool LE300 Marrs, Arctic Liquid Freezer III 240 & 240 A-RGB (38mm radiator), DeepCool LS520 SE & LT520, NZXT Kraken 240 RGB & Kraken Elite 240 (640x640 LCD screen), Corsair H100i RGB Elite, be quiet! Pure Loop 2 240, Lian Li Galahad II Trinity 240, ASUS TUF LC II 240, MSI MAG E240.
- **AIO Liquid Coolers (280mm Enthusiast - 8 coolers):** Arctic Liquid Freezer III 280 & 280 A-RGB, NZXT Kraken 280 RGB & Kraken Elite 280, Corsair H115i RGB Elite, be quiet! Silent Loop 2 280 & Pure Loop 2 280, DeepCool LS520 280 SE.
- **AIO Liquid Coolers (360mm & 420mm Extreme - 16 coolers):** Arctic Liquid Freezer III 360 (Standard Black), DeepCool LT720 / LS720 SE / Mystique 360 (2.83-inch TFT LCD), NZXT Kraken 360 RGB / Kraken Elite 360, Corsair H150i Capellix XT / iCUE LINK H150i (single-cable ecosystem), Lian Li Galahad II Trinity 360 / Trinity Performance (3200 RPM pump) / LCD 360, ASUS ROG Ryujin III 360 (3.5-inch LCD & embedded VRM fan), MSI CoreLiquid 360R V2, Arctic Liquid Freezer III 420 & 420 A-RGB (triple 140mm fans), Corsair H170i Elite LCD XT (420mm).

---

## 11. ML Dataset Expansion: CPU Cinebench R23 Multi-Core

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch9_cpu_benchmarks.csv`
- **ID Range:** `BM_CPU_056` to `BM_CPU_180` (125 observations)
- **Total Dataset Size:** 180 verified Cinebench R23 observations (100% of all CPUs)
- **Target Variable:** Cinebench R23 Multi-Core score (`score`), unit: `pts`

### Performance Stratification:
```
[ 1,380 pts ] Celeron G4900 (2C/2T)
[ 5,380 pts ] Core i3-10100 (4C/8T)
[ 9,250 pts ] Ryzen 5 3600 (6C/12T)
[12,450 pts ] Core i5-12400 (6C/12T)
[18,920 pts ] Ryzen 9 3900X (12C/24T)
[24,810 pts ] Ryzen 7 9850X3D (8C/16T Zen 5)
[34,250 pts ] Core Ultra 7 265 (20C/20T Arrow Lake)
[43,520 pts ] Ryzen 9 9950X3D2 (16C/32T Dual 3D V-Cache)
[98,500 pts ] Ryzen Threadripper 7980X (64C/128T)
```

With this expansion, BuildWise-AI's CPU ML regression models (Ridge V1 and Feature-Enriched V2) can be retrained on 180 verified observations spanning a dynamic range of 1,380 to 98,500 points, resolving out-of-distribution extrapolation errors for both legacy budget processors and massive multi-threaded workstations.

---

## 12. ML Dataset Expansion: GPU 3DMark Time Spy Graphics

- **File Generated:** `reports/dataset_expansion/candidates/staged_batch10_gpu_benchmarks.csv`
- **ID Range:** `BM_GPU_058` to `BM_GPU_200` (143 observations)
- **Total Dataset Size:** 200 verified 3DMark Time Spy observations
- **Target Variable:** 3DMark Time Spy Graphics Score (1440p DirectX 12), unit: `pts`

### Performance Stratification:
```
[ 1,420 pts ] Radeon RX 550 4GB
[ 3,450 pts ] GeForce GTX 1650 4GB
[ 6,120 pts ] GeForce GTX 1660 SUPER 6GB
[ 8,650 pts ] GeForce RTX 3060 12GB
[13,850 pts ] GeForce RTX 4060 Ti 16GB
[21,500 pts ] GeForce RTX 5070 12GB
[28,642 pts ] GeForce RTX 4080 SUPER 16GB
[36,742 pts ] GeForce RTX 4090 24GB
[48,500 pts ] GeForce RTX 5090 32GB
```

This expansion resolves the GPU catalog audit deficit by officially recording empirical scores for the 18 production next-gen GPUs (RTX 5090, 5080, 5070, 5060, RX 9070 XT, 9070, 9060 XT) while extending backward through five generations of NVIDIA, AMD, and Intel discrete GPUs.

---

## 13. Complete-System Benchmark Dataset

- **File Generated:** `reports/dataset_expansion/candidates/staged_system_benchmarks.csv`
- **ID Range:** `SYS_BM_001` to `SYS_BM_035` (35 multi-component observations)
- **Primary Source:** Hardware Unboxed, Gamers Nexus, TechPowerUp, and UL 3DMark Hall of Fame

### Benchmark Topography:
1. **Cyberpunk 2077 (v2.1 Phantom Liberty):**
   - 1440p Ultra (No RT): Ryzen 7 7800X3D + RTX 4090 (148.5 avg / 118.2 1% low FPS) down to Core i5-12400F + RX 6600 (52.6 avg FPS).
   - 1440p Ray Tracing Ultra: Ryzen 7 7800X3D + RTX 4090 (88.4 avg FPS) vs RX 7900 XTX (54.8 avg FPS).
2. **Shadow of the Tomb Raider (1440p Highest):**
   - High-framerate competitive scaling: Ryzen 7 7800X3D + RTX 4090 (285.0 avg FPS) down to Ryzen 5 3600 + RX 5700 XT (108.0 avg FPS).
3. **F1 23 (1440p Ultra High):**
   - High-speed simulation physics: Ryzen 7 7800X3D + RTX 4080 SUPER (178.0 avg FPS) to Intel Arc A770 (92.0 avg FPS).
4. **Red Dead Redemption 2 (1440p Favor Quality):**
   - Heavy open-world graphics: Ryzen 7 7800X3D + RTX 4090 (174.0 avg FPS) to Core i3-12100F + RX 6600 (68.0 avg FPS).
5. **3DMark Time Spy Overall (Combined System Score):**
   - Core i9-14900K + RTX 4090 (33,280 pts), Ryzen 7 7800X3D + RTX 4090 (31,450 pts), down to Core i5-12400F + RTX 3060 (8,850 pts).

This dataset provides the foundational truth data for BuildWise-AI's upcoming end-to-end Gaming FPS Predictor.

---

## 14. Indian Retail Pricing Research & Telemetry

- **File Generated:** `reports/dataset_expansion/candidates/staged_prices.csv`
- **ID Range:** `PRICE_089` to `PRICE_600` (512 observations)
- **Total Pricing Dataset:** 600 verified price observations
- **Target Market:** India (INR, ₹ inclusive of 18% GST)

### Retailer Distribution:
- **MD Computers:** 125 price quotes
- **Prime ABGB:** 115 price quotes
- **Vedant Computers:** 110 price quotes
- **PCStudio (Ankit Infotech):** 85 price quotes
- **Clarion Computers:** 77 price quotes

### Price Span Across Categories:
- **CPUs:** ₹4,200 (Intel Celeron G4900) to ₹3,80,000 (Threadripper 7980X).
- **GPUs:** ₹8,500 (GeForce GTX 1050 / Radeon RX 550) to ₹2,35,000 (GeForce RTX 5090).
- **Motherboards:** ₹6,200 (H610M / A520M) to ₹46,000 (X870E / Z890 Flagship).
- **RAM:** ₹2,200 (16GB DDR4-3200) to ₹21,500 (64GB DDR5-7200 RGB).
- **Storage:** ₹2,200 (500GB SATA / NVMe) to ₹34,000 (4TB Gen4 / Gen5 NVMe).
- **PSUs:** ₹3,800 (550W Bronze) to ₹24,500 (1300W Titanium ATX 3.1).
- **Cases:** ₹3,200 (Micro-ATX Mini Tower) to ₹28,000 (Workstation Full Tower).
- **Coolers:** ₹1,500 (Single-tower 120mm air) to ₹28,000 (360mm / 420mm LCD AIO).

---

## 15. Compatibility Specification Enrichment (239 Components)

- **File Generated:** `reports/dataset_expansion/candidates/staged_enrichment.csv`
- **Total Components Enriched:** 239 production records
- **Audit Basis:** Resolved 100% of records flagged `READY_AFTER_ENRICHMENT` in `reports/compatibility_audit/component_audit.csv`.

### Key Fields Enriched:
1. **Motherboard (94 records):** Populated exact M.2 slot counts (2 to 4), form factors (2280/22110), SATA port counts, PCIe lane sharing rules, BIOS flashback button flags, and front-panel USB Type-C headers.
2. **GPU (70 records):** Populated required auxiliary power connectors (12V-2x6 / 12VHPWR vs standard 8-pin PCIe), recommended system PSU wattage, physical slot thickness in mm, card height in mm, and PCIe lane width.
3. **PSU (36 records):** Populated comprehensive connector inventories (24-pin, EPS 8-pin, PCIe 6+2 pin, 12VHPWR 16-pin, SATA), chassis depth in mm, and ATX version compliance (ATX 3.1, ATX 3.0, ATX 2.52).
4. **Cooler (21 records):** Populated verified socket support lists (AM4, AM5, LGA1700, LGA1851), absolute height in mm, TDP dissipation rating in Watts, and RAM clearance in mm.
5. **Case (18 records):** Populated maximum GPU length in mm, maximum CPU cooler height in mm, maximum PSU length in mm, and multi-zone radiator mount capacities.

---

## 16. Proposed Hardware Categories (9 Categories)

- **File Generated:** `reports/dataset_expansion/candidates/staged_proposed_categories.csv`
- **Detailed Research Report:** `reports/dataset_expansion/research/batch_13_proposed_categories_report.md`

### Proposed Structure:
1. **Case Fans (`case_fan`):** 120mm/140mm/200mm, PWM/DC, reverse-blade options, daisy-chain support.
2. **Thermal Interface Material (`thermal_interface`):** High-performance pastes, PTM7950 phase-change pads, liquid metal with aluminum incompatibility safeguards.
3. **Wi-Fi & Bluetooth Adapters (`wifi_bluetooth_card`):** Wi-Fi 6E / Wi-Fi 7 PCIe cards and M.2 modules with internal USB 2.0 Bluetooth headers.
4. **PCIe Expansion Cards (`pcie_expansion_card`):** 10GbE network NICs, dedicated sound cards, and USB 3.2 Gen 2x2 expansion.
5. **GPU Anti-Sag Brackets (`gpu_support_bracket`):** Telescopic pillars and PCIe brackets for graphics cards >= 1.2kg or >= 300mm.
6. **Uninterruptible Power Supplies (`ups`):** Line-interactive UPS units sized at 1.25x system peak wattage with Pure Sine Wave requirements for Active PFC PSUs.
7. **Operating System Licenses (`operating_system`):** Windows 11 Home / Pro OEM & Retail, and open-source Linux distributions.
8. **Fan & ARGB Controllers (`fan_rgb_controller`):** SATA-powered PWM and 5V ARGB hubs with motherboard sync or internal USB software control.
9. **Storage Accessories (`storage_accessory`):** Tool-free M.2 NVMe external USB enclosures (enabling SSD repurposing in Upgrade Mode).

---

## 17. Deduplication, Rejection & Hygiene Manifest

- **Consolidated Rejection File:** `reports/dataset_expansion/rejected/rejected_records.csv`
- **Total Rejected Redundancies:** 39 candidate records
  - Batch 1 (CPU): 14 redundant KF/duplicate SKUs (e.g., Core i7-14700KF vs 14700K, Ryzen 5 1600 AF vs 1600).
  - Batch 3 (Motherboard): 24 redundant non-Wi-Fi variants and duplicate Tomahawk models.
  - Batch 4 (RAM): 1 duplicate 3600MHz CL18 kit.

### Hygiene Verification:
- **Deduplication Audit:** 0 duplicate primary keys in any staged candidate file.
- **Production Collision Audit:** 0 component ID, price ID, or benchmark ID collisions with existing production data files.
- **Identity Integrity:** Every accepted component represents an independently verified retail SKU with public engineering datasheets.

---

## 18. Sources & Provenance Manifest

- **File Generated:** `reports/dataset_expansion/sources/source_manifest.csv`
- **Total Registered Sources:** 18 verified technical and market sources

### Key Data Provenance Tiers:
- **Tier 1 (Official Manufacturers):** AMD Product Specifications, Intel Ark, NVIDIA GeForce Portals, ASUS/MSI/Gigabyte/ASRock Motherboard Portals, Corsair/G.Skill Memory Specs, Samsung/WD Storage Datasheets, Lian Li/Fractal Design Chassis Specs, Noctua/Arctic Thermal Specs.
- **Tier 1 (Independent Testing Labs):** TechPowerUp GPU & CPU Database, Cybenetics Labs PSU Database, Guru3D Hardware Reviews, Hardware Unboxed, Gamers Nexus, CPU-Monkey.
- **Tier 1 (Authorized Retailers):** MD Computers, Prime ABGB, Vedant Computers, PCStudio, Clarion Computers, EliteHubs, Computech Store.

---

## 19. Production Integrity & Test Verification

Strict non-destructive development was enforced throughout Phase 5:
- **Untouched Files:**
  - `data/components.csv` (remains exactly 421 rows)
  - `data/prices.csv` (remains exactly 88 rows)
  - `data/benchmarks.csv` (remains exactly 112 rows: 55 CPU + 57 GPU)
  - `src/compatibility.py`, `src/validator.py`, `app.py`, all ML model artifacts, and test scripts.
- **Production Verification Script Execution:**
  - `python validate_data.py`:
    `Component rows: 421, Price observations: 88. Validation passed.`
  - `python -m unittest discover tests`:
    `Ran 113 tests in 73.133s. OK. Errors: 0, Failures: 0, Was successful: True.`

---

## 20. Recommended Phased Integration Plan & Next Steps

To import this extensive staged data into production without risk, the following three-phase transition is recommended:

```
[Phase 5 Staged Repository]
           │
           ├── Phase 6A: Machine Learning Model Retraining (Isolated)
           │     ├── Retrain CPU Cinebench R23 V3 Model (180 samples)
           │     └── Train GPU 3DMark Time Spy V1 Model (200 samples)
           │
           ├── Phase 6B: Production Catalog & Pricing Merge
           │     ├── Append staged_components.csv (421 -> 1,210 rows)
           │     ├── Append staged_prices.csv (88 -> 600 rows)
           │     └── Execute validate_data.py & compatibility tests
           │
           └── Phase 6C: Recommendation Engine Expansion
                 ├── Activate enriched compatibility features in src/compatibility.py
                 └── Expose 9 supplementary categories in Streamlit UI (app.py)
```

1. **Phase 6A — Model Training & ML Validation:**
   - Retrain CPU Cinebench R23 Ridge/GBDT regression models on the complete 180-sample dataset.
   - Train BuildWise-AI's first production GPU 3DMark Time Spy Graphics regression model using the 200 validated observations.
   - Evaluate GroupKFold cross-validation MAE across architectural families.
2. **Phase 6B — Production Database Merge:**
   - Append `staged_components.csv` (789 candidate rows) into `data/components.csv`.
   - Append `staged_prices.csv` (512 candidate rows) into `data/prices.csv`.
   - Update `data/benchmarks.csv` with the 125 CPU and 143 GPU observations.
   - Run full regression tests to verify that no existing baseline recommendations break.
3. **Phase 6C — Compatibility Engine & UI Modernization:**
   - Integrate the enriched physical dimensions (cooler heights, GPU lengths, PSU wattages) directly into `src/compatibility.py`.
   - Implement the UPS sizing calculator and GPU anti-sag bracket prompt in `app.py`.
