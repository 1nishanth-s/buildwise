# CPU Benchmark Regression Experiment (Cinebench R23 Multi-Core)

## 1. Overview & Objective

This experiment implements an isolated, reproducible Machine Learning regression pipeline to predict CPU Cinebench R23 Multi-Core performance scores (`pts`) from physical hardware specifications.

The dataset consists of **55 verified CPU benchmark observations** collected from published, trusted hardware reviews and databases, paired directly with hardware specifications from `data/components.csv`.

> **Status:** `EXPERIMENTAL`  
> **Target Variable:** `score` (Cinebench R23 Multi-Core score in points)  
> **Evaluation Protocol:** 5-fold `GroupKFold` grouped by verified base silicon die / microarchitecture family (strict zero-leakage enforcement).

---

## 2. Input Features & Data Governance

### Predictive Features (Strict 6-Feature Allowlist)
To guarantee strict independence from market dynamics and ensure genuine generalization from physical hardware properties, exactly six features are permitted:

| Feature Name | Type | Processing | Description |
| :--- | :--- | :--- | :--- |
| `cores` | Numeric (`int`) | StandardScaler | Physical core count (P-cores + E-cores for hybrid architectures) |
| `threads` | Numeric (`int`) | StandardScaler | Logical threads supporting simultaneous multithreading |
| `boost_clock_ghz` | Numeric (`float`) | StandardScaler | Maximum factory boost frequency in GHz |
| `tdp_w` | Numeric (`float`) | StandardScaler | Thermal Design Power rating in Watts |
| `brand` | Categorical (`str`) | OneHotEncoder | Microprocessor manufacturer (`AMD`, `Intel`) |
| `socket` | Categorical (`str`) | OneHotEncoder | Motherboard socket interface (`AM4`, `AM5`, `LGA1700`, `LGA1851`) |

### Strict Exclusions
The following fields are strictly prohibited from entering the feature matrix:
- **Component prices**, historical prices, seller names, and availability indicators.
- **Component IDs** (`component_id`), benchmark IDs (`benchmark_id`), and model names (`model`).
- **Performance tier labels** (e.g., Tier 1, Entry, High-End).
- **Benchmark source names** and review URLs.
- **CPU family group identifiers** (`group_id` is used solely for cross-validation splitting).

---

## 3. Data Leakage Prevention: Silicon Family Grouping

A critical risk identified during the dataset audit was the presence of twin SKUs (such as Intel K and KF variants: 12600K/KF, 12700K/KF, 14600K/KF, 14700K/KF, 14900K/KF, Core Ultra 7 265K/KF). These pairs possess identical 6-feature vectors and identical or near-identical multi-core benchmark scores because the only difference is an enabled/disabled integrated GPU.

A random cross-validation split would place one twin in the training fold and the other in the validation fold, leading to massive optimistic data leakage.

### GroupKFold Strategy
To completely eliminate leakage:
1. All 55 CPUs are mapped to **30 distinct silicon families / die designs** in `data/ml/cpu_family_groups.csv`.
2. Cross-validation uses **5-fold `GroupKFold`**.
3. For every fold, an automated assertion verifies that:
   $$\text{TrainGroups} \cap \text{ValGroups} = \emptyset$$
4. Preprocessing transformers (`StandardScaler`, `OneHotEncoder`) are strictly fit inside each training fold.

---

## 4. Evaluated Algorithms

We evaluated four algorithms under identical 5-fold GroupKFold cross-validation:

1. **DummyRegressor (Baseline):** Predicts the mean score of the training fold (`strategy='mean'`).
2. **Ridge Regression:** Pipeline with `StandardScaler` for numeric features, `OneHotEncoder(handle_unknown='ignore')` for categorical features, and conservative $L_2$ regularization ($\alpha = 1.0$).
3. **RandomForestRegressor:** Ensemble of 100 decision trees with `max_depth=3`, `min_samples_leaf=2`, and `random_state=42` to constrain overfitting on the 55-sample dataset.
4. **HistGradientBoostingRegressor:** Histogram-based gradient booster with `max_iter=40`, `max_depth=3`, `learning_rate=0.05`, `min_samples_leaf=3`, `early_stopping=False`, and `random_state=42`.

---

## 5. Cross-Validation Results

All metrics represent out-of-fold predictions across the complete 55-observation dataset:

| Model | Aggregated OOF MAE | Aggregated OOF RMSE | Aggregated OOF $R^2$ | Mean Fold MAE $\pm$ Std | Status vs Baseline |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **DummyRegressor (Baseline)** | 8,739.2 pts | 10,167.7 pts | -0.050 | 8,739.2 $\pm$ 2,343.9 pts | Baseline |
| **Ridge Regression ($\alpha=1.0$)** | **1,483.7 pts** | **1,939.3 pts** | **0.962** | **1,483.7 $\pm$ 479.6 pts** | **-83.02% error (Best)** |
| **RandomForestRegressor** | 1,985.0 pts | 2,655.9 pts | 0.928 | 1,985.0 $\pm$ 766.5 pts | -77.29% error |
| **HistGradientBoostingRegressor** | 2,181.9 pts | 2,952.5 pts | 0.911 | 2,181.9 $\pm$ 818.7 pts | -75.03% error |

### Key Findings
- **Ridge Regression is the top performer**, achieving an out-of-fold MAE of **1,483.7 pts** (an **83.02% error reduction** compared to DummyRegressor) and an $R^2$ of **0.962**.
- Ridge exhibits exceptional stability across all 5 folds ($R^2$ ranges between 0.935 and 0.972).
- Tree ensembles suffered slightly higher out-of-fold variance due to the small sample size (55 observations) and inability to extrapolate beyond the maximum seen core counts in training folds.

---

## 6. Out-of-Fold Error Analysis

### Top Prediction Errors (Ridge)
1. **Ryzen 9 9950X (Actual: 42,871 pts | Predicted: 37,530.1 pts | Error: -5,340.9 pts / -12.46%):**  
   Zen 5 features substantial architectural IPC gains (~16%) over Zen 4. Without microarchitecture generation features, the model underpredicts top-end Zen 5 multithreading.
2. **Core i9-14900K / 14900KF (Actual: 38,712 pts | Predicted: 43,208.2 pts | Error: +4,496.2 pts / +11.61%):**  
   The 6.0 GHz boost clock is a single-core peak. Under multi-core loads, thermal throttling against the 253W power limit reduces effective all-core frequency.
3. **Core Ultra 9 285K (Actual: 42,620 pts | Predicted: 39,026.9 pts | Error: -3,593.1 pts / -8.43%):**  
   Arrow Lake lacks Hyper-Threading (24 cores / 24 threads), but high architectural IPC compensates significantly.
4. **Core i3-12100F (Actual: 8,443 pts | Predicted: 4,969.1 pts | Error: -3,473.9 pts / -41.15%):**  
   Pure 4P/8T quad-core processor. The linear model calibrated on higher core counts under-weights low-core efficiency.

---

## 7. Artifacts & Reproduction

- **Dataset Preparation:**  
  Run `python experiments/cpu_benchmark_regression/prepare_dataset.py`  
  Outputs: `data/ml/cpu_benchmark_training_v1.csv`

- **Training & Cross-Validation:**  
  Run `python experiments/cpu_benchmark_regression/train.py`  
  Outputs:
  - `experiments/cpu_benchmark_regression/oof_predictions.csv`
  - `experiments/cpu_benchmark_regression/evaluation.json`
  - `models/experimental/cpu_cinebench_r23_v1.joblib`
  - `models/experimental/cpu_cinebench_r23_v1_metadata.json`

- **Error Audit & Inspection:**  
  Run `python experiments/cpu_benchmark_regression/evaluate.py`

---

## 8. Phase 3C: Feature Enrichment & Model V2 Comparison

Phase 3C investigated whether adding verified microarchitecture and cache features (`architecture`, `cache_l3_mb`, `cache_l2_mb`, `base_clock_ghz`) improves predictions across controlled feature sets using the identical 5-fold `GroupKFold` silicon-family protocol.

### Feature Ablation Configurations
1. **Set A (V1 Baseline):** `cores`, `threads`, `boost_clock_ghz`, `tdp_w`, `brand`, `socket` (6 features).
2. **Set B (Architecture):** Set A + `architecture` (7 features).
3. **Set C (Cache L3):** Set A + `cache_l3_mb` (7 features).
4. **Set D (Combined Arch + L3):** Set A + `architecture` + `cache_l3_mb` (8 features).
5. **Set E (Comprehensive):** Set A + `architecture` + `cache_l3_mb` + `cache_l2_mb` + `base_clock_ghz` (10 features).

### Cross-Validation Results Summary (Ridge Regression)

| Feature Set | Features | Aggregated OOF MAE | Aggregated OOF RMSE | Aggregated OOF $R^2$ | Mean Fold MAE $\pm$ Std | vs V1 Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Set A (V1 Baseline)** | 6 | 1,483.7 pts | 1,939.3 pts | 0.9618 | 1,483.7 $\pm$ 479.6 pts | Baseline |
| **Set B (Architecture)** | 7 | 1,253.1 pts | 1,620.6 pts | 0.9733 | 1,253.1 $\pm$ 492.0 pts | -15.54% error |
| **Set C (Cache L3)** | 7 | 1,499.1 pts | 1,988.7 pts | 0.9598 | 1,499.1 $\pm$ 502.1 pts | +1.04% error |
| **Set D (Combined Arch + L3)** | 8 | 1,276.4 pts | 1,664.0 pts | 0.9719 | 1,276.4 $\pm$ 505.8 pts | -13.97% error |
| **Set E (Comprehensive)** | 10 | **1,125.7 pts** | **1,484.8 pts** | **0.9776** | **1,125.7 $\pm$ 412.8 pts** | **-24.13% error (Best)** |

### Error Reduction on Top Outlier Processors

| Processor Model | Actual Score | V1 (Set A) Error | V2 (Set E) Error | Absolute Error Reduction |
| :--- | :---: | :---: | :---: | :---: |
| **Ryzen 9 9950X** | 42,871 pts | -5,340.9 pts (-12.5%) | -3,504.7 pts (-8.2%) | **-1,836.2 pts (-34.4%)** |
| **Core i9-14900K / KF** | 38,712 pts | +4,496.2 pts (+11.6%) | +3,789.6 pts (+9.8%) | **-706.6 pts (-15.7%)** |
| **Core Ultra 9 285K** | 42,620 pts | -3,593.1 pts (-8.4%) | -2,848.9 pts (-6.7%) | **-744.2 pts (-20.7%)** |
| **Core i3-12100F** | 8,443 pts | -3,473.9 pts (-41.2%) | -1,947.6 pts (-23.1%) | **-1,526.3 pts (-43.9%)** |

### V2 Model Artifacts
- **Model Pipeline Artifact:** `models/experimental/cpu_cinebench_r23_v2.joblib`
- **Metadata Specification:** `models/experimental/cpu_cinebench_r23_v2_metadata.json`
- **Feature Comparison Table:** `experiments/cpu_benchmark_regression/feature_comparison.csv`
- **V2 Out-of-Fold Predictions:** `experiments/cpu_benchmark_regression/v2_oof_predictions.csv`
- **V2 Evaluation Metrics:** `experiments/cpu_benchmark_regression/v2_evaluation.json`
- **Reproduction Command:** `python experiments/cpu_benchmark_regression/train_v2.py`
