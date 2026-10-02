"""
Test Script for Milestone 1
Tests data ingestion and profiling functionality
"""

import sys
import os
from pathlib import Path

# Set console encoding to UTF-8 for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import DataIngestion
from src.profiling import DataProfiler


def test_data_ingestion():
    """Test data ingestion with sample CSV"""
    print("=" * 60)
    print("TEST: Data Ingestion")
    print("=" * 60)

    # Test with valid CSV
    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.csv"

    try:
        ingester = DataIngestion()
        data = ingester.load_csv(str(sample_path))

        print(f"[PASS] Successfully loaded CSV file")
        print(f"  File: {sample_path}")
        print(f"  Rows: {len(data)}")
        print(f"  Columns: {len(data.columns)}")
        print(f"  Column names: {list(data.columns)}")

        # Get file info
        file_info = ingester.get_file_info()
        print(f"\n[PASS] File info retrieved:")
        print(f"  File size: {file_info['file_size_mb']:.2f} MB")

        return True, data

    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        return False, None


def test_profiling():
    """Test data profiling"""
    print("\n" + "=" * 60)
    print("TEST: Data Profiling")
    print("=" * 60)

    try:
        # Load sample data for profiling test
        sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_dataset.csv"
        ingester = DataIngestion()
        data = ingester.load_csv(str(sample_path))

        profiler = DataProfiler(data)
        profile = profiler.generate_profile()

        print(f"[PASS] Profile generated successfully")

        # Verify basic info
        basic = profile['basic_info']
        print(f"\n[PASS] Basic Info:")
        print(f"  Rows: {basic['num_rows']}")
        print(f"  Columns: {basic['num_columns']}")
        print(f"  Memory: {basic['memory_usage_mb']:.2f} MB")

        # Verify data types
        print(f"\n[PASS] Data Types:")
        for col, dtype in profile['data_types'].items():
            print(f"  {col}: {dtype}")

        # Verify missing values
        print(f"\n[PASS] Missing Values:")
        missing = profile['missing_values']
        total_missing = sum(missing.values())
        print(f"  Total missing: {total_missing}")
        for col, count in missing.items():
            if count > 0:
                print(f"  {col}: {count}")

        # Verify numerical stats
        print(f"\n[PASS] Numerical Statistics:")
        for col, stats in profile['numerical_stats'].items():
            print(f"  {col}:")
            print(f"    Mean: {stats['mean']:.2f}")
            print(f"    Min: {stats['min']:.2f}")
            print(f"    Max: {stats['max']:.2f}")

        # Print summary
        print("\n" + profiler.get_profile_summary())

        return True

    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\n" + "=" * 60)
    print("TEST: Error Handling")
    print("=" * 60)

    ingester = DataIngestion()

    # Test non-existent file
    try:
        ingester.load_csv("nonexistent.csv")
        print("✗ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError as e:
        print(f"[PASS] Correctly raised FileNotFoundError: {str(e)}")

    # Test non-CSV file
    try:
        ingester.load_csv(__file__)  # This is a .py file
        print("[FAIL] Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"[PASS] Correctly raised ValueError: {str(e)}")

    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MILESTONE 1 TEST SUITE")
    print("=" * 60)

    results = []

    # Test 1: Data Ingestion
    success, data = test_data_ingestion()
    results.append(("Data Ingestion", success))

    # Test 2: Profiling (now self-contained)
    success = test_profiling()
    results.append(("Data Profiling", success))

    # Test 3: Error Handling
    success = test_error_handling()
    results.append(("Error Handling", success))

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
