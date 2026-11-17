"""
BuildWise-AI — Phase 11C: Machine Learning Integration Tests

Validates:
- Reusable PerformancePredictionService operations.
- CPU & GPU model artifact loading and inference.
- Hardware feature extraction, unit validation, and boundary enforcement.
- Graceful handling of missing/invalid specifications.
- Model failure containment without application crashes.
- Build Mode ML performance predictions and compatibility authority.
- Upgrade Mode side-by-side performance estimation and delta calculations.
- Strict isolation of non-CPU/GPU categories from synthetic/fake predictions.
- Zero modification to production CSV files and model artifacts.
"""
import hashlib
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

import app as app_module
from src.performance_service import PerformancePredictionService, get_performance_service
from src.validator import load_and_validate

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PRODUCTION_HASHES = {
    "components.csv": "6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc",
    "benchmarks.csv": "4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702",
    "prices.csv": "6a8a6e14cca32c120170ab244a0f93ebd6514d212264a2034ca96844c71ca625",
}


class PerformancePredictionServiceTests(unittest.TestCase):
    """Unit tests for PerformancePredictionService layer."""

    @classmethod
    def setUpClass(cls):
        cls.service = get_performance_service()
        cls.components, cls.prices, cls.issues = load_and_validate(ROOT / "data")
        cls.benchmarks = pd.read_csv(ROOT / "data" / "benchmarks.csv")

    def test_01_service_loads_artifacts(self):
        """1. Verifies that CPU and GPU pipelines and metadata load successfully."""
        self.assertTrue(self.service.is_cpu_model_available(), "CPU model pipeline should be available")
        self.assertTrue(self.service.is_gpu_model_available(), "GPU model pipeline should be available")

        cpu_meta = self.service.get_cpu_metadata()
        gpu_meta = self.service.get_gpu_metadata()
        self.assertEqual(cpu_meta.get("device_type"), "CPU")
        self.assertEqual(gpu_meta.get("device_type"), "GPU")
        self.assertEqual(cpu_meta.get("target_variable"), "cinebench_r23_multi_core_score")
        self.assertEqual(gpu_meta.get("target_variable"), "timespy_graphics_score")

    def test_02_valid_cpu_inference(self):
        """2. Tests inference on valid catalog CPUs across AMD and Intel."""
        cpu_samples = self.components[self.components["category"].str.casefold() == "cpu"].head(5)
        for _, row in cpu_samples.iterrows():
            res = self.service.predict_component(row.to_dict())
            self.assertEqual(res["status"], "available")
            self.assertEqual(res["target_suite"], "Cinebench R23")
            self.assertEqual(res["target_metric"], "Multi-Core Score")
            self.assertIsInstance(res["score"], float)
            self.assertGreater(res["score"], 1000.0)
            self.assertTrue(res["is_prediction"])
            self.assertIn("pts", res["score_formatted"])

    def test_03_valid_gpu_inference(self):
        """3. Tests inference on valid enriched catalog GPUs."""
        # Test with known enriched GPU component IDs
        enriched_ids = ["DS3_GPU_001", "DS3_GPU_002", "DS3_GPU_007", "DS3_GPU_009"]
        for cid in enriched_ids:
            matches = self.components[self.components["component_id"] == cid]
            if not matches.empty:
                row = matches.iloc[0].to_dict()
                res = self.service.predict_component(row)
                self.assertEqual(res["status"], "available")
                self.assertEqual(res["target_suite"], "3DMark Time Spy")
                self.assertEqual(res["target_metric"], "Graphics Score")
                self.assertIsInstance(res["score"], float)
                self.assertGreater(res["score"], 4000.0)
                self.assertTrue(res["is_prediction"])
                self.assertIn("pts", res["score_formatted"])

    def test_04_missing_cpu_features_imputation_and_rejection(self):
        """4. Tests median imputation for base_clock_ghz and rejection of missing cores."""
        # Missing base_clock_ghz should succeed via median imputation
        cpu_missing_base = {
            "category": "cpu",
            "brand": "AMD",
            "model": "Test CPU Missing Base",
            "specs_json": json.dumps({
                "cores": 8,
                "threads": 16,
                "boost_ghz": 5.0,
                # base_clock_ghz missing
                "tdp_w": 105,
                "socket": "AM5",
                "ram_type": "DDR5",
            }),
        }
        res_ok = self.service.predict_component(cpu_missing_base)
        self.assertEqual(res_ok["status"], "available")
        self.assertGreater(res_ok["score"], 10000.0)

        # Missing cores should be rejected cleanly
        cpu_missing_cores = {
            "category": "cpu",
            "brand": "AMD",
            "model": "Test CPU Missing Cores",
            "specs_json": json.dumps({
                "threads": 16,
                "boost_ghz": 5.0,
                "tdp_w": 105,
                "socket": "AM5",
            }),
        }
        res_fail = self.service.predict_component(cpu_missing_cores)
        self.assertEqual(res_fail["status"], "unavailable")
        self.assertIsNone(res_fail["score"])
        self.assertIn("cores", res_fail["message"].lower())

    def test_05_invalid_feature_values_rejected(self):
        """5. Confirms that absurd or physically impossible values are rejected."""
        # Negative cores
        bad_cpu_1 = {
            "category": "cpu",
            "brand": "AMD",
            "model": "Bad CPU",
            "specs_json": json.dumps({"cores": -4, "threads": 8, "boost_ghz": 4.5, "tdp_w": 65, "socket": "AM4"}),
        }
        res_1 = self.service.predict_component(bad_cpu_1)
        self.assertEqual(res_1["status"], "unavailable")

        # Threads fewer than cores
        bad_cpu_2 = {
            "category": "cpu",
            "brand": "AMD",
            "model": "Bad CPU 2",
            "specs_json": json.dumps({"cores": 8, "threads": 4, "boost_ghz": 4.5, "tdp_w": 65, "socket": "AM4"}),
        }
        res_2 = self.service.predict_component(bad_cpu_2)
        self.assertEqual(res_2["status"], "unavailable")

        # Boost clock > 10 GHz
        bad_cpu_3 = {
            "category": "cpu",
            "brand": "AMD",
            "model": "Bad CPU 3",
            "specs_json": json.dumps({"cores": 8, "threads": 16, "boost_ghz": 25.0, "tdp_w": 65, "socket": "AM4"}),
        }
        res_3 = self.service.predict_component(bad_cpu_3)
        self.assertEqual(res_3["status"], "unavailable")

    def test_06_unsupported_categories_receive_no_fake_predictions(self):
        """6. Confirms Motherboards, RAM, Cases, PSUs, Coolers, Storage receive unsupported status."""
        for cat in ["motherboard", "ram", "case", "psu", "cooler", "storage"]:
            sample_row = {"category": cat, "brand": "TestBrand", "model": "TestModel", "specs_json": "{}"}
            res = self.service.predict_component(sample_row)
            self.assertEqual(res["status"], "unsupported", f"Category '{cat}' must not receive ML predictions")
            self.assertIsNone(res["score"])
            self.assertFalse(res["is_prediction"])
            self.assertEqual(res["score_formatted"], "—")

    def test_07_model_failure_containment(self):
        """7. Verifies that simulated missing model file does not crash the service."""
        isolated_service = PerformancePredictionService()
        # Force pipeline to None
        isolated_service._cpu_pipeline = None
        isolated_service._cpu_load_attempted = True

        sample_cpu = self.components[self.components["category"].str.casefold() == "cpu"].iloc[0].to_dict()
        res = isolated_service.predict_cpu(sample_cpu)
        self.assertEqual(res["status"], "unavailable")
        self.assertIsNone(res["score"])
        self.assertIn("unavailable", res["message"].lower())


class BuildModeAndUpgradeModeIntegrationTests(unittest.TestCase):
    """Integration tests for Build Mode and Upgrade Mode ML prediction display and logic."""

    @classmethod
    def setUpClass(cls):
        cls.service = get_performance_service()
        cls.components, cls.prices, _ = load_and_validate(ROOT / "data")
        cls.benchmarks = pd.read_csv(ROOT / "data" / "benchmarks.csv")

    def test_08_cpu_upgrade_comparison_delta(self):
        """8. Tests side-by-side CPU comparison and percentage delta calculation."""
        cpus = self.components[self.components["category"].str.casefold() == "cpu"]
        # Ryzen 5 7600X vs Ryzen 9 7900X
        cpu_a = cpus[cpus["model"].str.contains("7600X", na=False)].iloc[0].to_dict()
        cpu_b = cpus[cpus["model"].str.contains("7900X", na=False)].iloc[0].to_dict()

        comp_res = self.service.compare_predicted_performance(cpu_a, cpu_b)
        self.assertEqual(comp_res["status"], "available")
        self.assertEqual(comp_res["category"], "cpu")
        self.assertEqual(comp_res["suite"], "Cinebench R23")
        self.assertGreater(comp_res["score_b"], comp_res["score_a"])
        self.assertGreater(comp_res["delta"], 0)
        self.assertGreater(comp_res["pct_change"], 0)
        self.assertTrue(comp_res["is_model_estimated"])

    def test_09_gpu_upgrade_comparison_delta(self):
        """9. Tests side-by-side GPU comparison and percentage delta calculation."""
        gpus = self.components[self.components["category"].str.casefold() == "gpu"]
        # RTX 3060 vs RTX 4070 SUPER
        gpu_a = gpus[gpus["component_id"] == "DS3_GPU_001"].iloc[0].to_dict()
        gpu_b = gpus[gpus["component_id"] == "DS3_GPU_007"].iloc[0].to_dict()

        comp_res = self.service.compare_predicted_performance(gpu_a, gpu_b)
        self.assertEqual(comp_res["status"], "available")
        self.assertEqual(comp_res["category"], "gpu")
        self.assertEqual(comp_res["suite"], "3DMark Time Spy")
        self.assertGreater(comp_res["score_b"], comp_res["score_a"])
        self.assertGreater(comp_res["delta"], 0)
        self.assertTrue(comp_res["is_model_estimated"])

    def test_10_upgrade_comparison_with_unsupported_category_or_missing_specs(self):
        """10. Tests that cross-category or incomplete specs return unavailable delta."""
        cpus = self.components[self.components["category"].str.casefold() == "cpu"]
        gpus = self.components[self.components["category"].str.casefold() == "gpu"]
        cpu = cpus.iloc[0].to_dict()
        gpu = gpus.iloc[0].to_dict()

        # Cross category CPU vs GPU must be rejected
        cross_res = self.service.compare_predicted_performance(cpu, gpu)
        self.assertEqual(cross_res["status"], "unavailable")

        # GPU with missing specs compared against valid GPU
        bad_gpu = {"category": "gpu", "brand": "Generic", "model": "Unknown", "specs_json": "{}"}
        miss_res = self.service.compare_predicted_performance(bad_gpu, gpu)
        self.assertEqual(miss_res["status"], "unavailable")

    def test_11_compatibility_remains_authoritative(self):
        """11. Verifies that high predicted performance never overrides compatibility rules."""
        # Fast AM5 CPU (high Cinebench score) vs LGA1700 Motherboard
        am5_cpu = {
            "component_id": "fast-am5-cpu",
            "category": "cpu",
            "brand": "AMD",
            "model": "Ryzen 9 7950X",
            "specs_json": json.dumps({"cores": 16, "threads": 32, "boost_ghz": 5.7, "tdp_w": 170, "socket": "AM5", "ram_type": "DDR5"}),
        }
        intel_mb = {
            "component_id": "intel-lga1700-mb",
            "category": "motherboard",
            "brand": "ASUS",
            "model": "PRIME Z790-P",
            "specs_json": json.dumps({"socket": "LGA1700", "chipset": "Z790"}),
        }
        # CPU prediction is available and high
        cpu_pred = self.service.predict_component(am5_cpu)
        self.assertEqual(cpu_pred["status"], "available")
        self.assertGreater(cpu_pred["score"], 35000.0)

        # Compatibility check must strictly fail (INCOMPATIBLE)
        compat_res = app_module.evaluate_component_compatibility(intel_mb, {"cpu": am5_cpu})
        self.assertEqual(compat_res["status"], "incompatible", "Compatibility check must remain strictly authoritative")

    def test_12_apptest_renders_ml_models_section_and_metrics(self):
        """12. Verifies Streamlit AppTest renders ML Performance Models in Home overview."""
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
        self.assertFalse(app.exception, f"AppTest raised an exception: {app.exception}")

        # Verify Home view metrics
        metric_labels = [item.label for item in app.metric]
        self.assertIn("Component Catalog", metric_labels)
        self.assertIn("Retail Price Observations", metric_labels)
        self.assertIn("Benchmark Observations", metric_labels)

        # Verify ML Performance Models section rendered
        markdown_texts = [item.value for item in app.markdown]
        self.assertTrue(
            any("Supervised Machine Learning Performance Prediction Models" in m for m in markdown_texts),
            "Expected ML Performance Models header not found in Home view",
        )
        self.assertTrue(
            any("CPU Performance Model" in m for m in markdown_texts),
            "Expected CPU Performance Model subsection not found",
        )
        self.assertTrue(
            any("GPU Performance Model" in m for m in markdown_texts),
            "Expected GPU Performance Model subsection not found",
        )

    def test_13_production_csv_hashes_remain_identical(self):
        """13. Confirms that production components.csv, benchmarks.csv, and prices.csv remain untouched."""
        data_dir = ROOT / "data"
        for filename, expected_hash in EXPECTED_PRODUCTION_HASHES.items():
            filepath = data_dir / filename
            self.assertTrue(filepath.is_file(), f"Production file {filename} does not exist")
            hasher = hashlib.sha256()
            with open(filepath, "rb") as f:
                hasher.update(f.read())
            actual_hash = hasher.hexdigest()
            self.assertEqual(
                actual_hash,
                expected_hash,
                f"Production file {filename} hash mismatch! Expected {expected_hash}, got {actual_hash}",
            )


if __name__ == "__main__":
    unittest.main()
