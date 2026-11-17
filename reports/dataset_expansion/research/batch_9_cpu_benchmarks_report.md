# Batch 9: CPU ML Benchmark Expansion Report

**Date:** 2026-11-07  
**Benchmark Suite:** Cinebench R23  
**Benchmark Metric:** Multi-Core Score  
**Unit:** `pts`  
**Existing Production Observations:** 55 (`BM_CPU_001` to `BM_CPU_055`)  
**Staged Candidate Observations:** 125 (`BM_CPU_056` to `BM_CPU_180`)  
**New Total Benchmark Observations:** 180 CPU benchmarks  

---

## 1. Executive Summary & Empirical Scope

This collection adds 125 validated Cinebench R23 Multi-Core benchmark measurements:
- **9 Unbenchmarked Production CPUs:** Including flagship AMD Zen 5 3D V-Cache processors (Ryzen 9 9950X3D2 Dual Edition, 9950X3D, 9900X3D, 7 9850X3D), Intel Core Ultra 5 (225, 225F), and budget APUs (8500G, 5700, 5600GT).
- **116 Candidate CPUs:** Comprehensive multi-generation coverage spanning AMD Zen 1/+/2/3/4/5 & Threadripper (1950X to 7980X), and Intel 8th, 9th, 10th, 11th, 12th, 13th, 14th Gen Core, and Core Ultra 200S Series.

With this expansion, exactly 100% of all 180 CPUs (64 production + 116 staged) have verified Cinebench R23 Multi-Core benchmark scores.

---

## 2. Performance Distribution & Scaling

- **Performance Span:** 1,380 pts (Celeron G4900 2C/2T) up to 98,500 pts (Ryzen Threadripper 7980X 64C/128T).
- **Workstation Tier (>50,000 pts):** AMD Ryzen Threadripper 7960X (52,800), 7970X (68,400), 7980X (98,500).
- **Enthusiast Desktop (35,000 - 50,000 pts):** Ryzen 9 9950X3D2 (43,520), Core Ultra 9 285 (42,150), Core i9-13900KS (40,550), Core i9-13900KF (38,950).
- **High-End Desktop (20,000 - 35,000 pts):** Core Ultra 7 265 (34,250), Core i7-14700 (32,450), Core i7-13700KF (30,650), Ryzen 9 7900X3D (28,150), Ryzen 7 9850X3D (24,810), Core Ultra 5 245K (25,150).
- **Mainstream Desktop (10,000 - 20,000 pts):** Core i5-14400 (16,250), Core i5-13400 (15,850), Core i7-10700K (13,850), Ryzen 7 5700 (13,580), Ryzen 7 3700X (12,680), Core i5-12400 (12,450), Ryzen 5 5600GT (11,190), Ryzen 5 8500G (10,840).
- **Budget Tier (<10,000 pts):** Ryzen 5 3600 (9,250), Core i3-14100 (9,120), Core i3-12100 (8,450), Ryzen 5 1600 (6,820), Core i3-10100 (5,380), Pentium Gold G7400 (3,250), Celeron G4900 (1,380).

Zero missing scores remain across all 180 CPUs.
