
import argparse
import json
import sys
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

ROOT = Path(__file__).resolve().parent.parent

BINARY_LABELS = ["TRUE_POSITIVE", "FALSE_POSITIVE"]
ALL_LABELS = [
    "TRUE_POSITIVE",
    "FALSE_POSITIVE",
    "INSUFFICIENT_EVIDENCE",
]


def load_json(path: Path):
    """Load JSON data from a file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_args():
    """Parse evaluation dataset and results paths."""
    parser = argparse.ArgumentParser(
        description="Evaluate AI security triage predictions."
    )

    parser.add_argument(
        "--dataset",
        default="samples/sast_findings.json",
        help="Path to labelled findings JSON.",
    )

    parser.add_argument(
        "--results",
        default="results/evaluation_results.json",
        help="Path to AI triage results JSON.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    dataset_path = Path(args.dataset)
    results_path = Path(args.results)

    # Resolve relative paths from the project root.
    if not dataset_path.is_absolute():
        dataset_path = ROOT / dataset_path

    if not results_path.is_absolute():
        results_path = ROOT / results_path

    if not dataset_path.is_file():
        print(f"ERROR: Dataset file not found: {dataset_path}")
        sys.exit(1)

    if not results_path.is_file():
        print(f"ERROR: Results file not found: {results_path}")
        sys.exit(1)

    dataset = load_json(dataset_path)
    results = load_json(results_path)

    if not isinstance(dataset, dict) or not isinstance(
        dataset.get("findings"), list
    ):
        raise ValueError("Dataset must contain a findings list.")

    if not isinstance(results, list):
        raise ValueError("Triage results must be a JSON list.")

    # Build ground-truth labels by original finding ID.
    expected = {}

    for finding in dataset["findings"]:
        if not isinstance(finding, dict):
            continue

        finding_id = finding.get("id")
        label = finding.get("expected_label")

        if not isinstance(finding_id, str) or not finding_id:
            continue

        if label not in ALL_LABELS[:2] + ["INSUFFICIENT_EVIDENCE"]:
            raise ValueError(
                f"Unsupported expected label for {finding_id}: {label}"
            )

        if finding_id in expected:
            raise ValueError(f"Duplicate dataset finding ID: {finding_id}")

        expected[finding_id] = label

    if not expected:
        raise ValueError("No valid labelled findings found in dataset.")

    actual = []
    predicted = []
    unmatched = []
    failed = []
    duplicate_results = []
    seen_ids = set()

    for result in results:
        if not isinstance(result, dict):
            failed.append("invalid_result_entry")
            continue

        finding_id = result.get("finding_id")

        if not isinstance(finding_id, str) or not finding_id:
            failed.append("missing_finding_id")
            continue

        if finding_id in seen_ids:
            duplicate_results.append(finding_id)
            continue

        seen_ids.add(finding_id)

        if finding_id not in expected:
            unmatched.append(finding_id)
            continue

        # Do not count API failures or fallback results as successful
        # model predictions.
        if result.get("error"):
            failed.append(finding_id)
            continue

        classification = result.get("classification")

        if classification not in ALL_LABELS:
            failed.append(finding_id)
            continue

        actual.append(expected[finding_id])
        predicted.append(classification)

    print("\n=== AI TRIAGE EVALUATION ===")
    print(f"Dataset: {dataset_path}")
    print(f"Results: {results_path}")
    print(f"Ground-truth findings: {len(expected)}")
    print(f"Valid evaluated findings: {len(actual)}")
    print(f"Failed predictions: {len(failed)}")
    print(f"Unmatched results: {len(unmatched)}")
    print(f"Duplicate results: {len(duplicate_results)}")

    coverage = len(actual) / len(expected)
    print(f"Evaluation coverage: {coverage:.1%}")

    if unmatched:
        print("Unmatched finding IDs:", unmatched)

    if failed:
        print("Failed finding IDs:", failed)

    if duplicate_results:
        print("Duplicate result IDs:", duplicate_results)

    if not actual:
        print("\nNo valid matching predictions to evaluate.")
        sys.exit(1)

    uncertain = predicted.count("INSUFFICIENT_EVIDENCE")
    decisive = [
        (a, p)
        for a, p in zip(actual, predicted)
        if p in BINARY_LABELS
    ]

    print(f"Uncertain predictions: {uncertain}")
    print(f"Decisive predictions: {len(decisive)}")

    print("\nClassification report:")
    print(
        classification_report(
            actual,
            predicted,
            labels=ALL_LABELS,
            zero_division=0,
        )
    )

    print("Confusion matrix")
    print("(rows = actual, columns = predicted)")
    print("Label order:", ALL_LABELS)
    print(confusion_matrix(actual, predicted, labels=ALL_LABELS))

    # Overall accuracy counts an abstention as incorrect when the
    # ground-truth label is TRUE_POSITIVE or FALSE_POSITIVE.
    print(f"\nOverall accuracy: {accuracy_score(actual, predicted):.3f}")

    # These binary metrics exclude uncertain predictions and must
    # always be reported alongside coverage and uncertainty.
    if decisive:
        decisive_actual = [a for a, _ in decisive]
        decisive_predicted = [p for _, p in decisive]

        precision, recall, f1, _ = precision_recall_fscore_support(
            decisive_actual,
            decisive_predicted,
            labels=["TRUE_POSITIVE"],
            average="binary",
            pos_label="TRUE_POSITIVE",
            zero_division=0,
        )

        print("\nBinary metrics on decisive predictions only:")
        print(
            "Accuracy:",
            f"{accuracy_score(decisive_actual, decisive_predicted):.3f}",
        )
        print(f"True-positive precision: {precision:.3f}")
        print(f"True-positive recall:    {recall:.3f}")
        print(f"True-positive F1-score:  {f1:.3f}")
        print(
            "Note: these metrics exclude uncertain predictions. "
            "Interpret them alongside overall accuracy and coverage."
        )


if __name__ == "__main__":
    main()
