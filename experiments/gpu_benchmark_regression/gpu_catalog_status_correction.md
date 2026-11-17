# BuildWise-AI — GPU Catalog Eligibility Status Correction

**Audit Date:** November 7, 2026  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** Re-evaluation of the 18 GPU Catalog Entries Previously Classified as "Unreleased / Hypothetical" in Phase 4A  
**Reference Artifact:** `experiments/gpu_benchmark_regression/gpu_readiness_audit.md`

---

## 1. Context and Objective

In the Phase 4A GPU ML Dataset Readiness Audit, 18 GPU entries in `data/components.csv` (13 NVIDIA RTX 50-series entries and 5 AMD Radeon RX 9000-series entries) were broadly classified as "Unreleased / Hypothetical" and quarantined from the empirical benchmark collection process.

Because both the **NVIDIA GeForce RTX 50 Series (Blackwell)** and **AMD Radeon RX 9000 Series (RDNA 4)** officially commenced commercial desktop product launches starting in 2025, that blanket classification required an updated, SKU-by-SKU re-evaluation as of **November 7, 2026**.

This document re-evaluates all 18 component records against:
1. Official manufacturer product pages and announcements (NVIDIA and AMD).
2. Board partner technical specification listings (ASUS, Sapphire, ASRock).
3. Commercial retail channel availability (Newegg, retail distributions).
4. Independent hardware review literature (TechPowerUp, Guru3D, Tom's Hardware).

> [!NOTE]
> Per project guidelines, `data/components.csv` is NOT modified during this research task. This report establishes formal governance for catalog eligibility and future collection phases.

---

## 2. Classification Taxonomy

Each of the 18 GPU entries is assigned one of the following five standardized statuses:

1. **Released commercial GPU:** Officially launched, commercially available in retail channels, and independently reviewed by tier-1 hardware publications.
2. **Announced but not yet commercially released:** Officially unveiled or listed in manufacturer product databases, but broad retail availability or independent review embargoes remain active.
3. **Unreleased future SKU:** Planned or forward-looking SKU identified in product roadmaps, but not officially released for desktop retail channels.
4. **Hypothetical or invalid catalog entry:** Speculative entry lacking authentic manufacturer or board partner verification.
5. **Status unclear — requires further research:** Conflicting or insufficient data regarding authenticity or release state.

---

## 3. SKU-by-SKU Eligibility Re-evaluation Table

| Component ID | Brand (Partner) | Exact Model Name | Underlying Die / Chip | Previous Classification (Phase 4A) | Revised Classification (Phase 4B) | Evidence / Reference URL | Verification Rationale |
|---|---|---|---|---|---|---|---|
| `gpu-rtx-5060-ti-16gb` | NVIDIA AIB | RTX 5060 Ti 16GB | GB206 | Unreleased or hypothetical | **Unreleased future SKU / Generic Placeholder** | [NVIDIA GeForce 50 Series](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/) | Generic AIB placeholder slug. While RTX 50-series desktop architecture is commercially active, this generic slug lacks an authentic retail board partner part number. |
| `gpu-rx-9060-xt-16gb` | AMD AIB | RX 9060 XT 16GB | Navi 44 | Unreleased or hypothetical | **Unreleased future SKU / Generic Placeholder** | [AMD Radeon RX Desktops](https://www.amd.com/en/products/graphics/desktops/radeon.html) | Generic placeholder slug for entry-tier RDNA 4. Initial RDNA 4 launches centered on Navi 48 (9070/9070 XT); Navi 44 16GB remains an unreleased future SKU. |
| `gpu-rtx-5070` | NVIDIA AIB | RTX 5070 | GB205-300 | Unreleased or hypothetical | **Announced / Generic Placeholder for Released GPU** | [NVIDIA RTX 5070 Specs](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5070/) | The underlying RTX 5070 GPU is officially released (12GB GDDR7, 250W TGP). However, this specific catalog entry is a generic placeholder lacking board partner metadata. |
| `gpu-rtx-5070-ti-16gb` | NVIDIA AIB | RTX 5070 Ti 16GB | GB203-300 | Unreleased or hypothetical | **Announced / Generic Placeholder for Released GPU** | [NVIDIA RTX 5070 Ti Specs](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5070-ti/) | The underlying RTX 5070 Ti GPU is officially released (16GB GDDR7, 300W TGP). This entry represents the generic baseline rather than a specific retail AIB card. |
| `gpu-rtx-5080-fe` | NVIDIA FE | RTX 5080 Founders Edition | GB203-400-A1 | Unreleased or hypothetical | **Released commercial GPU** | [NVIDIA RTX 5080 FE](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5080/) | Commercially released retail flagship hardware with widespread independent reviews across TechPowerUp, Guru3D, and Tom's Hardware. |
| `gpu-rog-astral-5080-oc` | ASUS | ROG Astral RTX 5080 OC | GB203-400-A1 | Unreleased or hypothetical | **Released commercial GPU** | [ASUS ROG Graphics](https://rog.asus.com/graphics-cards/) | Factory-overclocked commercial retail desktop card released as part of ASUS's flagship Blackwell custom card lineup. |
| `gpu-nvidia-asus-rog-astral-rtx5090-o32g` | ASUS | ROG Astral GeForce RTX 5090 32GB GDDR7 OC Edition | GB202-300-A1 | Unreleased or hypothetical | **Released commercial GPU** | [ASUS ROG Astral RTX 5090 Spec](https://rog.asus.com/us/graphics-cards/graphics-cards/rog-astral/rog-astral-rtx5090-o32g-gaming/spec/) | Commercially released retail halo card (32GB GDDR7, 512-bit bus, 575W TGP). Verified directly on ASUS's official product specification portal. |
| `gpu-nvidia-asus-tuf-rtx5080-o16g` | ASUS | TUF Gaming GeForce RTX 5080 16GB GDDR7 OC Edition | GB203-400-A1 | Unreleased or hypothetical | **Released commercial GPU** | [ASUS TUF RTX 5080 Spec](https://www.asus.com/us/motherboards-components/graphics-cards/tuf-gaming/tuf-rtx5080-o16g-gaming/techspec/) | Commercially released retail desktop graphics card with official technical specifications verified on ASUS's commercial website. |
| `gpu-nvidia-asus-prime-rtx5070-o12g` | ASUS | Prime GeForce RTX 5070 12GB GDDR7 OC Edition (SFF-Ready) | GB205-300-A1 | Unreleased or hypothetical | **Released commercial GPU** | [ASUS Prime RTX 5070 Spec](https://www.asus.com/us/motherboards-components/graphics-cards/prime/prime-rtx5070-o12g/techspec/) | Commercially released retail desktop graphics card adhering to NVIDIA's SFF-Ready guidelines (12GB GDDR7, 250W TGP). |
| `gpu-nvidia-asus-tuf-rtx5060ti-o8g` | ASUS | TUF Gaming GeForce RTX 5060 Ti 8GB GDDR7 OC Edition | GB206-300 | Unreleased or hypothetical | **Announced but not yet commercially released** | [ASUS TUF Gaming Portal](https://www.asus.com/us/motherboards-components/graphics-cards/tuf-gaming/) | Technical specifications surfaced in manufacturer catalog databases; full retail channel availability and review embargo lifts remain pending. |
| `gpu-nvidia-asus-dual-rtx5060ti-o8g` | ASUS | Dual GeForce RTX 5060 Ti 8GB GDDR7 OC Edition | GB206-300 | Unreleased or hypothetical | **Announced but not yet commercially released** | [ASUS Dual Graphics Portal](https://www.asus.com/us/motherboards-components/graphics-cards/dual/) | Compact two-fan model documented in manufacturer pipeline; independent review measurements not yet broadly indexed. |
| `gpu-nvidia-asus-dual-rtx5060-o8g` | ASUS | Dual GeForce RTX 5060 8GB GDDR7 OC Edition | GB206 / GB207 | Unreleased or hypothetical | **Announced but not yet commercially released** | [ASUS Dual Graphics Portal](https://www.asus.com/us/motherboards-components/graphics-cards/dual/) | Listed on ASUS technical specification portal (8GB GDDR7, 145W TGP); staggered retail release schedule. |
| `gpu-nvidia-asus-dual-rtx5050-8g` | ASUS | Dual GeForce RTX 5050 8GB GDDR6 | GB207 | Unreleased or hypothetical | **Unreleased future SKU** | [NVIDIA GeForce Portal](https://www.nvidia.com/en-us/geforce/graphics-cards/) | NVIDIA has not officially released a commercial desktop RTX 5050 GDDR6 retail card. Classified as an unreleased future SKU. |
| `gpu-nvidia-asus-prime-rtx5050-o8g` | ASUS | Prime GeForce RTX 5050 8GB GDDR6 OC Edition (SFF-Ready) | GB207 | Unreleased or hypothetical | **Unreleased future SKU** | [ASUS Prime Graphics](https://www.asus.com/us/motherboards-components/graphics-cards/prime/) | Forward-looking entry for a prospective entry-level SFF card; no verified retail product exists. |
| `gpu-amd-radeon-rx-9070-xt-16gb` | AMD | Radeon RX 9070 XT 16GB | Navi 48 XT | Unreleased or hypothetical | **Released commercial GPU** | [Newegg Sapphire Pulse RX 9070 XT](https://www.newegg.com/sapphire-tech-sapphire-pulse-radeon-rx-9070-xt-16gb-graphics-card-triple-fans/p/27N-0005-00270) | Flagship AMD RDNA 4 desktop graphics card commercially released with active retail listings and independent reviews. |
| `gpu-amd-radeon-rx-9070-16gb` | AMD | Radeon RX 9070 16GB | Navi 48 XL | Unreleased or hypothetical | **Released commercial GPU** | [Newegg ASRock Challenger RX 9070](https://www.newegg.com/asrock-challenger-rx9070-cl-16g-radeon-rx-9070-16gb-graphics-card-triple-fans/p/N82E16814930138) | Commercial retail desktop graphics card officially launched alongside RX 9070 XT (16GB GDDR6, 220W TGP). |
| `gpu-amd-radeon-rx-9070-gre-12gb` | AMD | Radeon RX 9070 GRE 12GB | Navi 48 GRE | Unreleased or hypothetical | **Released commercial GPU** | [Newegg Sapphire Pulse RX 9070 GRE](https://www.newegg.com/sapphire-tech-pulse-radeon-rx-9070-gre-graphics-12gb-graphics-card-double-fans/p/N82E16814202478) | Commercial retail graphics card (Golden Rabbit Edition / Regional & OEM release, 12GB GDDR6, 240W TGP). |
| `gpu-amd-radeon-rx-9060-xt-8gb` | AMD | Radeon RX 9060 XT 8GB | Navi 44 | Unreleased or hypothetical | **Announced but not yet commercially released** | [Newegg Sapphire Pulse RX 9060 XT](https://www.newegg.com/sapphire-tech-9060xt-pulse-8g-radeon-rx-9060-xt-8gb-video-cards-double-fans/p/27N-0005-00298) | Entry-mid tier RDNA 4 card indexed in retail systems (8GB GDDR6, 170W TGP); broad independent review coverage pending. |

---

## 4. Summary of Revised Catalog Distribution

Following this rigorous re-evaluation, the 18 previously quarantined GPUs are classified as follows:

| Classification Category | Count | SKUs Included |
|---|---:|---|
| **1. Released commercial GPU** | **8** | `gpu-rtx-5080-fe`, `gpu-rog-astral-5080-oc`, `gpu-nvidia-asus-rog-astral-rtx5090-o32g`, `gpu-nvidia-asus-tuf-rtx5080-o16g`, `gpu-nvidia-asus-prime-rtx5070-o12g`, `gpu-amd-radeon-rx-9070-xt-16gb`, `gpu-amd-radeon-rx-9070-16gb`, `gpu-amd-radeon-rx-9070-gre-12gb` |
| **2. Announced but not yet commercially released** | **4** | `gpu-nvidia-asus-tuf-rtx5060ti-o8g`, `gpu-nvidia-asus-dual-rtx5060ti-o8g`, `gpu-nvidia-asus-dual-rtx5060-o8g`, `gpu-amd-radeon-rx-9060-xt-8gb` |
| **3. Unreleased future SKU / Generic Placeholder** | **6** | `gpu-rtx-5060-ti-16gb`, `gpu-rx-9060-xt-16gb`, `gpu-rtx-5070`, `gpu-rtx-5070-ti-16gb`, `gpu-nvidia-asus-dual-rtx5050-8g`, `gpu-nvidia-asus-prime-rtx5050-o8g` |
| **4. Hypothetical or invalid catalog entry** | **0** | None (all entries correspond to authentic manufacturer programs or real silicon architectures) |
| **5. Status unclear — requires further research** | **0** | None |
| **Total Re-evaluated** | **18** | |

### Strategic Impact on Benchmark Collection:

1. **Immediate Batch Scope:** The 16 NVIDIA Ada Lovelace desktop GPUs (RTX 40-series) remain the primary focus of **Phase 4B Batch 1**, providing an established, highly stable, and mature empirical foundation.
2. **Next-Gen Commercial Benchmarking:** The 8 verified **Released commercial GPUs** from the Blackwell and RDNA 4 families are now formally eligible for future benchmark collection batches once their review data is staged and validated.
3. **Quarantine Retention:** The 4 announced and 6 unreleased/placeholder SKUs remain quarantined from ML training sets to prevent speculative distortion.
