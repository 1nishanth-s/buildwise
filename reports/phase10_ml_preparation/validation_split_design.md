# BuildWise-AI — Phase 10: Validation Split and Data Leakage Prevention Design

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 10 — Machine Learning Dataset Audit, Feature Engineering and Training Data Preparation  
**Scope:** Group-Aware Cross-Validation Strategy, Leakage Mitigation, and Sample-Size Limitations  

---

## 1. The Critical Challenge of Hardware Data Leakage

In hardware performance modeling, naive random row-level splitting (e.g. standard `train_test_split` or standard `KFold`) produces severe **data leakage** and overly optimistic evaluation metrics:
- **Variant Duplication:** Modern GPU markets feature dozens of partner board SKUs (ASUS ROG Strix, MSI Gaming X, Gigabyte AORUS, Zotac Trinity) built upon the identical underlying silicon die (e.g., AD104 or Navi 32) running near-identical boost clocks. If one RTX 4070 variant is placed in the training set and another RTX 4070 variant is in the test set, the model merely memorizes the SKU's baseline score rather than learning true architectural relationships.
- **Platform Correlation:** CPU families (e.g., 14th Gen Intel Raptor Lake Refresh) share identical cache architectures, microcode, and IPC characteristics.

---

## 2. CPU Validation Strategy ($N = 180$)

### 2.1 Grouping Criteria: Silicon Platform Families
The 180 CPU components are partitioned into **10 independent platform generation groups** defined by silicon vendor and physical socket interface:

| Group Identifier | Physical Platform & Silicon Family | CPU Records Count | Proportion (%) |
|---|---|---:|---:|
| `amd_am4` | AMD Zen, Zen+, Zen 2, Zen 3 (Ryzen 1000–5000) | 47 | 26.11% |
| `intel_lga1700` | Intel Alder Lake, Raptor Lake, Raptor Lake Refresh (12th–14th Gen) | 42 | 23.33% |
| `amd_am5` | AMD Zen 4, Zen 5 (Ryzen 7000–9000) | 27 | 15.00% |
| `intel_lga1200` | Intel Comet Lake, Rocket Lake (10th–11th Gen) | 27 | 15.00% |
| `intel_lga1151` | Intel Skylake, Kaby Lake, Coffee Lake (6th–9th Gen) | 19 | 10.56% |
| `intel_lga1851` | Intel Arrow Lake (Core Ultra 200 Series) | 10 | 5.56% |
| `amd_str5` | AMD Zen 4 Threadripper 7000 Series | 3 | 1.67% |
| `amd_str4` | AMD Zen / Zen+ Threadripper 1000/2000 Series | 2 | 1.11% |
| `amd_strx4` | AMD Zen 2 Threadripper 3000 Series | 2 | 1.11% |
| `intel_lga2066` | Intel Skylake-X High-End Desktop Silicon | 1 | 0.56% |
| **Total** | **10 Independent Platform Groups** | **180** | **100.0%** |

### 2.2 Recommended CPU Cross-Validation Scheme
- **Primary Scheme:** **5-Fold `GroupKFold`** stratified by group size, ensuring zero platform overlap between training folds and validation folds.
- **Holdout Evaluation:** **`GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)`**, yielding:
  - Training Set: Approximately 140–144 records (~80%) across 7–8 groups.
  - Test Holdout Set: Approximately 36–40 records (~20%) across 2–3 complete held-out platform families.
- **Target Feasibility:** With $N = 180$ and 10 groups, statistical power is sufficient for comparing regression algorithms and verifying generalization to unseen CPU platforms.

---

## 3. GPU Validation Strategy ($N = 57$)

### 3.1 Grouping Criteria: Underlying Physical Silicon Die
The 57 benchmarked GPUs are partitioned into **14 physical silicon die groups** (sourced from `data/ml/gpu_family_groups_v1.csv`):

| Base Die Group ID | Silicon Die & Architecture | GPU Records Count | Proportion (%) |
|---|---|---:|---:|
| `amd_rdna3_navi32` | AMD Navi 32 (RX 7700 XT, RX 7800 XT) | 11 | 19.30% |
| `amd_rdna3_navi31` | AMD Navi 31 (RX 7900 XT, RX 7900 XTX, RX 7900 GRE) | 6 | 10.53% |
| `amd_rdna3_navi33` | AMD Navi 33 (RX 7600, RX 7600 XT) | 6 | 10.53% |
| `nvidia_ada_ad107` | NVIDIA AD107 (GeForce RTX 4060) | 5 | 8.77% |
| `nvidia_ampere_ga106` | NVIDIA GA106 (GeForce RTX 3060 12GB) | 5 | 8.77% |
| `nvidia_ada_ad104` | NVIDIA AD104 (GeForce RTX 4070, RTX 4070 Super, RTX 4070 Ti) | 4 | 7.02% |
| `nvidia_ada_ad103` | NVIDIA AD103 (GeForce RTX 4070 Ti Super, RTX 4080 Super) | 3 | 5.26% |
| `nvidia_ada_ad106` | NVIDIA AD106 (GeForce RTX 4060 Ti 8GB/16GB) | 3 | 5.26% |
| `nvidia_ampere_ga104` | NVIDIA GA104 (GeForce RTX 3060 Ti, RTX 3070) | 3 | 5.26% |
| `amd_rdna2_navi22` | AMD Navi 22 (RX 6700 XT, RX 6750 XT) | 3 | 5.26% |
| `amd_rdna2_navi23` | AMD Navi 23 (RX 6600, RX 6650 XT) | 3 | 5.26% |
| `nvidia_ampere_ga107` | NVIDIA GA107 (GeForce RTX 3050 6GB/8GB) | 2 | 3.51% |
| `intel_bmg_g21` | Intel BMG-G21 (Arc B570, Arc B580) | 2 | 3.51% |
| `nvidia_ada_ad102` | NVIDIA AD102 (GeForce RTX 4090) | 1 | 1.75% |
| **Total** | **14 Physical Silicon Die Groups** | **57** | **100.0%** |

### 3.2 Recommended GPU Cross-Validation Scheme & Critical Limitations
- **Primary Scheme:** **4-Fold or 5-Fold `GroupKFold`** using `base_die_group_id`.
- **Sample Size Constraint:** With $N = 57$ observations across 14 groups, holding out entire architectures (e.g. holding out all of Ada Lovelace or all of RDNA 3) leaves too few training samples to fit non-linear estimators reliably.
- **Defensible Methodology:** Die-level grouping prevents board-partner SKU leakage (e.g. testing an ASUS RTX 4070 against a Gigabyte RTX 4070), but models must be evaluated primarily on interpolation within represented architecture families.
- **Explicit Generalization Boundary:** The GPU model must **not** claim generalization to entirely unseen architectures (e.g. NVIDIA Blackwell or AMD RDNA 4). Predictions on unseen architectures must be treated with wide confidence intervals.

---

## 4. Leakage-Proof Preprocessing Design

To ensure zero information leakage during Phase 11 model fitting:
1. **Pipeline Encapsulation:** All numerical scaling (`StandardScaler` / `RobustScaler`), categorical one-hot encoding (`OneHotEncoder(handle_unknown="ignore")`), and missing value imputation (`SimpleImputer(strategy="median")`) must be wrapped within a scikit-learn `Pipeline` or `ColumnTransformer`.
2. **Fit on Train Only:** `fit()` is called strictly on the training partition of each fold; `transform()` is called on the validation / test partition. Preprocessing parameters are never computed globally across the entire dataset.
