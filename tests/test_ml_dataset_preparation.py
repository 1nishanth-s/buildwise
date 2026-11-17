import hashlib
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

from experiments.performance_prediction.config import (
    BENCHMARKS_CSV,
    COMPONENTS_CSV,
    CPU_OUTPUT_COLUMNS,
    CPU_PREDICTIVE_FEATURES,
    CPU_TARGET,
    CPU_TRAINING_CSV,
    GPU_OUTPUT_COLUMNS,
    GPU_PREDICTIVE_FEATURES,
    GPU_TARGET,
    GPU_TRAINING_CSV,
    PRICES_CSV,
)
from experiments.performance_prediction.cpu_features import (
    extract_cpu_record_features,
    parse_cpu_specs,
)
from experiments.performance_prediction.dataset_preparation import (
    prepare_cpu_dataset,
    prepare_gpu_dataset,
)
from experiments.performance_prediction.feature_extraction import (
    extract_cpu_features,
    extract_gpu_features,
    get_feature_names,
)
from experiments.performance_prediction.gpu_features import (
    extract_gpu_record_features,
    parse_gpu_specs,
)
from experiments.performance_prediction.validation import (
    get_cpu_group_kfold,
    get_gpu_group_kfold,
    split_holdout_dataset,
)

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_HASHES = {
    "components.csv": "6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc",
    "prices.csv": "943e87ae76412d9ed37d442aafd7f079adb0344fede321c5989d37d97f929e7b",
    "benchmarks.csv": "4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702",
}


class MlDatasetPreparationTests(unittest.TestCase):
    """
    Comprehensive unit tests for Phase 10 ML Dataset Audit, Feature Extraction,
    and Training Data Preparation.
    """

    @classmethod
    def setUpClass(cls):
        # Load generated training datasets
        if not CPU_TRAINING_CSV.is_file():
            cls.df_cpu = prepare_cpu_dataset()
        else:
            cls.df_cpu = pd.read_csv(CPU_TRAINING_CSV)

        if not GPU_TRAINING_CSV.is_file():
            cls.df_gpu = prepare_gpu_dataset()
        else:
            cls.df_gpu = pd.read_csv(GPU_TRAINING_CSV)

    def test_01_cpu_benchmark_filtering(self):
        """1. Verifies that CPU dataset strictly filters Cinebench R23 records."""
        bench = pd.read_csv(BENCHMARKS_CSV)
        cpu_bench = bench[bench["benchmark_suite"] == "Cinebench R23"]
        self.assertEqual(len(cpu_bench), 180)
        self.assertEqual(len(self.df_cpu), 180)

    def test_02_gpu_benchmark_filtering(self):
        """2. Verifies that GPU dataset strictly filters 3DMark Time Spy records."""
        bench = pd.read_csv(BENCHMARKS_CSV)
        gpu_bench = bench[bench["benchmark_suite"] == "3DMark Time Spy"]
        self.assertEqual(len(gpu_bench), 57)
        self.assertEqual(len(self.df_gpu), 57)

    def test_03_correct_benchmark_metric_selection(self):
        """3. Confirms correct metrics: Multi-Core Score for CPU, Graphics Score for GPU."""
        bench = pd.read_csv(BENCHMARKS_CSV)
        cb_metrics = set(bench[bench["benchmark_suite"] == "Cinebench R23"]["benchmark_metric"])
        ts_metrics = set(bench[bench["benchmark_suite"] == "3DMark Time Spy"]["benchmark_metric"])
        self.assertEqual(cb_metrics, {"Multi-Core Score"})
        self.assertEqual(ts_metrics, {"Graphics Score"})

    def test_04_correct_target_extraction(self):
        """4. Confirms target columns exist and contain valid positive numeric values."""
        # CPU
        self.assertIn(CPU_TARGET, self.df_cpu.columns)
        self.assertEqual(self.df_cpu[CPU_TARGET].isnull().sum(), 0)
        self.assertTrue(all(self.df_cpu[CPU_TARGET] > 0))
        self.assertEqual(self.df_cpu[CPU_TARGET].min(), 1380.0)
        self.assertEqual(self.df_cpu[CPU_TARGET].max(), 98500.0)

        # GPU
        self.assertIn(GPU_TARGET, self.df_gpu.columns)
        self.assertEqual(self.df_gpu[GPU_TARGET].isnull().sum(), 0)
        self.assertTrue(all(self.df_gpu[GPU_TARGET] > 0))
        self.assertEqual(self.df_gpu[GPU_TARGET].min(), 4780.0)
        self.assertEqual(self.df_gpu[GPU_TARGET].max(), 36742.0)

    def test_05_valid_component_id_mapping(self):
        """5. Confirms all component IDs match real components in components.csv."""
        comp = pd.read_csv(COMPONENTS_CSV)
        cpu_cids = set(comp[comp["category"] == "cpu"]["component_id"])
        gpu_cids = set(comp[comp["category"] == "gpu"]["component_id"])

        self.assertTrue(set(self.df_cpu["component_id"]).issubset(cpu_cids))
        self.assertTrue(set(self.df_gpu["component_id"]).issubset(gpu_cids))

    def test_06_valid_specification_json_parsing(self):
        """6. Confirms specs_json parsing works with strings and dicts and handles invalid JSON."""
        # Valid string
        valid_json = '{"socket": "AM5", "cores": 8}'
        self.assertEqual(parse_cpu_specs(valid_json), {"socket": "AM5", "cores": 8})
        self.assertEqual(parse_gpu_specs(valid_json), {"socket": "AM5", "cores": 8})

        # Already dict
        self.assertEqual(parse_cpu_specs({"cores": 6}), {"cores": 6})
        self.assertEqual(parse_gpu_specs({"vram_gb": 12}), {"vram_gb": 12})

        # Empty / None / Invalid
        self.assertEqual(parse_cpu_specs(""), {})
        self.assertEqual(parse_cpu_specs(None), {})
        self.assertEqual(parse_cpu_specs("invalid{"), {})

    def test_07_correct_numerical_unit_conversion(self):
        """7. Confirms CPU frequencies are in GHz, GPU frequencies in MHz, and values are numeric."""
        # CPU
        self.assertTrue(all(self.df_cpu["boost_clock_ghz"] > 1.0))
        self.assertTrue(all(self.df_cpu["boost_clock_ghz"] < 10.0))
        self.assertTrue(all(self.df_cpu["tdp_w"] >= 15.0))

        # GPU
        self.assertTrue(all(self.df_gpu["base_clock_mhz"] >= 1000.0))
        self.assertTrue(all(self.df_gpu["boost_clock_mhz"] >= 1400.0))
        self.assertTrue(all(self.df_gpu["board_power_w"] >= 50.0))

    def test_08_correct_categorical_feature_extraction(self):
        """8. Confirms categorical features are properly formatted without empty strings."""
        # CPU
        self.assertTrue(set(self.df_cpu["brand"]).issubset({"AMD", "Intel"}))
        self.assertTrue(len(set(self.df_cpu["socket"])) >= 8)
        self.assertTrue(all(len(s.strip()) > 0 for s in self.df_cpu["socket"]))

        # GPU
        self.assertTrue(set(self.df_gpu["chipmaker"]).issubset({"AMD", "NVIDIA", "Intel"}))
        self.assertTrue(set(self.df_gpu["architecture"]).issubset(
            {"RDNA 3", "Ada Lovelace", "Ampere", "RDNA 2", "Xe2-HPG"}
        ))

    def test_09_missing_feature_handling(self):
        """9. Confirms base_clock_ghz has 30 missing values and is cleanly represented as NaN."""
        self.assertEqual(self.df_cpu["base_clock_ghz"].isnull().sum(), 30)
        self.assertEqual(self.df_cpu["base_clock_ghz"].notna().sum(), 150)

    def test_10_invalid_feature_handling(self):
        """10. Confirms extractor rejects non-positive cores or invalid specs."""
        invalid_cpu = {
            "component_id": "test_bad",
            "brand": "Intel",
            "model": "Bad Core",
            "specs_json": json.dumps({"cores": 0, "threads": 4, "boost_ghz": 4.0, "tdp_w": 65, "socket": "LGA1700"}),
        }
        with self.assertRaises(ValueError):
            extract_cpu_record_features(invalid_cpu)

    def test_11_missing_benchmark_target_exclusion(self):
        """11. Confirms unbenchmarked GPUs (161 components) are excluded from the GPU training dataset."""
        self.assertEqual(len(self.df_gpu), 57)
        comp = pd.read_csv(COMPONENTS_CSV)
        total_gpus = len(comp[comp["category"] == "gpu"])
        self.assertEqual(total_gpus, 218)
        self.assertEqual(total_gpus - len(self.df_gpu), 161)

    def test_12_no_benchmark_target_leakage_into_features(self):
        """12. Confirms that predictive feature sets strictly exclude benchmark targets."""
        cpu_features = get_feature_names("cpu")
        gpu_features = get_feature_names("gpu")

        self.assertNotIn(CPU_TARGET, cpu_features)
        self.assertNotIn(GPU_TARGET, cpu_features)
        self.assertNotIn(CPU_TARGET, gpu_features)
        self.assertNotIn(GPU_TARGET, gpu_features)
        self.assertNotIn("score", cpu_features)
        self.assertNotIn("score", gpu_features)

    def test_13_no_component_id_used_as_predictor(self):
        """13. Confirms component_id, benchmark_id, and URLs are not in predictive feature sets."""
        forbidden = ["component_id", "benchmark_id", "source_url", "url", "price_inr", "seller"]
        for feat in get_feature_names("cpu"):
            self.assertNotIn(feat.lower(), forbidden)
        for feat in get_feature_names("gpu"):
            self.assertNotIn(feat.lower(), forbidden)

    def test_14_dataset_creation_reproducibility(self):
        """14. Confirms that preparing datasets twice produces bit-for-bit identical DataFrames."""
        df_cpu_2 = prepare_cpu_dataset(output_path=None)
        pd.testing.assert_frame_equal(self.df_cpu, df_cpu_2)

        df_gpu_2 = prepare_gpu_dataset(output_path=None)
        pd.testing.assert_frame_equal(self.df_gpu, df_gpu_2)

    def test_15_group_aware_splitting_behavior(self):
        """15. Confirms GroupKFold and GroupShuffleSplit enforce zero group leakage."""
        # CPU 5-fold GroupKFold
        for train_idx, val_idx in get_cpu_group_kfold(self.df_cpu, n_splits=5):
            train_groups = set(self.df_cpu.iloc[train_idx]["group_id"])
            val_groups = set(self.df_cpu.iloc[val_idx]["group_id"])
            self.assertEqual(len(train_groups.intersection(val_groups)), 0)

        # GPU 4-fold GroupKFold
        for train_idx, val_idx in get_gpu_group_kfold(self.df_gpu, n_splits=4):
            train_groups = set(self.df_gpu.iloc[train_idx]["group_id"])
            val_groups = set(self.df_gpu.iloc[val_idx]["group_id"])
            self.assertEqual(len(train_groups.intersection(val_groups)), 0)

        # Holdout split
        train_df, test_df = split_holdout_dataset(self.df_cpu, test_size=0.20, random_state=42)
        self.assertEqual(len(set(train_df["group_id"]).intersection(set(test_df["group_id"]))), 0)

    def test_16_cpu_and_gpu_dataset_separation(self):
        """16. Confirms CPU and GPU datasets are completely independent and share no records."""
        cpu_cids = set(self.df_cpu["component_id"])
        gpu_cids = set(self.df_gpu["component_id"])
        self.assertEqual(len(cpu_cids.intersection(gpu_cids)), 0)
        self.assertEqual(self.df_cpu.columns.tolist(), CPU_OUTPUT_COLUMNS)
        self.assertEqual(self.df_gpu.columns.tolist(), GPU_OUTPUT_COLUMNS)

    def test_17_traceability_to_original_records(self):
        """17. Confirms every training row maps to verified component and benchmark IDs."""
        comp = pd.read_csv(COMPONENTS_CSV).set_index("component_id")
        bench = pd.read_csv(BENCHMARKS_CSV).set_index("benchmark_id")

        for _, row in self.df_cpu.iterrows():
            cid = row["component_id"]
            bid = row["benchmark_id"]
            self.assertIn(cid, comp.index)
            self.assertIn(bid, bench.index)

        for _, row in self.df_gpu.iterrows():
            cid = row["component_id"]
            bid = row["benchmark_id"]
            self.assertIn(cid, comp.index)
            self.assertIn(bid, bench.index)

    def test_18_no_modification_of_production_csv_files(self):
        """18. Confirms that components.csv and benchmarks.csv hashes remain untouched, and prices.csv preserves baseline rows."""
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
        prices = pd.read_csv(ROOT / "data" / "prices.csv")
        self.assertGreaterEqual(len(prices), 599)


if __name__ == "__main__":
    unittest.main()
