# Reference Gaming Build Audit

**Audit date:** 2026-10-26  
**Scope:** Existing production catalog and recommendation code only. The quarantined candidate dataset was not consulted.  
**Production changes:** None intended; this report is the only file created for this task.

## Summary

All seven requested component IDs exist in the production catalog and their brand/model strings match the requested products. The existing gaming recommendation function, run against the full production catalog with a ₹300,000 budget, selected those same seven IDs and included all required gaming categories.

The production compatibility checks returned `compatible` for the seven checks implemented by the app. This does **not** establish that every part of a complete, purchasable PC is verified. In particular, the 6000 MT/s EXPO memory profile is an overclocked profile whose kit-specific QVL/stability was not confirmed; no CPU cooler was selected; some product-specific official source pages could not be retrieved; and current delivery/stock was not confirmed for most seller listings.

| App price policy | App total | Estimate included? | Important limitation |
|---|---:|---|---|
| Lowest recorded price | ₹212,017 | No | Includes GPU at ₹87,622 and RAM at ₹10,999, both marked unavailable in their recorded observations. |
| Available-first recorded price | ₹285,395 | No | Uses seller observations marked available in the catalog, but the CPU observation is availability-unknown and this is not a live stock/delivery guarantee. |

The preserved ₹29,370 Corsair RM750x planning estimate remains in the price history. The recommender selected the separate ₹29,370 Global Klamp seller observation at the same amount; neither recommendation total counted the planning estimate.

**Assessment:** The configuration is promising for further review, and the documented app checks pass. It is **not sufficiently evidenced to present as a confirmed purchasable or fully validated build**. Refresh seller quotes and confirm the cooler and memory profile before treating it as actionable.

## Product identity and source evidence

The production IDs and catalog names were checked against `data/components.csv`; no mismatch was found, so the audit continued without substitutions.

| Component ID | Production brand and exact catalog model | Source checked on 2026-10-26 | Evidence and remaining caveats |
|---|---|---|---|
| `cpu-r5-9600x` | AMD — Ryzen 5 9600X | [ASUS CPU support list](https://www.asus.com/us/motherboards-components/motherboards/tuf-gaming/tuf-gaming-b850-plus-wifi/helpdesk_cpu/); [Flipkart listing](https://www.flipkart.com/amd-ryzen-5-9600x-3-9-ghz-upto-5-4-am5-socket-6-cores-12-threads-desktop-processor/p/itm6ccccb951eec3?pid=PSRH3GG5UGB8CNEU). AMD product-page request timed out. | ASUS lists Ryzen 5 9600X as validated on all PCB/BIOS versions for this board. The production catalog says AM5, 65 W TDP and DDR5, but its AMD official product source was not independently retrieved in this audit. Flipkart's page identifies the model and displayed ₹24,661, but did not establish delivery to a specific address. |
| `mb-asus-tuf-gaming-b850-plus-wifi` | ASUS — TUF Gaming B850-PLUS WiFi | [ASUS technical specifications](https://www.asus.com/motherboards-components/motherboards/tuf-gaming/tuf-gaming-b850-plus-wifi/techspec/); [ASUS CPU support list](https://www.asus.com/us/motherboards-components/motherboards/tuf-gaming/tuf-gaming-b850-plus-wifi/helpdesk_cpu/); [Prime ABGB listing](https://www.primeabgb.com/online-price-reviews-india/asus-tuf-gaming-b850-plus-wifi-amd-b850-ddr5-motherboard/). | ASUS confirms AM5, B850, DDR5, ATX, four DIMM slots, 256 GB maximum, M.2 2280 support, and Ryzen 5 9600X support since all BIOS versions. The retailer page displayed ₹27,769 and “Only 1 left” at check time; this is the page's statement, not a delivery guarantee. |
| `gpu-nvidia-asus-prime-rtx5070-o12g` | ASUS — Prime GeForce RTX 5070 12GB GDDR7 OC Edition (SFF-Ready) | [ASUS technical specifications](https://www.asus.com/us/motherboards-components/graphics-cards/prime/prime-rtx5070-o12g/techspec/); [Prime ABGB listing](https://www.primeabgb.com/online-price-reviews-india/asus-prime-rtx-5070-oc-edition-12gb-gddr7-graphics-card-prime-rtx5070-o12g/). The recorded MDComputers page returned HTTP 403. | ASUS confirms 12 GB GDDR7, 304 mm length, 750 W recommended system PSU and one 16-pin power connector. Prime ABGB's page identifies the same model but lists a 306 mm length, a 2 mm discrepancy; the manufacturer value is used for the clearance calculation. No current seller price/stock was established. |
| `gskill-flare-x5-ddr5-6000-cl36-32gb` | G.Skill — Flare X5 DDR5 32GB (2x16GB) 6000MT/s CL36, part `F5-6000J3636F16GX2-FX5` | [G.Skill product specification](https://www.gskill.com/specification/165/396/1662622664/F5-6000J3636F16GX2-FX5-Specification); [PC Studio listing](https://www.pcstudio.in/product/g-skill-flare-x5-32gb-16gb-x-2-ddr5-6000mhz-desktop-ram-matte-black/). | G.Skill confirms DDR5, 32 GB (16 GB x 2), 6000 MT/s tested profile and 36-36-36-96 latency. It explicitly says rated XMP/EXPO speed requires overclocking/BIOS adjustments and depends on the CPU/motherboard. This audit did not establish this exact kit's QVL entry or stable 6000 MT/s operation on the selected CPU/board. |
| `samsung-990-pro-1tb` | Samsung — 990 PRO 1TB | [Prime ABGB product listing](https://www.primeabgb.com/online-price-reviews-india/samsung-990-pro-1tb-pci-express-4-0-x4-gen-4-nvme-ssd-mz-v9p1t0bw/). Samsung product-page requests redirected to generic pages rather than an exact product specification. | The retailer listing identifies the 990 PRO 1TB and PCIe 4.0 x4 NVMe product. The production catalog records M.2 2280 and links a Newegg source; Samsung's exact-model specification could not be independently retrieved here. |
| `psu-750w-gold` | Corsair — RM750x (2024), 750W 80+ Gold | [Corsair product page](https://www.corsair.com/us/en/p/psu/cp-9020285-na/rm750x-fully-modular-atx-power-supply-cp-9020285-na); recorded [Amazon.in listing](https://www.amazon.in/CORSAIR-RM750x-Modular-Low-Noise-Supply/dp/B0DJ1M18CY). Amazon returned HTTP 503. | Corsair confirms the RM750x series' 750 W output and lists two EPS/ATX 12V 8-pin cables and a 12V-2x6 (12+4) cable. The exact Amazon offer/availability was not live-verified. |
| `case-nzxt-h5-flow-2024` | NZXT — H5 Flow (2024 Edition, `CC-H52FB-01`) | Attempted [NZXT product page](https://nzxt.com/products/h5-flow-2024), which redirected to the general case collection; [Prime ABGB listing](https://www.primeabgb.com/online-price-reviews-india/nzxt-h5-flow-2024-edition-e-atx-mid-tower-case-cabinet-cc-h52fb-01/); recorded [Amazon.in listing](https://www.amazon.in/NZXT-Flow-2024-Mid-Tower-Management/dp/B0D2MK6NML), which returned HTTP 503. | Prime ABGB identifies the exact SKU and lists ATX support and up to 410 mm GPU length. An exact-model NZXT specification page was not successfully retrieved; the seller page and existing catalog support these fit checks, but are weaker than a directly retrieved manufacturer specification. |

“Source checked” means the page was successfully retrieved during this audit unless the row explicitly says the request failed or redirected. Catalog `last_verified` dates are not treated as proof that a source was checked during this task.

## Recorded price observations

The following are all production price rows for the seven IDs. “Recorded availability” is the CSV status at the observation time, not current seller stock.

| Price observation ID | Component | Seller / basis | INR | Recorded check time | Recorded availability |
|---|---|---|---:|---|---|
| `price-cpu-r5-9600x-01` | CPU | Flipkart | ₹42,000 | 2026-10-17 | available |
| `price-cpu-r5-9600x-flipkart-retailnet-20261021-01` | CPU | RetailNet, Flipkart URL | ₹25,959 | 2026-10-21T18:25:45.226+05:30 | unknown |
| `price-mb-asus-tuf-b850-plus-wifi-20261021-01` | Motherboard | Prime ABGB | ₹27,769 | 2026-10-21T18:37:06.405+05:30 | available |
| `price-mb-asus-tuf-b850-plus-wifi-primeabgb-20261021-184954` | Motherboard | Prime ABGB | ₹27,769 | 2026-10-21T18:49:54.243+05:30 | available |
| `price-mb-asus-tuf-b850-plus-wifi-primeabgb-20261023-121224` | Motherboard | Prime ABGB | ₹27,769 | 2026-10-23T12:12:24.230+05:30 | available |
| `price-gpu-asus-prime-rtx5070-o12g-01` | GPU | Prime ABGB | ₹87,622 | 2026-10-17 | unavailable |
| `price-gpu-asus-prime-rtx5070-o12g-20261021-01` | GPU | Prime ABGB | ₹87,622 | 2026-10-21T18:25:45.226+05:30 | unavailable |
| `price-gpu-asus-prime-rtx5070-mdcomputers-20261023-120947` | GPU | MDComputers | ₹112,999 | 2026-10-23T12:09:47.768+05:30 | available |
| `price-ram-gskill-flare-x5-32gb-01` | RAM | Prime ABGB | ₹10,999 | 2026-10-17 | unavailable |
| `price-ram-gskill-flare-x5-32gb-20261021-01` | RAM | Prime ABGB | ₹10,999 | 2026-10-21T18:25:45.226+05:30 | unavailable |
| `price-ram-gskill-flare-x5-pcstudio-20261023-121027` | RAM | PC Studio | ₹59,000 | 2026-10-23T12:10:27.577+05:30 | available |
| `price-samsung-990-pro-1tb-primeabgb-20261021-184955` | Storage | Prime ABGB | ₹24,299 | 2026-10-21T18:49:55.225+05:30 | available |
| `price-psu-rm750x-2024-planning-estimate-01` | PSU | Preserved planning estimate; no seller/source/date | ₹29,370 | Not recorded | unknown |
| `price-psu-corsair-rm750x-amazon-20261023-120759` | PSU | Global Klamp, Amazon.in URL | ₹29,370 | 2026-10-23T12:07:59.374+05:30 | available |
| `price-case-nzxt-h5-flow-2024-01` | Case | Prime ABGB | ₹6,254 | 2026-10-17 | unavailable |
| `price-case-nzxt-h5-flow-2024-20261021-01` | Case | Prime ABGB | ₹6,254 | 2026-10-21T18:25:45.226+05:30 | unavailable |
| `price-case-nzxt-h5-flow-amazon-20261023-121052` | Case | Alltech Trading, Amazon.in URL | ₹5,999 | 2026-10-23T12:10:52.102+05:30 | available |

### Seller-page checks

- **CPU:** Flipkart's page displayed ₹24,661 on 2026-10-26, different from either stored observation. It did not establish delivery to a particular address. The seller field `RetailNet` in the ₹25,959 observation is not the same as the directly checked page's live displayed price.
- **Motherboard:** Prime ABGB displayed ₹27,769 and “Only 1 left” on the retrieved page. This is a current page display, not confirmed fulfillment.
- **GPU:** The Prime ABGB listing was retrievable for product/specification identity but did not establish current price or availability. MDComputers returned HTTP 403.
- **RAM:** The PC Studio listing was retrievable for exact product identity/specifications but did not establish current price or availability. Prime ABGB's listing likewise did not establish a current offer.
- **Storage:** Prime ABGB's product page was retrievable for product identity/specification, but no current offer price or availability was established.
- **PSU and case:** The recorded Amazon.in pages returned HTTP 503; current price/availability was not verified there. Prime ABGB's case page was retrievable for identity and dimensions, not a current offer.

Several observations are repeated at the same seller, price and URL; in particular, the three motherboard observations are all ₹27,769. They may be repeat checks rather than independent market offers. The ₹59,000 PC Studio RAM observation is much higher than the ₹10,999 Prime ABGB observations, but those Prime ABGB rows are marked unavailable; do not treat either as a current market price without refreshed quotes. The app's seven-day freshness classification is a metadata heuristic, not a live check.

## Compatibility results

The existing app compatibility path was executed against the exact catalog records. Each status below is the production check result; the accompanying limits are important because the code checks selected fields, not every real-world installation condition.

| Check | Result | Evidence/reason and limits |
|---|---|---|
| CPU socket, chipset and BIOS support | `compatible` | Both catalog records specify AM5; the CPU catalog lists B850; ASUS's CPU support page lists Ryzen 5 9600X as supported from all BIOS versions. The motherboard model and support page were retrieved. |
| CPU/board/RAM memory generation | `compatible` | The CPU, board and kit records all specify DDR5; G.Skill's exact part-number page confirms DDR5. |
| RAM kit capacity | `compatible` | 32 GB is below ASUS's stated 256 GB board maximum. |
| Motherboard/case form factor | `compatible` | The board is ATX; the case listing for `CC-H52FB-01` lists ATX support. Exact-model NZXT manufacturer documentation was not retrieved. |
| SSD interface and module size | `compatible` | Catalog/retailer evidence identifies NVMe and M.2 2280; ASUS documents NVMe M.2 slots including 2280 support for Ryzen 9000-series CPUs. Exact-model Samsung manufacturer specifications were not retrieved. |
| GPU physical length/case clearance | `compatible` | ASUS lists the card at 304 mm; the H5 Flow listing/catalog gives 410 mm maximum GPU length. Prime ABGB separately lists 306 mm for the card. Both lengths fit the stated maximum, but the 2 mm source disagreement remains. |
| PSU capacity and GPU connector | `compatible` | ASUS recommends a 750 W system PSU and specifies one 16-pin GPU connector. The selected PSU is 750 W; Corsair lists a 12V-2x6 (12+4) cable. This meets the stated recommendation exactly; it is not a measured load or margin analysis. |
| Board CPU power connectors | Supported by available specs | ASUS's board specifications list two 8-pin +12 V CPU power connectors; Corsair lists two EPS/ATX12V 8-pin cables. This additional check was compared directly; it is not a separate status emitted by the app helper. |

### Checks not established by the app's `compatible` result

- G.Skill states 6000 MT/s is an XMP/EXPO tested overclock profile requiring BIOS adjustments and dependent on CPU/board capability. DDR5 and capacity fit, but the exact kit's presence on the ASUS memory QVL and stable 6000 MT/s operation were not verified. Treat the rated profile as **unknown**, not guaranteed.
- No CPU cooler is included in the seven selected records. Cooler presence, socket fit, cooler-height clearance, and cooling adequacy are therefore **unknown**.
- The GPU-to-case check uses the published maximum clearance. It does not prove clearance under unspecified front-radiator/fan configurations or cable-bend clearance at the GPU power connector.
- The PSU wattage check establishes that 750 W meets ASUS's stated recommendation, not that the complete system has a measured transient or thermal margin.
- Operating system, display/peripherals, delivery, shipping/tax, assembly and exact seller fulfillment are outside this seven-component price total.

No documented incompatibility was found in the performed checks. These checks do not prove every aspect of the full build.

## Recommendation-engine reconciliation

The existing `build_recommendation` function was run using the full production catalog and price history, `purpose="gaming"`, and a **₹300,000** build-only budget. It selected exactly:

`cpu-r5-9600x`, `mb-asus-tuf-gaming-b850-plus-wifi`, `gpu-nvidia-asus-prime-rtx5070-o12g`, `gskill-flare-x5-ddr5-6000-cl36-32gb`, `samsung-990-pro-1tb`, `case-nzxt-h5-flow-2024`, and `psu-750w-gold`.

All seven required gaming categories (CPU, motherboard, GPU, RAM, storage, case and PSU) are present.

| Engine policy | CPU | Board | GPU | RAM | Storage | Case | PSU | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Lowest recorded price | ₹25,959 | ₹27,769 | ₹87,622 | ₹10,999 | ₹24,299 | ₹5,999 | ₹29,370 seller observation | **₹212,017** |
| Available-first recorded price | ₹25,959 | ₹27,769 | ₹112,999 | ₹59,000 | ₹24,299 | ₹5,999 | ₹29,370 seller observation | **₹285,395** |

The lowest-price result relies on the GPU and RAM observations whose recorded status is `unavailable`; it also uses a CPU observation marked `unknown`. The available-first result uses recent rows marked available for five categories, but its CPU price observation is still `unknown` and the pages checked did not establish current delivery/stock for all seven parts. “Available-first” means the app prioritizes recorded seller-observation metadata; it is not a live inventory lookup.

The PSU's ₹29,370 amount is present twice on separate bases: an undated planning estimate and a dated seller observation. In both app runs, the seller observation was selected and `includes_estimates` was false. The estimate remains preserved and was not treated as a seller quote.

## Final assessment and next steps

The configuration is **structurally plausible and passes the existing app's documented compatibility checks**, but the current evidence is insufficient to call it fully compatible or confirmed purchasable. The lowest total is not a reliable purchase total because it includes two rows marked unavailable; the alternative total still relies on recorded rather than fully rechecked seller availability.

Prioritized next steps:

1. Refresh seller quotes for GPU, RAM, storage, PSU and case; confirm exact model/SKU, delivered price and delivery availability for the buyer's location. Recheck the CPU observation as its current displayed Flipkart price differs from the stored record.
2. Confirm the exact RAM part number against the ASUS memory QVL for this CPU/board and decide whether to run its 6000 MT/s EXPO profile; otherwise plan for supported default memory settings.
3. Select and verify a suitable AM5 CPU cooler, including case-height and clearance checks.
4. If stronger documentation is required, retrieve exact-model official source material for the CPU, 990 PRO and H5 Flow 2024; the AMD request timed out, Samsung redirected to a generic page, and NZXT redirected to its case collection during this audit.
5. Re-run the recommendation after refreshing price history. Keep the seller observation and planning estimate as distinct price bases and preserve the complete historical rows.

## Production preservation

No production CSV, component ID, compatibility rule, application code, model label, ML experiment, or price observation was intentionally changed. Git metadata was not present at the project root. A pre-report SHA-256 baseline was captured for the project's non-staging, non-environment files; hashes are compared again after the requested checks.
