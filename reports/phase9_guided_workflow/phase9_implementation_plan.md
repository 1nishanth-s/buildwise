# BuildWise-AI — Phase 9: Guided PC Build Mode and Upgrade Mode Implementation Plan

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 9 — Guided PC Build Mode and Upgrade Mode  
**Objective:** Implement beginner-friendly guided sequential PC component selection (Build Mode) and existing system component replacement inspection (Upgrade Mode) in Streamlit without introducing combinatorial exhaustive search or fabricated ML claims.

---

## 1. Existing Architecture & Baseline Inspection

### 1.1 Production Datasets Baseline
The production dataset baseline established in Phase 7 and verified in Phase 8 remains active and protected:
- `data/components.csv`: 1,208 records, SHA-256 `6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc`
- `data/prices.csv`: 599 records, SHA-256 `943e87ae76412d9ed37d442aafd7f079adb0344fede321c5989d37d97f929e7b`
- `data/benchmarks.csv`: 237 records, SHA-256 `4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702`
- `validate_data.py`: Passes with 0 errors.

### 1.2 Preserved Core Utilities in `app.py`
The utility functions developed and verified in Phase 8 will be reused without modification:
- `is_indian_retailer_url(url)`: Domain whitelist validation for Indian computer retailers.
- `evaluate_indian_market_presence(entries)`: Classifies retailer presence into verified Indian listing, non-Indian listing, or unknown.
- `parse_specs(raw_value)`: Robust JSON string specification deserialization into Python dictionaries.
- `price_to_int(raw_value)`: Safe integer parsing with boundary and negative value checks.
- `observation_freshness(checked_at, freshness_days, now)`: Categorizes observations as recent (<=7 days) or stale.
- `price_lookup(prices_frame)`: Builds structured dictionary index of prices mapped by `component_id`.
- `choose_cheapest_price(component_id, prices_lookup, prefer_available)`: Lowest-price or available-first pricing lookup.

### 1.3 Deterministic Compatibility Engine (`src/compatibility.py`)
`src/compatibility.py` is the single source of truth for deterministic hardware rules and must remain 100% untouched. All rule checks return `CompatibilityResult(status, reason)` where `status` is strictly one of `{"compatible", "incompatible", "unknown"}`:
- `check_cpu_motherboard(cpu_specs, mb_specs, cpu_component_id=None)`: Checks socket alignment, chipset generation, and BIOS version requirements.
- `check_cpu_motherboard_ram(cpu_specs, mb_specs, ram_specs)`: Checks memory type (DDR4/DDR5) match across CPU, Motherboard, and RAM.
- `check_motherboard_ram_capacity(mb_specs, ram_specs)`: Checks maximum memory capacity and slot constraints.
- `check_ram_speed_qvl(ram_specs, mb_specs, ram_component_id=None, cpu_specs=None)`: Checks supported speeds and QVL vendor lists.
- `check_gpu_case(gpu_specs, case_specs)`: Checks physical clearance (`gpu_length_mm <= max_gpu_length_mm`).
- `check_psu(psu_specs, cpu_specs, gpu_specs)`: Evaluates combined CPU + GPU TDP plus system overhead against rated wattage.
- `check_cooler_case(cooler_specs, case_specs)`: Checks air cooler height or liquid radiator clearance against case limits.
- `check_cooler_socket(cooler_specs, cpu_specs, mb_specs=None)`: Checks socket mounting bracket compatibility.
- `check_storage_motherboard(storage_specs, mb_specs)`: Checks M.2 NVMe and SATA interface availability.

---

## 2. Proposed UI Workflow & Navigation

The Streamlit interface will feature a sidebar navigation menu with 5 distinct operational views:

```
Sidebar Navigation:
├── 1. Home / Dataset Overview       (Preserved baseline metrics & data overview)
├── 2. Build Mode (Guided)          (Sequential 8-step PC building workflow)
├── 3. Upgrade Mode                 (Existing system component upgrade analysis)
├── 4. Component Catalog Browser    (Preserved specification & price browser)
└── 5. Compatibility Inspector      (Preserved pairwise rule inspection)
```

### 2.1 Part A: Build Mode (Guided) Workflow
1. **Preferences & Budget Input:**
   - Budget input in INR (`st.number_input`, default ₹75,000, min ₹10,000, step ₹5,000).
   - Intended Use (`st.selectbox`): Gaming, Office & Everyday, Programming & Development, Content Creation, Workstation, General Purpose. (Documented as descriptive context; zero arbitrary scoring formulas).
2. **Sequential Selection Steps:**
   - Step 1: CPU
   - Step 2: Motherboard (evaluated against selected CPU)
   - Step 3: RAM (evaluated against selected Motherboard & CPU)
   - Step 4: Case (evaluated against selected Motherboard)
   - Step 5: GPU (skippable for APUs or budget configurations; evaluated against Case)
   - Step 6: PSU (evaluated against CPU, GPU, and system draw)
   - Step 7: CPU Cooler (skippable if stock cooler used; evaluated against CPU socket and Case)
   - Step 8: Storage (evaluated against Motherboard interfaces)
3. **Candidate Filtering & Selection UI:**
   - Live search by Brand / Model.
   - Live compatibility indicator badge (`Compatible`, `Incompatible`, `Unknown`) computed on-the-fly against already selected components.
   - Price display: Lowest recorded price, seller, availability, price type.
   - Empirical benchmark display: Cinebench R23 (CPU) or 3DMark Time Spy (GPU).
   - Direct manual selection button (`Select Component`) or skip button for optional parts (GPU, Cooler).
4. **Live Budget & Build Summary:**
   - Real-time running total of recorded prices vs total budget.
   - Remaining budget metric with over-budget warning if exceeded.
   - Breakdown of verified seller observations vs planning estimates vs unpriced items.
   - Comprehensive summary table showing all selected parts, specs, prices, benchmarks, and compatibility reasons.
   - "Change / Remove" action for each step and a "Reset Build" button.

### 2.2 Part B: Upgrade Mode Workflow
1. **Existing PC Configuration Input:**
   - User specifies currently installed hardware across all 8 categories.
   - Each category allows: (a) Selecting a verified catalog component, (b) "Unknown / Not Listed Hardware", or (c) "Not Installed / None".
   - Clear architectural invariant: Missing or unknown hardware is handled safely; dependent checks return `unknown` without crashing.
2. **Upgrade Budget Input:**
   - Optional budget in INR for the upgrade.
3. **Upgrade Target Category Selection:**
   - User chooses 1 hardware category to upgrade (e.g., GPU, CPU, RAM, Storage, PSU).
4. **Replacement Candidate Evaluation:**
   - Catalog components in the chosen category are presented with compatibility badges evaluated strictly against retained existing components.
   - For GPU: Evaluated against existing Case clearance and existing PSU wattage.
   - For CPU: Evaluated against existing Motherboard socket/chipset and existing Cooler/RAM.
   - For RAM: Evaluated against existing Motherboard generation and slot capacity.
   - For Storage: Evaluated against existing Motherboard interfaces.
5. **Empirical Benchmark Comparison:**
   - CPU vs CPU: Cinebench R23 Multi-Core (pts) baseline vs upgrade, showing score delta and percentage difference `((upgrade - baseline) / baseline) * 100`.
   - GPU vs GPU: 3DMark Time Spy Graphics (pts) baseline vs upgrade, showing score delta and percentage difference.
   - Missing data shows explicit "Benchmark data unavailable".
   - Notice: "ML-based performance predictions will be available after the project's CPU and GPU models have been trained and evaluated."
6. **Upgrade Summary & Budget Tracking:**
   - Displays baseline component, proposed upgrade component, price delta against upgrade budget, retained components, and full compatibility verification.

---

## 3. Session State Architecture & Isolation

Streamlit session state keys will be strictly namespaced to guarantee zero interference between Build Mode and Upgrade Mode:

| Mode | Session State Keys | Purpose |
|---|---|---|
| **Build Mode** | `build_budget`<br>`build_purpose`<br>`build_selections`<br>`build_step` | Tracks build budget, descriptive purpose, dict of selected components (`{category: component_dict}`), and current active step index. |
| **Upgrade Mode** | `upgrade_budget`<br>`existing_pc`<br>`upgrade_category`<br>`selected_upgrade` | Tracks upgrade budget, dict of existing components (`{category: {"status": "catalog"\|"unknown"\|"none", "component": dict}}`), target category, and chosen replacement. |
| **Navigation** | `nav_page` | Active navigation page selection in sidebar. |

### Reset Operations
- `Reset Build Mode`: Clears `build_selections`, resets `build_step = 0`, preserves `upgrade_*` state.
- `Reset Upgrade Mode`: Clears `existing_pc`, `selected_upgrade`, preserves `build_*` state.

---

## 4. Scalability & Architectural Safeguards (Anti-Combinatorial)

- **Zero DFS / Cartesian Product:** No recursive configuration generators, no Cartesian product expansion, no `build_recommendation` function.
- **On-Demand Single-Candidate Evaluation:** Candidate lists evaluate compatibility solely against the currently selected items (O(N) where N is category size <= 218).
- **Safe 3-State Compatibility:** `compatible`, `incompatible`, `unknown`. Incompatible components cannot be accidentally selected as compatible; unknown components show an evidence warning.
- **Budget Integrity:** Prices are never assumed to be ₹0; unpriced items are flagged as "Unpriced"; planning estimates are visibly differentiated from verified retailer listings.
- **Dataset Immutability:** No writing to `data/*.csv`.

---

## 5. Testing Strategy

1. **New Test Suite: `tests/test_guided_workflow.py`**
   - Unit tests covering:
     - Session state initialization and isolation between Build Mode and Upgrade Mode.
     - Sequential selection progression and component retention.
     - Dynamic revalidation when an earlier component is changed.
     - Budget calculation accuracy, including handling of unpriced items and planning estimates.
     - Compatibility enforcement (CPU-Motherboard, RAM-Motherboard, GPU-Case, PSU wattage).
     - Upgrade Mode existing PC specification handling (catalog, unknown, none).
     - Empirical benchmark comparison calculations and percentage differences for CPUs and GPUs.
     - Benchmark missingness handling ("Benchmark data unavailable").
     - Verifying absence of legacy combinatorial search and no dataset mutation.
2. **Regression Testing:**
   - All 94 existing tests in `test_compatibility.py`, `test_validator.py`, `test_cpu_ml_regression.py`, `test_performance_tier.py`, `test_recommendation.py` must continue to pass.
3. **Data Integrity Check:**
   - `validate_data.py` must pass with 0 errors.
   - SHA-256 hashes of all 3 CSVs must remain identical to baseline.
4. **Streamlit App Smoke Test:**
   - Headless run via `streamlit run app.py --server.headless true --server.port 8501`.
   - Smoke test script verifying HTTP 200 responses across all views.

---

## 6. Files Expected to Change

| File | Nature of Change |
|---|---|
| `app.py` | Implementation of Sidebar navigation, Build Mode workflow, Upgrade Mode workflow, session state handlers, live compatibility integration, budget calculations, and benchmark comparisons. |
| `tests/test_guided_workflow.py` | New comprehensive unit test suite covering guided Build Mode and Upgrade Mode logic, state isolation, compatibility evaluation, and pricing rules. |
| `reports/phase9_guided_workflow/*` | 11 required Phase 9 markdown reports and file change manifest. |
| Brain Artifact | `phase9_guided_workflow_report.md` in artifact directory. |
