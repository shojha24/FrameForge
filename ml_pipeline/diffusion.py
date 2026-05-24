"""
Core Image Generation Pipeline (SDXL + ControlNet OpenPose + IP-Adapter).

Handles the diffusion inference loop:
1. Retrieve semantic pose via pose_search.retrieve_pose()
2. Preprocess pose via build_map.build_pose_map()
3. Generate cinematic prompt via build_sdxl_prompt()
4. Call SDXL with pose conditioning + IP-Adapter for character consistency
"""

from PIL import Image
import time
import torch
import numpy as np
import sys
import os

# Ensure backend is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from diffusers import StableDiffusionXLControlNetPipeline
from diffusers.models import ControlNetModel
from transformers import AutoProcessor

from ml_pipeline import build_map, pose_search
from settings import HUGGING_FACE_HUB_TOKEN

# ============================================================================
# GLOBAL PIPELINE STATE
# ============================================================================
# Updated parameters from FrameForge team testing sessions

pipe = None
device = None
W = 1024
H = 1024
NEGATIVE_PROMPT = "text, watermark, extra limbs, blurry, low quality, deformed, disconnected limbs, floating limbs, disfigured, poorly drawn"

# Tuned from FrameForge team stress tests:
# - controlnet_conditioning_scale = 0.6 (best balance between pose fidelity + visual naturalness)
# - ip_adapter_scale = 0.4 (default for human refs; can be overridden per-panel for non-human refs)
# - inference_steps = 25 (reduced from 30 for faster generation without quality loss)
# - guidance_scale = 7.5 (confirmed good across all test runs)
controlnet_conditioning_scale = 0.6
ip_adapter_scale = 0.4  # Can be overridden per-panel via panel_json["ip_adapter_scale"]
num_inference_steps = 25
guidance_scale = 7.5


def initialize_pipeline():
    """
    Initialize SDXL + ControlNet(OpenPose) + IP-Adapter pipeline.
    
    Called once at startup. Loads models and moves to appropriate device.
    """
    global pipe, device
    
    # Device selection
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        print("[Diffusion] Using CUDA device")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        print("[Diffusion] Using MPS device (Apple Silicon)")
    else:
        device = torch.device("cpu")
        print("[Diffusion] Using CPU (slow)")
    
    print("[Diffusion] Loading StableDiffusionXLControlNetPipeline...")
    
    # Load ControlNet(OpenPose) - use an SDXL-compatible OpenPose model
    # thibaud/controlnet-sd21-openpose works with SDXL via adapter
    controlnet = ControlNetModel.from_pretrained(
        "thibaud/controlnet-openpose-sdxl-1.0",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    
    # Load SDXL pipeline with ControlNet
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        controlnet=controlnet,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        use_safetensors=True,
        variant="fp16" if torch.cuda.is_available() else None
    )
    pipe = pipe.to(device)
    
    # Load IP-Adapter
    try:
        print("[Diffusion] Loading IP-Adapter...")
        from diffusers.models import IPAdapterXL
        pipe.load_ip_adapter("tencent-ailab/IP-Adapter", subfolder="models", weight_name="ip-adapter_sdxl.bin")
    except Exception as e:
        print(f"[Diffusion] Warning: IP-Adapter not available: {e}")
    
    print("[Diffusion] Pipeline initialized!")


def build_sdxl_prompt(panel_json: dict) -> str:
    """
    Convert panel JSON → cinematic SDXL prompt string.
    
    Translates:
      - shot_type (ECU, CU, MS, WS, etc.) → photographic framing
      - camera_angle (Low/High/Eye) → compositional directionality
      - lighting_mood → quality, direction, color temperature
      - background → environment and texture
      - characters → spatial description
    
    Args:
        panel_json (dict): Panel metadata with all fields
    
    Returns:
        str: Cinematic, specific prompt ready for SDXL
    """
    # Check for custom prompt override (from user regeneration)
    if "_override_prompt" in panel_json:
        return panel_json["_override_prompt"]
    
    parts = []
    
    # Shot type in photographic terminology
    shot_type = panel_json.get("shot_type", "").upper()
    shot_desc = {
        "ECU": "extreme close-up, face filling the frame",
        "CU": "close-up, head and shoulders",
        "MS": "medium shot, from waist up",
        "WS": "wide shot, full body and environment",
        "ELS": "establishing shot, expansive wide view",
        "OTS": "over-the-shoulder shot",
        "POV": "point of view shot, first-person perspective",
    }.get(shot_type, f"{shot_type} shot")
    parts.append(shot_desc)
    
    # Camera angle movement
    camera_angle = panel_json.get("camera_angle", "").lower()
    if "low" in camera_angle:
        parts.append("low angle, looking upward, dramatic")
    elif "high" in camera_angle:
        parts.append("high angle, looking downward")
    elif "bird" in camera_angle:
        parts.append("bird's-eye view, overhead angle")
    elif "worm" in camera_angle:
        parts.append("worm's-eye view, extreme low angle")
    elif "dutch" in camera_angle:
        parts.append("dutch angle, tilted composition")
    
    # Lighting and mood (specific, not vague)
    lighting = panel_json.get("lighting_mood", "")
    if lighting and lighting.lower() != "none":
        parts.append(f"lighting: {lighting}")
    
    # Background and environment
    background = panel_json.get("background", "")
    if background and background.lower() != "none":
        parts.append(f"background: {background}")
    
    # Characters and positioning
    characters = panel_json.get("characters", [])
    for char in characters:
        if isinstance(char, dict):
            name = char.get("name", "character")
            position = char.get("position", "center")
            parts.append(f"{name} in {position}")
    
    # Action and visual atmosphere
    action_note = panel_json.get("action_note", "")
    if action_note and action_note.lower() != "none":
        parts.append(action_note)
    
    # Combine and finalize
    prompt = ", ".join(p.strip() for p in parts if p and p.strip())
    prompt += ", cinematic storyboard panel, highly detailed, professional lighting, vibrant colors"
    
    return prompt


def generate_panels(
    panel_jsons: list[dict],
    ip_adapter_image: Image.Image = None,
    hf_token: str = None
) -> list[Image.Image]:
    """
    Generate storyboard panel images for all panels.
    
    For each panel:
    1. Retrieve semantic pose via pose_search.retrieve_pose()
    2. Preprocess via build_map.build_pose_map()
    3. Build SDXL prompt via build_sdxl_prompt()
    4. Call SDXL + ControlNet + IP-Adapter
    
    Args:
        panel_jsons (list[dict]): Array of panel JSON objects
        ip_adapter_image (Image.Image, optional): Character reference image
        hf_token (str, optional): HuggingFace token for first-time pose downloads
    
    Returns:
        list[Image.Image]: Generated panel images
    """
    global pipe
    
    if pipe is None:
        initialize_pipeline()
    
    hf_token = hf_token or HUGGING_FACE_HUB_TOKEN
    
    print(f"\n{'='*80}")
    print(f"[Diffusion] Starting generation of {len(panel_jsons)} panels")
    print(f"[Diffusion] Canvas: {W}×{H}")
    print(f"[Diffusion] Parameters: steps={num_inference_steps}, guidance={guidance_scale}, controlnet={controlnet_conditioning_scale}")
    print(f"[Diffusion] Character reference: {'Yes' if ip_adapter_image is not None else 'No'}")
    print(f"{'='*80}\n")
    
    # Set IP-Adapter scale
    default_ip_scale = ip_adapter_scale
    if ip_adapter_image is not None:
        ip_adapter_image = ip_adapter_image.convert("RGB").resize((224, 224))
        try:
            pipe.set_ip_adapter_scale(default_ip_scale)
            print(f"[Diffusion] IP-Adapter initialized with scale={default_ip_scale}")
        except Exception as e:
            print(f"[Diffusion] Warning: Could not set IP-Adapter scale: {e}")
    else:
        # Create dummy black image
        ip_adapter_image = Image.new("RGB", (224, 224), color=(0, 0, 0))
        try:
            pipe.set_ip_adapter_scale(0.0)
            print(f"[Diffusion] No character reference provided; IP-Adapter disabled")
        except Exception:
            pass
    
    generated_panels = []
    
    for idx, panel_json in enumerate(panel_jsons):
        print(f"\n{'─'*80}")
        print(f"[Diffusion] PANEL {idx + 1}/{len(panel_jsons)}")
        print(f"{'─'*80}")
        
        try:
            # Log panel metadata
            print(f"[Panel Metadata]")
            print(f"  Caption: {panel_json.get('caption', 'N/A')}")
            print(f"  Shot Type: {panel_json.get('shot_type', 'N/A')}")
            print(f"  Camera Angle: {panel_json.get('camera_angle', 'N/A')}")
            print(f"  Characters: {panel_json.get('characters', [])}")
            print(f"  Position: {panel_json.get('position', 'N/A')}")
            
            # Build prompt
            prompt = build_sdxl_prompt(panel_json)
            print(f"\n[SDXL Prompt]")
            print(f"  {prompt}")
            
            # Retrieve and preprocess pose
            pose_query = panel_json.get("pose_query", "a person standing")
            position = panel_json.get("position", "center midground")
            camera_angle = panel_json.get("camera_angle", "Eye Level")
            
            print(f"\n[Pose Retrieval]")
            print(f"  Query: {pose_query[:80]}...")
            print(f"  Position: {position}")
            print(f"  Camera Angle: {camera_angle}")
            
            conditioning_map = build_map.get_conditioning_map(
                pose_query=pose_query,
                position_keyword=position,
                camera_angle=camera_angle,
                canvas_size=H if H == W else 1024,
                hf_token=hf_token
            )
            
            # Resize conditioning to match generation size
            conditioning_map = conditioning_map.resize((W, H), Image.Resampling.LANCZOS)
            print(f"  Conditioning map ready: {conditioning_map.size}")
            
            # Per-panel IP-Adapter scale (can be overridden in panel JSON)
            panel_ip_scale = panel_json.get("ip_adapter_scale", default_ip_scale)
            try:
                pipe.set_ip_adapter_scale(panel_ip_scale)
                print(f"\n[Generation Parameters]")
                print(f"  IP-Adapter Scale: {panel_ip_scale}")
                print(f"  ControlNet Scale: {controlnet_conditioning_scale}")
                print(f"  Inference Steps: {num_inference_steps}")
                print(f"  Guidance Scale: {guidance_scale}")
                print(f"  Canvas Size: {W}×{H}")
            except Exception:
                pass
            
            # Generate with OOM handling
            t0 = time.time()
            print(f"\n[Generation] Starting inference...")
            try:
                result = pipe(
                    prompt=prompt,
                    negative_prompt=NEGATIVE_PROMPT,
                    image=conditioning_map,
                    ip_adapter_image=ip_adapter_image,
                    controlnet_conditioning_scale=controlnet_conditioning_scale,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=H,
                    width=W,
                    generator=torch.Generator(device=device).manual_seed(42 + idx),
                )
                img = result.images[0]
                elapsed = time.time() - t0
                print(f"[Generation] ✅ Success in {elapsed:.2f}s")
                print(f"  Output size: {img.size}")
                generated_panels.append(img)
                
            except RuntimeError as oom_error:
                if "out of memory" in str(oom_error).lower():
                    print(f"[Generation] ⚠️  OOM error detected")
                    print(f"[Generation] Retrying at lower resolution (512×384)...")
                    
                    result = pipe(
                        prompt=prompt,
                        negative_prompt=NEGATIVE_PROMPT,
                        image=conditioning_map.resize((512, 384), Image.Resampling.LANCZOS),
                        ip_adapter_image=ip_adapter_image,
                        controlnet_conditioning_scale=controlnet_conditioning_scale,
                        num_inference_steps=20,  # Fewer steps at lower res
                        guidance_scale=guidance_scale,
                        height=384,
                        width=512,
                        generator=torch.Generator(device=device).manual_seed(42 + idx),
                    )
                    img = result.images[0]
                    img = img.resize((W, H), Image.Resampling.LANCZOS)
                    elapsed = time.time() - t0
                    print(f"[Generation] ✅ Generated at lower res, upscaled in {elapsed:.2f}s")
                    generated_panels.append(img)
                else:
                    raise
                    
        except Exception as e:
            print(f"[Generation] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            # Create blank fallback
            generated_panels.append(Image.new("RGB", (W, H), color=(0, 0, 0)))
    
    print(f"\n{'='*80}")
    print(f"[Diffusion] ✅ Generation complete!")
    print(f"[Diffusion] Generated {len(generated_panels)}/{len(panel_jsons)} panels")
    print(f"{'='*80}\n")
    return generated_panels

