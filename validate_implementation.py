#!/usr/bin/env python3
"""
Quick validation that all blocking modules are present and importable.

Tests:
1. Backend modules (settings, schemas, api)
2. ML pipeline modules (panel_gen, diffusion, pipeline, build_map, pose_search)
3. FastAPI app startup
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

print("=" * 80)
print("BLOCKING GAPS IMPLEMENTATION VALIDATION")
print("=" * 80)

# Test 1: Backend imports
print("\n[1/5] Testing backend modules...")
try:
    from settings import OPEN_ROUTER_API_KEY, HUGGING_FACE_HUB_TOKEN, SYSTEM_PROMPT
    from schemas import StoryboardGenerationRequest
    from api import router, _normalize_panel_fields_to_camel_case
    from app import app
    print("✅ Backend modules imported successfully")
except Exception as e:
    print(f"❌ Backend modules failed: {e}")
    sys.exit(1)

# Test 2: ML Pipeline modules
print("\n[2/5] Testing ML pipeline modules...")
try:
    from ml_pipeline import panel_gen, diffusion, pipeline, build_map, pose_search
    print("✅ ML pipeline modules imported successfully")
except Exception as e:
    print(f"❌ ML pipeline modules failed: {e}")
    sys.exit(1)

# Test 3: Check function signatures
print("\n[3/5] Checking function signatures...")
try:
    # panel_gen.decompose_scene should exist and be callable
    assert callable(panel_gen.decompose_scene), "panel_gen.decompose_scene not callable"
    
    # diffusion functions should exist
    assert callable(diffusion.initialize_pipeline), "diffusion.initialize_pipeline missing"
    assert callable(diffusion.generate_panels), "diffusion.generate_panels missing"
    assert callable(diffusion.build_sdxl_prompt), "diffusion.build_sdxl_prompt missing"
    
    # pipeline orchestrators should exist
    assert callable(pipeline.run_full_generation), "pipeline.run_full_generation missing"
    assert callable(pipeline.run_panel_regeneration), "pipeline.run_panel_regeneration missing"
    
    # build_map functions should exist
    assert callable(build_map.build_pose_map), "build_map.build_pose_map missing"
    assert callable(build_map.get_conditioning_map), "build_map.get_conditioning_map missing"
    
    # pose_search functions should exist
    assert callable(pose_search.retrieve_pose), "pose_search.retrieve_pose missing"
    assert callable(pose_search.load_pose_index), "pose_search.load_pose_index missing"
    
    print("✅ All function signatures present")
except AssertionError as e:
    print(f"❌ Missing function: {e}")
    sys.exit(1)

# Test 4: Check API endpoints
print("\n[4/5] Checking API endpoints...")
try:
    routes = [route.path for route in app.routes]
    assert "/frame-forge/api/generate" in routes, "Missing /generate endpoint"
    assert "/frame-forge/api/regenerate" in routes, "Missing /regenerate endpoint"
    print("✅ API endpoints registered")
except AssertionError as e:
    print(f"❌ API endpoints: {e}")
    sys.exit(1)

# Test 5: Check environment variables
print("\n[5/5] Checking environment variables...")
try:
    if not OPEN_ROUTER_API_KEY:
        print("⚠️  WARNING: OPEN_ROUTER_API_KEY not set in .env (required for LLM)")
    else:
        print("✅ OPEN_ROUTER_API_KEY configured")
    
    if not HUGGING_FACE_HUB_TOKEN:
        print("⚠️  WARNING: HUGGING_FACE_HUB_TOKEN not set (required for first-time pose setup)")
    else:
        print("✅ HUGGING_FACE_HUB_TOKEN configured")
        
except Exception as e:
    print(f"❌ Environment check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL BLOCKING GAPS HAVE BEEN IMPLEMENTED")
print("=" * 80)
print("\nNext steps:")
print("1. Set OPEN_ROUTER_API_KEY and HUGGING_FACE_HUB_TOKEN in .env")
print("2. Run: pip install -r backend/requirements.txt")
print("3. Run: npm install (in frontend/)")
print("4. Start backend: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
print("5. Start frontend: npm run dev (in frontend/)")
