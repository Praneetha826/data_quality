"""
LLM Client Module
Handles LLM integration for RAG pipeline
Supports: local models (Llama 3, Qwen) and cloud APIs (Gemini)
"""

from typing import Optional, Dict, Any
import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class LLMClient:
    """
    Client for LLM integration (configurable model and provider support)
    Supports:
    - Local models: meta-llama/Meta-Llama-3-8B-Instruct, Qwen/Qwen2.5-3B-Instruct
    - Cloud APIs: Gemini API
    """

    def __init__(self, model_name: Optional[str] = None, device: str = "cpu"):
        """
        Initialize the LLM client

        Args:
            model_name: Name of the model to use (reads from LLM_MODEL env var if None)
            device: Device to run inference on ('cpu' or 'cuda') - only for local models
        """
        # Read provider from environment variable
        self.provider = os.getenv("LLM_PROVIDER", "local").lower()
        
        # Read model name from environment variable if not provided
        if model_name is None:
            if self.provider == "gemini":
                model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
            else:
                model_name = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")

        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.genai_client = None
        self.inference_time = 0.0
        
        # Load based on provider
        if self.provider == "gemini":
            self._load_gemini()
        else:
            self._load_local_model()

    def _load_gemini(self):
        """Load Gemini API client"""
        try:
            # Explicitly use GEMINI_API_KEY, avoid GOOGLE_API_KEY override
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("GEMINI_API_KEY not found in environment variables")
                print("Will use rule-based fallback")
                self.genai_client = None
                return

            if not GENAI_AVAILABLE:
                print("google-genai package not installed")
                print("Install with: pip install google-genai")
                print("Will use rule-based fallback")
                self.genai_client = None
                return

            # Initialize the new Google GenAI client
            # Explicitly pass api_key to avoid GOOGLE_API_KEY override
            self.genai_client = genai.Client(api_key=api_key)
            
            # Get Gemini model from environment or use default
            gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
            
            print(f"Gemini API connected: {gemini_model}")

        except Exception as e:
            print(f"Error loading Gemini API: {e}")
            print("Will use rule-based fallback")
            self.genai_client = None

    def _load_local_model(self):
        """Load local Hugging Face model"""
        try:
            print(f"Loading local LLM model: {self.model_name}")
            print("This may take several minutes on CPU...")

            # Check for Hugging Face token
            hf_token = os.getenv("HF_TOKEN")
            if hf_token:
                print("Using Hugging Face authentication token")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                token=hf_token if hf_token else None
            )

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                token=hf_token if hf_token else None
            )

            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id
            )

            print(f"Model loaded successfully: {self.model_name}")

        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            print("Will use rule-based fallback")
            self.model = None
            self.pipeline = None

    def generate(self, prompt: str) -> str:
        """
        Generate response from LLM

        Args:
            prompt: Input prompt

        Returns:
            Generated response text
        """
        start_time = time.time()
        
        try:
            if self.provider == "gemini":
                response = self._generate_gemini(prompt)
            else:
                response = self._generate_local(prompt)
            
            self.inference_time = time.time() - start_time
            return response

        except Exception as e:
            print(f"Error generating response: {e}")
            raise RuntimeError(f"LLM generation failed: {e}")

    def _generate_gemini(self, prompt: str) -> str:
        """Generate response using Gemini API"""
        debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
        if debug_mode:
            print(f"DEBUG GEMINI: generation started")
            print(f"DEBUG GEMINI CONFIG:")
            print(f"DEBUG GEMINI CONFIG: provider={self.provider}")
            print(f"DEBUG GEMINI CONFIG: model={self.model_name}")
            print(f"DEBUG GEMINI CONFIG: api_key_configured={bool(os.getenv('GEMINI_API_KEY'))}")
            print(f"DEBUG GEMINI CONFIG: sdk=google-genai")
            print(f"DEBUG GEMINI: client type={type(self.genai_client)}")
            print(f"DEBUG GEMINI: prompt length={len(prompt)}")
        
        if self.genai_client is None:
            if debug_mode:
                print("DEBUG GEMINI ERROR TYPE: RuntimeError")
                print("DEBUG GEMINI ERROR MESSAGE: Gemini API client not loaded")
                print("DEBUG GEMINI ERROR REPR: RuntimeError('Gemini API client not loaded')")
            raise RuntimeError("Gemini API client not loaded")

        try:
            # Get Gemini model from environment or use default
            gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
            if debug_mode:
                print(f"DEBUG GEMINI: using model={gemini_model}")
            
            # Generate content using the new API
            if debug_mode:
                print(f"DEBUG GEMINI: calling generate_content...")
            response = self.genai_client.models.generate_content(
                model=gemini_model,
                contents=prompt
            )
            if debug_mode:
                print(f"DEBUG GEMINI: generation succeeded")
                print(f"DEBUG GEMINI: response type={type(response)}")
                print(f"DEBUG GEMINI: response text length={len(response.text) if hasattr(response, 'text') else 'N/A'}")
            
            return response.text
        except Exception as e:
            if debug_mode:
                print(f"DEBUG GEMINI ERROR TYPE: {type(e).__name__}")
                print(f"DEBUG GEMINI ERROR MESSAGE: {str(e)}")
                print(f"DEBUG GEMINI ERROR REPR: {repr(e)}")
                print(f"DEBUG GEMINI ERROR: falling back to rule-based")
            raise RuntimeError(f"Gemini API generation failed: {e}")

    def _generate_local(self, prompt: str) -> str:
        """Generate response using local model"""
        if self.pipeline is None:
            raise RuntimeError("Local LLM model not loaded")

        try:
            # Generate response
            outputs = self.pipeline(
                prompt,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )

            # Extract generated text
            generated_text = outputs[0]['generated_text']

            # Remove the prompt from the response
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()

            return generated_text

        except Exception as e:
            print(f"Error generating response: {e}")
            raise RuntimeError(f"Local LLM generation failed: {e}")

    def is_available(self) -> bool:
        """
        Check if LLM is available

        Returns:
            True if LLM is loaded and available
        """
        if self.provider == "gemini":
            return self.genai_client is not None
        else:
            return self.model is not None and self.pipeline is not None

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model

        Returns:
            Dictionary with model information
        """
        if self.provider == "gemini":
            configured_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        else:
            configured_model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
        
        return {
            "model_name": self.model_name,
            "provider": self.provider,
            "device": self.device,
            "available": self.is_available(),
            "tokenizer": self.tokenizer is not None,
            "model_loaded": self.model is not None,
            "pipeline_loaded": self.pipeline is not None,
            "genai_client": self.genai_client is not None,
            "inference_time": self.inference_time,
            "configured_model": configured_model,
            "configured_provider": os.getenv("LLM_PROVIDER", "local")
        }
