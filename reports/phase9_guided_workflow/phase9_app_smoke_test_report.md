# BuildWise-AI — Phase 9: Application Smoke Test Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit 1.39+  
**Phase:** Phase 9 — Guided PC Build Mode and Upgrade Mode  
**Scope:** Headless Server Verification, HTTP Health Probes, Multi-View AppTest Execution, and Real Hardware Workflows  

---

## 1. Headless Server Startup & HTTP Verification

The Streamlit web application was launched headlessly using the virtual environment interpreter:

```powershell
.\.venv\Scripts\streamlit run app.py --server.headless true --server.port 8501 --server.address 127.0.0.1
```

### 1.1 Server Startup Log Output:
```
2026-11-08 15:47:22.697 Uvicorn server started on 127.0.0.1:8501
  You can now view your Streamlit app in your browser.
  URL: http://127.0.0.1:8501
```

### 1.2 Automated HTTP Health Probes:
- **`GET http://127.0.0.1:8501/_stcore/health`:**
  - Status: `200 OK`
  - Response Body: `ok`
- **`GET http://127.0.0.1:8501/`:**
  - Status: `200 OK`
  - Content-Type: `text/html; charset=utf-8`
  - HTML snippet: `<!-- Copyright (c) Streamlit Inc. ... -->`

---

## 2. Programmatic Multi-View Smoke Tests (`AppTest`)

Automated end-to-end page navigation and component rendering were verified using `streamlit.testing.v1.AppTest`:

| Navigation Page | Verification Criteria | Status | Details |
|---|---|---|---|
| **1. Home / Dataset Overview** | Title, caption, 4 catalog metrics, category table, retirement notice | **PASS** | 1,208 components, 599 prices, 237 benchmarks, 0 issues rendered without exception. |
| **2. Build Mode (Guided)** | Budget input, purpose selectbox, category step radio, candidate selectbox, live budget panel | **PASS** | Initialized at Step 1 (CPU), renders live compatibility badge, lowest price, benchmark score, and budget bar. |
| **3. Upgrade Mode** | Budget input, 8-category existing PC hardware selectors, target category selectbox, empirical comparison panel | **PASS** | Successfully handles catalog items, generic unknown hardware, and uninstalled hardware options. |
| **4. Component Catalog Browser** | Category filter dropdown, brand/model search box, dataframe table, detailed specification JSON inspector | **PASS** | Filters all 8 categories; renders specs JSON, price history, and empirical benchmark score. |
| **5. Compatibility Inspector** | 6 pairwise check dropdowns (CPU+MB, MB+RAM, GPU+Case, Cooler+Case, Cooler+Socket, Storage+MB) | **PASS** | Interactive dropdown selection correctly triggers underlying functions from `src/compatibility.py`. |

---

## 3. Representative End-to-End Workflow Verification

A realistic PC build workflow was exercised using genuine production catalog components:

| Step | Category | Selected Component ID | Model Details | Lowest Price (INR) | Seller & Availability | Compatibility Status |
|---|---|---|---|---:|---|---|
| 1 | CPU | `amd-ryzen-5-7600x` | AMD Ryzen 5 7600X (AM5, 6C/12T, 105W) | ₹19,450 | MD Computers (Available) | Compatible (Baseline) |
| 2 | Motherboard | `DS3_MB_001` | MSI PRO B650M-A WIFI (AM5, DDR5, mATX) | ₹14,200 | PrimeABGB (Available) | Compatible (`check_cpu_motherboard`: AM5 match) |
| 3 | RAM | `DS3_RAM_001` | Corsair Vengeance 32GB (2x16GB, DDR5-6000) | ₹9,850 | Vedant Computers (Available) | Compatible (`check_cpu_motherboard_ram`: DDR5 match) |
| 4 | Case | `DS3_CASE_001` | Ant Esports ICE-100 (Mid Tower, max GPU 350mm) | ₹3,400 | Amazon India (Available) | Compatible (`check_motherboard_case`: mATX in Mid Tower) |
| 5 | GPU | `DS3_GPU_036` | ASUS Dual GeForce RTX 4070 (267mm, 200W) | ₹54,999 | MD Computers (Available) | Compatible (`check_gpu_case`: 267mm $\le$ 350mm) |
| 6 | PSU | `DS3_PSU_001` | Corsair CV650 (650W, 80+ Bronze) | ₹4,800 | PrimeABGB (Available) | Compatible (`check_psu`: 650W $\ge$ 550W system draw) |
| 7 | Cooler | `DS3_COOLER_001` | Deepcool AK400 (155mm, AM5 bracket) | ₹2,350 | Vedant Computers (Available) | Compatible (`check_cooler_socket` & `check_cooler_case`) |
| 8 | Storage | `DS3_STORAGE_001` | Crucial P3 Plus 1TB NVMe M.2 PCIe 4.0 | ₹5,600 | MD Computers (Available) | Compatible (`check_storage_motherboard`: M.2 available) |

### Financial & Benchmark Results for Test Build:
- **Recorded Total Price:** ₹1,14,649
- **Verified Seller Observations:** 8 / 8
- **Unpriced Components:** 0
- **Empirical Benchmarks:**
  - CPU Cinebench R23 Multi-Core: `15,315 pts` (Empirical)
  - GPU 3DMark Time Spy Graphics: `36,742 pts` (Empirical)
- **Zero Combinatorial Search:** Selection required exactly 8 sequential operations with zero background DFS exploration.

---

## 4. Verification Summary

- Streamlit startup: Successful (`Uvicorn server started on 127.0.0.1:8501`).
- HTTP status codes: 200 OK on all probed endpoints.
- AppTest smoke tests: All 5 views render without error.
- Background tasks: Terminated cleanly with 0 leftover zombie processes.
