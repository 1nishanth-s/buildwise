# CPU performance-tier experiment

This isolated, beginner-friendly experiment reads CPU specifications and the
existing `performance_tier` labels from `data/components.csv`. It does not
modify the catalog, train the production recommendation engine, or change
production recommendations.

## Run on Windows

From the project root:

```bat
.venv\Scripts\python.exe experiments\performance_tier\train.py
```

The script writes its audit and evaluation to
`experiments/performance_tier/evaluation.json`. Override the catalog or output
path with `--components PATH` and `--output PATH`.

## Data audit and feature choices

The current catalog contains 30 CPUs labeled `entry` (3), `mid` (7), `high`
(8), and `flagship` (12). These are preserved editorial assessments, not
verified benchmark ground truth. Their per-CPU provenance and a consistent
labeling rubric are not recorded.

Only the existing numeric `cores`, `threads`, and `boost_ghz` fields are used.
Each is present on all 30 labeled CPUs. No additional feature was safe to add
from this catalog:

- `base_ghz`, `cache_mb`, and `l3_cache_mb` are absent on all 30 CPUs.
- Structured `architecture` and `generation` fields are absent on all 30.
  Inferring these from product names or free-text notes would be inconsistent
  and is intentionally avoided.
- `tdp_w` is numeric on all 30, but its meaning is not normalized across
  manufacturers and product families; it is not a directly comparable power
  measurement in this dataset.
- `socket` has three values and `ram_type` has one value (DDR5 for all CPUs).
  Socket is a platform compatibility proxy rather than a reliable performance
  measure, and a constant feature carries no information.
- `use_cases` and `supported_chipsets` are present but are categorical lists
  describing editorial recommendations/platform compatibility, not
  consistently measured CPU performance.

The evaluation JSON lists every exact input-feature group with its feature
values, component IDs, original labels, and a conflict flag. There are 22
distinct vectors among the 30 CPUs. Six vectors are repeated; the
`(12 cores, 24 threads, 5.6 GHz boost)` group contains `cpu-r9-9900x`
(`flagship`) and `amd-ryzen-9-7900x` (`high`). Their labels conflict. Records
and labels remain unchanged.

## Group-aware evaluation

Alongside the original repeated stratified 3-fold record-level CV, the script
reports 20 seeded repeats of stratified 3-fold group CV. A group is the exact
normalized numeric input vector, and all records with that vector are kept
together. The same fixed models are trained independently within each
training fold; logistic-regression scaling remains inside its pipeline.
Accuracy, fixed-four-label macro-F1 and balanced accuracy, fold-level label
counts, distinct groups per split, pooled per-class metrics, and confusion
matrices are recorded. For consistent four-class balanced accuracy, a label
absent from a test fold contributes zero recall; such folds are explicitly
marked and are not meaningful full-class tests.

The grouped evaluation cannot meaningfully test all four classes in every
fold: the three `entry` CPUs occupy only two distinct feature groups, fewer
than the three groups required to put entry examples in each test fold.
Consequently some grouped test folds omit `entry` (the report records exactly
which ones), even though the corresponding training folds retain entry
examples. Group-aware results are an exploratory diagnostic, not a reliable
four-class generalization estimate. Do not use their score or the record-level
CV score as proof of performance on unseen CPU models.

Current fixed-seed results (mean ± population fold standard deviation):

| Model | Record-level accuracy | Record-level macro-F1 | Record-level balanced accuracy | Grouped accuracy | Grouped macro-F1 | Grouped balanced accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Majority baseline | 0.400 ± 0.000 | 0.143 ± 0.000 | 0.250 ± 0.000 | 0.400 ± 0.072 | 0.142 ± 0.018 | 0.250 ± 0.000 |
| Decision tree | 0.597 ± 0.121 | 0.573 ± 0.151 | 0.635 ± 0.137 | 0.569 ± 0.125 | 0.459 ± 0.139 | 0.520 ± 0.144 |
| Class-balanced tree | 0.620 ± 0.122 | 0.580 ± 0.157 | 0.645 ± 0.143 | 0.606 ± 0.134 | 0.491 ± 0.121 | 0.547 ± 0.132 |
| Small random forest | 0.592 ± 0.135 | 0.544 ± 0.167 | 0.609 ± 0.143 | 0.601 ± 0.157 | 0.461 ± 0.143 | 0.504 ± 0.141 |
| Scaled logistic regression | 0.558 ± 0.127 | 0.527 ± 0.150 | 0.593 ± 0.137 | 0.557 ± 0.162 | 0.447 ± 0.177 | 0.493 ± 0.187 |

The class-balanced tree has the highest average on these grouped folds, but the
entry class is absent from 20 of the 60 grouped test folds. This is not
evidence of a robust improvement; no model is selected from the grouped
results.

## Training-data improvement plan

Collect only sourced, clearly defined specifications before considering them
as features:

- Base and boost clock in GHz, with the manufacturer's meaning and core type
  identified where relevant.
- Architecture and generation as separate manufacturer-defined fields.
- Cache amounts with level and scope explicit (for example, L2 and L3, per
  core/chiplet/package as reported); do not combine unlike cache values into
  one ambiguous total.
- Power values with the vendor's original metric name, numeric value, unit,
  definition, and source. Keep terms such as AMD TDP and Intel processor base
  power / maximum turbo power separate; do not normalize them into one
  unlabeled `tdp_w` field.

For each specification, retain manufacturer/source name, official source URL,
verification date, and the original source wording or a citation to it. Do not
infer architecture, generation, cache, clock, or power from model names or
free-text notes. Missing fields remain missing until checked.

Keep measured benchmark results in a separate observation table/file, not in
the component's editorial tier field. A proposed benchmark observation schema:

| Field | Meaning |
| --- | --- |
| `observation_id` | Stable identifier for this observation |
| `component_id` | Exact catalog CPU identity, with a documented model/revision |
| `benchmark_name` | Benchmark application or suite name |
| `suite_version` | Exact suite/application version |
| `workload` | Named test, subtest, or workload configuration |
| `score` | Numeric measured result |
| `measurement_unit` | Explicit unit or declared unitless score |
| `source_url` | URL for the result or original test report |
| `collected_at` | ISO collection date (`YYYY-MM-DD`) |
| `test_context` | OS, software/configuration, BIOS, memory, cooling, power limits, and other relevant setup |
| `provenance_notes` | Test method, whether independently measured/reported, and any caveats |

Do not compare observations across incompatible suite versions, workloads,
units, or materially different test setups without a documented normalization
method. Retain the raw reported score and context; do not invent a composite
benchmark score.

For future editorial tier labels, document the intended workload scope first
(for example, gaming versus multi-threaded productivity), a written rubric and
decision procedure before reviewing candidate CPUs, the evidence sources and
publication dates for each decision, the reviewer/decision provenance, and a
short rationale with uncertainty or disagreements. Keep the label in its own
field with rubric version and review date. Do not backfill or change current
labels based on model output; maintain a history if future human review
revises a label.

IDs, product names, brands, URLs, notes, and labels are never model features.
No component IDs, labels, compatibility rules, or price observations are
changed by this experiment.

## Model comparison

Five fixed, modest models are compared on the same 20 repeats of stratified
3-fold cross-validation (60 folds total), with seed 42:

- Most-frequent-class baseline.
- Existing shallow decision tree (`max_depth=3`).
- The same tree with balanced class weights.
- A small balanced random forest (100 trees, depth 3, minimum leaf size 2).
- Logistic regression with `StandardScaler` and balanced class weights.

Scaling is part of a scikit-learn pipeline, so it is fitted on each training
fold only. Each model is otherwise trained only on that fold's training data.
The JSON reports mean and population standard deviation across folds for
accuracy, macro-F1, and balanced accuracy, plus pooled per-class precision,
recall, F1, support, and confusion matrices. Fold standard deviations are
descriptive variability, not confidence intervals; repeated folds are not
independent samples.

The existing 9-example holdout remains a preliminary historical comparison:
the majority baseline and tree each had 44.4% accuracy; macro-F1 was 0.154
and 0.488, respectively. It is not used to select settings. The cross-validation
model selection uses a cautious, explicit consistency rule: a candidate must
improve mean macro-F1, improve macro-F1 on more than half of matched folds,
and be no worse in mean accuracy or balanced accuracy than the current tree.
Even if a candidate passes, model selection on only 30 examples is uncertain.
The tree's old single-holdout macro-F1 advantage is not proof of generalization.

This experiment is small and educational. It cannot establish that a model
predicts real-world gaming or productivity performance, nor justify using the
model for buying decisions.
