# BuildWise-AI — Phase 10: Hardware Feature Quality and Selection Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 10 — Machine Learning Dataset Audit, Feature Engineering and Training Data Preparation  
**Audited Datasets:** `data/components.csv`, `data/benchmarks.csv`, `data/ml/gpu_feature_enrichment_v1.csv`  

---

## 1. Feature Engineering Principles & Anti-Leakage Safeguards

Supervised regression models predicting hardware performance must learn from genuine physical and architectural characteristics, not artifacts of metadata or retail listings. The following strict rules guided feature extraction:

1. **No Target Leakage:** Benchmark targets (`cinebench_r23_multi_core_score`, `timespy_graphics_score`) and any proxy metrics (e.g., single-core scores or normalized indices) are strictly prohibited from entering the feature matrix $X$.
2. **No Identifier Predictors:** `component_id`, `benchmark_id`, source URLs, and row indexes are preserved solely as non-predictive metadata for traceability.
3. **No Pricing Predictors:** `price_inr`, seller names, and retailer categories are excluded. Pricing fluctuates with supply/demand and does not dictate silicon computational capability.
4. **No Model-Name Memorization:** Exact product marketing strings are excluded from the predictor matrix to prevent decision trees from memorizing specific SKUs rather than generalizing hardware properties.
5. **No Fabricated Specifications:** Features with high missingness ($>50\%$) are rejected rather than imputed with synthetic random values.

---

## 2. CPU Feature Quality Analysis (180 Processors)

Every CPU in the 180-processor catalog was audited across potential architectural and operating parameters:

| Feature Name | Type | Unit | Available Records | Missing (%) | Decision | Architectural Rationale |
|---|---|---|---:|---:|---|---|
| `cores` | Integer | count | 180 / 180 | 0.0% | **Retained** | Physical core count is the primary multi-core throughput driver in Cinebench R23. |
| `threads` | Integer | count | 180 / 180 | 0.0% | **Retained** | Captures simultaneous multithreading (SMT/Hyper-Threading) capacity. |
| `boost_clock_ghz` | Float | GHz | 180 / 180 | 0.0% | **Retained** | Peak frequency determines maximum per-clock throughput ceiling. |
| `base_clock_ghz` | Float | GHz | 150 / 180 | 16.67% | **Imputation Candidate** | Guaranteed all-core sustained frequency; 30 records missing; suitable for median imputation during Phase 11. |
| `tdp_w` | Float | Watts | 180 / 180 | 0.0% | **Retained** | Thermal Design Power represents package electrical power limits and sustained headroom. |
| `brand` | Categorical | text | 180 / 180 | 0.0% | **Retained** | Categorizes AMD (81) vs Intel (99) architectural paradigms. |
| `socket` | Categorical | text | 180 / 180 | 0.0% | **Retained** | Proxies platform generation and memory topology (AM4, AM5, LGA1700, LGA1851, etc.). |
| `ram_type` | Categorical | text | 180 / 180 | 0.0% | **Retained** | Memory controller standard (DDR4 vs DDR5). |
| `architecture` | Categorical | text | 34 / 180 | 81.11% | **Excluded** | Microarchitecture string is missing in 81.1% of catalog entries; excluded to prevent high missingness artifacts. |
| `l3_cache_mb` | Float | MB | 0 / 180 | 100.0% | **Excluded** | L3 cache is undocumented in the canonical catalog CSV; excluded. |
| `l2_cache_mb` | Float | MB | 0 / 180 | 100.0% | **Excluded** | L2 cache is undocumented in the canonical catalog CSV; excluded. |
| `process_nm` | Float | nm | 0 / 180 | 100.0% | **Excluded** | Lithography node is undocumented in canonical catalog; excluded. |
| `integrated_graphics` | Boolean | bool | 150 / 180 | 16.67% | **Excluded** | iGPU presence is irrelevant to CPU multi-core rendering. |

---

## 3. GPU Feature Quality Analysis (57 Benchmarked GPUs)

The 57 benchmarked GPUs were audited across universal graphics parameters and vendor-specific compute metrics:

| Feature Name | Type | Unit | Available Records | Missing (%) | Decision | Architectural Rationale |
|---|---|---|---:|---:|---|---|
| `vram_gb` | Integer | GB | 57 / 57 | 0.0% | **Retained** | Framebuffer capacity; critical for 1440p DirectX 12 render targets in Time Spy. |
| `memory_bus_width_bits` | Integer | bits | 57 / 57 | 0.0% | **Retained** | Bus width directly dictates memory transfer concurrency across memory channels. |
| `memory_bandwidth_gbps` | Float | GB/s | 57 / 57 | 0.0% | **Retained** | Theoretical memory bandwidth in GB/s; core predictor of frame buffer fill rate. |
| `base_clock_mhz` | Float | MHz | 57 / 57 | 0.0% | **Retained** | Base graphics engine clock frequency. |
| `boost_clock_mhz` | Float | MHz | 57 / 57 | 0.0% | **Retained** | Maximum graphics engine boost clock frequency. |
| `board_power_w` | Float | Watts | 57 / 57 | 0.0% | **Retained** | Total graphics power (TGP / TDP); governs sustained silicon frequency boost limits. |
| `architecture` | Categorical | text | 57 / 57 | 0.0% | **Retained** | Identifies silicon generation: RDNA 3 (23), Ada Lovelace (16), Ampere (10), RDNA 2 (6), Xe2-HPG (2). |
| `chipmaker` | Categorical | text | 57 / 57 | 0.0% | **Retained** | Vendor indicator: AMD (29), NVIDIA (26), Intel (2). |
| `memory_type` | Categorical | text | 57 / 57 | 0.0% | **Retained** | Memory generation standard: GDDR6 (39), GDDR6X (18). |
| `cuda_cores` | Integer | count | 26 / 57 | 54.39% | **Excluded** | NVIDIA-specific shader ALU count; non-existent on AMD/Intel silicon; non-comparable. |
| `stream_processors` | Integer | count | 29 / 57 | 50.88% | **Excluded** | AMD-specific execution units; non-comparable to CUDA cores without complex IPC scaling. |
| `compute_units` | Integer | count | 29 / 57 | 50.88% | **Excluded** | AMD RDNA compute cluster structure; missing on NVIDIA/Intel. |
| `xe_cores` | Integer | count | 2 / 57 | 96.49% | **Excluded** | Intel Battlemage-specific execution units; excluded due to 96.5% missingness. |
| `cache_l2_mb` | Float | MB | 28 / 57 | 50.88% | **Excluded** | L2 cache missing on AMD entries; excluded. |
| `infinity_cache_mb` | Float | MB | 29 / 57 | 50.88% | **Excluded** | AMD-exclusive on-die cache; absent on NVIDIA/Intel. |
| `tensor_cores` / `rt_cores` | Integer | count | 26 / 57 | 54.39% | **Excluded** | AI / Ray Tracing hardware; Time Spy Graphics is a pure rasterization benchmark. |

---

## 4. Normalization and Transformation Rules

1. **Unit Standardization:**
   - Frequencies: CPU clock speeds normalized strictly to **Gigahertz (GHz)**; GPU clock speeds normalized to **Megahertz (MHz)**.
   - Power: Normalized to **Watts (W)**.
   - Memory capacity: Normalized to **Gigabytes (GB)**.
   - Memory bandwidth: Normalized to **Gigabytes per second (GB/s)**.
2. **Text Normalization:**
   - Categorical features (`brand`, `socket`, `ram_type`, `architecture`, `chipmaker`, `memory_type`) are stripped of extraneous whitespace, lowercased, and standardized (e.g. `lga-1700` $\rightarrow$ `lga1700`).
3. **Data Type Casting:**
   - Integer counts (`cores`, `threads`, `vram_gb`, `memory_bus_width_bits`) cast to standard `int64`.
   - Floating-point measurements cast to standard `float64`.
