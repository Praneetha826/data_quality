"""
Minimal Gemini API connectivity test
Independent of FAISS, embeddings, database, Streamlit, and RAG pipeline
"""

import os
from dotenv import load_dotenv

# CRITICAL: Remove GOOGLE_API_KEY BEFORE loading .env
# to prevent it from overriding GEMINI_API_KEY
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]
    print("[INFO] Removed GOOGLE_API_KEY from environment to prevent override")

# Load environment variables with override=True
load_dotenv(override=True)

print("=" * 60)
print("MINIMAL GEMINI API CONNECTIVITY TEST")
print("=" * 60)

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"[OK] GEMINI_API_KEY loaded (length={len(api_key)})")
else:
    print("[ERROR] GEMINI_API_KEY NOT loaded")
    print("ERROR: API key is missing from environment")
    exit(1)

# Check model
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
print(f"[OK] GEMINI_MODEL: {model}")

# Import google-genai
try:
    from google import genai
    print("[OK] google-genai SDK imported")
except ImportError as e:
    print(f"[ERROR] Failed to import google-genai: {e}")
    print("Install with: pip install google-genai")
    exit(1)

# Initialize client
try:
    print(f"\nInitializing Gemini client...")
    # Explicitly use GEMINI_API_KEY, not GOOGLE_API_KEY
    client = genai.Client(api_key=api_key)
    print("[OK] Gemini client initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize client: {type(e).__name__}: {e}")
    print(f"Exception repr: {repr(e)}")
    exit(1)

# Test simple generation
try:
    print(f"\nTesting generation with model: {model}")
    print("Prompt: 'Reply with exactly: Gemini connection successful.'")
    
    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: Gemini connection successful."
    )
    
    print(f"[OK] Generation succeeded")
    print(f"Response type: {type(response)}")
    print(f"Response text: {response.text}")
    
    if "Gemini connection successful" in response.text:
        print("\n" + "=" * 60)
        print("[SUCCESS] GEMINI API CONNECTIVITY TEST PASSED")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[WARNING] GEMINI API responded but with unexpected output")
        print("=" * 60)
        
except Exception as e:
    print(f"\n[ERROR] Generation failed")
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {str(e)}")
    print(f"Exception repr: {repr(e)}")
    
    # Check for common issues
    error_str = str(e).lower()
    if "api key" in error_str or "authentication" in error_str:
        print("\n[WARNING] Possible issue: Invalid API key or authentication failure")
    if "quota" in error_str or "billing" in error_str:
        print("\n[WARNING] Possible issue: Quota exceeded or billing required")
    if "model" in error_str:
        print("\n[WARNING] Possible issue: Model not found or not accessible")
    if "permission" in error_str or "access" in error_str:
        print("\n[WARNING] Possible issue: API key lacks permission or access denied")
    
    print("\n" + "=" * 60)
    print("[FAILED] GEMINI API CONNECTIVITY TEST FAILED")
    print("=" * 60)
    exit(1)
