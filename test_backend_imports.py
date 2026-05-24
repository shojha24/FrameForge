#!/usr/bin/env python3
"""
Test that all backend imports resolve correctly.
"""

import sys
import os

# Add project root to path (same as main.py does)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing backend imports...")
print(f"Python path includes: {os.path.dirname(os.path.abspath(__file__))}")

try:
    print("\n1. Importing settings...")
    from backend.settings import PROJECT_NAME, OPEN_ROUTER_API_KEY, HUGGING_FACE_HUB_TOKEN
    print("   ✅ settings imported")
    print(f"   ✅ PROJECT_NAME: {PROJECT_NAME}")
    print(f"   ✅ API Key available: {bool(OPEN_ROUTER_API_KEY)}")
    print(f"   ✅ HF Token available: {bool(HUGGING_FACE_HUB_TOKEN)}")
except Exception as e:
    print(f"   ❌ settings import failed: {e}")
    sys.exit(1)

try:
    print("\n2. Importing ml_pipeline.diffusion...")
    from ml_pipeline import diffusion
    print("   ✅ diffusion module imported")
except Exception as e:
    print(f"   ❌ diffusion import failed: {e}")
    sys.exit(1)

try:
    print("\n3. Importing ml_pipeline.pipeline...")
    from ml_pipeline import pipeline
    print("   ✅ pipeline module imported")
except Exception as e:
    print(f"   ❌ pipeline import failed: {e}")
    sys.exit(1)

try:
    print("\n4. Importing backend.api...")
    from backend import api
    print("   ✅ api module imported")
except Exception as e:
    print(f"   ❌ api import failed: {e}")
    sys.exit(1)

try:
    print("\n5. Importing backend.app...")
    from backend import app as app_module
    print("   ✅ app module imported")
except Exception as e:
    print(f"   ❌ app import failed: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("✅ All backend imports successful!")
print("="*80)
print("\nYou can now run: python backend/main.py")
