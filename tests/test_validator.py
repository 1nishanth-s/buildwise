from pathlib import Path
import unittest
import pandas as pd
from src.validator import COMPONENT_COLUMNS, PRICE_COLUMNS, validate_components, validate_prices


def component_row(**overrides):
    row = {col: "" for col in COMPONENT_COLUMNS}
    row.update({"component_id": "CPU_001", "category": "CPU", "brand": "Example", "model": "Example CPU", "specs_json": '{"socket":"AM4"}', "source_name": "Test source", "source_url": "https://example.com/product", "source_license": "review-required", "identity_status": "needs_review"})
    row.update(overrides)
    return row


def price_row(**overrides):
    row = {col: "" for col in PRICE_COLUMNS}
    row.update({"price_id": "PRICE_001", "component_id": "CPU_001", "seller": "Example seller", "price_inr": "10000", "source_url": "https://example.com/offer", "checked_at": "2026-10-17", "availability": "unknown"})
    row.update(overrides)
    return row


class ValidatorTests(unittest.TestCase):
    def test_asus_b850_seller_observation_is_recorded_and_valid(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        components = pd.read_csv(data_dir / "components.csv", dtype=str, keep_default_na=False)
        prices = pd.read_csv(data_dir / "prices.csv", dtype=str, keep_default_na=False)
        matches = prices[
            prices["price_id"] == "price-mb-asus-tuf-b850-plus-wifi-20261021-01"
        ]

        self.assertEqual(len(prices), 29)
        self.assertEqual(len(matches), 1)
        self.assertEqual(
            matches.iloc[0].to_dict(),
            {
                "price_id": "price-mb-asus-tuf-b850-plus-wifi-20261021-01",
                "component_id": "mb-asus-tuf-gaming-b850-plus-wifi",
                "seller": "Prime ABGB",
                "price_inr": "27769",
                "source_url": "https://www.primeabgb.com/online-price-reviews-india/asus-tuf-gaming-b850-plus-wifi-amd-b850-ddr5-motherboard/",
                "checked_at": "2026-10-21T18:37:06.405+05:30",
                "availability": "available",
                "price_type": "seller_observation",
                "provenance": "",
            },
        )
        self.assertEqual(validate_prices(prices, components), [])

    def test_fresh_seller_observations_for_gpu_ram_case_psu_and_motherboard(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        components = pd.read_csv(data_dir / "components.csv", dtype=str, keep_default_na=False)
        prices = pd.read_csv(data_dir / "prices.csv", dtype=str, keep_default_na=False)
        expected = {
            "price-gpu-asus-prime-rtx5070-mdcomputers-20261023-120947": (
                "gpu-nvidia-asus-prime-rtx5070-o12g", "112999", "MDComputers",
                "https://mdcomputers.in/product/asus-prime-graphics-card-rtx5070-o12g",
                "2026-10-23T12:09:47.768+05:30",
            ),
            "price-ram-gskill-flare-x5-pcstudio-20261023-121027": (
                "gskill-flare-x5-ddr5-6000-cl36-32gb", "59000", "PC Studio",
                "https://www.pcstudio.in/product/g-skill-flare-x5-32gb-16gb-x-2-ddr5-6000mhz-desktop-ram-matte-black/",
                "2026-10-23T12:10:27.577+05:30",
            ),
            "price-case-nzxt-h5-flow-amazon-20261023-121052": (
                "case-nzxt-h5-flow-2024", "5999", "Alltech Trading",
                "https://www.amazon.in/NZXT-Flow-2024-Mid-Tower-Management/dp/B0D2MK6NML",
                "2026-10-23T12:10:52.102+05:30",
            ),
            "price-psu-corsair-rm750x-amazon-20261023-120759": (
                "psu-750w-gold", "29370", "Global Klamp",
                "https://www.amazon.in/CORSAIR-RM750x-Modular-Low-Noise-Supply/dp/B0DJ1M18CY",
                "2026-10-23T12:07:59.374+05:30",
            ),
            "price-mb-asus-tuf-b850-plus-wifi-primeabgb-20261023-121224": (
                "mb-asus-tuf-gaming-b850-plus-wifi", "27769", "Prime ABGB",
                "https://www.primeabgb.com/online-price-reviews-india/asus-tuf-gaming-b850-plus-wifi-amd-b850-ddr5-motherboard/",
                "2026-10-23T12:12:24.230+05:30",
            ),
        }
        additions = prices[prices["price_id"].isin(expected)]

        self.assertEqual(len(prices), 29)
        self.assertEqual(len(additions), len(expected))
        for price_id, (component_id, amount, seller, url, checked_at) in expected.items():
            with self.subTest(price_id=price_id):
                row = additions[additions["price_id"] == price_id].iloc[0]
                self.assertEqual(row["component_id"], component_id)
                self.assertEqual(row["price_inr"], amount)
                self.assertEqual(row["seller"], seller)
                self.assertEqual(row["source_url"], url)
                self.assertEqual(row["checked_at"], checked_at)
                self.assertEqual(row["availability"], "available")
                self.assertEqual(row["price_type"], "seller_observation")
        self.assertEqual(validate_prices(prices, components), [])

    def test_deepcool_ak400_seller_observation_is_recorded_and_valid(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        components = pd.read_csv(data_dir / "components.csv", dtype=str, keep_default_na=False)
        prices = pd.read_csv(data_dir / "prices.csv", dtype=str, keep_default_na=False)
        matches = prices[
            prices["price_id"] == "price-cooler-deepcool-ak400-computech-20261026-113610"
        ]

        self.assertEqual(len(prices), 29)
        self.assertEqual(len(matches), 1)
        self.assertEqual(
            matches.iloc[0].to_dict(),
            {
                "price_id": "price-cooler-deepcool-ak400-computech-20261026-113610",
                "component_id": "cooler-deepcool-ak400-black",
                "seller": "Computech Store",
                "price_inr": "2290",
                "source_url": "https://computechstore.in/product/deepcool-ak400-cpu-air-cooler-black/",
                "checked_at": "2026-10-26T11:36:10+05:30",
                "availability": "available",
                "price_type": "seller_observation",
                "provenance": "",
            },
        )
        self.assertEqual(validate_prices(prices, components), [])

    def test_new_available_primeabgb_observations_are_valid(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        components = pd.read_csv(data_dir / "components.csv", dtype=str, keep_default_na=False)
        prices = pd.read_csv(data_dir / "prices.csv", dtype=str, keep_default_na=False)
        expected = {
            "price-mb-asus-tuf-b850-plus-wifi-primeabgb-20261021-184954": (
                "mb-asus-tuf-gaming-b850-plus-wifi", "27769",
                "https://www.primeabgb.com/online-price-reviews-india/asus-tuf-gaming-b850-plus-wifi-amd-b850-ddr5-motherboard/",
            ),
            "price-samsung-990-pro-1tb-primeabgb-20261021-184955": (
                "samsung-990-pro-1tb", "24299",
                "https://www.primeabgb.com/online-price-reviews-india/samsung-990-pro-1tb-pci-express-4-0-x4-gen-4-nvme-ssd-mz-v9p1t0bw/",
            ),
            "price-samsung-990-pro-4tb-primeabgb-20261021-1849557": (
                "samsung-990-pro-4tb", "79768",
                "https://www.primeabgb.com/online-price-reviews-india/samsung-990-pro-4tb-pci-express-4-0-x4-gen-4-nvme-ssd-mz-v9p4t0bw/",
            ),
            "price-samsung-9100-pro-1tb-primeabgb-20261021-184956": (
                "samsung-9100-pro-1tb", "28226",
                "https://www.primeabgb.com/online-price-reviews-india/samsung-9100-pro-1tb-pcie-gen-5-0-nvme-m-2-ssd-mz-vap1t0bw/",
            ),
        }
        additions = prices[
            prices["price_id"].isin({
                *expected,
            })
        ]

        self.assertEqual(len(additions), 4)
        for price_id, (component_id, price, source_url) in expected.items():
            row = additions[additions["price_id"] == price_id].iloc[0]
            self.assertEqual(row["component_id"], component_id)
            self.assertEqual(row["price_inr"], price)
            self.assertEqual(row["seller"], "Prime ABGB")
            self.assertEqual(row["availability"], "available")
            self.assertEqual(row["price_type"], "seller_observation")
            self.assertEqual(row["source_url"], source_url)
        self.assertEqual(validate_prices(prices, components), [])

    def test_valid_component_has_no_issues(self):
        self.assertEqual(validate_components(pd.DataFrame([component_row()])), [])

    def test_invalid_specs_json_is_reported(self):
        issues = validate_components(pd.DataFrame([component_row(specs_json="not-json")]))
        self.assertTrue(any("not valid JSON" in issue for issue in issues))

    def test_duplicate_rows_are_flagged_not_removed(self):
        frame = pd.DataFrame([component_row(), component_row(component_id="CPU_002")])
        issues = validate_components(frame)
        self.assertTrue(any("possible exact duplicates" in issue for issue in issues))
        self.assertEqual(len(frame), 2)

    def test_price_must_link_to_component(self):
        issues = validate_prices(pd.DataFrame([price_row(component_id="MISSING")]), pd.DataFrame([component_row()]))
        self.assertTrue(any("does not match a catalog record" in issue for issue in issues))

    def test_price_date_format_is_checked(self):
        issues = validate_prices(pd.DataFrame([price_row(checked_at="17/10/2026")]), pd.DataFrame([component_row()]))
        self.assertTrue(any("ISO date or timestamp" in issue for issue in issues))

    def test_iso_price_timestamp_is_accepted(self):
        issues = validate_prices(
            pd.DataFrame([price_row(checked_at="2026-10-21T18:25:45.226+05:30")]),
            pd.DataFrame([component_row()]),
        )
        self.assertEqual(issues, [])

    def test_duplicate_seller_observation_timestamp_is_flagged(self):
        frame = pd.DataFrame([
            price_row(),
            price_row(price_id="PRICE_002"),
        ])
        issues = validate_prices(frame, pd.DataFrame([component_row()]))
        self.assertTrue(any("duplicate seller observation" in issue for issue in issues))

    def test_non_finite_prices_are_rejected(self):
        for raw_price in ("nan", "inf", "-inf"):
            with self.subTest(price=raw_price):
                issues = validate_prices(
                    pd.DataFrame([price_row(price_inr=raw_price)]),
                    pd.DataFrame([component_row()]),
                )
                self.assertTrue(any("finite number greater than zero" in issue for issue in issues))

    def test_planning_estimate_requires_provenance_and_unknown_availability(self):
        estimate = price_row(
            seller="",
            source_url="",
            checked_at="",
            availability="unknown",
            price_type="planning_estimate",
            provenance="User-provided planning estimate; not independently verified.",
        )
        self.assertEqual(
            validate_prices(pd.DataFrame([estimate]), pd.DataFrame([component_row()])),
            [],
        )

        missing_provenance = dict(estimate, provenance="")
        issues = validate_prices(
            pd.DataFrame([missing_provenance]), pd.DataFrame([component_row()])
        )
        self.assertTrue(any("require provenance" in issue for issue in issues))

        claimed_stock = dict(estimate, availability="available")
        issues = validate_prices(
            pd.DataFrame([claimed_stock]), pd.DataFrame([component_row()])
        )
        self.assertTrue(any("availability must be unknown" in issue for issue in issues))

    def test_legacy_price_schema_remains_valid(self):
        legacy_price = price_row()
        self.assertEqual(
            validate_prices(
                pd.DataFrame([legacy_price]),
                pd.DataFrame([component_row()]),
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
