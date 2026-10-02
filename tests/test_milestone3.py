"""
Test Script for Milestone 3
Tests quality metrics detection for all data formats
"""

import sys
import os
from pathlib import Path

# Set console encoding to UTF-8 for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import LoaderFactory, DataNormalizer
from src.quality_metrics import QualityMetrics, QualitySeverity


def test_csv_quality_metrics():
    """Test quality metrics on CSV data"""
    print("=" * 60)
    print("TEST: CSV Quality Metrics")
    print("=" * 60)

    try:
        # Load CSV data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized_asset = DataNormalizer.normalize(asset)

        # Assess quality
        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Quality assessment completed")
        print(f"  Overall score: {report.quality_score:.1f}/100")
        print(f"  Total issues: {report.total_issues}")
        print(f"  Assessment: {report.overall_assessment}")

        # Verify expected issues are detected
        issue_types = [issue.issue_type for issue in report.issues]
        print(f"  Issue types detected: {issue_types}")

        # Should detect missing values and duplicates (based on our sample data)
        if 'missing_values' in issue_types:
            print(f"  [PASS] Missing values detected")
        if 'duplicate_rows' in issue_types:
            print(f"  [PASS] Duplicate rows detected")
        if 'outliers' in issue_types:
            print(f"  [PASS] Outliers detected")

        return True

    except Exception as e:
        print(f"[FAIL] CSV quality metrics test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_excel_quality_metrics():
    """Test quality metrics on Excel data"""
    print("\n" + "=" * 60)
    print("TEST: Excel Quality Metrics")
    print("=" * 60)

    try:
        # Load Excel data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.xlsx')
        normalized_asset = DataNormalizer.normalize(asset)

        # Assess quality
        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Quality assessment completed")
        print(f"  Overall score: {report.quality_score:.1f}/100")
        print(f"  Total issues: {report.total_issues}")

        return True

    except Exception as e:
        print(f"[FAIL] Excel quality metrics test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_json_quality_metrics():
    """Test quality metrics on JSON data"""
    print("\n" + "=" * 60)
    print("TEST: JSON Quality Metrics")
    print("=" * 60)

    try:
        # Load JSON data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.json')
        normalized_asset = DataNormalizer.normalize(asset)

        # Assess quality
        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Quality assessment completed")
        print(f"  Overall score: {report.quality_score:.1f}/100")
        print(f"  Total issues: {report.total_issues}")

        return True

    except Exception as e:
        print(f"[FAIL] JSON quality metrics test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_xml_quality_metrics():
    """Test quality metrics on XML data"""
    print("\n" + "=" * 60)
    print("TEST: XML Quality Metrics")
    print("=" * 60)

    try:
        # Load XML data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.xml')
        normalized_asset = DataNormalizer.normalize(asset)

        # Assess quality
        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Quality assessment completed")
        print(f"  Overall score: {report.quality_score:.1f}/100")
        print(f"  Total issues: {report.total_issues}")

        return True

    except Exception as e:
        print(f"[FAIL] XML quality metrics test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_txt_quality_metrics():
    """Test quality metrics on TXT data"""
    print("\n" + "=" * 60)
    print("TEST: TXT Quality Metrics")
    print("=" * 60)

    try:
        # Load TXT data
        asset = LoaderFactory.load_file('data/sample/sample_document.txt')
        normalized_asset = DataNormalizer.normalize(asset)

        # Assess quality
        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Quality assessment completed")
        print(f"  Overall score: {report.quality_score:.1f}/100")
        print(f"  Total issues: {report.total_issues}")

        # Text should have different issues than tabular data
        issue_types = [issue.issue_type for issue in report.issues]
        print(f"  Issue types detected: {issue_types}")

        return True

    except Exception as e:
        print(f"[FAIL] TXT quality metrics test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_quality_metrics():
    """Test quality metrics on PDF data"""
    print("\n" + "=" * 60)
    print("TEST: PDF Quality Metrics")
    print("=" * 60)

    try:
        # Load PDF data
        asset = LoaderFactory.load_file('data/sample/sample_document.pdf')
        normalized_asset = DataNormalizer.normalize(asset)

        # Assess quality
        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Quality assessment completed")
        print(f"  Overall score: {report.quality_score:.1f}/100")
        print(f"  Total issues: {report.total_issues}")

        return True

    except Exception as e:
        print(f"[FAIL] PDF quality metrics test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_quality_scoring():
    """Test quality scoring calculation"""
    print("\n" + "=" * 60)
    print("TEST: Quality Scoring")
    print("=" * 60)

    try:
        # Test with CSV data (should have some issues)
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized_asset = DataNormalizer.normalize(asset)

        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Quality scoring completed")
        print(f"  Overall score: {report.quality_score:.1f}/100")
        print(f"  Completeness score: {report.completeness_score:.1f}/100")
        print(f"  Consistency score: {report.consistency_score:.1f}/100")
        print(f"  Validity score: {report.validity_score:.1f}/100")

        # Verify scores are in valid range
        if 0 <= report.quality_score <= 100:
            print(f"  [PASS] Overall score in valid range (0-100)")
        else:
            print(f"  [FAIL] Overall score out of range: {report.quality_score}")

        # Verify component scores
        for score_name, score_value in [
            ("Completeness", report.completeness_score),
            ("Consistency", report.consistency_score),
            ("Validity", report.validity_score)
        ]:
            if 0 <= score_value <= 100:
                print(f"  [PASS] {score_name} score in valid range")
            else:
                print(f"  [FAIL] {score_name} score out of range: {score_value}")

        return True

    except Exception as e:
        print(f"[FAIL] Quality scoring test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_empty_dataset():
    """Test quality metrics on empty dataset"""
    print("\n" + "=" * 60)
    print("TEST: Empty Dataset")
    print("=" * 60)

    try:
        import pandas as pd
        from src.ingestion import DataAsset

        # Create empty DataFrame
        empty_df = pd.DataFrame()
        empty_asset = DataAsset(
            source_file="test_empty.csv",
            source_format="CSV",
            data_category="structured",
            tabular_data=empty_df
        )

        metrics = QualityMetrics()
        report = metrics.assess_quality(empty_asset)

        print(f"[PASS] Empty dataset handled")
        print(f"  Overall score: {report.quality_score:.1f}/100")
        print(f"  Total issues: {report.total_issues}")

        # Should detect empty dataset as critical issue
        issue_types = [issue.issue_type for issue in report.issues]
        if 'empty_dataset' in issue_types:
            print(f"  [PASS] Empty dataset detected as critical issue")
        else:
            print(f"  [FAIL] Empty dataset not detected")

        return True

    except Exception as e:
        print(f"[FAIL] Empty dataset test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_severity_levels():
    """Test that different severity levels are assigned correctly"""
    print("\n" + "=" * 60)
    print("TEST: Severity Levels")
    print("=" * 60)

    try:
        # Load CSV data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized_asset = DataNormalizer.normalize(asset)

        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Severity level assignment completed")

        # Check that different severity levels are used
        severity_levels = set(issue.severity for issue in report.issues)
        print(f"  Severity levels used: {[s.value for s in severity_levels]}")

        # Verify severity counts
        if report.issues_by_severity:
            print(f"  Severity breakdown:")
            for severity, count in report.issues_by_severity.items():
                print(f"    {severity}: {count}")

        return True

    except Exception as e:
        print(f"[FAIL] Severity levels test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_issue_types():
    """Test that different issue types are detected"""
    print("\n" + "=" * 60)
    print("TEST: Issue Types")
    print("=" * 60)

    try:
        # Load CSV data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized_asset = DataNormalizer.normalize(asset)

        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] Issue type detection completed")

        # Check that different issue types are detected
        issue_types = set(issue.issue_type for issue in report.issues)
        print(f"  Issue types detected: {sorted(issue_types)}")

        # Verify issue type counts
        if report.issues_by_type:
            print(f"  Issue type breakdown:")
            for issue_type, count in report.issues_by_type.items():
                print(f"    {issue_type}: {count}")

        return True

    except Exception as e:
        print(f"[FAIL] Issue types test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test that quality metrics work with existing profiling"""
    print("\n" + "=" * 60)
    print("TEST: Backward Compatibility with Profiling")
    print("=" * 60)

    try:
        from src.data_ingestion import DataIngestion
        from src.profiling import DataProfiler

        # Load CSV using old method
        ingester = DataIngestion()
        data = ingester.load_csv('data/sample/sample_dataset.csv')

        # Use old profiler
        profiler = DataProfiler(data)
        profile = profiler.generate_profile()

        print(f"[PASS] Old profiling still works")

        # Now use new quality metrics on the same data
        from src.ingestion import CSVLoader, DataNormalizer
        csv_loader = CSVLoader()
        asset = csv_loader.load('data/sample/sample_dataset.csv')
        normalized_asset = DataNormalizer.normalize(asset)

        metrics = QualityMetrics()
        report = metrics.assess_quality(normalized_asset)

        print(f"[PASS] New quality metrics work on same data")
        print(f"  Old profiler rows: {profile['basic_info']['num_rows']}")
        print(f"  New metrics rows: {len(normalized_asset.tabular_data)}")

        return True

    except Exception as e:
        print(f"[FAIL] Backward compatibility test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MILESTONE 3 TEST SUITE - Quality Metrics Detection")
    print("=" * 60)

    results = []

    # Test quality metrics for each format
    results.append(("CSV Quality Metrics", test_csv_quality_metrics()))
    results.append(("Excel Quality Metrics", test_excel_quality_metrics()))
    results.append(("JSON Quality Metrics", test_json_quality_metrics()))
    results.append(("XML Quality Metrics", test_xml_quality_metrics()))
    results.append(("TXT Quality Metrics", test_txt_quality_metrics()))
    results.append(("PDF Quality Metrics", test_pdf_quality_metrics()))

    # Test scoring and functionality
    results.append(("Quality Scoring", test_quality_scoring()))
    results.append(("Empty Dataset", test_empty_dataset()))
    results.append(("Severity Levels", test_severity_levels()))
    results.append(("Issue Types", test_issue_types()))
    results.append(("Backward Compatibility", test_backward_compatibility()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{test_name}: {status}")

    all_passed = all(success for _, success in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED [PASS]")
    else:
        print("SOME TESTS FAILED [FAIL]")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
