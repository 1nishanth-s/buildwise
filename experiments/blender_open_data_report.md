# Blender Open Data CPU benchmark investigation

**Checked:** 2026-10-26  
**Scope:** Public Blender Open Data query summaries matched against the current
30-CPU catalog. This is a data-source investigation, not a trained model.

## Decision

Blender Open Data has useful, structured CPU benchmark summaries and broad
coverage of the catalog. The filtered query checked here returns a median score
and an observation count for each device-name group, not individual benchmark
submissions. The underlying snapshot is large, and a selective raw-submission
export was not confirmed. Therefore, no regression model was trained and no
grouped median was treated as an individual observation.

The queries found 29 confident catalog model matches and one review-required
match in Blender 4.5.0 on Windows. In Blender 5.2.0 on Windows there are 28
confident matches, one review-required match, and one CPU with no Windows
result. The catalog currently has only three consistently populated numeric
CPU specification features (`cores`, `threads`, and `boost_ghz`) and 22
distinct feature vectors among its 30 CPUs. These findings support further
data collection, not a claim that a predictive model is ready or reliable.

The existing editorial `performance_tier` labels remain unchanged and are not
used as benchmark targets. This work does not modify catalog data, price
observations, compatibility rules, or production recommendations.

## Source and access findings

Sources checked:

- [Blender Open Data](https://opendata.blender.org/)
- [About Blender Open Data](https://opendata.blender.org/about/)
- [Structured benchmark query](https://opendata.blender.org/benchmarks/query/)
- [Snapshot listing](https://opendata.blender.org/snapshots/)
- [Blender Benchmark scene/script CDN](https://opendata.blender.org/cdn/BlenderBenchmark2.0/)

The site provides a structured Search Data query interface. A query filtered
to `compute_type=CPU`, `operating_system=Windows`, and one
`blender_version`, grouped by `device_name`, returned JSON columns for device
name, median score, and number of benchmarks. The query can be filtered and
downloaded through the site, but the response inspected for this report is
aggregated; its rows do not contain the individual score distribution,
submission dates, or per-submission system metadata. The About page says raw
submission data is available from each benchmark's detail view. A direct,
filtered export of those individual rows was not established in this
investigation.

The latest snapshot listing inspected was dated 2026-10-25. Its archive was
101,872,349 bytes compressed and contains a JSONL file of 1,895,595,411 bytes
uncompressed. No selective archive-download mechanism was confirmed, so the
full snapshot was not downloaded. The About page describes license-free data
as a project principle; the snapshot's included `LICENSE.txt` identifies CC0
1.0 Universal. Preserve that notice and verify the license attached to the
specific artifact used in any later collection.

### Benchmark versions, scenes, and metadata

Blender application versions are separate from Blender Benchmark script
versions. The query exposed 19 application versions, from 3.0.1 through 5.2.0.
The script archive exposed versions 2.0.0, 2.0.1, 3.0.0, 3.1.0, 3.1.1, and
3.1.2. Do not treat those version numbers as interchangeable.

The About page describes the score as estimated Cycles path-tracing samples per
minute summed across the benchmark scenes; higher is better. It describes
seven selectable benchmarks. The public CDN directory exposed nine scene
assets (`barbershop_interior`, `bmw27`, `classroom`, `fishy_cat`, `junkshop`,
`koro`, `monster`, `pavillon_barcelona`, and `victor`). The query response
does not group or filter by scene, and the exact selectable scene set for each
application version was not verified here. Consequently, scene/version
comparability must be checked from individual submission metadata before
combining observations.

The official sample submission metadata includes a timestamp; launcher and
benchmark-script labels/checksums; scene label/checksum; Blender version,
build date/time and hash; system OS, machine type, CPU/GPU device names, CPU
socket/core/thread counts; compute device type; and run statistics such as
render time and peak device memory. Availability can vary by submission. The
query summaries do not expose these individual-record fields.

The platform also reports compute-type totals (CPU 175,530; CUDA 2,925; HIP
20,809; METAL 10,962; ONEAPI 3,214; OPTIX 133,371) and operating-system totals
(Linux 44,820; macOS 24,742; Windows 277,249) across its benchmark data at the
time checked. These are platform-wide counts, not CPU-only matched counts.
Keep CPU results separate from GPU results, and keep operating systems and
benchmark versions separate unless a documented comparison design justifies
otherwise.

## Catalog match and coverage

Matching was case-insensitive and required the catalog model string to occur
as a complete alphanumeric-bounded string in the raw device name. This avoids
prefix matches such as `9900X` against `9900X3D`. The single review-required
candidate was matched on the distinct SKU token `9950X3D2`: the catalog model
is `Ryzen 9 9950X3D2 Dual Edition`, while Blender reports `AMD Ryzen 9
9950X3D2 16-Core Processor`. The omission of “Dual Edition” warrants identity
review before attaching observations to that component.

Counts below are the API's number of benchmarks grouped under that raw device
name for the specified Windows/application-version query. They are not counts
of independent CPU models, and the grouped medians are not underlying
individual scores.

| Component ID | Catalog model | Blender 4.5.0 raw device name | 4.5.0 status / count | Blender 5.2.0 raw device name | 5.2.0 status / count |
| --- | --- | --- | ---: | --- | ---: |
| `cpu-r5-9600x` | Ryzen 5 9600X | AMD Ryzen 5 9600X 6-Core Processor | Exact / 151 | AMD Ryzen 5 9600X 6-Core Processor | Exact / 32 |
| `cpu-r7-9700x` | Ryzen 7 9700X | AMD Ryzen 7 9700X 8-Core Processor | Exact / 403 | AMD Ryzen 7 9700X 8-Core Processor | Exact / 52 |
| `cpu-r7-9800x3d` | Ryzen 7 9800X3D | AMD Ryzen 7 9800X3D 8-Core Processor | Exact / 989 | AMD Ryzen 7 9800X3D 8-Core Processor | Exact / 164 |
| `cpu-r9-9900x` | Ryzen 9 9900X | AMD Ryzen 9 9900X 12-Core Processor | Exact / 300 | AMD Ryzen 9 9900X 12-Core Processor | Exact / 40 |
| `cpu-i5-14600k` | Core i5-14600K | Intel Core i5-14600K | Exact / 93 | Intel Core i5-14600K | Exact / 22 |
| `cpu-cu7-265k` | Core Ultra 7 265K | Intel Core Ultra 7 265K | Exact / 253 | Intel Core Ultra 7 265K | Exact / 16 |
| `amd-ryzen-9-9950x3d2-dual-edition` | Ryzen 9 9950X3D2 Dual Edition | AMD Ryzen 9 9950X3D2 16-Core Processor | Review / 3 | AMD Ryzen 9 9950X3D2 16-Core Processor | Review / 28 |
| `amd-ryzen-9-9950x3d` | Ryzen 9 9950X3D | AMD Ryzen 9 9950X3D 16-Core Processor | Exact / 825 | AMD Ryzen 9 9950X3D 16-Core Processor | Exact / 153 |
| `amd-ryzen-9-9950x` | Ryzen 9 9950X | AMD Ryzen 9 9950X 16-Core Processor | Exact / 489 | AMD Ryzen 9 9950X 16-Core Processor | Exact / 78 |
| `amd-ryzen-9-9900x3d` | Ryzen 9 9900X3D | AMD Ryzen 9 9900X3D 12-Core Processor | Exact / 29 | AMD Ryzen 9 9900X3D 12-Core Processor | Exact / 8 |
| `amd-ryzen-7-9850x3d` | Ryzen 7 9850X3D | AMD Ryzen 7 9850X3D 8-Core Processor | Exact / 19 | AMD Ryzen 7 9850X3D 8-Core Processor | Exact / 15 |
| `cpu-intel-core-ultra-9-285k` | Core Ultra 9 285K | Intel Core Ultra 9 285K | Exact / 256 | Intel Core Ultra 9 285K | Exact / 89 |
| `cpu-intel-core-ultra-7-265kf` | Core Ultra 7 265KF | Intel Core Ultra 7 265KF | Exact / 61 | Intel Core Ultra 7 265KF | Exact / 7 |
| `cpu-intel-core-ultra-5-245kf` | Core Ultra 5 245KF | Intel Core Ultra 5 245KF | Exact / 3 | Intel Core Ultra 5 245KF | Exact / 2 |
| `cpu-intel-core-ultra-5-225f` | Core Ultra 5 225F | Intel Core Ultra 5 225F | Exact / 10 | Intel Core Ultra 5 225F | Exact / 6 |
| `cpu-intel-core-ultra-5-225` | Core Ultra 5 225 | Intel Core Ultra 5 225 | Exact / 2 | — | No Windows result |
| `cpu-intel-core-i7-14700k` | Core i7-14700K | Intel Core i7-14700K | Exact / 84 | Intel Core i7-14700K | Exact / 17 |
| `cpu-intel-core-i7-14700kf` | Core i7-14700KF | Intel Core i7-14700KF | Exact / 115 | Intel Core i7-14700KF | Exact / 6 |
| `cpu-intel-core-i9-14900k` | Core i9-14900K | Intel Core i9-14900K | Exact / 249 | Intel Core i9-14900K | Exact / 80 |
| `cpu-intel-core-i9-14900kf` | Core i9-14900KF | Intel Core i9-14900KF | Exact / 63 | Intel Core i9-14900KF | Exact / 11 |
| `amd-ryzen-9-7950x3d` | Ryzen 9 7950X3D | AMD Ryzen 9 7950X3D 16-Core Processor | Exact / 149 | AMD Ryzen 9 7950X3D 16-Core Processor | Exact / 39 |
| `amd-ryzen-9-7950x` | Ryzen 9 7950X | AMD Ryzen 9 7950X 16-Core Processor | Exact / 186 | AMD Ryzen 9 7950X 16-Core Processor | Exact / 19 |
| `amd-ryzen-9-7900x` | Ryzen 9 7900X | AMD Ryzen 9 7900X 12-Core Processor | Exact / 127 | AMD Ryzen 9 7900X 12-Core Processor | Exact / 24 |
| `amd-ryzen-9-7900` | Ryzen 9 7900 | AMD Ryzen 9 7900 12-Core Processor | Exact / 72 | AMD Ryzen 9 7900 12-Core Processor | Exact / 3 |
| `amd-ryzen-7-7800x3d` | Ryzen 7 7800X3D | AMD Ryzen 7 7800X3D 8-Core Processor | Exact / 304 | AMD Ryzen 7 7800X3D 8-Core Processor | Exact / 67 |
| `amd-ryzen-7-7700x` | Ryzen 7 7700X | AMD Ryzen 7 7700X 8-Core Processor | Exact / 91 | AMD Ryzen 7 7700X 8-Core Processor | Exact / 14 |
| `amd-ryzen-5-7600x` | Ryzen 5 7600X | AMD Ryzen 5 7600X 6-Core Processor | Exact / 104 | AMD Ryzen 5 7600X 6-Core Processor | Exact / 11 |
| `amd-ryzen-5-7600` | Ryzen 5 7600 | AMD Ryzen 5 7600 6-Core Processor | Exact / 56 | AMD Ryzen 5 7600 6-Core Processor | Exact / 9 |
| `amd-ryzen-7-8700g` | Ryzen 7 8700G | AMD Ryzen 7 8700G w/ Radeon 780M Graphics | Exact / 26 | AMD Ryzen 7 8700G | Exact / 8 |
| `amd-ryzen-5-8600g` | Ryzen 5 8600G | AMD Ryzen 5 8600G w/ Radeon 760M Graphics | Exact / 19 | AMD Ryzen 5 8600G | Exact / 1 |

### Coverage summary

| Query | Confident model matches | Review-required | No Windows match | Grouped benchmark-count total | Per-model count min / median / max | Models with at least 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Blender 4.5.0, CPU, Windows | 29 of 30 | 1 | 0 | 5,531 | 2 / 98.5 / 989 | 27 of 30 |
| Blender 5.2.0, CPU, Windows | 28 of 30 | 1 | 1 | 1,021 | 1 / 17 / 164 | 26 of 29 returned |

The API's **per-device-name median score** range was 177.86–687.05
samples/minute for the 30 matched names in 4.5.0 and 188.64–711.84
samples/minute for the 29 returned names in 5.2.0. These ranges summarize
grouped medians, not the distribution of individual usable observations. The
Core Ultra 5 225 with no 5.2.0 Windows result appeared once in the 5.2.0 Linux
CPU query (median 223.69 samples/minute); it is deliberately not added to the
Windows coverage.

The 4.5.0 query has substantially higher counts for most models, but counts
alone do not establish independent systems, consistent hardware setup, or
independent samples. Models with low counts in 5.2.0 include Ryzen 5 8600G
(1), Core Ultra 5 245KF (2), Ryzen 9 7900 (3), and the review-required
9950X3D2 (28; identity still needs review). The per-model score and count
summaries are useful for source coverage assessment only.

## Proposed separate observation dataset

Keep benchmark measurements in a new file or table; do not put them into
`data/components.csv` or the editorial `performance_tier` field. Recommended
fields:

| Field | Purpose |
| --- | --- |
| `observation_id` | Stable identifier for one submitted benchmark observation |
| `component_id` | Catalog ID only after reviewed identity matching; otherwise blank |
| `canonical_cpu_identity` | Reviewed make/model/revision when there is no catalog match |
| `match_status` | Exact, reviewed, ambiguous, or unmatched; retain reviewer decision |
| `raw_device_name` | Unmodified CPU device string reported by Blender |
| `benchmark_name` | Blender Benchmark |
| `blender_version` | Exact application version/build where available |
| `benchmark_script_version` | Exact launcher/script version, separate from Blender version |
| `scene_name` | Raw scene/workload name and checksum when present |
| `compute_type` | CPU only for this dataset; exclude GPU rows |
| `operating_system` | Raw OS value and version/distribution when supplied |
| `score` | Numeric reported benchmark score |
| `score_unit` | `samples/minute`, as defined by Blender for this score |
| `source_url` | Submission detail URL or stable source record reference |
| `submitted_at` | Source timestamp, if present |
| `retrieved_at` | ISO date/time when the record was retrieved |
| `system_metadata` | Original machine, CPU/core/thread, device and run metadata |
| `data_license` | License applicable to the source artifact, including CC0 notice |
| `raw_payload` | Original source record or a stable reference to the retained raw file |

Retain each underlying submission. A future per-CPU summary should be derived
only after selecting a compatible cohort with the same Blender application
version, benchmark script, scene set/workload, compute type, and OS. If an
aggregate is justified, report the median and interquartile range of individual
scores and the number of observations, while keeping raw rows and source
references. Do not pool CPU and GPU results, different operating systems, or
different Blender/scene versions into one target. Review differences in
machine, memory, power limits, cooling, and other reported system metadata;
stratify or exclude materially incomparable runs rather than assuming CPU
identity alone explains the score.

## Is regression training justified?

Not yet. The 4.5.0 Windows query has 30 matched device-name groups (29
confident, one requiring review), and 5.2.0 has 29 (28 confident, one
requiring review). The grouped benchmark counts look substantial for many
models, but the query supplies medians and counts rather than the
individual observations and metadata needed to preserve run-level provenance
and check heterogeneity. The alternative full snapshot is about 1.9 GB
uncompressed, and a smaller filtered raw export was not confirmed. No data
was fabricated, and no per-CPU group median was expanded into duplicate
examples.

The current catalog has `cores`, `threads`, and `boost_ghz` for all 30 CPUs,
but just 22 distinct input vectors. `base_ghz`, cache, structured
architecture/generation, and consistently defined power values are not
available across the catalog CPUs. These features should only be added after
collecting manufacturer specifications with clear definitions and sources.
Repeated benchmark runs for one model improve the estimate for that model but
do not create more distinct CPU identities for a model test split.

Next steps before a modest regression experiment:

1. Locate or obtain a filtered export of individual Blender CPU submissions,
   including source/detail references and timestamps, without downloading the
   entire snapshot unless its size and storage needs are accepted.
2. Review the 9950X3D2 catalog identity, then manually review all candidate
   device-name mappings and preserve the original reported names.
3. Verify each record's Blender version, script version, scene set, OS, score
   unit, and system metadata; exclude GPU rows and incompatible cohorts.
4. Collect consistently defined manufacturer CPU specifications (at minimum
   sourced core/thread counts and clocks; add architecture, cache, or power
   only with explicit vendor definitions and provenance).
5. If coverage remains adequate after these checks, compare a simple baseline
   with one or two small regressors using splits grouped by CPU identity. Keep
   preprocessing fitted on training data only, and report MAE/RMSE and
   uncertainty. A Blender score measures this rendering workload, not every
   dimension of CPU performance.

No benchmark regression was trained in this investigation. Existing
performance-tier labels and the production PC recommendation engine remain
separate.
