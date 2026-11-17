# BuildWise-AI — Phase 9: Compatibility Integration Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 9 — Guided PC Build Mode and Upgrade Mode  
**Scope:** Integration of `src/compatibility.py` Deterministic Hardware Rules into Guided Workflows  

---

## 1. Single Source of Truth & Compatibility Philosophy

In BuildWise-AI, all hardware compatibility evaluation is strictly deterministic and rooted in documented manufacturer specifications.
- `src/compatibility.py` serves as the sole authoritative source of truth.
- Zero compatibility rules are duplicated or bypassed in UI logic.
- All checks adhere to the strict 3-state invariant:
  - **`compatible`**: Verified documented evidence establishes physical, electrical, and logical interoperability.
  - **`incompatible`**: Documented evidence proves a definite hardware conflict (e.g. mismatched socket, exceeding case clearance, or insufficient PSU wattage).
  - **`unknown`**: Specifications are missing, incomplete, or unconfirmed (e.g. undocumented BIOS versions or unverified memory QVL). **Unknown is never converted to compatible.**

---

## 2. Integrated Compatibility Functions & Rules Matrix

The table below maps each hardware pairing evaluated in `evaluate_component_compatibility` to its corresponding function in `src/compatibility.py`:

| Hardware Pair | Function in `src/compatibility.py` | Exact Evaluated Specification Fields | Deterministic Conflict Condition |
|---|---|---|---|
| **CPU + Motherboard** | `check_cpu_motherboard` | `socket`, `chipset`, `supported_chipsets`, `bios_version`, `minimum_bios_version` | Sockets do not match, chipset is not supported by CPU, or BIOS version is below minimum. |
| **CPU + Motherboard + RAM** | `check_cpu_motherboard_ram` | `ram_type` across CPU, Motherboard, and RAM | Distinct memory generations (e.g., DDR4 RAM with DDR5 Motherboard). |
| **Motherboard + RAM Capacity** | `check_motherboard_ram_capacity` | `ram_max_gb` (MB), `capacity_gb` (RAM) | Total RAM kit capacity exceeds motherboard maximum capacity. |
| **RAM Speed & QVL** | `check_ram_speed_qvl` | `speed_mtps`, `ram_type`, `qvl_list` | RAM speed exceeds platform baseline without validated QVL / EXPO / XMP support. |
| **GPU + Case** | `check_gpu_case` | `length_mm` (GPU), `max_gpu_length_mm` (Case) | GPU length exceeds maximum case clearance. |
| **PSU Capacity & Sizing** | `check_psu` | `wattage_w`, `power_connectors` (PSU), `recommended_system_psu_w`, `required_power_connectors` (GPU) | PSU wattage < recommended system wattage, or PSU lacks required PCIe power connectors. |
| **Cooler + CPU Socket** | `check_cooler_socket` | `supported_sockets` (Cooler), `socket` (CPU) | CPU socket is missing from cooler supported bracket list. |
| **Cooler + Case Clearance** | `check_cooler_case` | `height_mm` (Cooler), `max_cooler_height_mm` (Case) | Air cooler height exceeds case CPU cooler clearance. |
| **Storage + Motherboard** | `check_storage_motherboard` | `interface` (Storage), `m2_slots_count`, `sata_6gbps_ports` (MB) | M.2 drive selected when MB has 0 M.2 slots, or SATA drive when MB has 0 SATA ports. |

---

## 3. Handling of Missing & Incomplete Data (`unknown` State)

Missing evidence is treated with complete transparency:
1. When a component specification JSON is empty (`{}`) or lacks a critical attribute (such as `required_power_connectors` or `minimum_bios_version`), the check function returns `CompatibilityResult(status="unknown", reason=...)`.
2. The UI renders an amber badge: `⚠️ Compatibility: UNKNOWN (Evidence Required)`.
3. An expandable inspection drawer displays the exact reason:  
   `"PSU capacity 550 W meets the recommended system PSU capacity of 450 W. GPU required power connectors are not documented."`
4. The user is allowed to proceed if they verify physical connectors independently, but the configuration summary preserves the `unknown` status in the build manifest.

---

## 4. Incompatibility Safeguards & Selection Blocking

To guarantee that users do not inadvertently build physically incompatible systems:
- When any rule evaluates to `incompatible`, the primary selection button is replaced with a disabled button:  
  `Cannot Select Incompatible Component`
- An explanation of the conflict is highlighted directly above the button.
- If an earlier component is subsequently modified, creating retroactive conflicts with downstream components, `reevaluate_build_selections` immediately detects the mismatch and flags it in the UI header.

---

## 5. Verification & Test Evidence

All compatibility integration points are verified in:
- `tests/test_compatibility.py`: 47 tests passing (deterministic rule logic).
- `tests/test_guided_workflow.py`:
  - `test_cpu_motherboard_compatibility_check`: Passed.
  - `test_motherboard_ram_compatibility_check`: Passed.
  - `test_changing_earlier_component_triggers_revalidation`: Passed.
  - `test_unknown_compatibility_preserved`: Passed.
  - `test_upgrade_candidate_compatibility_against_retained_hardware`: Passed.
  - `test_upgrade_mode_with_unknown_retained_hardware`: Passed.
