import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean, pstdev

import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    recall_score,
)
from sklearn.model_selection import (
    RepeatedStratifiedKFold,
    StratifiedGroupKFold,
    train_test_split,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMPONENTS_PATH = ROOT / "data" / "components.csv"
DEFAULT_RESULTS_PATH = Path(__file__).resolve().parent / "evaluation.json"
LABELS = ("entry", "mid", "high", "flagship")
FEATURE_COLUMNS = ("cores", "threads", "boost_ghz")
CANDIDATE_SPEC_FIELDS = (
    "base_ghz",
    "cache_mb",
    "l3_cache_mb",
    "architecture",
    "generation",
    "tdp_w",
    "socket",
    "ram_type",
    "use_cases",
    "supported_chipsets",
)
RANDOM_SEED = 42
TEST_SIZE = 0.30
CV_SPLITS = 3
CV_REPEATS = 20


def _finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _is_populated(value):
    return value is not None and value != "" and value != []


def prepare_cpu_dataset(components_path=DEFAULT_COMPONENTS_PATH):
    """Return CPU features, editorial labels, and catalog data-quality counts."""
    feature_rows = []
    target_labels = []
    label_counts = Counter()
    missing_feature_counts = Counter()
    candidate_spec_coverage = Counter()
    missing_label_count = 0
    invalid_label_count = 0
    invalid_specs_count = 0
    missing_feature_row_count = 0
    cpu_record_count = 0
    component_ids = []
    brand_models = []
    feature_vector_labels = defaultdict(set)
    feature_vector_records = defaultdict(list)

    with Path(components_path).open(
        encoding="utf-8-sig", newline=""
    ) as components_file:
        for row in csv.DictReader(components_file):
            if str(row.get("category", "")).strip().casefold() != "cpu":
                continue
            cpu_record_count += 1
            component_ids.append(str(row.get("component_id", "")).strip())
            brand_models.append((
                str(row.get("brand", "")).strip().casefold(),
                str(row.get("model", "")).strip().casefold(),
            ))
            try:
                specs = json.loads(row.get("specs_json") or "{}")
            except (TypeError, ValueError):
                specs = None
            if not isinstance(specs, dict):
                invalid_specs_count += 1
                specs = {}

            for field in CANDIDATE_SPEC_FIELDS:
                if _is_populated(specs.get(field)):
                    candidate_spec_coverage[field] += 1

            original_label = str(specs.get("performance_tier", ""))
            label = original_label.strip().casefold()
            if not label:
                missing_label_count += 1
                continue
            if label not in LABELS:
                invalid_label_count += 1
                continue

            feature_values = {}
            missing_features = []
            for feature in FEATURE_COLUMNS:
                value = _finite_number(specs.get(feature))
                if value is None:
                    missing_feature_counts[feature] += 1
                    missing_features.append(feature)
                else:
                    feature_values[feature] = value
            if missing_features:
                missing_feature_row_count += 1
                continue

            feature_rows.append(feature_values)
            target_labels.append(label)
            label_counts[label] += 1
            vector_key = tuple(feature_values[feature] for feature in FEATURE_COLUMNS)
            feature_vector_labels[vector_key].add(label)
            feature_vector_records[vector_key].append({
                "component_id": str(row.get("component_id", "")).strip(),
                "original_label": original_label,
            })

    features = pd.DataFrame(feature_rows, columns=FEATURE_COLUMNS)
    labels = pd.Series(target_labels, name="performance_tier", dtype="string")
    vector_counts = Counter(
        tuple(row[feature] for feature in FEATURE_COLUMNS)
        for row in feature_rows
    )
    duplicate_vector_groups = sum(count > 1 for count in vector_counts.values())
    duplicate_vector_records = sum(
        count - 1 for count in vector_counts.values() if count > 1
    )
    feature_groups = []
    group_id_by_vector = {}
    for index, (vector, records) in enumerate(feature_vector_records.items(), 1):
        group_id_by_vector[vector] = index - 1
        group_labels = sorted({
            record["original_label"].strip().casefold()
            for record in records
        })
        feature_groups.append({
            "group_id": f"feature-vector-{index:02d}",
            "features": dict(zip(FEATURE_COLUMNS, vector)),
            "record_count": len(records),
            "records": records,
            "labels": group_labels,
            "has_conflicting_labels": len(group_labels) > 1,
        })
    grouped_label_counts = {
        label: sum(
            label in labels_for_vector
            for labels_for_vector in feature_vector_labels.values()
        )
        for label in LABELS
    }
    quality = {
        "cpu_records": cpu_record_count,
        "usable_labeled_examples": len(labels),
        "label_counts": {
            label: label_counts.get(label, 0) for label in LABELS
        },
        "missing_label_records": missing_label_count,
        "invalid_label_records": invalid_label_count,
        "invalid_specs_records": invalid_specs_count,
        "records_missing_features": missing_feature_row_count,
        "missing_feature_counts": {
            feature: missing_feature_counts.get(feature, 0)
            for feature in FEATURE_COLUMNS
        },
        "candidate_spec_coverage": {
            field: candidate_spec_coverage.get(field, 0)
            for field in CANDIDATE_SPEC_FIELDS
        },
        "duplicate_component_ids": sum(
            count - 1
            for count in Counter(component_ids).values()
            if count > 1
        ),
        "duplicate_brand_model_pairs": sum(
            count - 1
            for count in Counter(brand_models).values()
            if count > 1
        ),
        "duplicate_feature_vector_groups": duplicate_vector_groups,
        "duplicate_feature_vector_records": duplicate_vector_records,
        "conflicting_label_feature_vector_groups": sum(
            len(class_labels) > 1
            for class_labels in feature_vector_labels.values()
        ),
        "distinct_feature_groups_by_label": grouped_label_counts,
        "feature_vector_groups": feature_groups,
        "grouped_cv_feasibility": {
            "n_splits": CV_SPLITS,
            "minimum_distinct_groups_per_label": min(grouped_label_counts.values()),
            "all_labels_can_appear_in_every_test_fold": all(
                count >= CV_SPLITS for count in grouped_label_counts.values()
            ),
            "reason": (
                "At least one label occurs in fewer distinct feature groups "
                "than the number of folds, so every test fold cannot contain "
                "all labels while keeping identical vectors together."
                if any(count < CV_SPLITS for count in grouped_label_counts.values())
                else (
                    "Each label occurs in at least one distinct feature group "
                    "per fold, though stratified grouped assignment must still "
                    "be inspected."
                )
            ),
        },
    }
    group_ids = [
        group_id_by_vector[
            tuple(row[feature] for feature in FEATURE_COLUMNS)
        ]
        for row in feature_rows
    ]
    return features, labels, quality


def _metrics(actual, predicted):
    report = classification_report(
        actual,
        predicted,
        labels=list(LABELS),
        target_names=list(LABELS),
        output_dict=True,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(actual, predicted)),
        "macro_f1": float(f1_score(
            actual, predicted, labels=list(LABELS), average="macro", zero_division=0
        )),
        "weighted_f1": float(f1_score(
            actual, predicted, labels=list(LABELS), average="weighted", zero_division=0
        )),
        "balanced_accuracy": float(
            recall_score(
                actual,
                predicted,
                labels=list(LABELS),
                average="macro",
                zero_division=0,
            )
        ),
        "per_class": {
            label: {
                metric: float(report[label][metric])
                for metric in ("precision", "recall", "f1-score", "support")
            }
            for label in LABELS
        },
        "confusion_matrix": confusion_matrix(
            actual, predicted, labels=list(LABELS)
        ).tolist(),
    }


def _build_models():
    return {
        "majority_class_baseline": (
            "DummyClassifier(strategy='most_frequent')",
            DummyClassifier(strategy="most_frequent"),
        ),
        "decision_tree": (
            "DecisionTreeClassifier(max_depth=3, random_state=42)",
            DecisionTreeClassifier(max_depth=3, random_state=RANDOM_SEED),
        ),
        "class_balanced_decision_tree": (
            "DecisionTreeClassifier(max_depth=3, class_weight='balanced', "
            "random_state=42)",
            DecisionTreeClassifier(
                max_depth=3, class_weight="balanced", random_state=RANDOM_SEED
            ),
        ),
        "small_random_forest": (
            "RandomForestClassifier(n_estimators=100, max_depth=3, "
            "min_samples_leaf=2, class_weight='balanced', random_state=42)",
            RandomForestClassifier(
                n_estimators=100,
                max_depth=3,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=RANDOM_SEED,
            ),
        ),
        "scaled_logistic_regression": (
            "StandardScaler + LogisticRegression(class_weight='balanced', "
            "max_iter=1000, random_state=42)",
            make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=RANDOM_SEED,
                ),
            ),
        ),
    }


def _cross_validate_models(features, labels, group_ids=None, grouped=False):
    if grouped:
        if group_ids is None:
            raise ValueError("Group IDs are required for grouped cross-validation.")
        split_sets = []
        for repeat in range(CV_REPEATS):
            splitter = StratifiedGroupKFold(
                n_splits=CV_SPLITS,
                shuffle=True,
                random_state=RANDOM_SEED + repeat,
            )
            split_sets.extend(
                (repeat, fold_index, train_indices, test_indices)
                for fold_index, (train_indices, test_indices) in enumerate(
                    splitter.split(features, labels, groups=group_ids)
                )
            )
        method = "RepeatedStratifiedGroupKFold"
    else:
        splitter = RepeatedStratifiedKFold(
            n_splits=CV_SPLITS,
            n_repeats=CV_REPEATS,
            random_state=RANDOM_SEED,
        )
        split_sets = [
            (
                fold_index // CV_SPLITS,
                fold_index % CV_SPLITS,
                train_indices,
                test_indices,
            )
            for fold_index, (train_indices, test_indices) in enumerate(
                splitter.split(features, labels)
            )
        ]
        method = "RepeatedStratifiedKFold"

    splits = [
        (train_indices, test_indices)
        for _, _, train_indices, test_indices in split_sets
    ]
    feature_vectors = [
        tuple(row) for row in features.itertuples(index=False, name=None)
    ]
    duplicate_vectors = {
        vector
        for vector, count in Counter(feature_vectors).items()
        if count > 1
    }
    shared_duplicate_groups_per_fold = []
    if not grouped:
        for train_indices, test_indices in splits:
            train_vectors = {feature_vectors[index] for index in train_indices}
            test_vectors = {feature_vectors[index] for index in test_indices}
            shared_duplicate_groups_per_fold.append(
                len(train_vectors & test_vectors & duplicate_vectors)
            )
    fold_details = []
    for repeat, fold_index, train_indices, test_indices in split_sets:
        y_train = labels.iloc[train_indices]
        y_test = labels.iloc[test_indices]
        detail = {
            "repeat": repeat + 1,
            "fold": fold_index + 1,
            "train_examples": len(train_indices),
            "test_examples": len(test_indices),
            "train_label_counts": {
                label: int(y_train.value_counts().get(label, 0))
                for label in LABELS
            },
            "test_label_counts": {
                label: int(y_test.value_counts().get(label, 0))
                for label in LABELS
            },
            "test_missing_labels": [
                label
                for label in LABELS
                if y_test.value_counts().get(label, 0) == 0
            ],
        }
        if group_ids is not None:
            detail["train_distinct_feature_groups"] = len({
                group_ids[index] for index in train_indices
            })
            detail["test_distinct_feature_groups"] = len({
                group_ids[index] for index in test_indices
            })
            if grouped:
                detail["train_test_feature_groups_disjoint"] = not (
                    {group_ids[index] for index in train_indices}
                    & {group_ids[index] for index in test_indices}
                )
        fold_details.append(detail)
    results = {}

    for model_key, (model_description, model) in _build_models().items():
        fold_scores = []
        actual_values = []
        predicted_values = []
        for split_index, (train_indices, test_indices) in enumerate(splits):
            x_train = features.iloc[train_indices]
            x_test = features.iloc[test_indices]
            y_train = labels.iloc[train_indices]
            y_test = labels.iloc[test_indices]
            fitted_model = clone(model)
            fitted_model.fit(x_train, y_train)
            predictions = fitted_model.predict(x_test)
            actual_values.extend(y_test.tolist())
            predicted_values.extend(predictions.tolist())

            fold_scores.append({
                "repeat": split_sets[split_index][0] + 1,
                "fold": split_sets[split_index][1] + 1,
                "accuracy": float(accuracy_score(y_test, predictions)),
                "macro_f1": float(f1_score(
                    y_test,
                    predictions,
                    labels=list(LABELS),
                    average="macro",
                    zero_division=0,
                )),
                "balanced_accuracy": float(
                    recall_score(
                        y_test,
                        predictions,
                        labels=list(LABELS),
                        average="macro",
                        zero_division=0,
                    )
                ),
            })

        metric_summary = {}
        for metric in ("accuracy", "macro_f1", "balanced_accuracy"):
            values = [score[metric] for score in fold_scores]
            metric_summary[metric] = {
                "mean": fmean(values),
                "std": pstdev(values),
            }
        pooled_metrics = _metrics(actual_values, predicted_values)
        results[model_key] = {
            "model": model_description,
            "metrics": metric_summary,
            "per_class": pooled_metrics["per_class"],
            "confusion_matrix": pooled_metrics["confusion_matrix"],
            "fold_scores": fold_scores,
        }

    return {
        "method": method,
        "n_splits": CV_SPLITS,
        "n_repeats": CV_REPEATS,
        "total_folds": len(splits),
        "random_seed": RANDOM_SEED,
        "repeat_seed_strategy": (
            "Stratified group CV uses random_state=42 + zero-based repeat index."
            if grouped else "RepeatedStratifiedKFold uses random_state=42."
        ),
        "split_details": fold_details,
        "variation": (
            "Population standard deviation across repeated fold scores; "
            "these folds are not independent confidence intervals."
        ),
        "balanced_accuracy_definition": (
            "Macro-average recall over all four fixed labels. A label absent "
            "from a test fold contributes zero recall; folds missing a label "
            "are explicitly listed and are not meaningful full-class tests."
        ),
        "pooled_per_class_note": (
            "Per-class precision, recall, F1, support, and confusion matrices "
            "pool predictions from all repeated held-out folds; each CPU is "
            "held out once per repeat."
        ),
        "leakage_checks": {
            "identifiers_names_urls_or_labels_used_as_features": False,
            "scaler_fitted_within_training_folds": True,
            "folds_with_shared_duplicate_feature_vectors": (
                0 if grouped else sum(
                    count > 0 for count in shared_duplicate_groups_per_fold
                )
            ),
            "shared_duplicate_feature_vector_groups_across_folds": (
                0 if grouped else sum(shared_duplicate_groups_per_fold)
            ),
            "grouped_folds_keep_feature_vectors_together": (
                all(
                    detail["train_test_feature_groups_disjoint"]
                    for detail in fold_details
                )
                if grouped else None
            ),
            "warning": (
                "Groups are kept disjoint, but some test folds omit entry. "
                "The grouped scores therefore do not reliably evaluate all "
                "four classes."
                if grouped
                else (
                    "Different CPU records with identical input features can "
                    "occur in both sides of a fold. These are not duplicate "
                    "IDs, but their shared specifications may make "
                    "record-level CV optimistic for entirely unseen CPU models."
                )
            ),
        },
        "models": results,
        "model_selection": _select_model(results) if not grouped else None,
    }


def _select_model(results):
    reference = results["decision_tree"]
    candidates = []
    comparisons = {}
    for model_key, result in results.items():
        if model_key in ("decision_tree", "majority_class_baseline"):
            continue
        macro_deltas = [
            candidate_fold["macro_f1"] - reference_fold["macro_f1"]
            for candidate_fold, reference_fold in zip(
                result["fold_scores"], reference["fold_scores"]
            )
        ]
        comparisons[model_key] = {
            "mean_macro_f1_delta_vs_decision_tree": fmean(macro_deltas),
            "folds_with_higher_macro_f1_fraction": sum(
                delta > 0 for delta in macro_deltas
            ) / len(macro_deltas),
        }
        consistent = (
            comparisons[model_key]["mean_macro_f1_delta_vs_decision_tree"] > 0
            and comparisons[model_key]["folds_with_higher_macro_f1_fraction"] > 0.5
            and result["metrics"]["accuracy"]["mean"]
            >= reference["metrics"]["accuracy"]["mean"]
            and result["metrics"]["balanced_accuracy"]["mean"]
            >= reference["metrics"]["balanced_accuracy"]["mean"]
        )
        if consistent:
            candidates.append(model_key)

    selected_model = max(
        candidates,
        key=lambda key: results[key]["metrics"]["macro_f1"]["mean"],
        default="decision_tree",
    )
    return {
        "reference_model": "decision_tree",
        "rule": (
            "An alternative qualifies only if its mean macro-F1 is higher, "
            "macro-F1 is higher on more than half of matched folds, and its "
            "mean accuracy and balanced accuracy are not lower than the "
            "current decision tree."
        ),
        "comparisons": comparisons,
        "selected_model": selected_model,
        "conclusion": (
            "An alternative met the consistency rule; this selection remains "
            "uncertain because it is based on only 30 editorially labeled CPUs."
            if selected_model != "decision_tree"
            else (
                "No alternative met the consistency rule. Retain the current "
                "decision tree as an experimental reference only; no reliable "
                "improvement has been demonstrated."
            )
        ),
    }


def evaluate_dataset(features, labels, quality):
    """Evaluate the historical holdout and compare models with repeated CV."""
    if len(labels) < 2:
        raise ValueError("At least two usable labeled CPU records are required.")
    counts = labels.value_counts()
    if any(counts.get(label, 0) < CV_SPLITS for label in LABELS):
        raise ValueError(
            "Repeated stratified 3-fold CV needs at least three usable examples "
            "per performance tier."
        )

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=labels,
    )
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(x_train, y_train)
    decision_tree = DecisionTreeClassifier(max_depth=3, random_state=RANDOM_SEED)
    decision_tree.fit(x_train, y_train)

    baseline_metrics = _metrics(y_test, baseline.predict(x_test))
    tree_metrics = _metrics(y_test, decision_tree.predict(x_test))
    feature_group_lookup = {
        tuple(group["features"][feature] for feature in FEATURE_COLUMNS): index
        for index, group in enumerate(quality["feature_vector_groups"])
    }
    group_ids = [
        feature_group_lookup[
            tuple(row[feature] for feature in FEATURE_COLUMNS)
        ]
        for row in features.to_dict(orient="records")
    ]
    record_level_cv = _cross_validate_models(
        features, labels, group_ids=group_ids
    )
    group_aware_cv = _cross_validate_models(
        features, labels, group_ids=group_ids, grouped=True
    )
    missing_entry_test_folds = sum(
        "entry" in detail["test_missing_labels"]
        for detail in group_aware_cv["split_details"]
    )
    grouped_feasibility = dict(quality["grouped_cv_feasibility"])
    grouped_feasibility.update({
        "folds_missing_entry_in_test": missing_entry_test_folds,
        "total_grouped_folds": group_aware_cv["total_folds"],
        "observed_all_test_folds_contain_all_labels": (
            missing_entry_test_folds == 0
            and all(
                not detail["test_missing_labels"]
                for detail in group_aware_cv["split_details"]
            )
        ),
        "reliable_four_class_grouped_evaluation": (
            missing_entry_test_folds == 0
            and all(
                not detail["test_missing_labels"]
                for detail in group_aware_cv["split_details"]
            )
        ),
    })
    group_aware_cv["feasibility"] = grouped_feasibility
    return {
        "experiment": "CPU performance-tier educational prototype",
        "random_seed": RANDOM_SEED,
        "features": list(FEATURE_COLUMNS),
        "labels": list(LABELS),
        "data_quality": quality,
        "preliminary_holdout": {
            "test_fraction": TEST_SIZE,
            "train_examples": int(len(y_train)),
            "test_examples": int(len(y_test)),
            "train_label_counts": {
                label: int(y_train.value_counts().get(label, 0))
                for label in LABELS
            },
            "test_label_counts": {
                label: int(y_test.value_counts().get(label, 0))
                for label in LABELS
            },
            "not_used_for_model_selection": True,
            "interpretation": (
                "Retained as the original preliminary 9-example holdout for "
                "historical comparison; it is not a dependable estimate."
            ),
        },
        "baseline": {
            "model": "Most frequent training label",
            "metrics": baseline_metrics,
        },
        "decision_tree": {
            "model": "DecisionTreeClassifier(max_depth=3)",
            "metrics": tree_metrics,
        },
        "cross_validation": record_level_cv,
        "group_aware_cross_validation": group_aware_cv,
        "interpretation": (
            "Labels are editorial assessments rather than verified benchmark "
            "ground truth. Repeated cross-validation on 30 CPUs is uncertain; "
            "its fold variation is descriptive and not a confidence interval. "
            "Grouped evaluation is not reliable for all four classes because "
            "entry CPUs occupy fewer than three distinct feature groups. "
            "The experiment is separate from production recommendations."
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compare a majority baseline and small CPU tier classifiers with "
            "repeated stratified cross-validation."
        )
    )
    parser.add_argument(
        "--components",
        type=Path,
        default=DEFAULT_COMPONENTS_PATH,
        help="Path to the existing components.csv catalog.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RESULTS_PATH,
        help="Where to write the evaluation JSON.",
    )
    args = parser.parse_args()

    features, labels, quality = prepare_cpu_dataset(args.components)
    results = evaluate_dataset(features, labels, quality)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(results, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Usable labeled CPUs: {quality['usable_labeled_examples']}")
    print(f"Label counts: {quality['label_counts']}")
    print(
        "Preliminary holdout accuracy (baseline/tree): "
        f"{results['baseline']['metrics']['accuracy']:.3f} / "
        f"{results['decision_tree']['metrics']['accuracy']:.3f}"
    )
    for model_key, result in results["cross_validation"]["models"].items():
        metrics = result["metrics"]
        print(
            f"{model_key}: "
            f"accuracy={metrics['accuracy']['mean']:.3f}"
            f"+/-{metrics['accuracy']['std']:.3f}, "
            f"macro-F1={metrics['macro_f1']['mean']:.3f}"
            f"+/-{metrics['macro_f1']['std']:.3f}, "
            f"balanced_accuracy={metrics['balanced_accuracy']['mean']:.3f}"
            f"+/-{metrics['balanced_accuracy']['std']:.3f}"
        )
    print("Group-aware cross-validation:")
    for model_key, result in results["group_aware_cross_validation"]["models"].items():
        metrics = result["metrics"]
        print(
            f"{model_key}: "
            f"accuracy={metrics['accuracy']['mean']:.3f}"
            f"+/-{metrics['accuracy']['std']:.3f}, "
            f"macro-F1={metrics['macro_f1']['mean']:.3f}"
            f"+/-{metrics['macro_f1']['std']:.3f}, "
            f"balanced_accuracy={metrics['balanced_accuracy']['mean']:.3f}"
            f"+/-{metrics['balanced_accuracy']['std']:.3f}"
        )
    feasibility = results["group_aware_cross_validation"]["feasibility"]
    print(
        "All-label grouped evaluation reliable: "
        f"{feasibility['reliable_four_class_grouped_evaluation']} "
        f"({feasibility['folds_missing_entry_in_test']}/"
        f"{feasibility['total_grouped_folds']} folds omit entry from test)"
    )
    print(
        "Selection: "
        f"{results['cross_validation']['model_selection']['selected_model']} "
        f"({results['cross_validation']['model_selection']['conclusion']})"
    )
    print(f"Evaluation saved to: {args.output}")


if __name__ == "__main__":
    main()
