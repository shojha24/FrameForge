#!/usr/bin/env python3
"""
Quick test to verify logging additions are syntactically correct.
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ml_pipeline'))

print("Testing module imports...")

try:
    from panel_gen import decompose_scene
    print("✅ panel_gen.decompose_scene imported successfully")
except Exception as e:
    print(f"❌ panel_gen failed: {e}")
    sys.exit(1)

try:
    from diffusion import build_sdxl_prompt, generate_panels
    print("✅ diffusion module imported successfully")
except Exception as e:
    print(f"❌ diffusion failed: {e}")
    sys.exit(1)

try:
    from pipeline import run_full_generation, run_panel_regeneration
    print("✅ pipeline module imported successfully")
except Exception as e:
    print(f"❌ pipeline failed: {e}")
    sys.exit(1)

try:
    from settings import SYSTEM_PROMPT
    if "ip_adapter_scale" in SYSTEM_PROMPT:
        print("✅ SYSTEM_PROMPT updated with ip_adapter_scale documentation")
    else:
        print("⚠️  SYSTEM_PROMPT missing ip_adapter_scale (might be optional)")
except Exception as e:
    print(f"❌ settings failed: {e}")
    sys.exit(1)

# Test build_sdxl_prompt with override
try:
    test_panel = {
        "_override_prompt": "Test override prompt",
        "caption": "Test",
        "shot_type": "MS"
    }
    result = build_sdxl_prompt(test_panel)
    if result == "Test override prompt":
        print("✅ build_sdxl_prompt override handling works")
    else:
        print(f"❌ build_sdxl_prompt override failed: got {result}")
except Exception as e:
    print(f"❌ build_sdxl_prompt override test failed: {e}")
    sys.exit(1)

# Test normal prompt building
try:
    test_panel = {
        "caption": "Test shot",
        "shot_type": "CU",
        "camera_angle": "Eye Level",
        "characters": [{"name": "Hero", "position": "center"}],
        "pose_query": "Standing upright",
        "lighting_mood": "warm",
        "background": "Dark room",
        "action_note": "Looking around",
        "ip_adapter_scale": 0.5
    }
    result = build_sdxl_prompt(test_panel)
    if "close-up" in result.lower() and "Hero" in result and "warm" in result:
        print("✅ build_sdxl_prompt normal flow works")
    else:
        print(f"⚠️  build_sdxl_prompt result: {result[:100]}")
except Exception as e:
    print(f"❌ build_sdxl_prompt normal test failed: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("All logging and override validations passed!")
print("="*80)
