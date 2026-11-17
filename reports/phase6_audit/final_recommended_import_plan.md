# Phase 6: Final Recommended Production Import Plan

**Date:** 2026-11-07  
**Status:** **AWAITING USER APPROVAL PRIOR TO EXECUTION**  
**Execution Gate:** Strictly non-destructive. No production file shall be modified until the user reviews these reports and explicitly gives authorization to proceed.

---

## 1. Pre-Import Backup Protocol

Immediately upon receiving user approval, the integration engine will create timestamped physical backups of all production datasets in `data/backup_pre_phase6/`:
- `data/components.csv` -> `data/backup_pre_phase6/components_pre_phase6.csv`
- `data/prices.csv` -> `data/backup_pre_phase6/prices_pre_phase6.csv`
- `data/benchmarks.csv` -> `data/backup_pre_phase6/benchmarks_pre_phase6.csv`

---

## 2. Phased Integration Sequence

```
[Phase 6 Integration Sequence]
           │
           ├── Step 1: Component Catalog Import
           │     ├── Filter out held candidates (CAND_GPU_142, CAND_GPU_143)
           │     ├── Append 787 verified candidate rows to data/components.csv (421 -> 1,208 rows)
           │     └── Run validate_components() to confirm zero schema violations
           │
           ├── Step 2: Compatibility Enrichment Merge
           │     ├── Update specs_json for the 239 production components using staged_enrichment.csv
           │     └── Validate that compatibility rules in src/compatibility.py evaluate cleanly
           │
           ├── Step 3: CPU Benchmarks Merge
           │     ├── Append 125 Cinebench R23 observations to data/benchmarks.csv (55 -> 180 rows)
           │     └── Verify 100% CPU coverage across all 180 CPUs
           │
           ├── Step 4: Corrected GPU Benchmarks Merge
           │     ├── Re-map candidate GPU benchmark foreign keys to match their component models
           │     ├── Discard unconfirmed Intel Arc B770 observation
           │     ├── Append 65 verified GPU observations to data/benchmarks.csv (57 -> 122 rows)
           │     └── Keep unaligned candidate observations in staging pending realignment
           │
           ├── Step 5: Indian Retail Prices Merge
           │     ├── Append 512 historical seller price observations to data/prices.csv (88 -> 600 rows)
           │     └── Run validate_prices() to confirm foreign key validity
           │
           └── Step 6: Post-Integration Regression Testing
                 ├── Execute validate_data.py
                 └── Run complete 113-test automated unit test suite
```

---

## 3. Approval Gate Checklist for User

Before granting authorization to execute this plan, please confirm agreement on:
1. **Holding `CAND_GPU_142` and `CAND_GPU_143`** (unconfirmed RX 9070/XT reference cards).
2. **Holding unconfirmed Intel Arc B770** and the 66 misaligned candidate GPU benchmark rows until foreign keys are realigned.
3. **Keeping the 9 proposed hardware categories separate** in `staged_proposed_categories.csv`.
4. **Proceeding with the import of the 787 accepted components, 125 CPU benchmarks, 512 retail prices, and 239 compatibility enrichments.**
