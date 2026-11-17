# BuildWise-AI — Addendum: 3DMark Time Spy Scoring Formula and Terminology Correction

**Document Reference:** Formal Addendum to `experiments/gpu_benchmark_regression/gpu_readiness_audit.md`  
**Date:** November 7, 2026  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** Correction of UL 3DMark Time Spy scoring mathematics, official benchmark terminology, and machine learning target governance  

---

## 1. Purpose of Addendum

This addendum formally amends Section 3 of `experiments/gpu_benchmark_regression/gpu_readiness_audit.md`. Rather than silently overwriting the original audit documentation, this addendum documents the exact mathematical formulation specified in the official **UL 3DMark Technical Guide** and clarifies the strict terminology and weighting rules governing the regression target variable.

---

## 2. Mathematical Formulation Correction

In Section 3 of the original Phase 4A audit report, the 3DMark Time Spy Graphics Score formula was cited using a scaling constant of $165$:

$$\text{[Errant Phase 4A Formula] } S_{\text{graphics}} = 165 \times \frac{2}{\frac{1}{F_{\text{GT1}}} + \frac{1}{F_{\text{GT2}}}}$$

### Corrected Official UL 3DMark Formula

Per the official **UL 3DMark Technical Guide (Section 2.3: Time Spy Benchmark Scoring)**, the exact scaling coefficient for the Time Spy Graphics Score is **$164$**:

$$S_{\text{graphics}} = 164 \times \frac{2}{\frac{1}{F_{\text{GT1}}} + \frac{1}{F_{\text{GT2}}}}$$

Where:
- $F_{\text{GT1}}$ is the average rendering frame rate (in frames per second) measured across Graphics Test 1 (focusing on geometry processing, vertex shaders, tessellation, and shadow mapping).
- $F_{\text{GT2}}$ is the average rendering frame rate (in frames per second) measured across Graphics Test 2 (focusing on advanced compute shaders, dynamic illumination, and ray-marched volumetric lighting).
- The term $\frac{2}{\frac{1}{F_{\text{GT1}}} + \frac{1}{F_{\text{GT2}}}}$ represents the **harmonic mean** of the two graphics test frame rates, ensuring that a bottleneck in either graphical pipeline phase proportionately reduces the overall graphics score.

---

## 3. Standardized UL 3DMark Terminology

To eliminate ambiguity across dataset schemas, collection guides, and regression models, the following three distinct score definitions are formally established:

| Official Benchmark Term | Mathematical Representation | Primary Subsystem Stressed | Admissibility for GPU ML Target |
|---|:---:|---|:---:|
| **Time Spy Graphics Score** | $S_{\text{graphics}} = 164 \times \frac{2}{\frac{1}{F_{\text{GT1}}} + \frac{1}{F_{\text{GT2}}}}$ | Pure GPU rasterization, shading, compute, and VRAM bandwidth | **APPROVED (Sole Primary Target)** |
| **Time Spy CPU Score** | $S_{\text{cpu}} = 298 \times F_{\text{CPU}}$ | Host CPU multi-threaded physics and procedural simulation | **STRICTLY EXCLUDED (Not a GPU Metric)** |
| **Overall Time Spy Score** | $S_{\text{overall}} = \frac{1}{\frac{0.85}{S_{\text{graphics}}} + \frac{0.15}{S_{\text{cpu}}}}$ | Whole-system composite performance | **STRICTLY EXCLUDED (Target Leakage)** |

---

## 4. Weighted Harmonic Mean in the Overall Time Spy Score

The Overall Time Spy Score ($S_{\text{overall}}$) is computed as a **weighted harmonic mean** combining the Graphics Score and CPU Score with predetermined weights:

$$S_{\text{overall}} = \frac{1}{\frac{W_{\text{graphics}}}{S_{\text{graphics}}} + \frac{W_{\text{cpu}}}{S_{\text{cpu}}}} = \frac{1}{\frac{0.85}{S_{\text{graphics}}} + \frac{0.15}{S_{\text{cpu}}}}$$

Where:
- $W_{\text{graphics}} = 0.85$ (85% weight allocated to graphical rendering performance).
- $W_{\text{cpu}} = 0.15$ (15% weight allocated to host CPU physics simulation).

### Why the Overall Score Must Never Be Used as the ML Target

1. **Host CPU Leakage:** In review testbenches, the host processor varies significantly between publications (e.g., Core i9-14900K vs Core i9-13900K vs Ryzen 7 7800X3D). The $15\%$ CPU physics component introduces variance attributable to CPU clock speeds, thread scheduling, and DDR5 RAM timings rather than the GPU silicon under evaluation.
2. **Harmonic Penalty:** Because harmonic weighting heavily penalizes the lower of the two terms, a mid-tier GPU tested on an entry-level CPU would register an artificially suppressed overall score, while the exact same GPU tested on a flagship 14900K testbed would score significantly higher.
3. **Pure GPU Isolation:** The **Time Spy Graphics Score** strictly measures the GPU's isolated hardware capability ($F_{\text{GT1}}$ and $F_{\text{GT2}}$).

---

## 5. Machine Learning Governance Invariant

For all subsequent phases of BuildWise-AI GPU performance prediction:
- Target variable name: `score`
- Target metric specification: `benchmark_metric == 'Graphics Score'`
- Target suite specification: `benchmark_suite == '3DMark Time Spy'`
- Units: `pts` (integer points)
- Any source observation reporting a composite/overall score without isolating the Graphics Score is strictly disqualified and marked `rejected_composite_score`.
