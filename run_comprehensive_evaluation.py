"""
Comprehensive End-to-End Evaluation of Data Quality Assessment
Tests all supported file formats with known quality issues
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
            'rows': int(metadata.total_rows),
            'columns': int(metadata.total_columns),
            'total_issues': int(quality_report.total_issues),
            'quality_score': float(quality_report.quality_score),
            'completeness_score': float(quality_report.completeness_score),
            'consistency_score': float(quality_report.consistency_score),
            'validity_score': float(quality_report.validity_score),
            'detected_issues': [(i.issue_type, i.severity.value, i.description) for i in quality_report.issues],
            'expected_issues': expected_issues,
            'success': True
        }
        
        # Print results
        print(f"Format: {results['format']}")
        print(f"Category: {results['category']}")
        print(f"Rows: {results['rows']}")
        print(f"Columns: {results['columns']}")
        print(f"Quality Score: {results['quality_score']:.1f}/100")
        print(f"Completeness: {results['completeness_score']:.1f}/100")
        print(f"Consistency: {results['consistency_score']:.1f}/100")
        print(f"Validity: {results['validity_score']:.1f}/100")
        print(f"\nDetected Issues ({len(results['detected_issues'])}):")
        for issue_type, severity, desc in results['detected_issues']:
            print(f"  - [{severity.upper()}] {issue_type}: {desc}")
        
        # Compare with expected
        print(f"\nExpected Issues: {expected_issues}")
        
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
    print("COMPREHENSIVE DATA QUALITY ASSESSMENT EVALUATION")
    print("="*60)
    
    test_cases = [
        # CSV - Issues
        {
            'file': 'data/sample/test_csv_issues.csv',
            'expected': ['missing_values', 'duplicate_rows', 'outliers', 'negative_values']
        },
        # CSV - Clean
        {
            'file': 'data/sample/test_csv_clean.csv',
            'expected': []
        },
        # Excel - Issues
        {
            'file': 'data/sample/test_excel_issues.xlsx',
            'expected': ['missing_values', 'duplicate_rows', 'outliers', 'negative_values']
        },
        # Excel - Clean
        {
            'file': 'data/sample/test_excel_clean.xlsx',
            'expected': []
        },
        # JSON - Issues
        {
            'file': 'data/sample/test_json_issues.json',
            'expected': ['missing_values', 'duplicate_rows', 'outliers', 'negative_values']
        },
        # JSON - Clean (using sample)
        {
            'file': 'data/sample/sample_dataset.json',
            'expected': ['missing_values', 'duplicate_rows', 'outliers']
        },
        # XML - Issues
        {
            'file': 'data/sample/test_xml_issues.xml',
            'expected': ['missing_values', 'duplicate_rows', 'outliers', 'negative_values']
        },
        # XML - Clean (using sample)
        {
            'file': 'data/sample/sample_dataset.xml',
            'expected': ['missing_values', 'duplicate_rows', 'outliers']
        },
        # TXT - Issues
        {
            'file': 'data/sample/test_txt_issues.txt',
            'expected': ['very_short_text', 'repetitive_content', 'special_characters']
        },
        # TXT - Clean
        {
            'file': 'data/sample/test_txt_clean.txt',
            'expected': []
        },
        # PDF - Issues (using sample)
        {
            'file': 'data/sample/test_pdf_issues.pdf',
            'expected': ['very_short_text']
        },
        # PDF - Clean (using sample)
        {
            'file': 'data/sample/test_pdf_clean.pdf',
            'expected': ['very_short_text']
        },
    ]
    
    all_results = []
    
    for test_case in test_cases:
        result = test_file(test_case['file'], test_case['expected'])
        all_results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in all_results if r.get('success', False))
    failed = len(all_results) - successful
    
    print(f"Total Tests: {len(all_results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    print("\nDetailed Results:")
    for result in all_results:
        if result.get('success'):
            print(f"[PASS] {result['file']}: Score {result['quality_score']:.1f}/100, {result['total_issues']} issues")
        else:
            print(f"[FAIL] {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Save results
    with open('evaluation_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to evaluation_results.json")

if __name__ == "__main__":
    main()
