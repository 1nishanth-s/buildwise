# BuildWise AI — PC compatibility and budget recommendations

A beginner-friendly Windows project for checking documented PC component compatibility and comparing budget-based builds for Indian users with INR pricing.

## What the app currently does

- Stores component specifications separately from dated price observations.
- Validates required columns, price values, dates, and source information.
- Flags possible duplicate records for review; it **never deletes or merges them automatically**.
- Provides a Streamlit app with catalog readiness, validation results, compatibility explanations, and budget recommendations.
- Searches combinations of priced components that fit the entered budget. It prefers fewer documented incompatibilities, then fewer unknown checks, then a lower recorded-price total.
- Component price selection uses the lowest recorded price per component regardless of availability or age; when an equal-price seller observation and user planning estimate compete, the verified seller observation wins the tie. Observations older than 7 days are flagged as potentially stale historical records.
- Verifies Indian-market presence for recommended components: checks identifiable Indian retailer listings matching exact catalog parts (such as Prime ABGB, Computech Store, MDComputers, PC Studio, Flipkart, Amazon India, etc.), distinguishing `verified_indian_listing`, `no_verified_indian_listing`, and `unknown`. If no Indian retailer listing can be verified, users are warned instead of claiming the part is available in India.
- Simplified recommendation interface: the confusing user-facing "available-first" selection mode and stock-ranking controls have been removed in favor of transparent price-selection logic, visible check timestamps, and Indian-market presence indicators. Retailer listings demonstrate local-market presence at the check date, but do not guarantee live stock, cart checkout prices, or delivery eligibility to a user's address.
- Labels a recommendation as a complete build only when every category required by the chosen purpose is included with a recorded price; otherwise it reports a partial recommendation and names missing categories.
- Reports overall compatibility separately from completeness. If required checks are unknown, the build is not labeled fully compatible.
- Checks CPU/motherboard socket, supported chipset and documented BIOS data; CPU/motherboard/RAM memory generation; RAM kit capacity against the motherboard limit; motherboard/case form factor (including documented Micro-ATX/mATX and Mini-ITX/ITX aliases); GPU/case clearance; and GPU/PSU wattage and connector requirements.
- Storage interface and M.2 module size are checked only when the motherboard explicitly lists supported storage interfaces and M.2 sizes. The ASUS TUF Gaming B850-PLUS WiFi has official manual evidence for NVMe/SATA connectivity and documented M.2 sizes; other boards without those fields remain unknown. A SATA drive's physical size is not treated as a motherboard requirement.
- A PSU is checked in office/study builds even when no discrete GPU is selected. Without a documented system power requirement for the CPU-only build, PSU capacity and connector safety remain unknown rather than being skipped or inferred from CPU TDP.
- Offers upgrade suggestions for selected categories only. Compatibility with the user's existing parts remains unknown until those existing components and their specifications are supplied.
- Uses cataloged prices for budget calculations. Availability is displayed as price-source metadata and does not affect compatibility.
- Explicitly marked user-provided planning estimates may be included in budget totals; they are not presented as verified seller offers.
- Does not invent hardware records or current prices.

An isolated educational CPU performance-tier experiment lives in `experiments/performance_tier/`. It compares a small set of classifiers with a majority-class baseline using repeated stratified cross-validation and the labels already present in the catalog. The experiment does not change production recommendations; its small, editorially labeled dataset is not strong evidence of real-world CPU performance.

The current catalog contains 128 component records and 29 price rows covering 14 unique components: 14 have seller observations, and the PSU estimate is retained alongside its seller observation. An AM5 cooler (DeepCool AK400 Black) is included with verified Indian pricing, and the Cooler Master Hyper 212 Black remains preserved as an unpriced alternative. GPU, RAM, and case coverage includes newly recorded seller listings; stock and prices can change after the check timestamp. Price coverage and some compatibility specifications are incomplete, so recommendations may omit categories or show compatibility as unknown.

## Data strategy

1. Existing catalog rows identify the TechFuelHQ PC Builder Parts Dataset (CC BY 4.0). Review the source license and attribution requirements before reusing or adding data.
2. Add selected products from other sources only after checking their provenance, license, field quality, and suitability.
3. Keep raw source data unchanged under `data/raw/`; work on normalized copies under `data/processed/`.
4. Store component identity/specifications in `components.csv` and price observations in `prices.csv`. One product may have multiple price observations.
5. Treat missing compatibility facts as `unknown`, not as proof of compatibility.
6. Do not use USD prices as Indian retail prices. Add manually checked INR prices with a source URL and date.

## Setup on Windows (VS Code terminal / Command Prompt)

Install Python 3.10 or newer, then run:

```bat
cd path\to\BuildWise-AI
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt, or run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py` without activating the environment.

## Validate CSV files

```bat
python validate_data.py
```

Run tests:

```bat
python -m unittest discover -s tests -v
```

Run the isolated CPU performance-tier experiment on Windows:

```bat
.venv\Scripts\python.exe experiments\performance_tier\train.py
```

It writes evaluation metrics to `experiments/performance_tier/evaluation.json`. See that experiment's README for feature choices and limitations.

## CSV schemas

### `data/components.csv`
- `component_id`: stable internal ID, unique per catalog record
- `category`: CPU, Motherboard, RAM, GPU, Storage, PSU, Case, Cooler
- `brand`, `model`: identity fields; do not treat the model name alone as a unique identifier
- `specs_json`: optional JSON object containing source specifications
- `source_name`, `source_url`, `source_license`: provenance fields
- `identity_status`: `verified`, `needs_review`, or `unknown`

### `data/prices.csv`
- `price_id`: unique price-observation ID
- `component_id`: links to a component record
- `seller`: seller name
- `price_inr`: finite positive numeric INR amount, including user-provided estimates when explicitly labeled
- `source_url`: URL where the offer was checked
- `checked_at`: ISO date (`YYYY-MM-DD`) or ISO timestamp
- `availability`: `available`, `unavailable`, or `unknown`
- `price_type` (optional): `seller_observation` or `planning_estimate`; blank legacy values remain accepted
- `provenance` (optional): required when `price_type` is `planning_estimate`

Planning estimates must not claim a seller, source URL, or price-check date, and their availability must be `unknown`. The recommendation budget includes a selected estimate but labels both its row and the total accordingly.

## Compatibility rules and checks

Hardware compatibility is evaluated deterministically using documented manufacturer specifications:
- **CPU & Motherboard:** Socket match, chipset family match, and exact-pair BIOS validation evidence.
- **CPU, Motherboard & RAM Generation:** RAM generation match (e.g., DDR5 across all parts).
- **Motherboard & RAM Capacity:** RAM kit capacity checked against motherboard maximum memory capacity limit.
- **RAM Speed, Profile, CPU Limits & QVL:**
  - Evaluates explicitly documented memory profiles (`profile`: JEDEC, EXPO, or XMP).
  - Recognizes standard JEDEC specifications (e.g. DDR5 up to 5600 MT/s per JEDEC JESD79-5B; DDR4 up to 3200 MT/s). A memory speed alone (such as DDR5-5600) is never inferred to be EXPO/XMP solely because it exceeds 5200 MT/s.
  - Considers documented CPU memory-controller speed limits and DIMM configuration limits (e.g. 2-DIMM vs 4-DIMM limits such as 5600 MT/s vs 3600 MT/s) when reliable specification data is provided.
  - An explicitly documented EXPO/XMP overclock profile is checked against the motherboard's official qualified vendors list (`memory_qvl`). When confirmed on the QVL, profile stability is reported as `compatible`. When missing from the QVL, profile stability is reported as `unknown` (unverified on motherboard QVL), never falsely marked `incompatible`.
  - When memory profile information is missing for speeds exceeding baseline, status is reported as `unknown` rather than inventing profile details.
- **Motherboard & Case:** Form-factor compatibility checking documented case support for ATX, Micro-ATX, and Mini-ITX boards.
- **Storage & Motherboard:** Form factor (e.g., M.2 2280) and interface protocol (NVMe Gen 4/5, SATA) checked against motherboard M.2 slot specifications.
- **GPU & Case Clearance:** GPU physical length compared to case maximum GPU clearance.
- **PSU Capacity & Connectors:** Continuous wattage compared to GPU recommended system PSU requirement; power connectors (such as 16-pin 12V-2x6) verified against PSU cable inventory.
- **CPU Cooler Socket Support:** Cooler documented socket support (`socket_support`) compared against CPU and motherboard socket specifications (`compatible` when explicitly documented, `incompatible` on mismatch, `unknown` when missing/ambiguous).
- **CPU Cooler Case Clearance:** Cooler height (`height_mm`) compared against case maximum CPU cooler height (`max_cpu_cooler_mm`). Clearance margin is calculated and reported in millimetres. Exact zero clearance fits geometrically (`compatible` reporting 0 mm clearance). Cooler exceeding case limit is `incompatible`.
- **Thermal Realism:** The system does not invent operating temperature or acoustic guarantees from advertised cooler TDP dissipation ratings.

## Important limitations

This is a rule-based project, not a trained machine-learning recommender. Compatibility is reported only for documented rules and specifications; missing facts remain unknown. ASUS's CPU-support table lists the catalogued Ryzen 5 9600X as validated since BIOS `all` on the exact TUF Gaming B850-PLUS WiFi model (checked 2026-10-23). This manufacturer status is recorded as pair-specific evidence, not as an invented numeric BIOS version, and does not apply to other CPU/motherboard pairs. BIOS support for other common catalog pairings, including installed BIOS status where required, remains unknown unless separately documented. Storage support is documented for the ASUS TUF Gaming B850-PLUS WiFi only; other motherboard/storage combinations may remain unknown. Memory overclock profiles (e.g. DDR5-6000 EXPO) unconfirmed on the motherboard QVL remain `unknown`. Office-build PSU requirements without a discrete GPU are not inferred from CPU TDP alone. The app can only search combinations for which valid recorded prices exist. It does not fetch live prices, estimate missing prices, or guarantee that an offer can be purchased. Availability labels and freshness warnings describe only what the seller page showed at the recorded check time; availability may change and delivery eligibility may vary.
