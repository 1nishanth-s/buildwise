import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest

import app as app_module
from src.compatibility import check_cpu_motherboard, check_gpu_case
from src.validator import load_and_validate

ROOT = Path(__file__).resolve().parents[1]


class ModernApplicationAndCatalogTests(unittest.TestCase):
    """
    Validates application startup, dataset loading, component browsing,
    price utilities, and the verified retirement of the legacy exhaustive engine.
    """

    def test_legacy_exhaustive_engine_is_retired(self):
        """Verifies that the legacy build_recommendation and DFS helpers do not exist in app.py."""
        self.assertFalse(
            hasattr(app_module, "build_recommendation"),
            "build_recommendation must be completely retired from app.py",
        )
        self.assertFalse(
            hasattr(app_module, "_check_candidate_compatibility"),
            "_check_candidate_compatibility must be retired from app.py",
        )
        self.assertFalse(
            hasattr(app_module, "PURPOSE_LAYOUT"),
            "PURPOSE_LAYOUT must be retired from app.py",
        )

    def test_app_starts_and_renders_clean_interface(self):
        """Verifies that the Streamlit application starts and renders all required sections without errors."""
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        self.assertFalse(app.exception, f"AppTest raised an exception: {app.exception}")

        # Verify title and header
        titles = [item.value for item in app.title]
        self.assertTrue(
            any("BuildWise-AI — PC Component Intelligence System" in t for t in titles),
            "Expected system title not found in app.title",
        )

        # Verify future workflow notice
        info_messages = [item.value for item in app.info]
        self.assertTrue(
            any("legacy exhaustive recommendation engine has been retired" in msg for msg in info_messages),
            "Expected engine retirement notice not found in app.info",
        )

        # Verify metrics display
        metric_labels = [item.label for item in app.metric]
        self.assertIn("Component Catalog", metric_labels)
        self.assertIn("Retail Price Observations", metric_labels)
        self.assertIn("Benchmark Observations", metric_labels)
        self.assertIn("Data Validation Issues", metric_labels)

    def test_app_does_not_contain_legacy_budget_form(self):
        """Confirms that the old budget recommendation form and exhaustive search controls are gone."""
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=10).run()
        self.assertEqual(
            len(app.form),
            0,
            "Legacy recommendation form must not exist in app.py",
        )

    def test_dataset_loading_in_app(self):
        """Verifies production datasets load cleanly into pandas DataFrames."""
        components, prices, issues = load_and_validate(ROOT / "data")
        self.assertFalse(components.empty)
        self.assertFalse(prices.empty)
        self.assertEqual(len(components), 1208)
        self.assertGreaterEqual(len(prices), 599)
        self.assertEqual(len(issues), 0)

    def test_is_indian_retailer_url(self):
        """Verifies Indian retailer domain validation utility."""
        self.assertTrue(app_module.is_indian_retailer_url("https://mdcomputers.in/product/cpu.html"))
        self.assertTrue(app_module.is_indian_retailer_url("https://www.primeabgb.com/item/123"))
        self.assertTrue(app_module.is_indian_retailer_url("https://vedantcomputers.com/offer"))
        self.assertFalse(app_module.is_indian_retailer_url("https://newegg.com/product"))
        self.assertFalse(app_module.is_indian_retailer_url("https://amazon.com/dp/B08"))
        self.assertFalse(app_module.is_indian_retailer_url(""))
        self.assertFalse(app_module.is_indian_retailer_url(None))

    def test_evaluate_indian_market_presence(self):
        """Verifies market presence classification across seller observations and planning estimates."""
        verified_entry = [{
            "seller": "MD Computers",
            "source_url": "https://mdcomputers.in/item",
            "price_type": "seller_observation",
            "checked_at": "2026-10-28",
        }]
        res_verified = app_module.evaluate_indian_market_presence(verified_entry)
        self.assertEqual(res_verified["status"], "verified_indian_listing")
        self.assertEqual(res_verified["retailer"], "MD Computers")

        foreign_entry = [{
            "seller": "BestBuy",
            "source_url": "https://bestbuy.com/item",
            "price_type": "seller_observation",
            "checked_at": "2026-10-28",
        }]
        res_foreign = app_module.evaluate_indian_market_presence(foreign_entry)
        self.assertEqual(res_foreign["status"], "no_verified_indian_listing")

        empty_entry = []
        res_empty = app_module.evaluate_indian_market_presence(empty_entry)
        self.assertEqual(res_empty["status"], "unknown")

    def test_parse_specs_utility(self):
        """Verifies safe JSON specification parsing."""
        valid_json = '{"socket": "AM5", "tdp_w": 105}'
        parsed = app_module.parse_specs(valid_json)
        self.assertEqual(parsed["socket"], "AM5")
        self.assertEqual(parsed["tdp_w"], 105)

        already_dict = {"socket": "AM4"}
        self.assertEqual(app_module.parse_specs(already_dict), {"socket": "AM4"})
        self.assertEqual(app_module.parse_specs(""), {})
        self.assertEqual(app_module.parse_specs(None), {})
        self.assertEqual(app_module.parse_specs("invalid json{"), {})

    def test_price_to_int_utility(self):
        """Verifies integer price conversion and boundary checks."""
        self.assertEqual(app_module.price_to_int(12500), 12500)
        self.assertEqual(app_module.price_to_int("12500"), 12500)
        self.assertEqual(app_module.price_to_int(12500.4), 12500)
        self.assertEqual(app_module.price_to_int(12500.8), 12501)
        self.assertIsNone(app_module.price_to_int(-50))
        self.assertIsNone(app_module.price_to_int("invalid"))
        self.assertIsNone(app_module.price_to_int(None))

    def test_observation_freshness(self):
        """Verifies recent and stale price observation classification."""
        fixed_now = datetime(2026, 11, 8, 12, 0, 0, tzinfo=timezone.utc)
        recent_date = "2026-11-05T10:00:00+05:30"
        status, days = app_module.observation_freshness(recent_date, freshness_days=7, now=fixed_now)
        self.assertEqual(status, "recent")
        self.assertLessEqual(days, 7)

        stale_date = "2026-10-15T10:00:00+05:30"
        status, days = app_module.observation_freshness(stale_date, freshness_days=7, now=fixed_now)
        self.assertEqual(status, "stale")
        self.assertGreater(days, 7)

    def test_choose_cheapest_price_lowest_vs_available(self):
        """Verifies price selection under lowest-price and available-first policies."""
        lookup = {
            "test-comp": [
                {
                    "price_id": "p-1",
                    "price_inr": 8000,
                    "availability": "unavailable",
                    "freshness": "stale",
                    "price_type": "seller_observation",
                },
                {
                    "price_id": "p-2",
                    "price_inr": 8500,
                    "availability": "available",
                    "freshness": "recent",
                    "price_type": "seller_observation",
                },
                {
                    "price_id": "p-3",
                    "price_inr": 7500,
                    "availability": "unknown",
                    "freshness": "unknown",
                    "price_type": "planning_estimate",
                },
            ]
        }
        # Lowest price policy: selects lowest price (planning estimate is ranked after equal seller obs, but here 7500 is lowest)
        cheapest = app_module.choose_cheapest_price("test-comp", lookup, prefer_available=False)
        self.assertEqual(cheapest["price_id"], "p-3")
        self.assertEqual(cheapest["price_inr"], 7500)

        # Available-first policy: selects available and recent over cheaper unavailable or estimate
        available_best = app_module.choose_cheapest_price("test-comp", lookup, prefer_available=True)
        self.assertEqual(available_best["price_id"], "p-2")
        self.assertEqual(available_best["price_inr"], 8500)

    def test_compatibility_engine_integration_without_old_recommender(self):
        """Verifies that direct compatibility inspection functions remain fully operational."""
        cpu_specs = {
            "socket": "AM5",
            "supported_chipsets": ["B650", "X670"],
            "minimum_bios_version": "1.20",
        }
        mb_compatible = {
            "socket": "AM5",
            "chipset": "B650",
            "bios_version": "1.20",
        }
        mb_incompatible = {"socket": "AM4", "chipset": "B550"}

        res_compat = check_cpu_motherboard(cpu_specs, mb_compatible)
        self.assertEqual(res_compat.status, "compatible")

        res_incompat = check_cpu_motherboard(cpu_specs, mb_incompatible)
        self.assertEqual(res_incompat.status, "incompatible")

        gpu_specs = {"length_mm": 320}
        case_fits = {"max_gpu_length_mm": 360}
        case_too_small = {"max_gpu_length_mm": 300}

        self.assertEqual(check_gpu_case(gpu_specs, case_fits).status, "compatible")
        self.assertEqual(check_gpu_case(gpu_specs, case_too_small).status, "incompatible")


if __name__ == "__main__":
    unittest.main()
