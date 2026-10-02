"""
Minimal Gemini API model availability test
Tests current Flash models to find one that works
"""

import os
from dotenv import load_dotenv

# CRITICAL: Remove GOOGLE_API_KEY BEFORE loading .env
# to prevent it from overriding GEMINI_API_KEY
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]
    print("[INFO] Removed GOOGLE_API_KEY from environment before loading .env")

# Load environment variables with override=True
load_dotenv(override=True)

print("=" * 70)
print("GEMINI FLASH MODEL AVAILABILITY TEST")
print("=" * 70)

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"[OK] GEMINI_API_KEY loaded (length={len(api_key)}, prefix={api_key[:10]}...)")
else:
    print("[ERROR] GEMINI_API_KEY NOT loaded")
    exit(1)

# Import SDK
try:
    from google import genai
    print("[OK] google-genai SDK imported")
except ImportError as e:
    print(f"[ERROR] Failed to import google-genai: {e}")
    exit(1)

# Initialize client
try:
    client = genai.Client(api_key=api_key)
    print("[OK] Gemini client initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize client: {e}")
    exit(1)

# Models to test
models_to_test = [
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-2.5-flash-lite"
]

print("\n" + "=" * 70)
print("TESTING MODELS")
print("=" * 70)

successful_model = None

for model in models_to_test:
    print(f"\n[TEST] Model: {model}")
    print("-" * 70)
    
    try:
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: OK."
        )
        
        print(f"[SUCCESS] Model {model} is available")
        print(f"Response: {response.text[:100]}...")
        successful_model = model
        break
        
    except Exception as e:
        error_str = str(e)
        if "403" in error_str:
            print(f"[FAILED] HTTP Status: 403 PERMISSION_DENIED")
            print(f"Error: Key reported as leaked or permission denied")
        elif "404" in error_str:
            print(f"[FAILED] HTTP Status: 404 NOT_FOUND")
            print(f"Error: Model not found or not available")
        elif "429" in error_str:
            print(f"[FAILED] HTTP Status: 429 RESOURCE_EXHAUSTED")
            print(f"Error: Quota exceeded")
        elif "503" in error_str:
            print(f"[FAILED] HTTP Status: 503 UNAVAILABLE")
            print(f"Error: Model experiencing high demand")
        else:
            print(f"[FAILED] HTTP Status: Unknown")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)[:200]}...")

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

if successful_model:
    print(f"[SUCCESS] Working model found: {successful_model}")
    print(f"\nTo use this model, update .env:")
    print(f"LLM_PROVIDER=gemini")
    print(f"GEMINI_MODEL={successful_model}")
else:
    print("[FAILED] No working Flash model found")
    print("\nAll tested models failed. Possible causes:")
    print("1. Free tier quota exhausted")
    print("2. Account/project restrictions")
    print("3. All models experiencing high demand")
    print("4. Billing required for newer models")

print("=" * 70)
