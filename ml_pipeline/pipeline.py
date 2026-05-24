"""
Pipeline Orchestrator.

Coordinates data flow between API (api.py), LLM decomposer (panel_gen.py),
and diffusion engine (diffusion.py).
"""

import base64
import io
import sys
import os
from PIL import Image

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ml_pipeline import panel_gen, diffusion
from backend.settings import HUGGING_FACE_HUB_TOKEN


async def run_full_generation(
    scene_prompt: str,
    num_panels: int,
    visual_style: str,
    ip_image_data: str = None,
    hf_token: str = None
) -> dict:
    """
    Orchestrates end-to-end storyboard generation.
    
    Steps:
    1. Call panel_gen.decompose_scene() to get panel JSON array
    2. Decode base64 character image
    3. Call diffusion.generate_panels() to generate images
    4. Return compiled result
    
    Args:
        scene_prompt (str): Raw scene description
        num_panels (int): Number of panels
        ip_image_data (str, optional): Base64 character reference image
        visual_style (str): Visual style for generation
        hf_token (str, optional): HuggingFace token
    
    Returns:
        dict: Contains panels, generated_images, sdxl_prompts
    """
    print(f"\n{'='*80}")
    print(f"[Pipeline Orchestrator] Full Generation Request")
    print(f"{'='*80}")
    print(f"[Request Summary]")
    print(f"  Scene: {scene_prompt[:100]}{'...' if len(scene_prompt) > 100 else ''}")
    print(f"  Panels: {num_panels}")
    print(f"  Character Reference: {'Yes (provided)' if ip_image_data else 'No'}")
    
    hf_token = hf_token or HUGGING_FACE_HUB_TOKEN
    
    # Step 1: Decompose scene into panels
    try:
        panel_jsons = await panel_gen.decompose_scene(scene_prompt, num_panels, visual_style)
        print(f"\n[Pipeline] ✅ LLM generated {len(panel_jsons)} panels")
        for panel in panel_jsons:
            panel["visual_style"] = visual_style
    except Exception as e:
        print(f"\n[Pipeline] ❌ ERROR: LLM decomposition failed: {e}")
        raise
    
    # Step 2: Decode character reference image if provided
    ip_image = None
    if ip_image_data:
        try:
            # Assume base64 encoded
            img_bytes = base64.b64decode(ip_image_data)
            ip_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            print(f"[Pipeline] ✅ Loaded character reference: {ip_image.size}")
        except Exception as e:
            print(f"[Pipeline] ⚠️  WARNING: Could not decode character image: {e}")
    
    # Step 3: Generate images
    try:
        print(f"\n[Pipeline] Starting image generation for {len(panel_jsons)} panels...")
        generated_images = diffusion.generate_panels(
            panel_jsons,
            ip_adapter_image=ip_image,
            hf_token=hf_token
        )
        print(f"\n[Pipeline] ✅ Generated {len(generated_images)} images")
    except Exception as e:
        print(f"\n[Pipeline] ❌ ERROR: Diffusion failed: {e}")
        raise
    
    # Step 4: Build SDXL prompts for each panel
    print(f"\n[Pipeline] Building SDXL prompts...")
    sdxl_prompts = []
    for idx, panel in enumerate(panel_jsons, 1):
        prompt = diffusion.build_sdxl_prompt(panel)
        sdxl_prompts.append(prompt)
    print(f"[Pipeline] ✅ Built {len(sdxl_prompts)} prompts")
    
    # Step 5: Convert images to base64 for API response
    print(f"\n[Pipeline] Encoding images to base64...")
    generated_images_b64 = []

    # Save to disk for debugging
    debug_dir = os.path.join(project_root, "debug_output")
    os.makedirs(debug_dir, exist_ok=True)

    for idx, img in enumerate(generated_images):
        # Save to disk
        save_path = os.path.join(debug_dir, f"panel_{idx+1}.png")
        img.save(save_path)
        print(f"[Pipeline] 💾 Saved panel {idx+1} to {save_path}")
        
        # Encode to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        generated_images_b64.append(img_base64)

    print(f"[Pipeline] ✅ Encoded {len(generated_images_b64)} images")
    
    print(f"\n{'='*80}")
    print(f"[Pipeline Orchestrator] Generation Complete")
    print(f"{'='*80}\n")
    
    return {
        "panels": panel_jsons,
        "generated_images": generated_images_b64,
        "sdxl_prompts": sdxl_prompts
    }


async def run_panel_regeneration(
    panel_json: dict,
    custom_prompt: str,
    ip_image_data: str = None,
    hf_token: str = None
) -> dict:
    """
    Regenerate a single panel with user-edited metadata.
    
    Steps:
    1. Decode character image if provided
    2. Call diffusion.generate_panels() with single panel (ignoring auto-prompt)
    3. Return new image + original metadata
    
    Args:
        panel_json (dict): Edited panel metadata
        custom_prompt (str): Override prompt for generation
        ip_image_data (str, optional): Base64 character reference
        hf_token (str, optional): HuggingFace token
    
    Returns:
        dict: Contains panel, custom_prompt, generated_image
    """
    print(f"\n{'='*80}")
    print(f"[Pipeline Orchestrator] Panel Regeneration Request")
    print(f"{'='*80}")
    print(f"[Panel Metadata]")
    print(f"  Caption: {panel_json.get('caption', 'N/A')[:60]}")
    print(f"  Shot Type: {panel_json.get('shot_type', 'N/A')}")
    print(f"  Camera Angle: {panel_json.get('camera_angle', 'N/A')}")
    print(f"  Characters: {panel_json.get('characters', [])}")
    print(f"\n[Custom Prompt Override]")
    print(f"  {custom_prompt[:100]}{'...' if len(custom_prompt) > 100 else ''}")
    
    hf_token = hf_token or HUGGING_FACE_HUB_TOKEN
    
    # Decode character image if provided
    ip_image = None
    if ip_image_data:
        try:
            img_bytes = base64.b64decode(ip_image_data)
            ip_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            print(f"\n[Pipeline] ✅ Loaded character reference: {ip_image.size}")
        except Exception as e:
            print(f"\n[Pipeline] ⚠️  WARNING: Could not decode character image: {e}")
    
    # Generate single panel
    try:
        print(f"\n[Pipeline] Regenerating single panel...")
        # Inject custom_prompt into panel_json if provided
        panel_to_generate = panel_json.copy()
        if custom_prompt:
            panel_to_generate["_override_prompt"] = custom_prompt
        
        generated_images = diffusion.generate_panels(
            [panel_to_generate],
            ip_adapter_image=ip_image,
            hf_token=hf_token
        )
        img = generated_images[0]
        print(f"[Pipeline] ✅ Regenerated panel successfully")
    except Exception as e:
        print(f"[Pipeline] ❌ ERROR: Diffusion failed: {e}")
        raise
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    print(f"\n{'='*80}")
    print(f"[Pipeline Orchestrator] Regeneration Complete")
    print(f"{'='*80}\n")
    
    return {
        "panel": panel_json,
        "custom_prompt": custom_prompt,
        "generated_image": img_base64
    }