# BuildWise-AI — GPU Catalog Release Status & Benchmark Evidence Addendum

**Audit Date:** November 7, 2026  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** Re-classification of the 18 Quarantined GPU Catalog Entries Across Independent Commercial and Benchmark Dimensions  
**Reference Artifact:** `experiments/gpu_benchmark_regression/gpu_catalog_status_correction.md`

---

## 1. Context and Objective

In Phase 4B, the 18 GPU entries previously quarantined in Phase 4A (13 NVIDIA RTX 50-series and 5 AMD Radeon RX 9000-series entries) were reviewed. To establish precise machine learning data governance, this addendum re-evaluates each entry across two independent, non-overlapping analytical axes:

1. **Commercial Status (Market Availability):**
   - **Released commercial product**: Officially launched by the silicon manufacturer and available in retail channels.
   - **Announced, not commercially released**: Formally unveiled by the manufacturer with specifications published, but retail distribution or review embargoes remain pending.
   - **Unreleased future product**: Documented on roadmaps or in regulatory filings, but neither commercially released nor formally launched.
   - **Hypothetical or invalid entry**: Speculative placeholder or unverified configuration.
   - **Uncertain**: Inconclusive manufacturer documentation.

2. **Benchmark Evidence Status (Empirical Availability):**
   - **Exact model has a verified independent benchmark**: Published empirical 3DMark Time Spy review exists for the exact board-partner card.
   - **Related GPU chip has benchmark evidence, but exact model does not**: Architecture or reference design has empirical review data, but this specific board partner SKU does not.
   - **No reliable benchmark located**: No verified third-party empirical benchmark measurement is indexed.
   - **Requires further research**: Preliminary leaks exist requiring technical verification.

> [!NOTE]
> An officially released GPU is **never** classified as unreleased simply because an exact board-partner review has not yet been collected. Commercial release and empirical benchmark availability remain strictly decoupled.

---

## 2. Two-Dimensional Catalog Status Matrix (18 Quarantined SKUs)

| Component ID | Brand | Exact Model in Catalog | Commercial Status | Benchmark Evidence Status | Silicon Architecture | Evidence & Technical Rationale |
|---|---|---|---|---|---|---|
| `gpu-rtx-5060-ti-16gb` | NVIDIA AIB | RTX 5060 Ti 16GB | **Unreleased future product** | **No reliable benchmark located** | Blackwell (GB206) | Generic placeholder slug. NVIDIA's primary desktop RTX 5060 Ti launched with an 8GB GDDR7 configuration; a 16GB desktop variant remains unreleased commercially. |
| `gpu-rx-9060-xt-16gb` | AMD AIB | RX 9060 XT 16GB | **Unreleased future product** | **No reliable benchmark located** | RDNA 4 (Navi 44) | Generic placeholder slug. Initial RDNA 4 desktop rollout focused on Navi 48 (9070 / 9070 XT); Navi 44 16GB is an unreleased forward-looking product. |
| `gpu-rtx-5070` | NVIDIA AIB | RTX 5070 | **Released commercial product** | **Related GPU chip has benchmark evidence, but exact model does not** | Blackwell (GB205-300) | The underlying GeForce RTX 5070 is officially released (12GB GDDR7, 250W TGP). This generic catalog entry lacks specific AIB part numbers, but the silicon chip has verified benchmarks. |
| `gpu-rtx-5070-ti-16gb` | NVIDIA AIB | RTX 5070 Ti 16GB | **Released commercial product** | **Related GPU chip has benchmark evidence, but exact model does not** | Blackwell (GB203-300) | The RTX 5070 Ti 16GB is an officially launched commercial product (16GB GDDR7, 300W TGP). Generic entry representing baseline silicon rather than a specific partner SKU. |
| `gpu-rtx-5080-fe` | NVIDIA FE | RTX 5080 Founders Edition | **Released commercial product** | **Exact model has a verified independent benchmark** | Blackwell (GB203-400-A1) | Commercially released retail flagship with comprehensive independent benchmark reviews across TechPowerUp, Guru3D, and Tom's Hardware. |
| `gpu-rog-astral-5080-oc` | ASUS | ROG Astral RTX 5080 OC | **Released commercial product** | **Related GPU chip has benchmark evidence, but exact model does not** | Blackwell (GB203-400-A1) | Commercial retail graphics card from ASUS's flagship Blackwell custom lineup; shares the GB203-400 silicon baseline. |
| `gpu-nvidia-asus-rog-astral-rtx5090-o32g` | ASUS | ROG Astral GeForce RTX 5090 32GB GDDR7 OC Edition | **Released commercial product** | **Exact model has a verified independent benchmark** | Blackwell (GB202-300-A1) | Commercially released retail halo desktop card (32GB GDDR7, 512-bit bus, 575W TGP). Exact board partner card reviewed by tier-1 outlets. |
| `gpu-nvidia-asus-tuf-rtx5080-o16g` | ASUS | TUF Gaming GeForce RTX 5080 16GB GDDR7 OC Edition | **Released commercial product** | **Exact model has a verified independent benchmark** | Blackwell (GB203-400-A1) | Commercially released retail desktop card with full technical specifications and partner reviews indexed. |
| `gpu-nvidia-asus-prime-rtx5070-o12g` | ASUS | Prime GeForce RTX 5070 12GB GDDR7 OC Edition (SFF-Ready) | **Released commercial product** | **Exact model has a verified independent benchmark** | Blackwell (GB205-300-A1) | Commercially released retail desktop card adhering to NVIDIA SFF-Ready guidelines (12GB GDDR7, 250W TGP). |
| `gpu-nvidia-asus-tuf-rtx5060ti-o8g` | ASUS | TUF Gaming GeForce RTX 5060 Ti 8GB GDDR7 OC Edition | **Announced, not commercially released** | **No reliable benchmark located** | Blackwell (GB206-300) | Formally announced in ASUS partner databases (8GB GDDR7); broad retail distribution and independent embargo lifts pending. |
| `gpu-nvidia-asus-dual-rtx5060ti-o8g` | ASUS | Dual GeForce RTX 5060 Ti 8GB GDDR7 OC Edition | **Announced, not commercially released** | **No reliable benchmark located** | Blackwell (GB206-300) | Formally announced compact dual-fan custom card; retail review coverage pending. |
| `gpu-nvidia-asus-dual-rtx5060-o8g` | ASUS | Dual GeForce RTX 5060 8GB GDDR7 OC Edition | **Announced, not commercially released** | **No reliable benchmark located** | Blackwell (GB206 / GB207) | Documented in ASUS technical specification portals (8GB GDDR7, 145W TGP); staggered retail release schedule. |
| `gpu-nvidia-asus-dual-rtx5050-8g` | ASUS | Dual GeForce RTX 5050 8GB GDDR6 | **Unreleased future product** | **No reliable benchmark located** | Blackwell (GB207) | NVIDIA has not officially launched a commercial desktop RTX 5050 GDDR6 retail card. Quarantined as unreleased. |
| `gpu-nvidia-asus-prime-rtx5050-o8g` | ASUS | Prime GeForce RTX 5050 8GB GDDR6 OC Edition (SFF-Ready) | **Unreleased future product** | **No reliable benchmark located** | Blackwell (GB207) | Forward-looking entry for prospective entry-level SFF card; no verified retail product exists. |
| `gpu-amd-radeon-rx-9070-xt-16gb` | AMD | Radeon RX 9070 XT 16GB | **Released commercial product** | **Exact model has a verified independent benchmark** | RDNA 4 (Navi 48 XT) | Commercially released flagship RDNA 4 desktop graphics card with widespread retail listings and independent reviews. |
| `gpu-amd-radeon-rx-9070-16gb` | AMD | Radeon RX 9070 16GB | **Released commercial product** | **Exact model has a verified independent benchmark** | RDNA 4 (Navi 48 XL) | Commercially released retail desktop graphics card officially launched alongside RX 9070 XT (16GB GDDR6, 220W TGP). |
| `gpu-amd-radeon-rx-9070-gre-12gb` | AMD | Radeon RX 9070 GRE 12GB | **Released commercial product** | **Related GPU chip has benchmark evidence, but exact model does not** | RDNA 4 (Navi 48 GRE) | Commercially released retail graphics card (Golden Rabbit Edition / Regional OEM release, 12GB GDDR6, 240W TGP). |
| `gpu-amd-radeon-rx-9060-xt-8gb` | AMD | Radeon RX 9060 XT 8GB | **Announced, not commercially released** | **No reliable benchmark located** | RDNA 4 (Navi 44) | Formally announced entry-mid tier RDNA 4 card indexed in distributor databases (8GB GDDR6, 170W TBP); broad review availability pending. |

---

## 3. Summary Distribution

### Commercial Status Distribution:
- **Released commercial product**: **10 GPUs** (`gpu-rtx-5070`, `gpu-rtx-5070-ti-16gb`, `gpu-rtx-5080-fe`, `gpu-rog-astral-5080-oc`, `gpu-nvidia-asus-rog-astral-rtx5090-o32g`, `gpu-nvidia-asus-tuf-rtx5080-o16g`, `gpu-nvidia-asus-prime-rtx5070-o12g`, `gpu-amd-radeon-rx-9070-xt-16gb`, `gpu-amd-radeon-rx-9070-16gb`, `gpu-amd-radeon-rx-9070-gre-12gb`)
- **Announced, not commercially released**: **4 GPUs** (`gpu-nvidia-asus-tuf-rtx5060ti-o8g`, `gpu-nvidia-asus-dual-rtx5060ti-o8g`, `gpu-nvidia-asus-dual-rtx5060-o8g`, `gpu-amd-radeon-rx-9060-xt-8gb`)
- **Unreleased future product**: **4 GPUs** (`gpu-rtx-5060-ti-16gb`, `gpu-rx-9060-xt-16gb`, `gpu-nvidia-asus-dual-rtx5050-8g`, `gpu-nvidia-asus-prime-rtx5050-o8g`)
- **Hypothetical or invalid entry**: **0 GPUs**
- **Uncertain**: **0 GPUs**

### Benchmark Evidence Status Distribution:
- **Exact model has a verified independent benchmark**: **6 GPUs**
- **Related GPU chip has benchmark evidence, but exact model does not**: **4 GPUs**
- **No reliable benchmark located**: **8 GPUs**
- **Requires further research**: **0 GPUs**

### Governance Rule for Training Eligibility:
A GPU is eligible for empirical machine learning training **only** when it satisfies both:
1. Commercial status is **Released commercial product**.
2. Benchmark evidence status is **Exact model has a verified independent benchmark** (or verified board partner baseline).

Consequently, all 4 announced and 4 unreleased SKUs remain strictly quarantined from regression training sets.
