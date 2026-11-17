# BuildWise-AI — Phase 9: Upgrade Mode Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 9 — Guided PC Build Mode and Upgrade Mode  
**Scope:** Architecture, Existing Hardware Specification, Replacement Evaluation, Benchmark Delta Analysis, and Budget Tracking in Upgrade Mode  

---

## 1. Objective & Operational Scope

Upgrade Mode empowers users who already own a desktop computer to evaluate replacement components against their existing hardware.
Key functional principles:
1. **User Choice:** The user selects which hardware category to upgrade. The system never arbitrarily chooses or forces a component upgrade.
2. **Retained Hardware Evaluation:** Candidates in the target upgrade category are evaluated strictly against the components the user intends to keep.
3. **Incomplete Information Safety:** The user can specify any component as "Catalog Component", "Unknown / Not Listed Hardware", or "Not Installed / None". Missing or unknown hardware safely produces an `unknown` check without runtime exceptions.
4. **Empirical Benchmarks Only:** Performance comparisons rely strictly on recorded empirical benchmark observations from `data/benchmarks.csv`. No synthetic scores or uncalibrated formulas are fabricated.

---

## 2. Existing Hardware Specification Workflow

Users configure their existing system across the 8 standard hardware categories (`cpu`, `motherboard`, `ram`, `gpu`, `psu`, `case`, `cooler`, `storage`):

| Configuration Mode | UI Behavior | System State Representation | Compatibility Impact |
|---|---|---|---|
| **Catalog Component** | Dropdown allows selecting a genuine model from `data/components.csv` (1,208 records). | `{"status": "catalog", "component_id": str, "brand": str, "model": str, "specs_json": dict}` | Deterministic specification rules evaluate compatibility with candidate replacements. |
| **Unknown / Not Listed** | Freeform generic classification for proprietary or unlisted OEM components. | `{"status": "unknown", "component_id": "unknown_<cat>", "brand": "Generic", "model": "Unknown"}` | Dependent checks produce status `unknown` with an explanation: `"Retained hardware specifications unknown; cannot verify compatibility"`. |
| **Not Installed / None** | Used when a component is absent (e.g., no dedicated GPU in an APU build, or stock box cooler). | `{"status": "none", "component_id": "none_<cat>", "brand": "None", "model": "Not Installed"}` | Excluded from retained check lists; power calculations treat wattage draw as 0 W. |

---

## 3. Retained Component Isolation & Replacement Evaluation

When the user selects a target category to upgrade (e.g., GPU), the application constructs `retained_dict`:
$$\text{retained\_dict} = \{ c: \text{entry} \mid c \in \text{BUILD\_CATEGORIES}, c \neq \text{up\_cat}, \text{entry.status} \neq \text{"none"} \}$$

### Evaluation Rules Across Categories:
- **GPU Upgrade:**
  - Evaluated against retained `case`: checks `check_gpu_case(candidate_specs, case_specs)` (GPU length $\le$ max case GPU clearance).
  - Evaluated against retained `psu`: checks `check_psu(psu_specs, cpu_specs, candidate_specs)` (PSU rated wattage $\ge$ recommended system wattage and required PCIe power connectors).
- **CPU Upgrade:**
  - Evaluated against retained `motherboard`: checks `check_cpu_motherboard` (socket alignment, supported chipsets, BIOS).
  - Evaluated against retained `cooler`: checks `check_cooler_socket` (bracket support).
  - Evaluated against retained `ram` + `motherboard`: checks `check_cpu_motherboard_ram` (memory generation match).
- **RAM Upgrade:**
  - Evaluated against retained `motherboard`: checks `check_motherboard_ram_capacity` (capacity limit) and memory generation match.
- **Storage Upgrade:**
  - Evaluated against retained `motherboard`: checks `check_storage_motherboard` (M.2 NVMe slots and SATA interface availability).

---

## 4. Empirical Benchmark Comparisons

Where empirical benchmark observations exist in `data/benchmarks.csv`, Upgrade Mode displays direct comparative performance metrics:
1. **CPU Comparisons:**
   - Evaluated strictly using **Cinebench R23 Multi-Core Score** (pts).
   - Example verified comparison:
     - Baseline: AMD Ryzen 7 7800X3D (`17,762 pts`, Source: CPU-Monkey)
     - Upgrade: AMD Ryzen 7 7700X (`20,399 pts`, Source: CPU-Monkey)
     - Delta: `+2,637 pts (+14.8%)`
2. **GPU Comparisons:**
   - Evaluated strictly using **3DMark Time Spy Graphics Score** (pts).
   - Example verified comparison:
     - Baseline: NVIDIA RTX 4070 (`DS3_GPU_036`, `36,742 pts`, Source: Guru3D)
     - Upgrade: NVIDIA RTX 4070 Ti (`DS3_GPU_035`, `28,642 pts`, Source: Guru3D)
     - Delta: `-8,100 pts (-22.0%)`
3. **Missing Benchmark Handling:**
   - If either baseline or candidate hardware lacks empirical data, the UI displays `Benchmark data unavailable`.
   - Cross-category comparisons (e.g. CPU vs GPU) are strictly rejected with an incompatible suites notice.
4. **Mandatory ML Boundary Notice:**
   - The UI prominently displays:  
     `"ML-based performance predictions will be available after the project's CPU and GPU models have been trained and evaluated."`

---

## 5. Upgrade Budget Tracking & State Isolation

- **Upgrade Budget Input:** User enters target upgrade budget (default ₹30,000, step ₹2,000).
- **Price Analysis:** Lowest recorded price of candidate is compared against budget, reporting remaining funds or over-budget amounts.
- **Reset Isolation:** Clicking `Reset Upgrade Mode` executes `reset_upgrade_mode()`, clearing existing hardware specifications and upgrade candidate selections without modifying `build_selections` or `build_budget`.

---

## 6. Verification & Test Evidence

All Upgrade Mode functionality is verified in `tests/test_guided_workflow.py` under `GuidedWorkflowUpgradeModeTests`:
- `test_cpu_benchmark_comparison_same_metric`: Passed.
- `test_gpu_benchmark_comparison_same_metric`: Passed.
- `test_cross_category_and_missing_benchmark_handling`: Passed.
- `test_upgrade_candidate_compatibility_against_retained_hardware`: Passed.
- `test_upgrade_mode_with_unknown_retained_hardware`: Passed.
