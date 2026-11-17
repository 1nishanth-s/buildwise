"""
BuildWise-AI — Unit Tests for CPU Benchmark ML Regression Pipeline

Tests:
1. Dataset join integrity and exact sample count (55 observations).
2. Benchmark target validity (suite, metric, unit, positive numeric values).
3. Strict 6-feature allowlist enforcement.
4. Absolute exclusion of prices, sellers, tiers, and non-predictive identifiers.
5. Duplicate benchmark_id and component_id detection.
6. CPU category verification against components catalog.
7. GroupKFold strict silicon family zero-overlap separation.
8. Pipeline preprocessing data leakage prevention.
9. Model training, cross-validation, and prediction generation.
10. Evaluation metric generation and baseline outperformance verification.
11. Experimental model artifact and metadata persistence.
"""

import json
import os
import unittest
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from experiments.cpu_benchmark_regression.prepare_dataset import (
    get_project_root,
    prepare_cpu_benchmark_dataset,
    PREDICTIVE_NUMERIC_FEATURES,
    PREDICTIVE_CATEGORICAL_FEATURES,
    PREDICTIVE_FEATURES,
    TARGET_COLUMN
)
from experiments.cpu_benchmark_regression.train import (
    get_model_pipeline,
    cross_validate_model
)


class TestCpuMlRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = get_project_root()
        cls.dataset_csv = cls.root / "data" / "ml" / "cpu_benchmark_training_v1.csv"
        cls.family_csv = cls.root / "data" / "ml" / "cpu_family_groups.csv"
        cls.provenance_csv = cls.root / "data" / "ml" / "cpu_feature_provenance.csv"
        cls.exp_dir = cls.root / "experiments" / "cpu_benchmark_regression"
        cls.eval_json = cls.exp_dir / "evaluation.json"
        cls.oof_csv = cls.exp_dir / "oof_predictions.csv"
        cls.model_joblib = cls.root / "models" / "experimental" / "cpu_cinebench_r23_v1.joblib"
        cls.model_meta = cls.root / "models" / "experimental" / "cpu_cinebench_r23_v1_metadata.json"
        
        # Ensure dataset is loaded
        if not cls.dataset_csv.is_file():
            cls.df = prepare_cpu_benchmark_dataset(project_root=cls.root)
        else:
            cls.df = pd.read_csv(cls.dataset_csv)

    def test_dataset_join_and_sample_count(self):
        """Confirm that exactly 55 verified benchmark samples are prepared."""
        self.assertEqual(len(self.df), 55)
        self.assertTrue(self.dataset_csv.is_file())
        self.assertTrue(self.family_csv.is_file())
        self.assertTrue(self.provenance_csv.is_file())

    def test_benchmark_target_validity(self):
        """Confirm all targets are valid, positive Cinebench R23 Multi-Core scores."""
        scores = self.df[TARGET_COLUMN].values
        self.assertTrue(all(isinstance(s, (int, float, np.floating)) for s in scores))
        self.assertTrue(all(s > 0 for s in scores))
        self.assertGreater(float(np.min(scores)), 5000.0)
        self.assertLess(float(np.max(scores)), 60000.0)

    def test_feature_allowlist_enforcement(self):
        """Confirm strictly the 6 allowed features are present and non-null."""
        expected_features = ["cores", "threads", "boost_clock_ghz", "tdp_w", "brand", "socket"]
        self.assertEqual(PREDICTIVE_FEATURES, expected_features)
        for col in expected_features:
            self.assertIn(col, self.df.columns)
            self.assertEqual(self.df[col].isnull().sum(), 0)

    def test_price_feature_exclusion(self):
        """Strictly enforce that no price, seller, or tier data exists in features."""
        forbidden_keywords = ["price", "cost", "seller", "merchant", "tier", "budget", "inr"]
        for col in PREDICTIVE_FEATURES:
            for kw in forbidden_keywords:
                self.assertNotIn(kw, col.lower())
        
        for col in self.df.columns:
            for kw in forbidden_keywords:
                self.assertNotIn(kw, col.lower())

    def test_duplicate_detection(self):
        """Ensure no duplicate benchmark IDs or component IDs exist."""
        self.assertEqual(self.df["benchmark_id"].nunique(), 55)
        self.assertEqual(self.df["component_id"].nunique(), 55)

    def test_cpu_category_validation(self):
        """Confirm all joined component IDs belong strictly to CPU category."""
        components_file = self.root / "data" / "components.csv"
        comp_df = pd.read_csv(components_file)
        cpu_ids = set(comp_df[comp_df["category"] == "cpu"]["component_id"])
        
        for cid in self.df["component_id"]:
            self.assertIn(cid, cpu_ids)

    def test_groupkfold_family_separation(self):
        """Assert zero overlap between train and validation silicon families on all folds."""
        gkf = GroupKFold(n_splits=5)
        X = self.df[PREDICTIVE_FEATURES]
        y = self.df[TARGET_COLUMN].values
        groups = self.df["group_id"].values
        
        self.assertGreaterEqual(len(set(groups)), 25)
        
        for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups), 1):
            train_groups = set(groups[train_idx])
            val_groups = set(groups[val_idx])
            overlap = train_groups.intersection(val_groups)
            self.assertEqual(
                len(overlap), 0,
                f"Data leakage detected in fold {fold}: {overlap}"
            )

    def test_preprocessing_leakage_prevention(self):
        """Confirm preprocessor pipeline can be fitted strictly on fold training data."""
        pipe = get_model_pipeline("ridge")
        train_df = self.df.iloc[:40]
        test_df = self.df.iloc[40:]
        
        pipe.fit(train_df[PREDICTIVE_FEATURES], train_df[TARGET_COLUMN].values)
        preds = pipe.predict(test_df[PREDICTIVE_FEATURES])
        self.assertEqual(len(preds), len(test_df))
        self.assertFalse(np.isnan(preds).any())

    def test_model_training_and_baseline_beating(self):
        """Confirm models cross-validate and Ridge substantially outperforms Dummy baseline."""
        dummy_res = cross_validate_model(self.df, "dummy", n_splits=5)
        ridge_res = cross_validate_model(self.df, "ridge", n_splits=5)
        
        self.assertGreater(dummy_res["aggregated_oof_mae"], 8000.0)
        self.assertLess(ridge_res["aggregated_oof_mae"], 2500.0)
        self.assertGreater(ridge_res["aggregated_oof_r2"], 0.90)
        self.assertLess(ridge_res["aggregated_oof_mae"], dummy_res["aggregated_oof_mae"])

    def test_evaluation_artifacts_exist(self):
        """Confirm evaluation.json and oof_predictions.csv exist and are well-formed."""
        self.assertTrue(self.eval_json.is_file())
        self.assertTrue(self.oof_csv.is_file())
        
        with open(self.eval_json, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
        
        self.assertIn("dummy", eval_data)
        self.assertIn("ridge", eval_data)
        self.assertIn("random_forest", eval_data)
        self.assertIn("hist_gradient_boosting", eval_data)
        
        oof = pd.read_csv(self.oof_csv)
        self.assertEqual(len(oof), 55)
        self.assertIn("actual_score", oof.columns)
        self.assertIn("pred_ridge", oof.columns)
        self.assertIn("abs_err_ridge", oof.columns)

    def test_experimental_model_artifact_persistence(self):
        """Confirm saved experimental model loads and predicts accurately."""
        self.assertTrue(self.model_joblib.is_file())
        self.assertTrue(self.model_meta.is_file())
        
        pipeline = joblib.load(self.model_joblib)
        preds = pipeline.predict(self.df[PREDICTIVE_FEATURES])
        self.assertEqual(len(preds), 55)
        self.assertTrue(all(p > 0 for p in preds))
        
        with open(self.model_meta, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["status"], "EXPERIMENTAL")
        self.assertEqual(meta["n_training_samples"], 55)
        self.assertIn("disclaimer", meta)


class TestCpuMlRegressionV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = get_project_root()
        cls.enrich_csv = cls.root / "data" / "ml" / "cpu_feature_enrichment_v1.csv"
        cls.report_md = cls.root / "experiments" / "cpu_benchmark_regression" / "feature_enrichment_report.md"
        cls.feat_comp_csv = cls.root / "experiments" / "cpu_benchmark_regression" / "feature_comparison.csv"
        cls.v2_eval_json = cls.root / "experiments" / "cpu_benchmark_regression" / "v2_evaluation.json"
        cls.v2_oof_csv = cls.root / "experiments" / "cpu_benchmark_regression" / "v2_oof_predictions.csv"
        cls.v2_joblib = cls.root / "models" / "experimental" / "cpu_cinebench_r23_v2.joblib"
        cls.v2_meta = cls.root / "models" / "experimental" / "cpu_cinebench_r23_v2_metadata.json"
        
        from experiments.cpu_benchmark_regression.train_v2 import load_enriched_dataset
        cls.df = load_enriched_dataset(project_root=cls.root)

    def test_feature_enrichment_parsing(self):
        """Confirm enrichment dataset exists with 275 records across 55 unique CPUs."""
        self.assertTrue(self.enrich_csv.is_file())
        self.assertTrue(self.report_md.is_file())
        
        df_enrich = pd.read_csv(self.enrich_csv)
        self.assertEqual(len(df_enrich), 275)
        self.assertEqual(df_enrich["component_id"].nunique(), 55)
        expected_features = {"architecture", "cache_l3_mb", "cache_l2_mb", "base_clock_ghz", "cpu_codename"}
        self.assertEqual(set(df_enrich["feature_name"].unique()), expected_features)

    def test_source_provenance(self):
        """Confirm all enrichment records cite official manufacturer sources with verified status."""
        df_enrich = pd.read_csv(self.enrich_csv)
        self.assertTrue(all(df_enrich["verification_status"] == "verified"))
        self.assertTrue(all(df_enrich["source_url"].str.startswith("https://")))
        valid_sources = {"AMD Official Product Specifications", "Intel ARK"}
        self.assertTrue(all(s in valid_sources for s in df_enrich["source_name"]))

    def test_missing_specification_handling(self):
        """Confirm merged dataset contains complete specifications for all 55 CPUs with zero nulls."""
        self.assertEqual(len(self.df), 55)
        required_cols = ["architecture", "cache_l3_mb", "cache_l2_mb", "base_clock_ghz", "cpu_codename"]
        for col in required_cols:
            self.assertIn(col, self.df.columns)
            self.assertEqual(self.df[col].isnull().sum(), 0)

    def test_cache_unit_conversions(self):
        """Confirm cache and clock specifications have valid positive numeric types in expected ranges."""
        self.assertTrue(all(12.0 <= x <= 128.0 for x in self.df["cache_l3_mb"]))
        self.assertTrue(all(3.0 <= x <= 40.0 for x in self.df["cache_l2_mb"]))
        self.assertTrue(all(2.0 <= x <= 5.0 for x in self.df["base_clock_ghz"]))

    def test_feature_allowlist_enforcement_v2(self):
        """Enforce that no prices, sellers, tiers, or IDs enter predictive feature sets."""
        from experiments.cpu_benchmark_regression.train_v2 import FEATURE_CONFIGURATIONS
        forbidden = ["price", "cost", "seller", "merchant", "tier", "budget", "inr", "component_id"]
        for name, config in FEATURE_CONFIGURATIONS.items():
            for f in config["numeric"] + config["categorical"]:
                for kw in forbidden:
                    self.assertNotIn(kw, f.lower())

    def test_groupkfold_separation_v2(self):
        """Confirm zero silicon family overlap across all folds in V2 GroupKFold."""
        gkf = GroupKFold(n_splits=5)
        groups = self.df["group_id"].values
        X = self.df[["cores", "threads", "boost_clock_ghz", "tdp_w", "cache_l3_mb", "cache_l2_mb", "base_clock_ghz", "brand", "socket", "architecture"]]
        y = self.df["score"].values
        
        for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups), 1):
            train_g = set(groups[train_idx])
            val_g = set(groups[val_idx])
            overlap = train_g.intersection(val_g)
            self.assertEqual(len(overlap), 0, f"Overlap in V2 fold {fold}: {overlap}")

    def test_preprocessing_leakage_prevention_v2(self):
        """Confirm V2 Pipeline fits strictly within training data."""
        from experiments.cpu_benchmark_regression.train_v2 import get_v2_model_pipeline
        num_cols = ["cores", "threads", "boost_clock_ghz", "tdp_w", "cache_l3_mb", "cache_l2_mb", "base_clock_ghz"]
        cat_cols = ["brand", "socket", "architecture"]
        all_cols = num_cols + cat_cols
        
        pipe = get_v2_model_pipeline("ridge", num_cols, cat_cols)
        train_df = self.df.iloc[:40]
        test_df = self.df.iloc[40:]
        
        pipe.fit(train_df[all_cols], train_df["score"].values)
        preds = pipe.predict(test_df[all_cols])
        self.assertEqual(len(preds), len(test_df))
        self.assertFalse(np.isnan(preds).any())

    def test_v1_versus_v2_comparison(self):
        """Confirm that V2 (Set E Comprehensive) achieves lower MAE and RMSE than V1 Baseline."""
        self.assertTrue(self.feat_comp_csv.is_file())
        self.assertTrue(self.v2_eval_json.is_file())
        
        with open(self.v2_eval_json, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
        
        v1_mae = eval_data["Set_A_V1_Baseline"]["ridge"]["aggregated_oof_mae"]
        v2_mae = eval_data["Set_E_Comprehensive"]["ridge"]["aggregated_oof_mae"]
        v1_rmse = eval_data["Set_A_V1_Baseline"]["ridge"]["aggregated_oof_rmse"]
        v2_rmse = eval_data["Set_E_Comprehensive"]["ridge"]["aggregated_oof_rmse"]
        v1_r2 = eval_data["Set_A_V1_Baseline"]["ridge"]["aggregated_oof_r2"]
        v2_r2 = eval_data["Set_E_Comprehensive"]["ridge"]["aggregated_oof_r2"]
        
        self.assertLess(v2_mae, v1_mae)
        self.assertLess(v2_rmse, v1_rmse)
        self.assertGreater(v2_r2, v1_r2)
        # Check error reduction is at least 15%
        reduction_pct = ((v1_mae - v2_mae) / v1_mae) * 100.0
        self.assertGreater(reduction_pct, 15.0)

    def test_v2_model_artifact_loading(self):
        """Confirm V2 model artifact and metadata load cleanly and produce valid predictions."""
        self.assertTrue(self.v2_joblib.is_file())
        self.assertTrue(self.v2_meta.is_file())
        
        pipe = joblib.load(self.v2_joblib)
        with open(self.v2_meta, "r", encoding="utf-8") as f:
            meta = json.load(f)
        
        self.assertEqual(meta["status"], "EXPERIMENTAL")
        self.assertEqual(meta["model_version"], "v2")
        self.assertEqual(meta["training_samples_count"], 55)
        
        preds = pipe.predict(self.df[meta["predictive_features"]])
        self.assertEqual(len(preds), 55)
        self.assertTrue(all(p > 0 for p in preds))


if __name__ == "__main__":
    unittest.main()
