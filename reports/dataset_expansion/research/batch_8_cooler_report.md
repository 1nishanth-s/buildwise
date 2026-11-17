# Batch 8: CPU Coolers Expansion Research Report

**Date:** 2026-11-07  
**Category:** CPU Coolers (`cooler`)  
**Existing Production Coolers:** 23  
**Staged Candidates Added:** 77 (`CAND_COOLER_001` to `CAND_COOLER_077`)  
**New Category Total:** 100 coolers  

---

## 1. Executive Summary & Cooling Topography

This expansion scales the BuildWise-AI CPU cooler database from 23 to 100 components, introducing comprehensive coverage across low-profile SFF, budget single-towers, flagship dual-towers, and 120/240/280/360/420mm liquid AIO systems:

| Cooling Class | Staged Count | Representative Models |
|---|---|---|
| **Low-Profile / SFF (37mm - 69mm)** | 10 | Noctua NH-L9a-AM5 / NH-L9i-17xx, Thermalright AXP90-X47 / AXP90-X53 Full Copper / AXP120-X67, ID-Cooling IS-55 / IS-47-XT, DeepCool AN600, Scythe Big Shuriken 3 Rev. B, Thermalright Silver Soul 110 |
| **Single-Tower Air Coolers (120mm)** | 16 | Thermalright Assassin Spirit 120 EVO / Burst Assassin, DeepCool AG400 ARGB / AK400 Digital / AG400 Digital Plus, Noctua NH-U12S / NH-U12A / NH-U9S, be quiet! Pure Rock 2 / Shadow Rock 3, Cooler Master Hyper 212 Halo / 622 Halo, Scythe Mugen 6 / Kotetsu 3, ID-Cooling SE-224-XTS |
| **Heavyweight Dual-Tower Air Coolers** | 14 | Noctua NH-D15 G2 / NH-D12L, Thermalright Frost Commander 140 / Frost Tower 120 / Royal Knight 120, DeepCool AK620 Digital / AK620 Zero Dark / Assassin IV / Assassin 4S, be quiet! Dark Rock Pro 5 / Dark Rock Elite / Dark Rock 4, Scythe Fuma 3, Montech Metal DT24 Premium |
| **AIO Liquid Coolers (120mm & 240mm)** | 13 | Corsair H60x RGB Elite, DeepCool LE300 Marrs, Arctic Liquid Freezer III 240 & 240 A-RGB (38mm thick), DeepCool LS520 SE & LT520, NZXT Kraken 240 RGB & Kraken Elite 240, Corsair H100i RGB Elite, be quiet! Pure Loop 2 240, Lian Li Galahad II Trinity 240, ASUS TUF LC II 240, MSI MAG E240 |
| **AIO Liquid Coolers (280mm Enthusiast)** | 8 | Arctic Liquid Freezer III 280 & 280 A-RGB, NZXT Kraken 280 RGB & Kraken Elite 280, Corsair H115i RGB Elite, be quiet! Silent Loop 2 280 & Pure Loop 2 280, DeepCool LS520 280 SE |
| **AIO Liquid Coolers (360mm & 420mm Extreme)** | 16 | Arctic Liquid Freezer III 360 (Standard Black), DeepCool LT720 / LS720 SE / Mystique 360 (with TFT LCD), NZXT Kraken 360 RGB / Kraken Elite 360 (IPS LCD), Corsair H150i Capellix XT / iCUE LINK H150i, Lian Li Galahad II Trinity 360 / Performance / LCD 360, ASUS ROG Ryujin III 360, MSI CoreLiquid 360R V2, Arctic Liquid Freezer III 420 & 420 A-RGB, Corsair H170i Elite LCD XT |

---

## 2. Technical Validation & Socket Compatibility

Every candidate cooler records verified mechanical compatibility attributes:
- **Full Socket Mapping:** Verified mounting bracket support for Intel `LGA1700`, `LGA1851`, `LGA1200` and AMD `AM4`, `AM5`.
- **Physical Cooler Height:** Crucial for PC Case clearance checks in `src/compatibility.py`.
- **Radiator Thickness & Dimensions:** 27mm standard vs 38mm extra-thick Arctic radiators.
- **TDP Rating:** Accurate thermal headroom estimates from 65W (low profile) up to 350W (triple 140mm AIO).
- **Noise Levels & Fan RPM:** Direct manufacturer decibel ratings and airflow CFM values.

Zero identity or model collision with production catalog was verified.
