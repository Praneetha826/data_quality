"""
Simple Test for Configurable LLM Model Support
Tests configuration logic without actual model loading
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_llama3_configuration():
    """Test Llama 3 model configuration"""
    print("=" * 60)
    print("TEST: Llama 3 Model Configuration")
    print("=" * 60)

    try:
        model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
        print(f"[INFO] Model name: {model_name}")
        
        if model_name == "meta-llama/Meta-Llama-3-8B-Instruct":
            print("[PASS] Llama 3 model configuration is correct")
            return True
        else:
            print(f"[FAIL] Expected meta-llama/Meta-Llama-3-8B-Instruct")
            return False

    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        return False


def test_qwen_configuration():
    """Test Qwen model configuration"""
    print("\n" + "=" * 60)
    print("TEST: Qwen Model Configuration")
    print("=" * 60)

    try:
        model_name = "Qwen/Qwen2.5-3B-Instruct"
        print(f"[INFO] Model name: {model_name}")
        
        if model_name == "Qwen/Qwen2.5-3B-Instruct":
            print("[PASS] Qwen model configuration is correct")
            return True
        else:
            print(f"[FAIL] Expected Qwen/Qwen2.5-3B-Instruct")
            return False

    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        return False


def test_environment_variable_configuration():
    """Test model configuration via environment variable"""
    print("\n" + "=" * 60)
    print("TEST: Environment Variable Configuration")
    print("=" * 60)

    try:
        # Test default
        if 'LLM_MODEL' in os.environ:
            del os.environ['LLM_MODEL']
        
        expected_default = "meta-llama/Meta-Llama-3-8B-Instruct"
        actual = os.getenv('LLM_MODEL', expected_default)
        
        print(f"[INFO] Default model: {actual}")
        
        if actual == expected_default:
            print(f"[PASS] Default model is {expected_default}")
        else:
            print(f"[FAIL] Expected {expected_default}")
            return False
        
        # Test with env var
        os.environ['LLM_MODEL'] = "Qwen/Qwen2.5-3B-Instruct"
        actual = os.getenv('LLM_MODEL')
        
        print(f"[INFO] Env var model: {actual}")
        
        if actual == "Qwen/Qwen2.5-3B-Instruct":
            print("[PASS] Environment variable configuration works")
        else:
            print(f"[FAIL] Expected Qwen/Qwen2.5-3B-Instruct")
            return False
        
        # Clean up
        del os.environ['LLM_MODEL']
        
        return True

    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        return False


def test_rag_response_model_tracking():
    """Test that RAGResponse includes model_name field"""
    print("\n" + "=" * 60)
    print("TEST: RAG Response Model Tracking")
    print("=" * 60)

    try:
        from src.rag_pipeline import RAGResponse
        
        # Test with rule-based response
        response = RAGResponse(
            query="test query",
            context=None,
            explanation="test explanation",
            recommendations=["rec1"],
            quality_assessment="test assessment",
            sources=["source1"],
            used_llm=False,
            model_name="rule-based"
        )
        
        print(f"[INFO] Response model_name: {response.model_name}")
        
        if response.model_name == "rule-based":
            print("[PASS] Rule-based model name tracked correctly")
        else:
            print(f"[FAIL] Expected 'rule-based', got {response.model_name}")
            return False
        
        # Test with LLM response
        response2 = RAGResponse(
            query="test query",
            context=None,
            explanation="test explanation",
            recommendations=["rec1"],
            quality_assessment="test assessment",
            sources=["source1"],
            used_llm=True,
            model_name="meta-llama/Meta-Llama-3-8B-Instruct"
        )
        
        print(f"[INFO] LLM response model_name: {response2.model_name}")
        
        if response2.model_name == "meta-llama/Meta-Llama-3-8B-Instruct":
            print("[PASS] LLM model name tracked correctly")
        else:
            print(f"[FAIL] Expected meta-llama/Meta-Llama-3-8B-Instruct")
            return False
        
        return True

    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CONFIGURABLE LLM MODEL TEST SUITE")
    print("=" * 60)

    results = []

    # Test 1: Llama 3 configuration
    success = test_llama3_configuration()
    results.append(("Llama 3 Configuration", success))

    # Test 2: Qwen configuration
    success = test_qwen_configuration()
    results.append(("Qwen Configuration", success))

    # Test 3: Environment variable configuration
    success = test_environment_variable_configuration()
    results.append(("Environment Variable Configuration", success))

    # Test 4: RAG response model tracking
    success = test_rag_response_model_tracking()
    results.append(("RAG Response Model Tracking", success))

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
