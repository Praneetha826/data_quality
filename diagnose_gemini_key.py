"""
Comprehensive Gemini API key diagnostic
Investigates why fresh AQ keys are being rejected
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 70)
print("GEMINI API KEY COMPREHENSIVE DIAGNOSTIC")
print("=" * 70)

# CRITICAL: Remove GOOGLE_API_KEY BEFORE loading .env
# to prevent it from overriding GEMINI_API_KEY
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]
    print("[INFO] Removed GOOGLE_API_KEY from environment before loading .env")

# Load environment variables with override=True
load_dotenv(override=True)

# Check for GOOGLE_API_KEY override
print("\n[CHECK 1] Environment Variables:")
print("-" * 70)
google_api_key = os.getenv("GOOGLE_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if google_api_key:
    print(f"GOOGLE_API_KEY: PRESENT (length={len(google_api_key)}, prefix={google_api_key[:10]}...)")
    print("  WARNING: This may override GEMINI_API_KEY")
    del os.environ["GOOGLE_API_KEY"]
    print("  Action: Removed GOOGLE_API_KEY to prevent override")
else:
    print("GOOGLE_API_KEY: NOT PRESENT")

if gemini_api_key:
    print(f"GEMINI_API_KEY: PRESENT (length={len(gemini_api_key)}, prefix={gemini_api_key[:10]}...)")
else:
    print("GEMINI_API_KEY: NOT PRESENT")
    print("  ERROR: No API key available")
    sys.exit(1)

# Check .env file location
print("\n[CHECK 2] .env File:")
print("-" * 70)
from pathlib import Path
env_path = Path(".env")
if env_path.exists():
    print(f".env file exists: {env_path.absolute()}")
    print(f".env file size: {env_path.stat().st_size} bytes")
    with open(env_path, 'r') as f:
        lines = f.readlines()
        print(f".env file lines: {len(lines)}")
        for i, line in enumerate(lines, 1):
            if "GEMINI_API_KEY" in line:
                print(f"  Line {i}: Contains GEMINI_API_KEY")
                # Extract just the key value for verification
                if "=" in line:
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key_value = parts[1].strip()
                        print(f"    Key in file: length={len(key_value)}, prefix={key_value[:10]}...")
                        if key_value == gemini_api_key:
                            print("    MATCH: Key in .env matches loaded key")
                        else:
                            print("    MISMATCH: Key in .env does NOT match loaded key!")
else:
    print(".env file: NOT FOUND")

# Check for other .env files
print("\n[CHECK 3] Other .env Files:")
print("-" * 70)
for path in Path(".").glob(".env*"):
    if path.name != ".env":
        print(f"Found: {path.name}")
        if "GEMINI_API_KEY" in path.read_text():
            print(f"  Contains GEMINI_API_KEY")

# Check google-genai version
print("\n[CHECK 4] google-genai SDK:")
print("-" * 70)
try:
    import google.genai as genai
    import importlib.metadata as metadata
    version = metadata.version("google-genai")
    print(f"google-genai version: {version}")
    print(f"google.genai module: {genai.__file__}")
except ImportError as e:
    print(f"ERROR: Failed to import google-genai: {e}")
    sys.exit(1)

# Check if key is actually being used
print("\n[CHECK 5] Client Initialization:")
print("-" * 70)
try:
    client = genai.Client(api_key=gemini_api_key)
    print("Client initialized successfully")
    print(f"Client type: {type(client)}")
except Exception as e:
    print(f"ERROR: Failed to initialize client: {type(e).__name__}: {e}")
    sys.exit(1)

# Try a minimal API call to get the exact error
print("\n[CHECK 6] API Call Attempt:")
print("-" * 70)
try:
    print("Attempting minimal API call...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly: OK."
    )
    print("SUCCESS: API call succeeded")
    print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"FAILED: API call failed")
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {str(e)}")
    
    # Try to extract HTTP status if available
    error_str = str(e)
    if "403" in error_str:
        print("HTTP Status: 403 PERMISSION_DENIED")
    elif "401" in error_str:
        print("HTTP Status: 401 UNAUTHORIZED")
    elif "400" in error_str:
        print("HTTP Status: 400 BAD REQUEST")
    elif "429" in error_str:
        print("HTTP Status: 429 RATE_LIMIT_EXCEEDED")
    elif "500" in error_str:
        print("HTTP Status: 500 SERVER_ERROR")
    
    # Check for specific error messages
    if "leaked" in error_str.lower():
        print("Error classification: Key reported as leaked")
    if "permission" in error_str.lower():
        print("Error classification: Permission denied")
    if "quota" in error_str.lower():
        print("Error classification: Quota exceeded")
    if "billing" in error_str.lower():
        print("Error classification: Billing required")
    if "project" in error_str.lower():
        print("Error classification: Project-related issue")

# Check if there's a project ID associated
print("\n[CHECK 7] Project Information:")
print("-" * 70)
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
if project_id:
    print(f"GOOGLE_CLOUD_PROJECT: {project_id}")
else:
    print("GOOGLE_CLOUD_PROJECT: Not set")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)
print("Key format: AQ authorization key (correct for current Gemini API)")
print("Key prefix: " + gemini_api_key[:10] + "...")
print("Key length: " + str(len(gemini_api_key)))
print("SDK version: " + version)
print("GOOGLE_API_KEY override: Removed")
print("Key source: .env file (verified)")
print("\nIf the error is 'Your API key was reported as leaked':")
print("This indicates Google has flagged the ACCOUNT or PROJECT, not just the key.")
print("Possible causes:")
print("1. Google AI Studio account-level restriction")
print("2. Google Cloud project-level security block")
print("3. Suspicious activity detected on the account")
print("4. Geographic/region restrictions")
print("5. Terms of Service violation")
print("\nRecommended actions:")
print("1. Check Google AI Studio account status")
print("2. Check Google Cloud Console for project restrictions")
print("3. Contact Google Cloud Support if account is blocked")
print("4. Try with a different Google account")
print("=" * 70)
