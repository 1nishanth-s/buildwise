# BuildWise-AI — Phase 9: Guided Build Mode Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 9 — Guided PC Build Mode and Upgrade Mode  
**Scope:** Architecture, UI Workflow, Compatibility Integration, and Budget Tracking in Guided Build Mode  

---

## 1. Overview and Design Philosophy

Phase 8 removed the legacy exhaustive configuration search engine (`build_recommendation`), which used combinatorial recursive depth-first search (DFS) over Cartesian products. BuildWise-AI Phase 9 replaces that obsolete design with a user-empowered, sequential guided workflow:
- **User-Driven Selection:** The user makes component decisions sequentially. The system assists with live deterministic compatibility checks, pricing visibility in INR, budget tracking, and empirical benchmark presentation.
- **Zero Combinatorial Explosion:** The application never generates, scores, or ranks complete PC configurations automatically. There are no recursive loops or Cartesian product calculations.
- **Descriptive Use Context:** The user specifies their intended primary use (e.g., Gaming, Content creation, Workstation) strictly as context; the system does not apply arbitrary global weighting or fabricated workload fitness scores.

---

## 2. Guided Selection Sequence & Workflow

The guided build mode implements an 8-step sequential hardware progression:

| Step | Category | Category Label | Evaluated Compatibility Relationships | Optional / Skippable |
|---|---|---|---|---|
| 1 | `cpu` | CPU / Processor | Baseline (socket, memory controller, TDP) | No |
| 2 | `motherboard` | Motherboard | Socket match vs CPU, chipset generation, BIOS requirements | No |
| 3 | `ram` | RAM Memory | Memory generation match (DDR4/DDR5) vs MB & CPU, max capacity | No |
| 4 | `case` | PC Case / Chassis | Form factor clearance (ATX, Micro-ATX, Mini-ITX) vs MB | No |
| 5 | `gpu` | Graphics Card (GPU) | Physical card length vs Case clearance, PSU wattage draw | **Yes** (integrated graphics / APU / install later) |
| 6 | `psu` | Power Supply Unit (PSU) | Combined system power draw vs rated PSU wattage, PCIe connectors | No |
| 7 | `cooler` | CPU Cooler | Mounting socket vs CPU/MB, cooler height vs Case clearance | **Yes** (stock box cooler / install later) |
| 8 | `storage` | Storage Drive | M.2 NVMe slot availability, SATA port availability vs MB | No |

---

## 3. Dynamic Revalidation on Earlier Changes

A critical safety invariant required by Phase 9 is handling modifications to earlier selections without data loss or silent retention of invalid configurations:
1. **Change Tracking:** When a user selects a component in an earlier step (for example, switching from an AMD AM5 CPU to an Intel LGA1700 CPU after having selected an AM5 motherboard), the `reevaluate_build_selections` pure function inspects all currently active selections.
2. **Conflict Highlighting:** If a newly introduced pairing violates documented hardware rules (e.g., LGA1700 CPU on an AM5 socket), the UI flags an immediate warning:  
   `⚠️ Incompatibility Conflict Detected: A previously selected component is conflicting with other selections.`
3. **Explicit User Resolution:** The conflicting category and component ID are prominently highlighted with individual `Remove / Change Selection` controls. Selections are not erased behind the user's back, and incompatible builds cannot be submitted as valid.

---

## 4. Live Budget & Price Tracking

The right-hand budget panel maintains a continuous, real-time breakdown of the user's configuration:
- **Total Budget (INR):** Configurable by the user (`st.number_input`, default ₹75,000, step ₹5,000).
- **Recorded Total (INR):** Sum of lowest recorded prices for selected hardware.
- **Remaining Budget (INR):** `Budget - Recorded Total`. Automatically shows an over-budget error if negative.
- **Price Type Transparency:** Distinctly displays counts of:
  - Verified retailer observations (`seller_observation` from Indian retailers like MD Computers, PrimeABGB, Vedant Computers).
  - User-provided planning estimates (`planning_estimate`).
  - Unpriced components (explicitly displayed as `Price unavailable`; missing prices are never treated as ₹0).
- **Confirmed Available Total:** Tracks the subtotal of components currently in stock at verified retailers.

---

## 5. Build Summary & Reset Isolation

Upon selecting components across the categories:
- A structured tabular summary presents Category, Component Name (Brand + Model), Lowest Price, Seller, Availability, and Empirical Benchmark scores.
- An expander details every pairwise compatibility check with rule citations and reasons.
- **Session State Isolation:** The `Reset Build` button calls `reset_build_mode()`, clearing `st.session_state.build_selections` and setting `build_step = 0`, while leaving `st.session_state.upgrade_existing` completely untouched.

---

## 6. Verification & Test Evidence

All Build Mode functionality is tested in `tests/test_guided_workflow.py` under `GuidedWorkflowBuildModeTests`:
- `test_build_categories_order_and_labels`: Passed.
- `test_component_filtering_by_category`: Passed.
- `test_cpu_motherboard_compatibility_check`: Passed.
- `test_motherboard_ram_compatibility_check`: Passed.
- `test_multiple_component_selections_retention`: Passed.
- `test_changing_earlier_component_triggers_revalidation`: Passed.
- `test_budget_totals_and_missing_price_handling`: Passed.
- `test_unknown_compatibility_preserved`: Passed.
