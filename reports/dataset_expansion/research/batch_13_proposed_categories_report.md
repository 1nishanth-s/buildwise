# Batch 13: Proposed Additional Hardware Categories Research Report

**Date:** 2026-11-07  
**Total Proposed Categories:** 9 categories  
**Output Staging File:** `reports/dataset_expansion/candidates/staged_proposed_categories.csv`  

---

## 1. Executive Summary & Architectural Rationale

To advance BuildWise-AI from a component-only picker to an end-to-end PC building advisor, nine supplementary hardware categories have been designed. Each proposed category includes exact schema field recommendations, automated compatibility enforcement rules, and verified retail products with market pricing in India:

| ID | Category Name | Role in Recommendation Engine | Primary Compatibility Dependency |
|---|---|---|---|
| **PROP_CAT_01** | **Case Fans** | Optimize chassis airflow, prevent thermal throttling | Case mount locations & motherboard 4-pin PWM / 5V ARGB headers |
| **PROP_CAT_02** | **Thermal Interface Material** | CPU/GPU thermal transfer, repasting upgrades | Surface material compatibility (Liquid metal forbidden on aluminum) |
| **PROP_CAT_03** | **Wi-Fi & Bluetooth Cards** | Wireless connectivity for non-Wi-Fi boards | PCIe physical slot clearance & internal USB 2.0 Bluetooth header |
| **PROP_CAT_04** | **PCIe Expansion Cards** | High-speed 10GbE LAN, studio audio DACs, USB hubs | Motherboard PCIe lane bifurcation and physical slot arrangement |
| **PROP_CAT_05** | **GPU Anti-Sag Brackets** | Prevent PCB warp & slot damage for GPUs >= 1.2kg | Case shroud clearance & available lower PCIe slots |
| **PROP_CAT_06** | **UPS Units** | Safeguard against Indian power cuts & voltage spikes | System peak wattage sizing (UPS W >= System W * 1.25) & Pure Sine Wave |
| **PROP_CAT_07** | **OS Licenses** | Complete build budgeting & platform security | TPM 2.0, Secure Boot, and RAM capacity thresholds (>128GB -> Pro) |
| **PROP_CAT_08** | **Fan & ARGB Controllers** | Expand limited motherboard fan and RGB headers | PSU SATA power injection & internal USB 2.0 data connection |
| **PROP_CAT_09** | **Storage Accessories** | Repurpose replaced SSDs into portable USB-C drives | M.2 Key type (M-Key NVMe vs B+M SATA) & USB-C speed matching |

---

## 2. Integration Roadmap for BuildWise-AI

1. **Build Mode Enhancement:**
   - When a budget case with 0 or 1 fan is selected, auto-suggest a 3-pack of PWM fans (`PROP_CAT_01`).
   - When a GPU exceeding 300mm / 1.2kg is configured, auto-attach an anti-sag pillar (`PROP_CAT_05`).
   - Sizing a matching UPS (`PROP_CAT_06`) tailored to calculated total system power for Indian users.
2. **Upgrade Mode Enhancement:**
   - When a user upgrades their M.2 SSD, automatically recommend an external NVMe enclosure (`PROP_CAT_09`) to convert their previous SSD into high-speed portable storage.
   - When upgrading a high-TDP processor, prompt for thermal compound (`PROP_CAT_02`).

All proposed categories are staged in `staged_proposed_categories.csv` without modifying existing schema definitions.
