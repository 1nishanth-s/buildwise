# Reference Gaming Build: Final End-to-End Acceptance Audit & Actionability Report

**Audit & Update date:** 2026-10-26 (Antigravity: Final End-to-End Acceptance Audit)  
**Build budget used for the app check:** ₹300,000  
**Production status:** Verified and audited end-to-end. Recommendation engine features full 8-category coverage with CPU cooler compatibility checks (socket support and case clearance), refined RAM speed/profile/CPU limits/QVL evaluation, dated historical price handling, and verified Indian retailer listing evidence. Complete 8-category recommendation total: **₹214,307** (dynamically calculated by recommendation engine). Overall compatibility status: **`unknown`** (cooler checks pass with 15 mm margin, but RAM EXPO profile remains unverified on motherboard QVL). All 128 catalog components, 29 price observations, quarantined candidate dataset (671 components), and ML experiment remain protected and intact.

---

## 1. Executive Summary

This actionability update resolves the missing cooler in the BuildWise-AI reference gaming recommendation by adding a verified, in-stock AM5 cooler to the production dataset:

* **Catalog & Price Preservation:** The production catalog now contains exactly **128 components** and **29 price observations**. The Cooler Master Hyper 212 Black (`cooler-cm-hyper-212-black`) and all prior 28 price observations (including the ₹29,370 Corsair RM750x user planning estimate) were preserved without modification.
* **New Verified Cooler Added:** The **DeepCool AK400 Black** (part number `R-AK400-BKNNMN-G-1`) was verified via official DeepCool documentation and added to [`data/components.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/data/components.csv) as `cooler-deepcool-ak400-black`.
* **Verified Seller Price Observation Added:** An active, in-stock seller listing from Computech Store at **₹2,290** was verified on October 26, 2026, and appended to [`data/prices.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/data/prices.csv) (`price-cooler-deepcool-ak400-computech-20261026-113610`).
* **Physical Clearance Confirmed:**
  * **Cooler Height:** The DeepCool AK400 Black measures **155 mm** in height.
  * **Case Clearance:** The NZXT H5 Flow (2024 Edition, `CC-H52FB-01`) officially supports CPU coolers up to **170 mm**.
  * **Nominal Clearance:** **15 mm** of vertical clearance (`compatible`).
  * **GPU Clearance:** 304 mm card length vs 410 mm official case clearance leaves **106 mm of clearance** (`compatible`).
* **Cooling Adequacy Assessment:** AMD's official specifications confirm the Ryzen 5 9600X ships **without a cooler** (PIB) and has a **default TDP of 65W**. DeepCool rates the AK400 for up to 220W heat dissipation via 4 direct-touch heatpipes and a 120mm FDB fan. This provides generous advertised headroom for 65W gaming operation. However, real-world temperatures and noise levels depend on ambient temperature, fan curves, and CPU boost/PBO modes, which cannot be guaranteed by advertised TDP ratings alone.
* **Recommendation Results at ₹300,000 Budget:**
  * **Category Coverage:** All **8 required categories** (CPU, Motherboard, GPU, RAM, Storage, Case, PSU, Cooler) are selected.
  * **Build Status:** **`complete`** (0 missing categories).
  * **Recorded-Price Total:** **₹214,307** (includes DeepCool AK400 Black at ₹2,290; all 8 components fit within budget).
  * **Indian Market Presence:** All **8 selected components** have verified Indian retailer listings (`verified_indian_listing`).
  * **Interface Simplification:** User-facing "available-first" ranking mode and freshness sliders were removed; recommendation relies on transparent lowest recorded prices with clear observation dates.
  * **Planning Estimates:** Does not count the preserved ₹29,370 planning estimate (`includes_estimates: False`); selects the separate ₹29,370 Global Klamp seller observation on Amazon.in.
  * **Overall Compatibility:** Evaluated as **`unknown`**. The DeepCool AK400 Black passes both CPU cooler socket support (`compatible`, AM5) and case clearance (`compatible`, 15 mm margin). However, overall compatibility remains `unknown` because the G.Skill Flare X5 DDR5-6000 EXPO overclock profile is unconfirmed on the ASUS TUF Gaming B850-PLUS WiFi Memory QVL.
* **Conclusion:** The recommendation now achieves complete category coverage with priced components. However, **it should not be labeled confirmed purchasable or fully validated**. Seller availability reflects point-in-time checks (not guaranteed stock or checkout reservations), delivery/tax costs vary by location, and memory EXPO stability remains uncertified.

---

## 2. Component Identities and Evidence Base

All nine cataloged products involved in the reference gaming build were verified:

| Component ID | Catalog Identity | Official / Primary Source | Status & Verified Findings |
|---|---|---|---|
| `cpu-r5-9600x` | AMD Ryzen 5 9600X | [ASUS CPU Support](https://www.asus.com/us/motherboards-components/motherboards/tuf-gaming/tuf-gaming-b850-plus-wifi/helpdesk_cpu/); [AMD 9600X Specs](https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-5-9600x.html) | AM5 socket, 6 cores/12 threads, 65W default TDP. AMD officially confirms **Thermal Solution (PIB): Not Included**. Validated by ASUS across all BIOS versions for the TUF B850 board. |
| `mb-asus-tuf-gaming-b850-plus-wifi` | ASUS TUF Gaming B850-PLUS WiFi | [ASUS Tech Specs](https://www.asus.com/motherboards-components/motherboards/tuf-gaming/tuf-gaming-b850-plus-wifi/techspec/) | ATX form factor, AMD B850 chipset, AM5 socket, 4x DDR5 DIMMs (up to 256 GB), M.2 PCIe 5.0/4.0 NVMe support, dual 8-pin 12V CPU power inputs. |
| `gpu-nvidia-asus-prime-rtx5070-o12g` | ASUS Prime GeForce RTX 5070 12GB GDDR7 OC Edition (`PRIME-RTX5070-O12G`) | [ASUS GPU Tech Specs](https://www.asus.com/motherboards-components/graphics-cards/prime/prime-rtx5070-o12g/techspec/) | 12GB GDDR7, official dimensions **304 x 126 x 50 mm** (2.5 slots). Requires 1x 16-pin power connector; ASUS recommends a 750W system PSU. |
| `gskill-flare-x5-ddr5-6000-cl36-32gb` | G.Skill Flare X5 32GB (2x16GB) DDR5-6000 CL36 (`F5-6000J3636F16GX2-FX5`) | [G.Skill Specification](https://www.gskill.com/specification/165/396/1662622664/F5-6000J3636F16GX2-FX5-Specification); [ASUS Memory QVL](https://www.asus.com/motherboards-components/motherboards/tuf-gaming/tuf-gaming-b850-plus-wifi/helpdesk_qvl_memory/) | DDR5, 32GB kit (2x16GB), AMD EXPO profile at 6000 MT/s (36-36-36-96 at 1.35V), SPD default 4800 MT/s at 1.10V. **Not explicitly listed on ASUS TUF B850 Memory QVL**. EXPO stability remains unconfirmed. |
| `samsung-990-pro-1tb` | Samsung 990 PRO 1TB | [Prime ABGB Listing](https://www.primeabgb.com/online-price-reviews-india/samsung-990-pro-1tb-pci-express-4-0-x4-gen-4-nvme-ssd-mz-v9p1t0bw/) | M.2 2280 form factor, PCIe Gen 4.0 x4 NVMe protocol. Fully compatible with motherboard M.2 slot specifications. |
| `psu-750w-gold` | Corsair RM750x (2024), 750W 80+ Gold | [Corsair RM750x Product Page](https://www.corsair.com/us/en/p/psu/cp-9020285-na/rm750x-fully-modular-atx-power-supply-cp-9020285-na) | 750W continuous rated output, ATX 3.1 compliant, native 12V-2x6 (12+4 pin) cable and dual EPS/ATX 12V 8-pin cables. Matches GPU and motherboard power requirements. |
| `case-nzxt-h5-flow-2024` | NZXT H5 Flow (2024 Edition, `CC-H52FB-01`) | [NZXT Official Specs](https://support.nzxt.com/hc/en-us/articles/40225168535451-H5-Flow-2024-Specs) | ATX mid-tower. Official specs confirm: **Max CPU Cooler Clearance: 170 mm**; **Max GPU Clearance: 410 mm** (without front radiator); ATX/Micro-ATX/Mini-ITX motherboard support. |
| `cooler-deepcool-ak400-black` *(New)* | DeepCool AK400 Black (`R-AK400-BKNNMN-G-1`) | [DeepCool Official Specs](https://www.deepcool.com/products/Cooling/cpuaircoolers/AK400-Performance-CPU-Cooler-1851-1700-AM5/2024/15222.shtml); [Computech Store](https://computechstore.in/product/deepcool-ak400-cpu-air-cooler-black/) | Air cooler with 4 direct-touch 6mm copper heatpipes, matrix fin array, 120mm FDB fan (500–1850 RPM). Official dimensions **120 x 97 x 155 mm (Height: 155 mm)**. Supports AM5/AM4 & LGA 1700/1200/115x. Rated up to 220W dissipation. |
| `cooler-cm-hyper-212-black` *(Preserved)* | Cooler Master Hyper 212 Black (`RR-S4KK-25SN-R1`) | [Cooler Master Official Specs](https://www.coolermaster.com/en-global/products/hyper-212-black/) | Air cooler with 4 direct-contact copper heatpipes, SickleFlow 120 Edge PWM fan. Official dimensions 125 x 74 x 152 mm (Height: 152 mm). AM5/AM4 support. Preserved in catalog as an unpriced alternative. |

---

## 3. Verified Cooler Addition & Price Observation

### DeepCool AK400 Black Details:
* **Manufacturer:** DeepCool
* **Model:** AK400 Black
* **Part Number:** `R-AK400-BKNNMN-G-1`
* **Sockets Supported:** AMD AM5, AMD AM4, Intel LGA1700, LGA1200, LGA1151, LGA1150, LGA1155
* **Dimensions (L x W x H):** 120 x 97 x 155 mm (Height: 155 mm)
* **Heat Dissipation Rating:** Up to 220 W

### Price Observation Recorded in `data/prices.csv`:
* **Price ID:** `price-cooler-deepcool-ak400-computech-20261026-113610`
* **Component ID:** `cooler-deepcool-ak400-black`
* **Seller:** Computech Store
* **Price (INR):** ₹2,290
* **Direct URL:** `https://computechstore.in/product/deepcool-ak400-cpu-air-cooler-black/`
* **Checked At:** `2026-10-26T11:36:10+05:30`
* **Availability:** `available` (confirmed in stock at check time)
* **Price Type:** `seller_observation`
* **Provenance:** (empty; verified seller observation)

---

## 4. Hardware Compatibility Assessment

| Check Item | App Status | Basis & Supporting Evidence | Real-World Caveats / Gaps |
|---|---|---|---|
| **CPU Socket & Chipset** | `compatible` | Both specify AMD AM5; CPU supports AMD B850; ASUS official CPU support table validates 9600X on all BIOS versions. | BIOS update recommended for latest AGESA microcode. |
| **RAM Generation & Capacity** | `compatible` | CPU, Motherboard, and RAM are DDR5. 32 GB kit is well within the motherboard's 256 GB limit. | Basic JEDEC operation (4800 MT/s at 1.1V) is supported. |
| **RAM 6000 MT/s EXPO Profile** | `unknown` | G.Skill documents tested 6000 MT/s at 1.35V profile. AMD official Ryzen 5 9600X specs support DDR5-5600 for 2 DIMMs; 6000 MT/s is an EXPO overclock profile. Evaluated via `check_ram_speed_qvl`. | **Unlisted on ASUS TUF B850 Memory QVL**. Missing from the official QVL leaves profile stability unverified (`unknown`), but is not marked `incompatible`. Real-world EXPO stability depends on CPU memory controller quality and board trace routing. |
| **Motherboard to Case Form Factor** | `compatible` | ASUS TUF B850 is ATX; NZXT H5 Flow (2024) officially supports ATX. | None. Stand-off positions and backplate align. |
| **Storage Interface & Size** | `compatible` | Samsung 990 PRO is M.2 2280 PCIe 4.0 x4 NVMe; ASUS B850 officially supports M.2 2280 NVMe across multiple slots. | None. |
| **GPU Physical Length to Case** | `compatible` | ASUS Prime RTX 5070 length is 304 mm; NZXT H5 Flow (2024) official spec supports up to 410 mm GPU length. | 106 mm clearance bare. Front radiator/fan installation would reduce clearance by 55–60 mm (still leaves ~45–50 mm margin). |
| **CPU Cooler Socket Mounting** | `compatible` | DeepCool officially documents AM5 bracket support for `R-AK400-BKNNMN-G-1`; verified by `check_cooler_socket`. | Installs onto standard AM5 stock motherboard backplate. |
| **CPU Cooler Height to Case** | `compatible` | Cooler height is 155 mm; NZXT H5 Flow (2024) officially supports coolers up to 170 mm; verified by `check_cooler_case`. | **15 mm physical clearance** (clearance margin calculated as 170 - 155 = 15 mm). |
| **CPU Cooler Thermal Adequacy** | `unknown` (untested) | 9600X is 65W default TDP. AK400 Black has 4 direct-touch heatpipes, 220W dissipation rating, and 120mm FDB fan. | Ample advertised headroom for 65W gaming. Real-world thermals depend on ambient temperature, airflow, and power limits; no temperature guarantee is inferred from advertised TDP. |
| **PSU Capacity & GPU Power Cable** | `compatible` | Corsair RM750x provides 750W continuous power (matches ASUS recommendation); provides native 12V-2x6 cable (matches 16-pin GPU requirement). | Component rating match. Does not replace bench-testing transient spike behavior. |

---

## 5. Recommendation Engine Reconciliation (₹300,000 Budget)

Running `build_recommendation` in `app.py` with `budget_inr=300000`, `purpose="gaming"`, and `includes_peripherals=False` produces the following reconciliation:

```
Required Categories (8): cpu, motherboard, gpu, ram, storage, case, psu, cooler
Selected Categories (8): cpu, motherboard, gpu, ram, storage, case, psu, cooler
Missing Categories: []
Build Status: complete
Includes Estimates: False
Overall Compatibility: unknown (cooler socket and height clearance are compatible with 15 mm margin; RAM DDR5-6000 EXPO profile remains unverified on motherboard QVL)
Price Selection Mode: lowest_price
Total Price: ₹214,307
```

### Component Selection Breakdown & Indian Market Evidence

| Category | Component ID | Brand & Model | Recorded Price (INR) | Indian Retailer Listing | Check Date | Indian Market Presence | Availability at Check |
|---|---|---|---:|---|---|---|---|
| **CPU** | `cpu-r5-9600x` | AMD Ryzen 5 9600X | ₹25,959 | RetailNet on Flipkart | 2026-10-21 | `verified_indian_listing` | unknown |
| **Motherboard** | `mb-asus-tuf-gaming-b850-plus-wifi` | ASUS TUF Gaming B850-PLUS WiFi | ₹27,769 | Prime ABGB | 2026-10-21 | `verified_indian_listing` | available |
| **GPU** | `gpu-nvidia-asus-prime-rtx5070-o12g` | ASUS Prime RTX 5070 12GB OC | ₹87,622 | Prime ABGB | 2026-10-17 | `verified_indian_listing` | unavailable |
| **RAM** | `gskill-flare-x5-ddr5-6000-cl36-32gb` | G.Skill Flare X5 32GB DDR5-6000 | ₹10,999 | Prime ABGB | 2026-10-17 | `verified_indian_listing` | unavailable |
| **Storage** | `samsung-990-pro-1tb` | Samsung 990 PRO 1TB NVMe | ₹24,299 | Prime ABGB | 2026-10-21 | `verified_indian_listing` | available |
| **Case** | `case-nzxt-h5-flow-2024` | NZXT H5 Flow (2024, CC-H52FB-01) | ₹5,999 | Alltech Trading on Amazon.in | 2026-10-23 | `verified_indian_listing` | available |
| **PSU** | `psu-750w-gold` | Corsair RM750x (2024) 750W Gold | ₹29,370 | Global Klamp on Amazon.in | 2026-10-23 | `verified_indian_listing` | available |
| **Cooler** | `cooler-deepcool-ak400-black` | DeepCool AK400 Black | ₹2,290 | Computech Store | 2026-10-26 | `verified_indian_listing` | available |
| **TOTAL** | | | **₹214,307** | **All 8 parts verified from Indian retailers** | | **Complete Build** | |

### Critical Limitations & Verification Notes:
1. **Indian-Market Evidence vs Live Stock:** Every recommended component has documented local-market presence from a recognized Indian retailer. However, a retailer listing does **not** guarantee live stock, immediate warehouse fulfillment, or delivery to specific PIN codes.
2. **Recorded Price Observations:** Totals are based on lowest recorded historical prices (totaling ₹214,307). Recorded observations from 2026-10-17 for GPU and RAM were marked `unavailable` when checked, and are older than the 7-day freshness window. Current checkout prices and active stock must be re-verified with sellers before purchase.
3. **Simplified Interface:** Complex "available-first" sorting that prioritized higher-priced stock over lower recorded prices was removed from the user interface. The UI cleanly presents prices, check timestamps, and verified Indian retailer presence without pretending to perform live inventory checks.
4. **Preserved Planning Estimate:** The ₹29,370 user planning estimate for the Corsair RM750x is preserved in `prices.csv` (`includes_estimates: False`), with the recommender selecting the independently verified Global Klamp Amazon.in seller observation.

---

## 6. Verification and Test Results

From the project root (`E:\BuildWise-AI\BuildWise-AI1`), the complete validation and unit test suites were executed:

### Test Suite Execution:
```bat
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
* **Result:** Ran **85 tests in 56.1s**.
* **Status:** **OK (all 85 tests passed, 0 failures, 0 errors)**.
* **Key Passing Tests:**
  * `test_ddr5_5600_not_automatically_classified_as_expo_xmp`: PASS (clarifies that DDR5-5600 test uses an unlisted kit operating within standard JEDEC baseline specifications; verifies that it is not classified as EXPO/XMP, does not claim QVL validation, and contrasts with a QVL-listed kit that reports exact QVL validation).
  * `test_explicit_expo_profile_evaluated_separately_from_ddr_generation`: PASS (confirms basic DDR5 generation check is compatible, while unlisted EXPO profile stability is evaluated separately as unknown).
  * `test_ram_missing_from_motherboard_qvl_remains_unverified_not_incompatible`: PASS (confirms unlisted QVL status returns honest unknown, never falsely incompatible).
  * `test_missing_memory_profile_information_returns_honest_unknown`: PASS (confirms speeds exceeding baseline with undocumented profile return honest unknown).
  * `test_cpu_specific_dimm_configuration_limits_respected`: PASS (confirms CPU memory controller DIMM limits e.g. 5600 MT/s for 2 DIMMs vs 3600 MT/s for 4 DIMMs are respected).
  * `test_ak400_black_cooler_socket_and_height_clearance_pass`: PASS (AK400 Black socket and 155 mm height pass with AM5 CPU and 170 mm case, reporting 15 mm clearance).
  * `test_cooler_socket_mismatch_is_incompatible`: PASS (socket mismatch reliably returns `incompatible`).
  * `test_cooler_taller_than_case_limit_is_incompatible`: PASS (cooler exceeding case height limit reliably returns `incompatible`).
  * `test_missing_cooler_socket_information_is_unknown`: PASS (missing socket specs return `unknown`).
  * `test_missing_cooler_height_or_case_clearance_is_unknown`: PASS (missing cooler height or case clearance return `unknown`).
  * `test_exact_zero_clearance_fits_geometrically_and_reports_zero_clearance`: PASS (exact 0 mm clearance fits geometrically and reports 0 mm clearance).
  * `test_gaming_recommendation_cooler_is_compatible_and_overall_build_is_unknown`: PASS (confirms cooler compatibility is `compatible` in the recommendation, but overall build status remains `unknown` due to unlisted RAM EXPO profile).
  * `test_gaming_recommendation_includes_priced_cpu_cooler`: PASS (confirms cooler is selected and all 8 categories are present).
  * `test_evaluation_reports_holdout_record_and_grouped_cv`: PASS (isolated ML performance-tier experiment remains fully operational).

### Data Validation Execution:
```bat
.\.venv\Scripts\python.exe validate_data.py
```
* **Component rows validated:** 128
* **Price observations validated:** 29
* **Validation issues:** 0
* **Status:** **Validation passed**.

---

## 7. Change and Preservation Record

* **Files Changed:**
  * [`data/components.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/data/components.csv): Appended `cooler-deepcool-ak400-black` (total 128 rows).
  * [`data/prices.csv`](file:///e:/BuildWise-AI/BuildWise-AI1/data/prices.csv): Appended Computech Store seller observation (total 29 rows).
  * [`tests/test_validator.py`](file:///e:/BuildWise-AI/BuildWise-AI1/tests/test_validator.py): Updated price row count assertions to 29 and added validation test for the new cooler observation.
  * [`tests/test_recommendation.py`](file:///e:/BuildWise-AI/BuildWise-AI1/tests/test_recommendation.py): Updated unpriced cooler regression test fixture to filter out cooler prices, and added `test_gaming_recommendation_includes_priced_cpu_cooler`.
  * [`reference_build_actionability_update.md`](file:///e:/BuildWise-AI/BuildWise-AI1/reference_build_actionability_update.md): Updated with DeepCool AK400 Black documentation, Computech Store pricing, clearances, and full 8-category recommendation reconciliation.
* **Files Unchanged & Preserved:**
  * `app.py`, `src/compatibility.py`, `src/validator.py`: Preserved without core code modification.
  * `candidate_dataset_staging/`: 671 candidate components remain completely quarantined.
  * `experiments/performance_tier/`: ML training and evaluation scripts remain untouched.
  * `cooler-cm-hyper-212-black`: Preserved as an unpriced alternative cooler record.
* **Timestamped Backups Created:**
  * Stored in [`backups/20261026_131500/`](file:///e:/BuildWise-AI/BuildWise-AI1/backups/20261026_131500/):
    * `backups/20261026_131500/app.py`
    * `backups/20261026_131500/components.csv`
    * `backups/20261026_131500/prices.csv`
    * `backups/20261026_131500/README.md`
    * `backups/20261026_131500/reference_build_actionability_update.md`
    * `backups/20261026_131500/test_recommendation.py`
  * Prior backup: [`backups/20261026_115300/`](file:///e:/BuildWise-AI/BuildWise-AI1/backups/20261026_115300/)

---

## 8. Prioritized Next Steps

1. **Verify Live Checkout Quotes & Delivery:** Prior to making actual component purchases, confirm active cart availability, shipping fees, and PIN code delivery eligibility with each respective retailer (Computech Store, Prime ABGB, MDComputers, PC Studio, Amazon.in/RetailNet).
2. **Resolve RAM QVL / EXPO Profile:** Perform empirical BIOS stability testing of the G.Skill Flare X5 kit at 6000 MT/s on the ASUS TUF Gaming B850-PLUS WiFi, or run the kit at standard JEDEC DDR5-4800 speeds pending formal QVL certification.
3. **Monitor Alternative Cooler Stock:** Re-check stock for the Cooler Master Hyper 212 Black (`RR-S4KK-25SN-R1`) if builder preference leans toward Cooler Master.
