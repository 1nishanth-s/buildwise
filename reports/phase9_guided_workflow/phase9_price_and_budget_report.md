# BuildWise-AI — Phase 9: Price and Budget Intelligence Report

**Date:** 2026-11-08  
**Environment:** Windows 11, VS Code, Python 3.12 (venv), Streamlit  
**Phase:** Phase 9 — Guided PC Build Mode and Upgrade Mode  
**Scope:** Retail Price Observations, Indian Retailer Domain Verification, Currency Handling (INR), and Live Budget Calculation  

---

## 1. Production Retail Price Dataset Architecture

The retail price intelligence in BuildWise-AI is powered by `data/prices.csv` (599 records), connecting to the 1,208-component catalog via foreign key `component_id`.
Key schema fields:
- `price_id`: Unique observation identifier.
- `component_id`: Catalog reference ID.
- `seller`: Name of retailer (e.g., MD Computers, PrimeABGB, Vedant Computers).
- `price_inr`: Integer price in Indian Rupees (₹).
- `source_url`: Verifiable retail listing URL.
- `checked_at`: Timestamp / date of observation.
- `availability`: Stock status (`available`, `out_of_stock`, `unknown`).
- `price_type`: `seller_observation` (verified scraped/recorded retail listing) or `planning_estimate` (user reference).
- `provenance`: Traceable source documentation.

---

## 2. Price Observation Policies & Selection Logic

Two pricing policies are supported via `choose_cheapest_price(component_id, prices_lookup, prefer_available)`:

1. **Lowest Recorded Price Policy (`prefer_available=False`):**
   - Ranks all observations for the given `component_id` strictly by `price_inr` ascending.
   - Seller observations take precedence over planning estimates at equal price points.
2. **Available-First Policy (`prefer_available=True`):**
   - Prioritizes currently available in-stock listings with recent observations (checked within 7 days).
   - Priority hierarchy:
     1. Available + Recent observation
     2. Unknown availability / Unknown freshness
     3. Available + Stale observation
     4. Out of stock observation
     5. Planning estimate

---

## 3. Verified Indian Retailer Market Presence

The pure function `evaluate_indian_market_presence` inspects the domain of `source_url` against `INDIAN_RETAILER_DOMAINS`:
- Supported domains: `primeabgb.com`, `mdcomputers.in`, `vedantcomputers.com`, `pcstudio.in`, `computechstore.in`, `elitehubs.com`, `theitdepot.com`, `clarioncomputers.in`, `tpstech.in`, `compify.in`, `flipkart.com`, `amazon.in`.
- Classification statuses:
  - `verified_indian_listing`: Observation comes from an active Indian retailer domain.
  - `no_verified_indian_listing`: Observation is from an international source or unverified seller.
  - `unknown`: No retail URL or unpriced record.

---

## 4. Live Budget Calculation & Safeguards

The `calculate_build_budget` function calculates financial metrics dynamically in real time:

$$\text{Recorded Total} = \sum_{i \in \text{selected}} \text{price\_inr}_i \quad (\text{where } \text{price\_inr}_i \neq \text{None})$$
$$\text{Remaining Budget} = \text{Budget} - \text{Recorded Total}$$

### Critical Financial Safeguards:
1. **No Implicit Zero Pricing:** If a catalog component has no recorded price observations, `price_inr` is set to `None`, displayed as `Price unavailable`. It is **never** counted as ₹0, preventing false "free component" math.
2. **Unpriced Component Alerts:** When unpriced items are selected, a prominent warning is rendered:  
   `⚠️ K component(s) have unrecorded prices and are not included in the recorded total.`
3. **Over-Budget Detection:** If `Recorded Total > Budget`, `is_over_budget` triggers an immediate error banner with the exact excess deficit.
4. **Price Basis Breakdown:** The budget summary explicitly categorizes:
   - Verified retailer prices count.
   - User planning estimates count.
   - Confirmed available in-stock subtotal vs total recorded catalog prices.

---

## 5. Verification & Test Evidence

Tested in `tests/test_guided_workflow.py` and `tests/test_recommendation.py`:
- `test_is_indian_retailer_url`: Passed.
- `test_evaluate_indian_market_presence`: Passed.
- `test_price_to_int_utility`: Passed.
- `test_observation_freshness`: Passed.
- `test_choose_cheapest_price_lowest_vs_available`: Passed.
- `test_budget_totals_and_missing_price_handling`: Passed.
- `test_historical_and_unavailable_price_records_distinction`: Passed.
