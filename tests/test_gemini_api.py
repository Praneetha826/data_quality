"""
Tests for Gemini API integration
"""

import os
import pytest
from src.llm_client import LLMClient


def test_gemini_provider_configuration():
    """Test Gemini provider configuration"""
    # Save original env vars
    original_provider = os.getenv("LLM_PROVIDER")
    original_api_key = os.getenv("GEMINI_API_KEY")
    original_model = os.getenv("GEMINI_MODEL")
    
    try:
        # Test with missing API key
        os.environ["LLM_PROVIDER"] = "gemini"
        os.environ["GEMINI_API_KEY"] = ""
        
        client = LLMClient()
        model_info = client.get_model_info()
        
        assert model_info["provider"] == "gemini"
        assert model_info["available"] == False
        # genai_client should be None when API key is missing
        assert model_info["genai_client"] == None or model_info["genai_client"] == False
        
    finally:
        # Restore original env vars
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider
        else:
            os.environ.pop("LLM_PROVIDER", None)
        if original_api_key:
            os.environ["GEMINI_API_KEY"] = original_api_key
        else:
            os.environ.pop("GEMINI_API_KEY", None)
        if original_model:
            os.environ["GEMINI_MODEL"] = original_model
        else:
            os.environ.pop("GEMINI_MODEL", None)


def test_gemini_with_valid_api_key():
    """Test Gemini client with valid API key configuration"""
    # Save original env vars
    original_provider = os.getenv("LLM_PROVIDER")
    original_api_key = os.getenv("GEMINI_API_KEY")
    original_model = os.getenv("GEMINI_MODEL")
    
    try:
        # Test with API key (but we won't actually call the API in test)
        os.environ["LLM_PROVIDER"] = "gemini"
        os.environ["GEMINI_API_KEY"] = "test_key_12345"
        os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"
        
        client = LLMClient()
        model_info = client.get_model_info()
        
        assert model_info["provider"] == "gemini"
        assert model_info["configured_provider"] == "gemini"
        assert model_info["configured_model"] == "gemini-1.5-flash"
        
    finally:
        # Restore original env vars
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider
        else:
            os.environ.pop("LLM_PROVIDER", None)
        if original_api_key:
            os.environ["GEMINI_API_KEY"] = original_api_key
        else:
            os.environ.pop("GEMINI_API_KEY", None)
        if original_model:
            os.environ["GEMINI_MODEL"] = original_model
        else:
            os.environ.pop("GEMINI_MODEL", None)


def test_local_provider_still_works():
    """Test that local provider still works for Llama 3/Qwen"""
    # Save original env vars
    original_provider = os.getenv("LLM_PROVIDER")
    original_model = os.getenv("LLM_MODEL")
    
    try:
        # Test with local provider
        os.environ["LLM_PROVIDER"] = "local"
        os.environ["LLM_MODEL"] = "meta-llama/Meta-Llama-3-8B-Instruct"
        
        client = LLMClient()
        model_info = client.get_model_info()
        
        assert model_info["provider"] == "local"
        assert model_info["configured_provider"] == "local"
        assert model_info["configured_model"] == "meta-llama/Meta-Llama-3-8B-Instruct"
        
    finally:
        # Restore original env vars
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider
        else:
            os.environ.pop("LLM_PROVIDER", None)
        if original_model:
            os.environ["LLM_MODEL"] = original_model
        else:
            os.environ.pop("LLM_MODEL", None)


def test_gemini_generate_without_api_key():
    """Test that Gemini generate fails gracefully without API key"""
    # Save original env vars
    original_provider = os.getenv("LLM_PROVIDER")
    original_api_key = os.getenv("GEMINI_API_KEY")
    
    try:
        os.environ["LLM_PROVIDER"] = "gemini"
        os.environ["GEMINI_API_KEY"] = ""
        
        client = LLMClient()
        
        # Should raise RuntimeError when trying to generate
        with pytest.raises(RuntimeError):
            client.generate("test prompt")
        
    finally:
        # Restore original env vars
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider
        else:
            os.environ.pop("LLM_PROVIDER", None)
        if original_api_key:
            os.environ["GEMINI_API_KEY"] = original_api_key
        else:
            os.environ.pop("GEMINI_API_KEY", None)


def test_provider_tracking():
    """Test that provider is correctly tracked in model info"""
    # Save original env vars
    original_provider = os.getenv("LLM_PROVIDER")
    
    try:
        # Test Gemini
        os.environ["LLM_PROVIDER"] = "gemini"
        client_gemini = LLMClient()
        info_gemini = client_gemini.get_model_info()
        assert info_gemini["provider"] == "gemini"
        
        # Test local
        os.environ["LLM_PROVIDER"] = "local"
        client_local = LLMClient()
        info_local = client_local.get_model_info()
        assert info_local["provider"] == "local"
        
    finally:
        # Restore original env vars
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider
        else:
            os.environ.pop("LLM_PROVIDER", None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
