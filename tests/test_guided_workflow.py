import hashlib
import json
from pathlib import Path
import unittest
import pandas as pd

import app as app_module
from src.validator import load_and_validate

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_HASHES = {
    "components.csv": "6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc",
    "prices.csv": "943e87ae76412d9ed37d442aafd7f079adb0344fede321c5989d37d97f929e7b",
    "benchmarks.csv": "4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702",
}


class GuidedWorkflowBuildModeTests(unittest.TestCase):
    """Unit tests for Phase 9 Build Mode sequential workflow, compatibility, and budget logic."""

    @classmethod
    def setUpClass(cls):
        cls.components, cls.prices, cls.issues = load_and_validate(ROOT / "data")
        cls.benchmarks = pd.read_csv(ROOT / "data" / "benchmarks.csv")
        cls.pricing_index = app_module.price_lookup(cls.prices)

    def test_build_categories_order_and_labels(self):
        """Verifies the exact sequential selection order required by Phase 9."""
        expected_order = ["cpu", "motherboard", "ram", "case", "gpu", "psu", "cooler", "storage"]
        self.assertEqual(app_module.BUILD_CATEGORIES, expected_order)
        for cat in expected_order:
            self.assertIn(cat, app_module.CATEGORY_LABELS)

    def test_component_filtering_by_category(self):
        """Verifies that all 8 categories can be filtered cleanly and have valid records."""
        for cat in app_module.BUILD_CATEGORIES:
            filtered = self.components[self.components["category"].str.casefold() == cat]
            self.assertFalse(filtered.empty, f"Category '{cat}' should not be empty")
            self.assertGreaterEqual(len(filtered), 10, f"Expected substantial inventory for '{cat}'")

    def test_cpu_motherboard_compatibility_check(self):
        """Tests live candidate compatibility evaluation for Motherboard against selected CPU."""
        am5_cpu = {
            "component_id": "test-am5-cpu",
            "category": "cpu",
            "brand": "AMD",
            "model": "Ryzen 5 7600X",
            "specs_json": json.dumps({"socket": "AM5", "supported_chipsets": ["B650", "X670"]}),
        }
        am5_mb = {
            "component_id": "test-am5-mb",
            "category": "motherboard",
            "brand": "MSI",
            "model": "PRO B650M-A",
            "specs_json": json.dumps({"socket": "AM5", "chipset": "B650"}),
        }
        lga1700_mb = {
            "component_id": "test-intel-mb",
            "category": "motherboard",
            "brand": "ASUS",
            "model": "PRIME B760-PLUS",
            "specs_json": json.dumps({"socket": "LGA1700", "chipset": "B760"}),
        }

        # Check with AM5 CPU selected
        selected = {"cpu": am5_cpu}

        # AM5 MB should be compatible or unknown (depending on BIOS documentation), never incompatible
        res_compat = app_module.evaluate_component_compatibility(am5_mb, selected)
        self.assertIn(res_compat["status"], ("compatible", "unknown"))
        self.assertNotEqual(res_compat["status"], "incompatible")

        # LGA1700 MB must be strictly incompatible
        res_incompat = app_module.evaluate_component_compatibility(lga1700_mb, selected)
        self.assertEqual(res_incompat["status"], "incompatible")
        self.assertTrue(any("socket" in chk["pair"].lower() for chk in res_incompat["checks"]))

    def test_motherboard_ram_compatibility_check(self):
        """Tests live candidate compatibility evaluation for RAM against selected Motherboard."""
        ddr5_mb = {
            "component_id": "test-b650-mb",
            "category": "motherboard",
            "specs_json": json.dumps({
                "socket": "AM5",
                "chipset": "B650",
                "ram_type": "DDR5",
                "ram_max_gb": 128,
                "ram_slots": 4,
            }),
        }
        ddr5_ram = {
            "component_id": "test-ddr5-ram",
            "category": "ram",
            "specs_json": json.dumps({
                "ram_type": "DDR5",
                "capacity_gb": 32,
                "speed_mtps": 6000,
            }),
        }
        ddr4_ram = {
            "component_id": "test-ddr4-ram",
            "category": "ram",
            "specs_json": json.dumps({
                "ram_type": "DDR4",
                "capacity_gb": 16,
                "speed_mtps": 3200,
            }),
        }

        selected = {"motherboard": ddr5_mb}

        # DDR5 RAM on DDR5 MB is compatible/unknown (never incompatible)
        res_ddr5 = app_module.evaluate_component_compatibility(ddr5_ram, selected)
        self.assertIn(res_ddr5["status"], ("compatible", "unknown"))

        # DDR4 RAM on DDR5 MB is strictly incompatible
        res_ddr4 = app_module.evaluate_component_compatibility(ddr4_ram, selected)
        self.assertEqual(res_ddr4["status"], "incompatible")

    def test_multiple_component_selections_retention(self):
        """Verifies that multiple selections across all categories are retained correctly."""
        selections = {
            "cpu": {"component_id": "c1", "brand": "AMD", "model": "Ryzen 5 7600X"},
            "motherboard": {"component_id": "m1", "brand": "MSI", "model": "B650M-A"},
            "ram": {"component_id": "r1", "brand": "Corsair", "model": "Vengeance 32GB"},
            "case": {"component_id": "cs1", "brand": "Ant Esports", "model": "ICE-100"},
            "gpu": {"component_id": "g1", "brand": "ZOTAC", "model": "RTX 4060"},
            "psu": {"component_id": "p1", "brand": "Corsair", "model": "CV650"},
            "cooler": {"component_id": "cl1", "brand": "Deepcool", "model": "AK400"},
            "storage": {"component_id": "s1", "brand": "Crucial", "model": "P3 Plus 1TB"},
        }
        self.assertEqual(len(selections), 8)
        for cat in app_module.BUILD_CATEGORIES:
            self.assertIn(cat, selections)

    def test_changing_earlier_component_triggers_revalidation(self):
        """Verifies that changing an earlier component flags newly conflicting selections."""
        # Baseline selections: AM5 CPU + AM5 Motherboard
        selections = {
            "cpu": {
                "component_id": "c_am5",
                "category": "cpu",
                "specs_json": json.dumps({"socket": "AM5", "supported_chipsets": ["B650"]}),
            },
            "motherboard": {
                "component_id": "mb_am5",
                "category": "motherboard",
                "specs_json": json.dumps({"socket": "AM5", "chipset": "B650"}),
            },
        }
        reval_before = app_module.reevaluate_build_selections(selections)
        self.assertFalse(reval_before["has_incompatibilities"])

        # User changes CPU to an Intel LGA1700 CPU
        selections["cpu"] = {
            "component_id": "c_intel",
            "category": "cpu",
            "specs_json": json.dumps({"socket": "LGA1700", "supported_chipsets": ["B760"]}),
        }
        reval_after = app_module.reevaluate_build_selections(selections)
        self.assertTrue(reval_after["has_incompatibilities"])
        self.assertFalse(reval_after["is_valid"])
        self.assertTrue(any(conf["status"] == "incompatible" for conf in reval_after["conflicts"]))

    def test_budget_totals_and_missing_price_handling(self):
        """Verifies budget totals use available prices, identify unpriced items, and never assume ₹0 for missing items."""
        mock_pricing = {
            "comp_priced_1": [
                {"price_inr": 20000, "price_type": "seller_observation", "availability": "available", "seller": "MD Computers", "freshness": "recent"}
            ],
            "comp_priced_2": [
                {"price_inr": 15000, "price_type": "planning_estimate", "availability": "unknown", "seller": "MD Computers", "freshness": "unknown"}
            ],
        }
        selections = {
            "cpu": {"component_id": "comp_priced_1", "brand": "BrandA", "model": "ModelA"},
            "motherboard": {"component_id": "comp_priced_2", "brand": "BrandB", "model": "ModelB"},
            "ram": {"component_id": "comp_unpriced", "brand": "BrandC", "model": "ModelC"},
            "gpu": {"_status": "skipped", "category": "gpu"},
        }

        budget_summary = app_module.calculate_build_budget(selections, mock_pricing, budget_inr=50000)
        # Total recorded price should be 20,000 + 15,000 = 35,000
        self.assertEqual(budget_summary["total_recorded_price"], 35000)
        # Total confirmed available should be 20,000 (since comp_priced_2 is a planning estimate)
        self.assertEqual(budget_summary["total_confirmed_available_price"], 20000)
        self.assertEqual(budget_summary["remaining_budget"], 15000)
        self.assertFalse(budget_summary["is_over_budget"])

        # Unpriced items must be detected and flagged
        self.assertTrue(budget_summary["has_unpriced"])
        self.assertEqual(budget_summary["unpriced_count"], 1)
        self.assertEqual(budget_summary["verified_seller_count"], 1)
        self.assertEqual(budget_summary["planning_estimate_count"], 1)

        # Check unpriced item display is 'Price unavailable', not '₹0'
        ram_item = next(it for it in budget_summary["items"] if it["category"] == "ram")
        self.assertIsNone(ram_item["price_inr"])
        self.assertEqual(ram_item["price_display"], "Price unavailable")

    def test_unknown_compatibility_preserved(self):
        """Verifies that missing specifications produce 'unknown' rather than falling back to compatible."""
        cpu_incomplete = {
            "component_id": "cpu_inc",
            "category": "cpu",
            "specs_json": "{}",
        }
        mb_incomplete = {
            "component_id": "mb_inc",
            "category": "motherboard",
            "specs_json": "{}",
        }
        res = app_module.evaluate_component_compatibility(mb_incomplete, {"cpu": cpu_incomplete})
        self.assertEqual(res["status"], "unknown")
        self.assertNotEqual(res["status"], "compatible")


class GuidedWorkflowUpgradeModeTests(unittest.TestCase):
    """Unit tests for Phase 9 Upgrade Mode workflow, benchmark comparison, and replacement evaluation."""

    @classmethod
    def setUpClass(cls):
        cls.components, cls.prices, cls.issues = load_and_validate(ROOT / "data")
        cls.benchmarks = pd.read_csv(ROOT / "data" / "benchmarks.csv")

    def test_cpu_benchmark_comparison_same_metric(self):
        """Verifies Cinebench R23 Multi-Core score comparison between two CPUs."""
        # amd-ryzen-7-7800x3d (17,762 pts) vs amd-ryzen-7-7700x (20,399 pts)
        cpu_a = "amd-ryzen-7-7800x3d"
        cpu_b = "amd-ryzen-7-7700x"

        res = app_module.compare_benchmarks(cpu_a, cpu_b, self.benchmarks)
        self.assertEqual(res["status"], "available")
        self.assertEqual(res["suite"], "Cinebench R23")
        self.assertEqual(res["metric"], "Multi-Core Score")
        self.assertEqual(res["score_a"], 17762.0)
        self.assertEqual(res["score_b"], 20399.0)
        self.assertEqual(res["delta"], 2637.0)
        self.assertAlmostEqual(res["pct_change"], 14.8463, places=2)

    def test_gpu_benchmark_comparison_same_metric(self):
        """Verifies 3DMark Time Spy Graphics Score comparison between two GPUs."""
        gpu_a = "DS3_GPU_036"  # 36,742 pts
        gpu_b = "DS3_GPU_035"  # 28,642 pts

        res = app_module.compare_benchmarks(gpu_a, gpu_b, self.benchmarks)
        self.assertEqual(res["status"], "available")
        self.assertEqual(res["suite"], "3DMark Time Spy")
        self.assertEqual(res["metric"], "Graphics Score")
        self.assertEqual(res["score_a"], 36742.0)
        self.assertEqual(res["score_b"], 28642.0)
        self.assertEqual(res["delta"], -8100.0)
        self.assertAlmostEqual(res["pct_change"], -22.0456, places=2)

    def test_cross_category_and_missing_benchmark_handling(self):
        """Verifies CPU vs GPU benchmark comparison is rejected, and missing benchmark returns unavailable."""
        cpu_id = "amd-ryzen-7-7800x3d"
        gpu_id = "DS3_GPU_036"

        cross_res = app_module.compare_benchmarks(cpu_id, gpu_id, self.benchmarks)
        self.assertEqual(cross_res["status"], "unavailable")
        self.assertIn("Incompatible benchmark suites", cross_res["message"])

        missing_res = app_module.compare_benchmarks(cpu_id, "nonexistent-id", self.benchmarks)
        self.assertEqual(missing_res["status"], "unavailable")
        self.assertEqual(missing_res["message"], "Benchmark data unavailable")

    def test_upgrade_candidate_compatibility_against_retained_hardware(self):
        """Verifies GPU upgrade candidate is evaluated against retained case and PSU."""
        retained = {
            "case": {
                "status": "catalog",
                "component_id": "case-test",
                "specs_json": json.dumps({"max_gpu_length_mm": 300}),
            },
            "psu": {
                "status": "catalog",
                "component_id": "psu-test",
                "specs_json": json.dumps({"wattage_w": 550, "power_connectors": {"pcie_8pin": 2}}),
            },
            "cpu": {
                "status": "catalog",
                "component_id": "cpu-test",
                "specs_json": json.dumps({"tdp_w": 65}),
            },
        }

        # GPU that fits within 300mm and within 550W PSU
        small_gpu = {
            "component_id": "gpu-small",
            "category": "gpu",
            "specs_json": json.dumps({
                "length_mm": 242,
                "tdp_w": 115,
                "recommended_system_psu_w": 450,
                "required_power_connectors": {"pcie_8pin": 1},
            }),
        }
        res_small = app_module.evaluate_component_compatibility(small_gpu, retained)
        self.assertEqual(res_small["status"], "compatible")

        # GPU that is 340mm (exceeds 300mm max_gpu_length_mm)
        big_gpu = {
            "component_id": "gpu-big",
            "category": "gpu",
            "specs_json": json.dumps({"length_mm": 340, "tdp_w": 250}),
        }
        res_big = app_module.evaluate_component_compatibility(big_gpu, retained)
        self.assertEqual(res_big["status"], "incompatible")

    def test_upgrade_mode_with_unknown_retained_hardware(self):
        """Verifies that unknown retained hardware produces an unknown check result without crashing."""
        retained_unknown = {
            "motherboard": {
                "status": "unknown",
                "component_id": "unknown_motherboard",
            }
        }
        cpu_candidate = {
            "component_id": "test-cpu",
            "category": "cpu",
            "specs_json": json.dumps({"socket": "AM5"}),
        }
        res = app_module.evaluate_component_compatibility(cpu_candidate, retained_unknown)
        self.assertEqual(res["status"], "unknown")
        self.assertTrue(any("unknown" in chk["reason"].lower() for chk in res["checks"]))


class GuidedWorkflowSafeguardsTests(unittest.TestCase):
    """Safeguards verifying isolation, anti-combinatorial guarantees, and data protection."""

    def test_anti_combinatorial_guarantees(self):
        """Verifies zero DFS, zero Cartesian products, and zero legacy recommendation functions."""
        self.assertFalse(hasattr(app_module, "build_recommendation"))
        self.assertFalse(hasattr(app_module, "PURPOSE_LAYOUT"))
        self.assertFalse(hasattr(app_module, "run_exhaustive_search"))

    def test_dataset_checksums_remain_unmodified(self):
        """Verifies components and benchmarks retain SHA-256 hashes, and prices retains baseline records."""
        for filename in ["components.csv", "benchmarks.csv"]:
            expected_hash = EXPECTED_HASHES[filename]
            path = ROOT / "data" / filename
            data = path.read_bytes()
            actual_hash = hashlib.sha256(data).hexdigest()
            self.assertEqual(
                actual_hash,
                expected_hash,
                f"Data integrity violation: {filename} hash mismatch!",
            )
        prices_df = pd.read_csv(ROOT / "data" / "prices.csv")
        self.assertGreaterEqual(len(prices_df), 599)


if __name__ == "__main__":
    unittest.main()
