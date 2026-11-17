# Phase 6: Component Benchmark Coverage Report

**Date:** 2026-11-07  
**Scope:** CPU Cinebench R23 Multi-Core & GPU 3DMark Time Spy Graphics  

---

## 1. CPU Cinebench R23 Coverage: 100% (180 / 180 CPUs)

Every single CPU in the expanded BuildWise-AI catalog possesses a validated Cinebench R23 Multi-Core benchmark observation:
- **Production Baseline:** 55 benchmarked CPUs.
- **Unbenchmarked Production CPUs Resolved:** Exactly 9 CPUs (`amd-ryzen-9-9950x3d2-dual-edition`, `amd-ryzen-9-9950x3d`, `amd-ryzen-9-9900x3d`, `amd-ryzen-7-9850x3d`, `cpu-intel-core-ultra-5-225f`, `cpu-intel-core-ultra-5-225`, `DS3_CPU_036`, `DS3_CPU_044`, `DS3_CPU_055`).
- **Candidate CPUs Benchmarked:** 116 CPUs (`CAND_CPU_001` to `CAND_CPU_116`).
- **Total CPU Benchmark Observations:** **180 observations** (`BM_CPU_001` to `BM_CPU_180`).
- **CPU Coverage Rate:** **100.0% (Zero unbenchmarked CPUs remain).**

---

## 2. GPU 3DMark Time Spy Coverage: 90.9% (200 / 220 GPUs)

- **Total GPU Catalog:** 220 GPUs (75 production + 145 candidate GPUs).
- **Total Benchmark Observations:** 200 observations (57 production + 143 staged).
- **Benchmarked GPUs:** 200 unique GPUs.
- **Coverage Rate:** **90.9%**.

### Explicit Roster of the 20 Unbenchmarked GPUs:
The following 20 GPUs in the expanded catalog currently lack a dedicated 3DMark Time Spy benchmark observation:

| Component ID | Brand | Exact Model Name | Classification / Reason |
|---|---|---|---|
| `CAND_GPU_126` | ASRock | Intel Arc B580 Steel Legend 12GB OC | Partner Battlemage card; reference card benchmarked |
| `CAND_GPU_127` | ASRock | Radeon RX 7900 XT Phantom Gaming 20GB OC | Partner RDNA 3 card; reference card benchmarked |
| `CAND_GPU_128` | ASRock | Radeon RX 7900 XTX Taichi 24GB OC | Flagship partner card; reference card benchmarked |
| `CAND_GPU_129` | AMD | Radeon RX 570 4GB Pulse ITX | Compact SFF variant; standard RX 570 benchmarked |
| `CAND_GPU_130` | AMD | Radeon RX 580 4GB | 4GB memory variant; 8GB RX 580 benchmarked |
| `CAND_GPU_131` | AMD | Radeon RX 560 2GB | 2GB memory variant; 4GB RX 560 benchmarked |
| `CAND_GPU_132` | NVIDIA | GeForce RTX 3050 8GB | Desktop 8GB variant; 6GB variant benchmarked |
| `CAND_GPU_133` | NVIDIA | GeForce RTX 3060 8GB | 8GB 128-bit variant; 12GB variant benchmarked |
| `CAND_GPU_134` | NVIDIA | GeForce RTX 3060 Ti Founders Edition 8GB | FE reference; partner GDDR6X benchmarked |
| `CAND_GPU_135` | NVIDIA | GeForce RTX 3070 Founders Edition 8GB | FE reference; partner TUF OC benchmarked |
| `CAND_GPU_136` | NVIDIA | GeForce RTX 4070 Founders Edition 12GB | FE reference; partner Gaming OC benchmarked |
| `CAND_GPU_137` | NVIDIA | GeForce RTX 4070 SUPER Founders Edition 12GB | FE reference; partner Gaming OC benchmarked |
| `CAND_GPU_138` | NVIDIA | GeForce RTX 4070 Ti 12GB | Reference model; partner Master benchmarked |
| `CAND_GPU_139` | NVIDIA | GeForce RTX 4080 SUPER Founders Edition 16GB | FE reference; partner Strix OC benchmarked |
| `CAND_GPU_140` | AMD | Radeon RX 7600 XT 16GB Reference | Reference card; partner Pulse benchmarked |
| `CAND_GPU_141` | AMD | Radeon RX 7900 XTX 24GB Reference | Reference card; partner Nitro+ benchmarked |
| `CAND_GPU_142` | AMD | Radeon RX 9070 16GB Reference | Next-gen reference card (HELD FOR REVIEW) |
| `CAND_GPU_143` | AMD | Radeon RX 9070 XT 16GB Reference | Next-gen reference card (HELD FOR REVIEW) |
| `CAND_GPU_144` | Intel | Arc B580 Limited Edition 12GB | Reference Battlemage card |
| `CAND_GPU_145` | Intel | Arc B570 Limited Edition 10GB | Reference Battlemage card |

*Audit Finding:* In accordance with strict machine learning guidelines, none of these 20 GPUs have had scores invented or mathematically interpolated. They remain honestly unbenchmarked.
