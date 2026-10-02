"""
Quality Detection Evaluation Script
Evaluates quality detection on controlled datasets
"""

import sys
import os
import json
import time
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import LoaderFactory, DataNormalizer
from src.quality_metrics import QualityMetrics


def evaluate_dataset(dataset_path, expected_file):
    """Evaluate a single dataset"""
    print(f"\n{'='*60}")
    print(f"Evaluating: {dataset_path}")
    print(f"{'='*60}")

    # Load expected results
    with open(expected_file, 'r') as f:
        expected = json.load(f)

    # Load dataset
    start_time = time.time()
    asset = LoaderFactory.load_file(dataset_path)
    normalized = DataNormalizer.normalize(asset)
    load_time = time.time() - start_time

    # Quality assessment
    start_time = time.time()
    metrics = QualityMetrics()
    quality_report = metrics.assess_quality(normalized)
    quality_time = time.time() - start_time

    # Extract detected issues
    detected_issues = list(set([issue.issue_type for issue in quality_report.issues]))

    # Compare with expected
    expected_issues = expected.get('expected_issues', [])

    # Calculate metrics
    true_positives = set(detected_issues) & set(expected_issues)
    false_positives = set(detected_issues) - set(expected_issues)
    false_negatives = set(expected_issues) - set(detected_issues)

    tp = len(true_positives)
    fp = len(false_positives)
    fn = len(false_negatives)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # Build result
    result = {
        "dataset": os.path.basename(dataset_path),
        "format": expected.get('format'),
        "data_category": expected.get('data_category'),
        "expected_issues": expected_issues,
        "detected_issues": detected_issues,
        "quality_score": float(quality_report.quality_score),
        "completeness_score": float(quality_report.completeness_score),
        "consistency_score": float(quality_report.consistency_score),
        "validity_score": float(quality_report.validity_score),
        "expected_quality_score": expected.get('expected_quality_score'),
        "description": expected.get('description'),
        "performance": {
            "load_time": round(load_time, 3),
            "quality_time": round(quality_time, 3)
        },
        "detection_metrics": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3)
        },
        "evaluation_timestamp": datetime.utcnow().isoformat()
    }

    # Print results
    print(f"Format: {result['format']}")
    print(f"Category: {result['data_category']}")
    print(f"Expected Issues: {expected_issues}")
    print(f"Detected Issues: {detected_issues}")
    print(f"Quality Score: {result['quality_score']}/100")
    print(f"Completeness: {result['completeness_score']}/100")
    print(f"Consistency: {result['consistency_score']}/100")
    print(f"Validity: {result['validity_score']}/100")
    print(f"\nDetection Metrics:")
    print(f"  True Positives: {tp}")
    print(f"  False Positives: {fp}")
    print(f"  False Negatives: {fn}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall: {recall:.3f}")
    print(f"  F1 Score: {f1:.3f}")
    print(f"\nPerformance:")
    print(f"  Load Time: {load_time:.3f}s")
    print(f"  Quality Time: {quality_time:.3f}s")

    return result


def main():
    """Run evaluation on all datasets"""
    print("="*60)
    print("QUALITY DETECTION EVALUATION")
    print("="*60)

    # Define datasets to evaluate
    datasets = [
        ("evaluation/structured/clean_dataset.csv", "evaluation/expected_results/clean_dataset.json"),
        ("evaluation/structured/missing_values.csv", "evaluation/expected_results/missing_values.json"),
        ("evaluation/structured/duplicate_records.csv", "evaluation/expected_results/duplicate_records.json"),
        ("evaluation/structured/outlier_dataset.csv", "evaluation/expected_results/outlier_dataset.json"),
        ("evaluation/structured/type_inconsistency.csv", "evaluation/expected_results/type_inconsistency.json"),
        ("evaluation/structured/mixed_quality_dataset.csv", "evaluation/expected_results/mixed_quality_dataset.json"),
        ("evaluation/semi_structured/clean_dataset.json", "evaluation/expected_results/clean_dataset.json.json"),
        ("evaluation/semi_structured/quality_issues.json", "evaluation/expected_results/quality_issues.json.json"),
        ("evaluation/semi_structured/clean_dataset.xml", "evaluation/expected_results/clean_dataset.xml.json"),
        ("evaluation/unstructured/clean_document.txt", "evaluation/expected_results/clean_document.txt.json"),
        ("evaluation/unstructured/poor_quality_document.txt", "evaluation/expected_results/poor_quality_document.txt.json"),
    ]

    results = []
    for dataset_path, expected_file in datasets:
        try:
            result = evaluate_dataset(dataset_path, expected_file)
            results.append(result)
        except Exception as e:
            print(f"ERROR evaluating {dataset_path}: {e}")
            import traceback
            traceback.print_exc()

    # Save results
    output_file = "evaluation/reports/quality_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*60}")

    # Generate markdown report
    generate_markdown_report(results)

    return results


def generate_markdown_report(results):
    """Generate human-readable markdown report"""
    output_file = "evaluation/reports/quality_results.md"

    with open(output_file, 'w') as f:
        f.write("# Quality Detection Evaluation Report\n\n")
        f.write(f"**Generated:** {datetime.utcnow().isoformat()}\n\n")
        f.write(f"**Total Datasets Evaluated:** {len(results)}\n\n")

        # Summary statistics
        f.write("## Summary Statistics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")

        total_tp = sum(r['detection_metrics']['true_positives'] for r in results)
        total_fp = sum(r['detection_metrics']['false_positives'] for r in results)
        total_fn = sum(r['detection_metrics']['false_negatives'] for r in results)

        overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0

        f.write(f"| Total True Positives | {total_tp} |\n")
        f.write(f"| Total False Positives | {total_fp} |\n")
        f.write(f"| Total False Negatives | {total_fn} |\n")
        f.write(f"| Overall Precision | {overall_precision:.3f} |\n")
        f.write(f"| Overall Recall | {overall_recall:.3f} |\n")
        f.write(f"| Overall F1 Score | {overall_f1:.3f} |\n\n")

        # Detailed results
        f.write("## Detailed Results\n\n")
        for result in results:
            f.write(f"### {result['dataset']}\n\n")
            f.write(f"- **Format:** {result['format']}\n")
            f.write(f"- **Category:** {result['data_category']}\n")
            f.write(f"- **Expected Issues:** {result['expected_issues']}\n")
            f.write(f"- **Detected Issues:** {result['detected_issues']}\n")
            f.write(f"- **Quality Score:** {result['quality_score']}/100\n")
            f.write(f"- **Completeness:** {result['completeness_score']}/100\n")
            f.write(f"- **Consistency:** {result['consistency_score']}/100\n")
            f.write(f"- **Validity:** {result['validity_score']}/100\n")
            f.write(f"- **Description:** {result['description']}\n\n")
            f.write("**Detection Metrics:**\n")
            f.write(f"- True Positives: {result['detection_metrics']['true_positives']}\n")
            f.write(f"- False Positives: {result['detection_metrics']['false_positives']}\n")
            f.write(f"- False Negatives: {result['detection_metrics']['false_negatives']}\n")
            f.write(f"- Precision: {result['detection_metrics']['precision']}\n")
            f.write(f"- Recall: {result['detection_metrics']['recall']}\n")
            f.write(f"- F1 Score: {result['detection_metrics']['f1']}\n\n")
            f.write("**Performance:**\n")
            f.write(f"- Load Time: {result['performance']['load_time']}s\n")
            f.write(f"- Quality Time: {result['performance']['quality_time']}s\n\n")
            f.write("---\n\n")

    print(f"Markdown report saved to: {output_file}")


if __name__ == "__main__":
    main()
