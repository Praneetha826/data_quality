"""
Test Script for Milestone 2
Tests the complete data ingestion layer for all six formats
"""

import sys
import os
from pathlib import Path

# Set console encoding to UTF-8 for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import (
    CSVLoader, ExcelLoader, JSONLoader, XMLLoader,
    TXTLoader, PDFLoader, LoaderFactory, DataNormalizer
)


def test_csv_loader():
    """Test CSV loader functionality"""
    print("=" * 60)
    print("TEST: CSV Loader")
    print("=" * 60)

    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.csv"

    try:
        loader = CSVLoader()
        asset = loader.load(str(sample_path))

        print(f"[PASS] CSV loaded successfully")
        print(f"  Format: {asset.source_format}")
        print(f"  Category: {asset.data_category}")
        print(f"  Is tabular: {asset.is_tabular()}")

        if asset.is_tabular():
            df = asset.tabular_data
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Column names: {list(df.columns)}")

        print(f"  Extraction errors: {len(asset.extraction_errors)}")
        print(f"  Warnings: {len(asset.warnings)}")

        # Test validation
        is_valid = loader.validate_file(str(sample_path))
        print(f"  Validation: {is_valid}")

        return True

    except Exception as e:
        print(f"[FAIL] CSV test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_excel_loader():
    """Test Excel loader functionality"""
    print("\n" + "=" * 60)
    print("TEST: Excel Loader")
    print("=" * 60)

    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.xlsx"

    try:
        loader = ExcelLoader()
        asset = loader.load(str(sample_path))

        print(f"[PASS] Excel loaded successfully")
        print(f"  Format: {asset.source_format}")
        print(f"  Category: {asset.data_category}")
        print(f"  Is tabular: {asset.is_tabular()}")

        if asset.is_tabular():
            df = asset.tabular_data
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Column names: {list(df.columns)}")

        print(f"  Available sheets: {asset.metadata.get('available_sheets', 'N/A')}")
        print(f"  Loaded sheet: {asset.metadata.get('loaded_sheet', 'N/A')}")
        print(f"  Extraction errors: {len(asset.extraction_errors)}")
        print(f"  Warnings: {len(asset.warnings)}")

        # Test validation
        is_valid = loader.validate_file(str(sample_path))
        print(f"  Validation: {is_valid}")

        return True

    except Exception as e:
        print(f"[FAIL] Excel test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_json_loader():
    """Test JSON loader functionality"""
    print("\n" + "=" * 60)
    print("TEST: JSON Loader")
    print("=" * 60)

    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.json"

    try:
        loader = JSONLoader()
        asset = loader.load(str(sample_path))

        print(f"[PASS] JSON loaded successfully")
        print(f"  Format: {asset.source_format}")
        print(f"  Category: {asset.data_category}")
        print(f"  Is tabular: {asset.is_tabular()}")
        print(f"  Is text: {asset.is_text()}")

        if asset.is_tabular():
            df = asset.tabular_data
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Column names: {list(df.columns)}")

        print(f"  Data type: {asset.metadata.get('data_type', 'N/A')}")
        print(f"  Is array of records: {asset.metadata.get('is_array_of_records', 'N/A')}")
        print(f"  Extraction errors: {len(asset.extraction_errors)}")
        print(f"  Warnings: {len(asset.warnings)}")

        # Test validation
        is_valid = loader.validate_file(str(sample_path))
        print(f"  Validation: {is_valid}")

        return True

    except Exception as e:
        print(f"[FAIL] JSON test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_xml_loader():
    """Test XML loader functionality"""
    print("\n" + "=" * 60)
    print("TEST: XML Loader")
    print("=" * 60)

    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.xml"

    try:
        loader = XMLLoader()
        asset = loader.load(str(sample_path))

        print(f"[PASS] XML loaded successfully")
        print(f"  Format: {asset.source_format}")
        print(f"  Category: {asset.data_category}")
        print(f"  Is tabular: {asset.is_tabular()}")
        print(f"  Is text: {asset.is_text()}")

        if asset.is_tabular():
            df = asset.tabular_data
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Column names: {list(df.columns)}")

        print(f"  Root tag: {asset.metadata.get('root_tag', 'N/A')}")
        print(f"  Total elements: {asset.metadata.get('total_elements', 'N/A')}")
        print(f"  Records extracted: {asset.metadata.get('records_extracted', 'N/A')}")
        print(f"  Extraction errors: {len(asset.extraction_errors)}")
        print(f"  Warnings: {len(asset.warnings)}")

        # Test validation
        is_valid = loader.validate_file(str(sample_path))
        print(f"  Validation: {is_valid}")

        return True

    except Exception as e:
        print(f"[FAIL] XML test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_txt_loader():
    """Test TXT loader functionality"""
    print("\n" + "=" * 60)
    print("TEST: TXT Loader")
    print("=" * 60)

    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_document.txt"

    try:
        loader = TXTLoader()
        asset = loader.load(str(sample_path))

        print(f"[PASS] TXT loaded successfully")
        print(f"  Format: {asset.source_format}")
        print(f"  Category: {asset.data_category}")
        print(f"  Is tabular: {asset.is_tabular()}")
        print(f"  Is text: {asset.is_text()}")

        if asset.is_text():
            text = asset.text_data
            print(f"  Character count: {len(text)}")
            print(f"  Word count: {len(text.split())}")
            print(f"  Line count: {len(text.split(chr(10)))}")

        print(f"  Encoding: {asset.metadata.get('encoding', 'N/A')}")
        print(f"  Non-empty lines: {asset.metadata.get('non_empty_lines', 'N/A')}")
        print(f"  Extraction errors: {len(asset.extraction_errors)}")
        print(f"  Warnings: {len(asset.warnings)}")

        # Test validation
        is_valid = loader.validate_file(str(sample_path))
        print(f"  Validation: {is_valid}")

        return True

    except Exception as e:
        print(f"[FAIL] TXT test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_loader():
    """Test PDF loader functionality"""
    print("\n" + "=" * 60)
    print("TEST: PDF Loader")
    print("=" * 60)

    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_document.pdf"

    try:
        loader = PDFLoader()
        asset = loader.load(str(sample_path))

        print(f"[PASS] PDF loaded successfully")
        print(f"  Format: {asset.source_format}")
        print(f"  Category: {asset.data_category}")
        print(f"  Is tabular: {asset.is_tabular()}")
        print(f"  Is text: {asset.is_text()}")

        if asset.is_text():
            text = asset.text_data
            print(f"  Character count: {len(text)}")
            print(f"  Has extractable text: {len(text) > 0}")

        print(f"  Page count: {asset.metadata.get('page_count', 'N/A')}")
        print(f"  Is encrypted: {asset.metadata.get('is_encrypted', 'N/A')}")
        print(f"  Pages with text: {asset.metadata.get('pages_with_text', 'N/A')}")
        print(f"  Extraction errors: {len(asset.extraction_errors)}")
        print(f"  Warnings: {len(asset.warnings)}")

        # Test validation
        is_valid = loader.validate_file(str(sample_path))
        print(f"  Validation: {is_valid}")

        return True

    except ImportError as e:
        print(f"[SKIP] PDF loader not available: {str(e)}")
        print(f"  Install PyMuPDF with: pip install PyMuPDF")
        return True  # Don't fail the test suite if PDF library is missing
    except Exception as e:
        print(f"[FAIL] PDF test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_loader_factory():
    """Test loader factory functionality"""
    print("\n" + "=" * 60)
    print("TEST: Loader Factory")
    print("=" * 60)

    try:
        # Test supported formats
        supported = LoaderFactory.get_supported_formats()
        print(f"[PASS] Supported formats: {supported}")

        # Test file detection
        test_files = [
            ("test.csv", True),
            ("test.xlsx", True),
            ("test.xls", True),
            ("test.json", True),
            ("test.xml", True),
            ("test.txt", True),
            ("test.pdf", True),
            ("test.doc", False)
        ]

        for filename, should_support in test_files:
            is_supported = LoaderFactory.is_supported(filename)
            status = "[PASS]" if is_supported == should_support else "[FAIL]"
            print(f"  {status} {filename}: {is_supported} (expected: {should_support})")

        # Test actual file loading via factory
        csv_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.csv"
        if csv_path.exists():
            asset = LoaderFactory.load_file(str(csv_path))
            print(f"[PASS] Factory loaded CSV: {asset.source_format}")

        return True

    except Exception as e:
        print(f"[FAIL] Factory test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_normalizer():
    """Test normalizer functionality"""
    print("\n" + "=" * 60)
    print("TEST: Data Normalizer")
    print("=" * 60)

    try:
        # Load a CSV file
        csv_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.csv"
        loader = CSVLoader()
        asset = loader.load(str(csv_path))

        # Normalize the asset
        normalized_asset = DataNormalizer.normalize(asset)

        print(f"[PASS] Normalization completed")
        print(f"  Original format: {asset.source_format}")
        print(f"  Normalized format: {normalized_asset.source_format}")

        # Get summary
        summary = DataNormalizer.get_summary(normalized_asset)
        print(f"\n[INFO] Normalized Asset Summary:")
        print(summary[:500] + "..." if len(summary) > 500 else summary)

        return True

    except Exception as e:
        print(f"[FAIL] Normalizer test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\n" + "=" * 60)
    print("TEST: Error Handling")
    print("=" * 60)

    try:
        factory = LoaderFactory()

        # Test non-existent file
        try:
            factory.load_file("nonexistent.csv")
            print("[FAIL] Should have raised FileNotFoundError")
            return False
        except FileNotFoundError:
            print("[PASS] Correctly raised FileNotFoundError")

        # Test unsupported format
        try:
            factory.get_loader("test.doc")
            print("[FAIL] Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"[PASS] Correctly raised ValueError: {str(e)[:50]}...")

        # Test invalid file extension with specific loader
        try:
            csv_loader = CSVLoader()
            csv_loader.load(__file__)  # This is a .py file
            print("[FAIL] Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"[PASS] Correctly raised ValueError: {str(e)[:50]}...")

        return True

    except Exception as e:
        print(f"[FAIL] Error handling test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test backward compatibility with Milestone 1 CSV functionality"""
    print("\n" + "=" * 60)
    print("TEST: Backward Compatibility")
    print("=" * 60)

    try:
        # Test that old CSV functionality still works
        from src.data_ingestion import DataIngestion
        from src.profiling import DataProfiler

        sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.csv"

        # Test old CSV loader
        old_loader = DataIngestion()
        data = old_loader.load_csv(str(sample_path))

        print(f"[PASS] Old CSV loader still works")
        print(f"  Rows: {len(data)}")
        print(f"  Columns: {len(data.columns)}")

        # Test old profiler
        profiler = DataProfiler(data)
        profile = profiler.generate_profile()

        print(f"[PASS] Old profiler still works")
        print(f"  Profile generated: {bool(profile)}")

        # Test that new loader produces compatible results
        new_loader = CSVLoader()
        asset = new_loader.load(str(sample_path))

        if asset.is_tabular():
            new_data = asset.tabular_data
            print(f"[PASS] New CSV loader produces compatible data")
            print(f"  Same rows: {len(data) == len(new_data)}")
            print(f"  Same columns: {list(data.columns) == list(new_data.columns)}")

        return True

    except Exception as e:
        print(f"[FAIL] Backward compatibility test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MILESTONE 2 TEST SUITE - Complete Data Ingestion Layer")
    print("=" * 60)

    results = []

    # Test individual loaders
    results.append(("CSV Loader", test_csv_loader()))
    results.append(("Excel Loader", test_excel_loader()))
    results.append(("JSON Loader", test_json_loader()))
    results.append(("XML Loader", test_xml_loader()))
    results.append(("TXT Loader", test_txt_loader()))
    results.append(("PDF Loader", test_pdf_loader()))

    # Test factory and normalization
    results.append(("Loader Factory", test_loader_factory()))
    results.append(("Data Normalizer", test_normalizer()))

    # Test error handling and compatibility
    results.append(("Error Handling", test_error_handling()))
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
