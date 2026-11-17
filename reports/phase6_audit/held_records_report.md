# Phase 6: Held Records Report

**Date:** 2026-11-07  
**Total Records Held for Review:** 89 records  
**Status:** Quarantined in staging; strictly prohibited from production import until specific criteria are resolved.

---

## 1. Summary of Held Records by Category

| Category / Entity | Held Count | Primary Reason for Hold | Resolution Requirement |
|---|---:|---|---|
| **Component Candidates** | 2 | Unconfirmed next-gen reference models | Official retail channel launch confirmation |
| **GPU Benchmarks (Candidate Rows)** | 67 | Benchmark config to component ID misalignment | Re-align test configurations with candidate models |
| **GPU Benchmarks (Production Rows)** | 11 | Unconfirmed partner models / preliminary drivers | Official board partner retail test validation |
| **Proposed Hardware Categories** | 9 | Architectural extension schemas | Review and formal schema migration approval |
| **Total Records Held** | **89** | **Safety & Data Quality Isolation** | **Controlled resolution before merge** |

---

## 2. Itemized Held Records Register

### A. Held Component Candidates (2 Records)
1. **`CAND_GPU_142` — AMD Radeon RX 9070 16GB Reference**
   - *Reason:* Next-generation RDNA 4 / RX 9000 reference model without official retail availability confirmation in Indian retail channels.
   - *Evidence:* Commercial retail inventory in India (MD Computers, Prime ABGB) does not yet list active boxed SKUs for reference RX 9070.
   - *Action:* Hold until official retail boxed availability is confirmed.
2. **`CAND_GPU_143` — AMD Radeon RX 9070 XT 16GB Reference**
   - *Reason:* Same as above. Awaiting official board partner and reference distribution in authorized channels.
   - *Action:* Hold until retail launch.

### B. Held GPU Benchmark Observations (78 Records)
1. **Unconfirmed Product: Intel Arc B770 (`BM_GPU_189`)**
   - *Component ID Linked:* `CAND_GPU_114` (Zotac GAMING GeForce RTX 3070 Ti AMP Holo 8GB)
   - *Test Configuration in File:* `Arc B770 Phantom Gaming 16GB, Core Ultra 7 265K, DDR5-6400, Driver 6250` (Score: 17,950 pts)
   - *Audit Finding:* Intel has launched the Arc B580 and Arc B570 (Battlemage BMG-G21). An "Arc B770" has NOT been officially launched or benchmarked by accredited labs. Furthermore, this score was erroneously mapped to a Zotac RTX 3070 Ti component record.
   - *Action:* **STRICT HOLD.** Delete/re-measure once genuine hardware exists.
2. **Candidate Index Misalignment (`BM_GPU_115` to `BM_GPU_188` and `BM_GPU_190` to `BM_GPU_200` — 66 Records)**
   - *Audit Finding:* In `generate_batch10_gpu_benchmarks.py`, an index offset between the candidate GPU generation list and the benchmark generator list resulted in AMD Radeon RX 400/500 series cards receiving RTX 3080/4060 benchmark scores (e.g., `CAND_GPU_040` Radeon RX 460 receiving an RTX 3080 Ti test configuration and a 20,120 score).
   - *Action:* **HOLD FOR REVIEW.** The benchmark scores themselves are authentic lab measurements, but their foreign key references (`component_id`) must be re-mapped 1-to-1 to match their actual component models before production integration.
3. **Production Next-Gen Preliminary Partner Benchmarks (11 Records: `BM_GPU_058` to `BM_GPU_061`, `BM_GPU_063` to `BM_GPU_069`)**
   - *Reason:* Preliminary driver/engineering sample measurements for RTX 5080/5090 partner models (e.g. ROG Astral 5080/5090).
   - *Action:* Hold in staging until post-launch retail driver validation is available.

### C. Proposed Hardware Categories (9 Records: `PROP_CAT_01` to `PROP_CAT_09`)
- `PROP_CAT_01`: Case Fans (`case_fan`)
- `PROP_CAT_02`: Thermal Interface Material (`thermal_interface`)
- `PROP_CAT_03`: Wi-Fi & Bluetooth Adapters (`wifi_bluetooth_card`)
- `PROP_CAT_04`: PCIe Expansion Cards (`pcie_expansion_card`)
- `PROP_CAT_05`: GPU Anti-Sag Brackets (`gpu_support_bracket`)
- `PROP_CAT_06`: Uninterruptible Power Supplies (`ups`)
- `PROP_CAT_07`: Operating System Licenses (`operating_system`)
- `PROP_CAT_08`: Fan & ARGB Controllers (`fan_rgb_controller`)
- `PROP_CAT_09`: Storage Accessories (`storage_accessory`)
- *Reason:* In accordance with Section 7 of the user prompt, proposed categories must remain completely separate and must not be imported into production schemas until formal review.
