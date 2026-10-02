"""
Focused Final Validation - Quality Engine
Tests problematic and clean files for each format
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import LoaderFactory, DataNormalizer
from src.quality_metrics import QualityMetrics, QualitySeverity
from src.metadata_generator import MetadataGenerator
import json

def test_file(filepath, expected_issues):
    """Test a single file and return results"""
    print(f"\n{'='*60}")
    print(f"Testing: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        # Load file
        asset = LoaderFactory.load_file(filepath)
        normalized = DataNormalizer.normalize(asset)
        
        # Quality assessment
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)
        
        # Metadata
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)
        
        # Results
        results = {
            'file': os.path.basename(filepath),
            'format': metadata.source_format,
            'category': metadata.data_category,
            'total_rows': int(metadata.total_rows),
            'total_columns': int(metadata.total_columns),
            'total_issues': int(quality_report.total_issues),
            'quality_score': float(quality_report.quality_score),
            'completeness_score': float(quality_report.completeness_score),
            'consistency_score': float(quality_report.consistency_score),
            'validity_score': float(quality_report.validity_score),
            'component_scores_applicable': quality_report.component_scores_applicable,
            'detected_issues': [(i.issue_type, i.severity.value, i.description) for i in quality_report.issues],
            'expected_issues': expected_issues,
            'success': True
        }
        
        # Print results
        print(f"Format: {results['format']}")
        print(f"Category: {results['category']}")
        print(f"Rows: {results['total_rows']}")
        print(f"Columns: {results['total_columns']}")
        print(f"Quality Score: {results['quality_score']:.1f}/100")
        if results['component_scores_applicable']:
            print(f"Completeness: {results['completeness_score']:.1f}/100")
            print(f"Consistency: {results['consistency_score']:.1f}/100")
            print(f"Validity: {results['validity_score']:.1f}/100")
        else:
            print("Completeness: N/A (not applicable)")
            print("Consistency: N/A (not applicable)")
            print("Validity: N/A (not applicable)")
        print(f"\nDetected Issues ({len(results['detected_issues'])}):")
        for issue_type, severity, desc in results['detected_issues']:
            print(f"  - [{severity.upper()}] {issue_type}: {desc}")
        
        # Compare with expected
        print(f"\nExpected Issues: {expected_issues}")
        
        # Check if expected issues were detected
        detected_types = [i[0] for i in results['detected_issues']]
        matched = [e for e in expected_issues if e in detected_types]
        missing = [e for e in expected_issues if e not in detected_types]
        
        if missing:
            print(f"MISSING EXPECTED ISSUES: {missing}")
            results['matched'] = False
        else:
            print("All expected issues detected")
            results['matched'] = True
        
        return results
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'file': os.path.basename(filepath),
            'success': False,
            'error': str(e)
        }

def main():
    print("="*60)
    print("FOCUSED QUALITY ENGINE VALIDATION")
    print("="*60)
    
    test_cases = [
        # CSV
        {
            'file': 'data/sample/test_csv_issues.csv',
            'expected': ['missing_values', 'duplicate_rows', 'outliers', 'negative_values']
        },
        {
            'file': 'data/sample/test_csv_clean.csv',
            'expected': []
        },
        # TXT - text is 185 chars, so not "very short" but has special characters
        {
            'file': 'data/sample/test_txt_problematic.txt',
            'expected': ['many_special_characters']
        },
        {
            'file': 'data/sample/test_txt_clean.txt',
            'expected': []
        },
        # PDF - text is 169 chars, so not "very short" but has repetitive content and special characters
        {
            'file': 'data/sample/test_pdf_problematic.pdf',
            'expected': ['repetitive_content', 'many_special_characters']
        },
        {
            'file': 'data/sample/test_pdf_clean.pdf',
            'expected': []
        },
    ]
    
    all_results = []
    
    for test_case in test_cases:
        result = test_file(test_case['file'], test_case['expected'])
        all_results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("QUALITY ENGINE VALIDATION SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in all_results if r.get('success', False))
    matched = sum(1 for r in all_results if r.get('matched', False))
    failed = len(all_results) - successful
    
    print(f"Total Tests: {len(all_results)}")
    print(f"Successful (no errors): {successful}")
    print(f"Matched Expected Issues: {matched}")
    print(f"Failed: {failed}")
    
    print("\nDetailed Results:")
    for result in all_results:
        if result.get('success'):
            match_status = "[MATCHED]" if result.get('matched') else "[MISSING ISSUES]"
            print(f"[PASS] {result['file']}: Score {result['quality_score']:.1f}/100, {result['total_issues']} issues {match_status}")
        else:
            print(f"[FAIL] {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Save results
    with open('quality_engine_validation.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to quality_engine_validation.json")

if __name__ == "__main__":
    main()
