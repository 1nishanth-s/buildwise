# Phase 6: Rejected Records Report

**Date:** 2026-11-07  
**Total Records Formally Rejected:** 39 records  
**File Origin:** `reports/dataset_expansion/rejected/rejected_records.csv`  
**Hygiene Policy:** Strict deduplication, removal of redundant silicon clones, and elimination of non-differentiated SKUs.

---

## 1. Summary of Rejections by Category

| Category | Rejected Count | Dominant Rejection Reason | Verified Alternative Retained |
|---|---:|---|---|
| **CPU** | 14 | Redundant iGPU-disabled 'KF' variants; Duplicate silicon revisions | Retained primary 'K' models with active iGPU; Retained 1600 Zen 1 |
| **Motherboard** | 24 | Redundant non-Wi-Fi clones; Duplicate board partner models | Retained Wi-Fi enabled primary models; Replaced with MPG Carbon |
| **RAM** | 1 | Duplicate frequency/timing SKU (3600MHz CL18) | Retained primary Corsair Vengeance LPX 3600 CL18 SKU |
| **Total** | **39** | **Zero redundant duplicates permitted in production** | **100% catalog purity preserved** |

---

## 2. Complete Rejection Register

### Category A: CPUs (14 Rejected)
1. `Core i9-14900KF`: Redundant iGPU-disabled clone of Core i9-14900K (identical silicon). Retained: Core i9-14900K.
2. `Core i9-14900F`: Redundant iGPU-disabled clone of Core i9-14900. Retained: Core i9-14900.
3. `Core i7-14700KF`: Redundant iGPU-disabled clone of Core i7-14700K. Retained: Core i7-14700K.
4. `Core i5-14600KF`: Redundant iGPU-disabled clone of Core i5-14600K. Retained: Core i5-14600K.
5. `Core i9-13900F`: Redundant locked iGPU-disabled clone of Core i9-13900. Retained: Core i9-13900.
6. `Core i5-13600KF`: Redundant iGPU-disabled clone of Core i5-13600K. Retained: Core i5-13600K.
7. `Core i5-13400F`: Redundant clone of Core i5-13400. Retained: Core i5-13400.
8. `Core i9-12900F`: Redundant clone of Core i9-12900. Retained: Core i9-12900.
9. `Core i7-12700KF`: Redundant clone of Core i7-12700K. Retained: Core i7-12700K.
10. `Core i5-12600KF`: Redundant clone of Core i5-12600K. Retained: Core i5-12600K.
11. `Core i5-12400F`: Redundant clone of Core i5-12400. Retained: Core i5-12400.
12. `Core i3-12100F`: Redundant clone of Core i3-12100. Retained: Core i3-12100.
13. `Core i5-10600KF`: Redundant clone of Core i5-10600K. Retained: Core i5-10600K.
14. `Ryzen 5 1600 AF`: 12nm Zen+ refresh duplicate of Ryzen 5 1600/2600. Retained: Ryzen 5 1600 and Ryzen 5 2600.

### Category C: Motherboards (24 Rejected)
1. `ASUS PRIME B650-PLUS (Non-WiFi)`: Redundant non-Wi-Fi clone. Retained: ASUS TUF GAMING B650-PLUS WIFI.
2. `MSI PRO B650-P (Non-WiFi)`: Redundant non-Wi-Fi clone. Retained: MSI PRO B650-P WIFI.
3. `Gigabyte B650 GAMING X (Non-WiFi)`: Redundant non-Wi-Fi clone. Retained: Gigabyte B650 GAMING X AX.
4. `ASRock B650 Pro RS (Non-WiFi)`: Redundant non-Wi-Fi clone. Retained: ASRock B650 Pro RS WiFi.
5. `ASUS TUF GAMING B760-PLUS (Non-WiFi)`: Redundant clone. Retained: ASUS TUF GAMING B760-PLUS WIFI.
6. `MSI MAG B760 TOMAHAWK (Non-WiFi)`: Redundant clone. Retained: MSI MAG B760 TOMAHAWK WIFI.
7. `Gigabyte B760 GAMING X (Non-WiFi)`: Redundant clone. Retained: Gigabyte B760 GAMING X AX.
8. `ASRock B760 Pro RS (Non-WiFi)`: Redundant clone. Retained: ASRock B760 Pro RS WiFi.
9. `ASUS PRIME Z790-P (Non-WiFi)`: Redundant clone. Retained: ASUS PRIME Z790-P WIFI.
10. `MSI PRO Z790-P (Non-WiFi)`: Redundant clone. Retained: MSI PRO Z790-P WIFI.
11. `Gigabyte Z790 GAMING X (Non-WiFi)`: Redundant clone. Retained: Gigabyte Z790 GAMING X AX.
12. `ASRock Z790 Pro RS (Non-WiFi)`: Redundant clone. Retained: ASRock Z790 Pro RS WiFi.
13. `ASUS PRIME Z890-P (Non-WiFi)`: Redundant clone. Retained: ASUS PRIME Z890-P WIFI.
14. `MSI PRO Z890-P (Non-WiFi)`: Redundant clone. Retained: MSI PRO Z890-P WIFI.
15. `Gigabyte Z890 GAMING X (Non-WiFi)`: Redundant clone. Retained: Gigabyte Z890 GAMING X AX.
16. `ASRock Z890 Pro RS (Non-WiFi)`: Redundant clone. Retained: ASRock Z890 Pro RS WiFi.
17. `ASUS PRIME B860-PLUS (Non-WiFi)`: Redundant clone. Retained: ASUS PRIME B860-PLUS WIFI.
18. `MSI MAG B860 TOMAHAWK (Non-WiFi)`: Redundant clone. Retained: MSI MAG B860 TOMAHAWK WIFI.
19. `Gigabyte B860 GAMING X (Non-WiFi)`: Redundant clone. Retained: Gigabyte B860 GAMING X AX.
20. `ASRock B860 Pro RS (Non-WiFi)`: Redundant clone. Retained: ASRock B860 Pro RS WiFi.
21. `ASUS PRIME B850-PLUS (Non-WiFi)`: Redundant clone. Retained: ASUS PRIME B850-PLUS WIFI.
22. `Gigabyte B850 GAMING X (Non-WiFi)`: Redundant clone. Retained: Gigabyte B850 GAMING X AX.
23. `ASRock B850 Pro RS (Non-WiFi)`: Redundant clone. Retained: ASRock B850 Pro RS WiFi.
24. `MSI MAG X670E TOMAHAWK WIFI`: Collision with existing production record `DS3_MB_...`. Replaced in candidates with: `MSI MPG X670E CARBON WIFI`.

### Category D: RAM (1 Rejected)
1. `Corsair Vengeance LPX 16GB (2x8GB) DDR4 3600MHz CL18 (Duplicate SKU CMK16GX4M2D3600C18)`: Duplicate timing profile. Retained: `CMK16GX4M2Z3600C18`.
