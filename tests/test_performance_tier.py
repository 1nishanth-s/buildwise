import unittest
from pathlib import Path

from experiments.performance_tier.train import (
    CANDIDATE_SPEC_FIELDS,
    CV_REPEATS,
    FEATURE_COLUMNS,
    LABELS,
    evaluate_dataset,
    prepare_cpu_dataset,
)


ROOT = Path(__file__).resolve().parents[1]


class PerformanceTierExperimentTests(unittest.TestCase):
    def test_prepares_catalog_without_identifier_features(self):
        features, labels, quality = prepare_cpu_dataset(
            ROOT / "data" / "components.csv"
        )

        self.assertEqual(tuple(features.columns), FEATURE_COLUMNS)
        self.assertEqual(len(features), 30)
        self.assertEqual(len(labels), 30)
        self.assertEqual(
            quality["label_counts"],
            {"entry": 3, "mid": 7, "high": 8, "flagship": 12},
        )
        self.assertEqual(quality["records_missing_features"], 0)
        self.assertEqual(quality["missing_label_records"], 0)
        self.assertEqual(quality["invalid_label_records"], 0)
        self.assertEqual(quality["invalid_specs_records"], 0)
        self.assertFalse({"component_id", "brand", "model"} & set(features.columns))
        self.assertEqual(
            set(quality["candidate_spec_coverage"]),
            set(CANDIDATE_SPEC_FIELDS),
        )
        self.assertEqual(quality["candidate_spec_coverage"]["base_ghz"], 0)
        self.assertEqual(quality["candidate_spec_coverage"]["cache_mb"], 0)
        self.assertEqual(quality["candidate_spec_coverage"]["architecture"], 0)
        self.assertEqual(quality["candidate_spec_coverage"]["generation"], 0)
        self.assertEqual(quality["candidate_spec_coverage"]["tdp_w"], 30)
        self.assertEqual(quality["duplicate_feature_vector_groups"], 6)
        self.assertEqual(quality["duplicate_feature_vector_records"], 8)
        self.assertEqual(quality["conflicting_label_feature_vector_groups"], 1)
        self.assertEqual(len(quality["feature_vector_groups"]), 22)
        repeated_groups = [
            group
            for group in quality["feature_vector_groups"]
            if group["record_count"] > 1
        ]
        self.assertEqual(len(repeated_groups), 6)
        conflicting_groups = [
            group
            for group in repeated_groups
            if group["has_conflicting_labels"]
        ]
        self.assertEqual(len(conflicting_groups), 1)
        conflict = conflicting_groups[0]
        self.assertEqual(
            conflict["features"],
            {"cores": 12.0, "threads": 24.0, "boost_ghz": 5.6},
        )
        self.assertEqual(
            {
                record["component_id"]: record["original_label"]
                for record in conflict["records"]
            },
            {
                "cpu-r9-9900x": "flagship",
                "amd-ryzen-9-7900x": "high",
            },
        )
        self.assertEqual(quality["distinct_feature_groups_by_label"]["entry"], 2)
        self.assertFalse(
            quality["grouped_cv_feasibility"][
                "all_labels_can_appear_in_every_test_fold"
            ]
        )

    def test_evaluation_reports_holdout_record_and_grouped_cv(self):
        features, labels, quality = prepare_cpu_dataset(
            ROOT / "data" / "components.csv"
        )

        first = evaluate_dataset(features, labels, quality)
        self.assertEqual(first["random_seed"], 42)
        self.assertEqual(first["preliminary_holdout"]["train_examples"], 21)
        self.assertEqual(first["preliminary_holdout"]["test_examples"], 9)
        self.assertTrue(
            first["preliminary_holdout"]["not_used_for_model_selection"]
        )
        self.assertEqual(first["baseline"]["metrics"]["accuracy"], 4 / 9)
        self.assertEqual(first["decision_tree"]["metrics"]["accuracy"], 4 / 9)
        self.assertEqual(first["decision_tree"]["metrics"]["macro_f1"], 0.488095238095238)

        cross_validation = first["cross_validation"]
        self.assertEqual(cross_validation["method"], "RepeatedStratifiedKFold")
        self.assertEqual(cross_validation["n_splits"], 3)
        self.assertEqual(cross_validation["n_repeats"], CV_REPEATS)
        self.assertEqual(cross_validation["total_folds"], 3 * CV_REPEATS)
        self.assertFalse(
            cross_validation["leakage_checks"][
                "identifiers_names_urls_or_labels_used_as_features"
            ]
        )
        self.assertTrue(
            cross_validation["leakage_checks"][
                "scaler_fitted_within_training_folds"
            ]
        )
        self.assertGreater(
            cross_validation["leakage_checks"][
                "folds_with_shared_duplicate_feature_vectors"
            ],
            0,
        )
        self.assertEqual(
            set(cross_validation["models"]),
            {
                "majority_class_baseline",
                "decision_tree",
                "class_balanced_decision_tree",
                "small_random_forest",
                "scaled_logistic_regression",
            },
        )
        for result in cross_validation["models"].values():
            self.assertEqual(len(result["fold_scores"]), 3 * CV_REPEATS)
            for metric in ("accuracy", "macro_f1", "balanced_accuracy"):
                self.assertIn("mean", result["metrics"][metric])
                self.assertIn("std", result["metrics"][metric])
                self.assertGreaterEqual(result["metrics"][metric]["std"], 0)
            self.assertEqual(set(result["per_class"]), set(LABELS))
            self.assertEqual(len(result["confusion_matrix"]), len(LABELS))
            self.assertEqual(
                sum(map(sum, result["confusion_matrix"])),
                len(labels) * CV_REPEATS,
            )

        selection = cross_validation["model_selection"]
        self.assertEqual(selection["reference_model"], "decision_tree")
        self.assertIn(selection["selected_model"], cross_validation["models"])
        self.assertTrue(selection["conclusion"])

        group_cv = first["group_aware_cross_validation"]
        self.assertEqual(group_cv["method"], "RepeatedStratifiedGroupKFold")
        self.assertEqual(group_cv["total_folds"], 3 * CV_REPEATS)
        self.assertTrue(
            group_cv["leakage_checks"][
                "grouped_folds_keep_feature_vectors_together"
            ]
        )
        self.assertEqual(
            group_cv["feasibility"]["folds_missing_entry_in_test"],
            CV_REPEATS,
        )
        self.assertFalse(
            group_cv["feasibility"]["reliable_four_class_grouped_evaluation"]
        )
        for detail in group_cv["split_details"]:
            self.assertTrue(detail["train_test_feature_groups_disjoint"])
            self.assertGreater(detail["train_distinct_feature_groups"], 0)
            self.assertGreater(detail["test_distinct_feature_groups"], 0)
        for result in group_cv["models"].values():
            self.assertEqual(len(result["fold_scores"]), 3 * CV_REPEATS)
            for metric in ("accuracy", "macro_f1", "balanced_accuracy"):
                self.assertIn("mean", result["metrics"][metric])
                self.assertIn("std", result["metrics"][metric])
            self.assertEqual(set(result["per_class"]), set(LABELS))
            self.assertEqual(
                sum(map(sum, result["confusion_matrix"])),
                len(labels) * CV_REPEATS,
            )


if __name__ == "__main__":
    unittest.main()
