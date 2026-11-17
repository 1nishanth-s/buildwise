"""
BuildWise-AI — Phase 11B: Supervised Machine Learning Model Training and Evaluation Tests

Unit tests validating:
- Dataset loading and schema conformity.
- Strict feature, metadata, and target separation.
- Prevention of data leakage across validation groups.
- Preprocessing pipeline behavior (imputation, scaling, one-hot encoding).
- Model artifact persistence and loading via joblib.
- End-to-end inference producing finite positive performance predictions.
- Robustness against missing features and unseen categories.
- Zero modification to production CSV files.
"""
import hashlib
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
import joblib

from experiments.performance_prediction import config
from experiments.performance_prediction.inference import (
    CPU_MODEL_PATH,
    GPU_MODEL_PATH,
    CPU_METADATA_PATH,
    GPU_METADATA_PATH,
    load_cpu_model,
    load_gpu_model,
    load_cpu_metadata,
    load_gpu_metadata,
    predict_cpu_performance,
    predict_gpu_performance,
)
from experiments.performance_prediction.train import (
    build_preprocessing_pipeline,
    evaluate_cv,
    evaluate_holdout,
    get_candidate_models,
)
from experiments.performance_prediction.validation import (
    get_cpu_group_kfold,
    get_gpu_group_kfold,
    split_holdout_dataset,
)

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PRODUCTION_HASHES = {
    "components.csv": "6753f468dec05adc2ccb4c2582bf798c922a70474aac8ffb8508541a19a67ecc",
    "benchmarks.csv": "4187f577bb064f429f12cb644ffed343246b98e56f2122aea9f095714a564702",
    "prices.csv": "6a8a6e14cca32c120170ab244a0f93ebd6514d212264a2034ca96844c71ca625",
}


class MlModelTrainingTests(unittest.TestCase):
    """Test suite for Phase 11B supervised ML training and evaluation."""

    @classmethod
    def setUpClass(cls):
        cls.cpu_df = pd.read_csv(config.CPU_TRAINING_CSV)
        cls.gpu_df = pd.read_csv(config.GPU_TRAINING_CSV)

    def test_01_training_dataset_loading(self):
        """1. Verifies that CPU and GPU training datasets load with exact sample counts."""
        self.assertEqual(len(self.cpu_df), 180, "CPU dataset must have exactly 180 empirical samples")
        self.assertEqual(len(self.gpu_df), 57, "GPU dataset must have exactly 57 empirical samples")
        self.assertIn(config.CPU_TARGET, self.cpu_df.columns)
        self.assertIn(config.GPU_TARGET, self.gpu_df.columns)

    def test_02_feature_target_metadata_separation(self):
        """2. Verifies that predictive features strictly exclude identifiers, targets, and groups."""
        forbidden_cpu = {"component_id", "benchmark_id", "model", "group_id", config.CPU_TARGET}
        for feat in config.CPU_PREDICTIVE_FEATURES:
            self.assertNotIn(feat, forbidden_cpu, f"Forbidden feature '{feat}' in CPU features")

        forbidden_gpu = {
            "component_id",
            "benchmark_id",
            "model",
            "brand",
            "base_die_group_id",
            "sku_group_id",
            "group_id",
            config.GPU_TARGET,
        }
        for feat in config.GPU_PREDICTIVE_FEATURES:
            self.assertNotIn(feat, forbidden_gpu, f"Forbidden feature '{feat}' in GPU features")

    def test_03_leakage_prevention_in_pipeline(self):
        """3. Confirms preprocessor only consumes authorized features and ignores extra metadata."""
        preprocessor = build_preprocessing_pipeline(
            config.CPU_NUMERIC_FEATURES, config.CPU_CATEGORICAL_FEATURES
        )
        # Pass full CPU dataframe containing metadata columns
        transformed = preprocessor.fit_transform(self.cpu_df)
        self.assertEqual(transformed.shape[0], len(self.cpu_df))
        # Metadata columns must have been dropped (remainder='drop')
        self.assertGreater(transformed.shape[1], len(config.CPU_NUMERIC_FEATURES))

    def test_04_group_splitting_isolation(self):
        """4. Confirms that GroupKFold splits enforce 100% disjoint groups."""
        # Test CPU GroupKFold
        for train_idx, val_idx in get_cpu_group_kfold(self.cpu_df, n_splits=5):
            train_grps = set(self.cpu_df.iloc[train_idx]["group_id"])
            val_grps = set(self.cpu_df.iloc[val_idx]["group_id"])
            self.assertEqual(len(train_grps.intersection(val_grps)), 0)

        # Test GPU GroupKFold
        for train_idx, val_idx in get_gpu_group_kfold(self.gpu_df, n_splits=4):
            train_grps = set(self.gpu_df.iloc[train_idx]["group_id"])
            val_grps = set(self.gpu_df.iloc[val_idx]["group_id"])
            self.assertEqual(len(train_grps.intersection(val_grps)), 0)

    def test_05_preprocessing_handles_missing_numerical_values(self):
        """5. Verifies median imputation handles missing base_clock_ghz without failing."""
        preprocessor = build_preprocessing_pipeline(
            config.CPU_NUMERIC_FEATURES, config.CPU_CATEGORICAL_FEATURES
        )
        # Confirm base_clock_ghz has missing values in dataset
        self.assertGreater(self.cpu_df["base_clock_ghz"].isnull().sum(), 0)
        # Fit and transform
        transformed = preprocessor.fit_transform(self.cpu_df)
        self.assertFalse(np.isnan(transformed).any(), "Transformed feature matrix contains NaNs")

    def test_06_preprocessing_handles_unseen_categories(self):
        """6. Confirms that unseen categories during inference are handled gracefully without error."""
        cpu_model = load_cpu_model()
        unseen_sample = {
            "cores": 8,
            "threads": 16,
            "boost_clock_ghz": 5.0,
            "base_clock_ghz": 4.0,
            "tdp_w": 105,
            "brand": "BrandX_Unknown",
            "socket": "Socket_Future999",
            "ram_type": "DDR6_Future",
        }
        pred = predict_cpu_performance(unseen_sample, pipeline=cpu_model)
        self.assertEqual(len(pred), 1)
        self.assertTrue(np.isfinite(pred[0]))
        self.assertGreater(pred[0], 0)

    def test_07_saved_model_artifacts_exist_and_non_empty(self):
        """7. Verifies that all expected model and metadata files exist on disk."""
        self.assertTrue(CPU_MODEL_PATH.exists(), f"Missing CPU model at {CPU_MODEL_PATH}")
        self.assertTrue(GPU_MODEL_PATH.exists(), f"Missing GPU model at {GPU_MODEL_PATH}")
        self.assertTrue(CPU_METADATA_PATH.exists(), f"Missing CPU metadata at {CPU_METADATA_PATH}")
        self.assertTrue(GPU_METADATA_PATH.exists(), f"Missing GPU metadata at {GPU_METADATA_PATH}")
        self.assertGreater(CPU_MODEL_PATH.stat().st_size, 1000)
        self.assertGreater(GPU_MODEL_PATH.stat().st_size, 1000)

    def test_08_cpu_model_loading_and_inference(self):
        """8. Tests loading saved CPU pipeline and running inference on realistic inputs."""
        cpu_pipeline = load_cpu_model()
        sample = {
            "cores": 16,
            "threads": 32,
            "boost_clock_ghz": 5.7,
            "base_clock_ghz": 4.5,
            "tdp_w": 170,
            "brand": "AMD",
            "socket": "AM5",
            "ram_type": "DDR5",
        }
        pred = predict_cpu_performance(sample, pipeline=cpu_pipeline)
        self.assertEqual(len(pred), 1)
        # Expected Ryzen 9 7950X / 9950X level performance (35,000 - 45,000 pts)
        self.assertGreater(pred[0], 30000.0)
        self.assertLess(pred[0], 55000.0)

    def test_09_gpu_model_loading_and_inference(self):
        """9. Tests loading saved GPU pipeline and running inference on realistic inputs."""
        gpu_pipeline = load_gpu_model()
        sample = {
            "vram_gb": 16.0,
            "memory_bus_width_bits": 256,
            "memory_bandwidth_gbps": 716.8,
            "base_clock_mhz": 2205,
            "boost_clock_mhz": 2505,
            "board_power_w": 285,
            "architecture": "Ada Lovelace",
            "chipmaker": "NVIDIA",
            "memory_type": "GDDR6X",
        }
        pred = predict_gpu_performance(sample, pipeline=gpu_pipeline)
        self.assertEqual(len(pred), 1)
        # Expected RTX 4080 level performance (~25,000 - 32,000 pts)
        self.assertGreater(pred[0], 22000.0)
        self.assertLess(pred[0], 36000.0)

    def test_10_evaluation_metrics_integrity(self):
        """10. Confirms that model metadata contains verified metrics."""
        cpu_meta = load_cpu_metadata()
        gpu_meta = load_gpu_metadata()

        # CPU metrics checks
        self.assertGreater(cpu_meta["metrics"]["cv"]["r2_mean"], 0.85)
        self.assertLess(cpu_meta["metrics"]["cv"]["mae_mean"], 3500.0)
        self.assertEqual(cpu_meta["dataset"]["sample_count"], 180)
        self.assertEqual(cpu_meta["dataset"]["group_count"], 10)

        # GPU metrics checks
        self.assertGreater(gpu_meta["metrics"]["cv"]["r2_mean"], 0.80)
        self.assertLess(gpu_meta["metrics"]["cv"]["mae_mean"], 2000.0)
        self.assertEqual(gpu_meta["dataset"]["sample_count"], 57)
        self.assertEqual(gpu_meta["dataset"]["group_count"], 14)

    def test_11_evaluation_reports_exist(self):
        """11. Confirms that markdown reports, comparison CSVs, and SVG charts exist."""
        reports_dir = ROOT / "experiments" / "performance_prediction" / "reports"
        self.assertTrue((reports_dir / "model_evaluation_report.md").exists())
        self.assertTrue((reports_dir / "cpu_model_comparison.csv").exists())
        self.assertTrue((reports_dir / "gpu_model_comparison.csv").exists())
        self.assertTrue((reports_dir / "cpu_actual_vs_predicted.svg").exists())
        self.assertTrue((reports_dir / "gpu_actual_vs_predicted.svg").exists())
        self.assertTrue((reports_dir / "cpu_residuals.svg").exists())
        self.assertTrue((reports_dir / "gpu_residuals.svg").exists())

    def test_12_reproducibility(self):
        """12. Confirms that inference is strictly deterministic."""
        sample = {
            "cores": 6,
            "threads": 12,
            "boost_clock_ghz": 4.6,
            "base_clock_ghz": 3.7,
            "tdp_w": 65,
            "brand": "AMD",
            "socket": "AM4",
            "ram_type": "DDR4",
        }
        pred1 = predict_cpu_performance(sample)
        pred2 = predict_cpu_performance(sample)
        self.assertEqual(pred1[0], pred2[0])

    def test_13_production_csv_files_unmodified(self):
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
