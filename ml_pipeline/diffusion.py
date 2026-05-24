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
ip_adapter_loaded = False  # ADD THIS
W = 640
H = 384
NEGATIVE_PROMPT = "text, watermark, extra limbs, blurry, low quality, deformed, disconnected limbs, floating limbs, disfigured, poorly drawn"

# Tuned from FrameForge team stress tests:
# - controlnet_conditioning_scale = 0.6 (best balance between pose fidelity + visual naturalness)
# - ip_adapter_scale = 0.4 (default for human refs; can be overridden per-panel for non-human refs)
# - inference_steps = 25 (reduced from 30 for faster generation without quality loss)
# - guidance_scale = 7.5 (confirmed good across all test runs)
controlnet_conditioning_scale = 0.6
ip_adapter_scale = 0.4  # Can be overridden per-panel via panel_json["ip_adapter_scale"]
num_inference_steps = 20
guidance_scale = 7.5


def initialize_pipeline():
    """
    Initialize SDXL + ControlNet(OpenPose) + IP-Adapter pipeline.
    
    Called once at startup. Loads models and moves to appropriate device.
    """
    global pipe, device, ip_adapter_loaded
    
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
        "RunDiffusion/Juggernaut-XL-v9",
        controlnet=controlnet,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        use_safetensors=True,
        variant="fp16" if torch.cuda.is_available() else None
    )
    pipe.enable_vae_slicing()    # splits VAE decode into slices
    pipe.enable_vae_tiling()     # tiles large images
    pipe.enable_attention_slicing(1)
    pipe.enable_model_cpu_offload()
    
    # Load IP-Adapter
    try:
        print("[Diffusion] Loading IP-Adapter...")
        pipe.load_ip_adapter(
            "h94/IP-Adapter",
            subfolder="sdxl_models",
            weight_name="ip-adapter_sdxl.bin"
        )
        ip_adapter_loaded = True
        print("[Diffusion] IP-Adapter loaded successfully")
    except Exception as e:
        ip_adapter_loaded = False
        print(f"[Diffusion] Warning: IP-Adapter not available: {e}")

    
    print("[Diffusion] Pipeline initialized!")


def build_sdxl_prompt(panel_json: dict) -> str:
    """
    Convert panel JSON → cinematic SDXL prompt string (optimized for CLIP 77-token limit).
    
    CRITICAL: CLIP tokenizer truncates at 77 tokens. Order matters!
    Put most important visual info FIRST so it survives truncation.
    
    Priority order:
    1. Shot type + camera angle (essential framing)
    2. Lighting (mood/atmosphere)
    3. Background (setting)
    4. Characters + positions
    5. Action (narrative momentum)
    6. Continuity context (nice-to-have, gets cut if over limit)
    7. Style (usually cut, but included for safety)
    
    Args:
        panel_json (dict): Panel metadata with all fields
    
    Returns:
        str: Prompt optimized to fit CLIP's 77-token limit
    """
    # Check for custom prompt override (from user regeneration)
    if "_override_prompt" in panel_json:
        return panel_json["_override_prompt"]
    
    parts = []
    
    # FIRST: Shot type (most important for framing) - keep concise
    shot_type = panel_json.get("shot_type", "").upper()
    shot_desc = {
        "ECU": "extreme close-up",
        "CU": "close-up",
        "MS": "medium shot",
        "WS": "wide shot",
        "ELS": "establishing shot",
        "OTS": "over-the-shoulder",
        "POV": "point of view",
    }.get(shot_type, f"{shot_type} shot")
    parts.append(shot_desc)
    
    # Camera angle (visual composition)
    camera_angle = panel_json.get("camera_angle", "").lower()
    if "low" in camera_angle:
        parts.append("low angle")
    elif "high" in camera_angle:
        parts.append("high angle")
    elif "bird" in camera_angle:
        parts.append("bird's-eye view")
    elif "worm" in camera_angle:
        parts.append("worm's-eye view")
    elif "dutch" in camera_angle:
        parts.append("dutch angle")
    
    # SECOND: Lighting (mood is crucial for diffusion)
    lighting = panel_json.get("lighting_mood", "")
    if lighting and lighting.lower() != "none":
        parts.append(f"{lighting} lighting")
    
    # THIRD: Background (environmental context)
    background = panel_json.get("background", "")
    if background and background.lower() != "none":
        # Shorten if too long
        bg_text = background[:50] if len(background) > 50 else background
        parts.append(bg_text)
    
    # FOURTH: Characters and positioning (who's in frame)
    characters = panel_json.get("characters", [])
    if characters:
        char_descriptions = []
        for char in characters:
            if isinstance(char, dict):
                name = char.get("name", "character")
                position = char.get("position", "center")
                char_descriptions.append(f"{name} {position}")
        if char_descriptions:
            parts.append(", ".join(char_descriptions))
    
    # FIFTH: Action/narrative (what's happening)
    action_note = panel_json.get("action_note", "")
    if action_note and action_note.lower() != "none":
        # Shorten if too long
        action_text = action_note[:40] if len(action_note) > 40 else action_note
        parts.append(action_text)

    # SIXTH: Continuity context (might get truncated, but helps when it fits)
    prev_context = panel_json.get("_previous_context", "")
    if prev_context:
        # Make context ultra-concise to maximize chance of fitting
        parts.append(f"[prev: {prev_context[:30]}]")
    
    # SEVENTH: Style (least important, likely to be truncated)
    style = panel_json.get("visual_style", "cinematic, professional lighting")
    parts.append(f'"{style}"')

    prompt = ", ".join(parts)
    
    return prompt


def extract_panel_context(panel_json: dict) -> str:
    """
    Extract key visual and narrative elements from a panel for use in the next panel's prompt.
    Creates continuity context by capturing environment, lighting, and character states.
    
    Args:
        panel_json (dict): Panel metadata
    
    Returns:
        str: Normalized context string for next panel's prompt
    """
    context_elements = []
    
    # Capture setting/environment for visual consistency
    background = panel_json.get("background", "")
    if background and background.lower() != "none":
        context_elements.append(f"environment: {background}")
    
    # Capture lighting continuity
    lighting = panel_json.get("lighting_mood", "")
    if lighting and lighting.lower() != "none":
        context_elements.append(f"lighting: {lighting}")
    
    # Capture character states and positions
    characters = panel_json.get("characters", [])
    if characters:
        char_context = []
        for char in characters:
            if isinstance(char, dict):
                name = char.get("name", "character")
                position = char.get("position", "center")
                char_context.append(f"{name} at {position}")
        if char_context:
            context_elements.append(f"characters: {', '.join(char_context)}")
    
    # Capture action momentum for scene flow
    action_note = panel_json.get("action_note", "")
    if action_note and action_note.lower() != "none":
        context_elements.append(f"action: {action_note[:50]}")
    
    # Capture overall mood/tone
    caption = panel_json.get("caption", "")
    if caption:
        context_elements.append(f"scene beat: {caption[:40]}")
    
    return "; ".join(context_elements)



def build_panel_sequence_context(panel_jsons: list[dict]) -> list[dict]:
    """
    Enrich panel JSONs with previous/next panel context for better continuity.
    Modifies panels in-place to include _previous_context and _next_panel_idx fields.
    
    Args:
        panel_jsons (list[dict]): List of panel metadata dicts
    
    Returns:
        list[dict]: Same list, modified with context fields
    """
    for idx, panel in enumerate(panel_jsons):
        # Add reference to next panel index for continuity planning
        panel["_panel_index"] = idx
        panel["_total_panels"] = len(panel_jsons)
        
        # Add previous panel context if not the first panel
        if idx > 0:
            prev_panel = panel_jsons[idx - 1]
            prev_context = extract_panel_context(prev_panel)
            panel["_previous_context"] = prev_context
        
        # Add reference to next panel for lookahead (optional)
        if idx < len(panel_jsons) - 1:
            panel["_next_panel_idx"] = idx + 1
    
    return panel_jsons



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

    # Set IP-Adapter scale — only if adapter actually loaded
    if ip_adapter_loaded:
        if ip_adapter_image is not None:
            ip_adapter_image = ip_adapter_image.convert("RGB").resize((224, 224))
            try:
                pipe.set_ip_adapter_scale(default_ip_scale)
                print(f"[Diffusion] IP-Adapter initialized with scale={default_ip_scale}")
            except Exception as e:
                print(f"[Diffusion] Warning: Could not set IP-Adapter scale: {e}")
        else:
            print(f"[Diffusion] No character reference provided; IP-Adapter disabled")
            ip_adapter_image = None  # Don't pass it at all
    else:
        print(f"[Diffusion] IP-Adapter not loaded; skipping")
        ip_adapter_image = None  # Force None so gen_kwargs never includes it
    
    # Build panel sequence context for better continuity
    print(f"\n[Continuity] Building panel context for seamless transitions...")
    panel_jsons = build_panel_sequence_context(panel_jsons)
    
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
                canvas_width=W,
                canvas_height=H,
                hf_token=hf_token
            )
            
            # Handle case where pose conditioning failed (graceful fallback)
            if conditioning_map is not None:
                # Resize conditioning to match generation size
                conditioning_map = conditioning_map.resize((W, H), Image.Resampling.LANCZOS)
                print(f"  Conditioning map ready: {conditioning_map.size}")
            else:
                print(f"  [Fallback] Generating without pose conditioning")
                conditioning_map = None
            
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
                # Build kwargs, conditionally including conditioning_map
                gen_kwargs = {
                    "prompt": prompt,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "controlnet_conditioning_scale": controlnet_conditioning_scale,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "height": H,
                    "width": W,
                    "generator": torch.Generator(device=device).manual_seed(42 + idx),
                }
                if conditioning_map is not None:
                    gen_kwargs["image"] = conditioning_map

                # Only pass ip_adapter_image if adapter is loaded AND we have a reference
                if ip_adapter_loaded and ip_adapter_image is not None:
                    gen_kwargs["ip_adapter_image"] = ip_adapter_image
                
                result = pipe(**gen_kwargs)
                img = result.images[0]
                elapsed = time.time() - t0
                print(f"[Generation] ✅ Success in {elapsed:.2f}s")
                print(f"  Output size: {img.size}")
                generated_panels.append(img)
                
            except RuntimeError as oom_error:
                if "out of memory" in str(oom_error).lower():
                    print(f"[Generation] ⚠️  OOM error detected")
                    print(f"[Generation] Retrying at lower resolution (512×384)...")
                    
                    retry_kwargs = {
                        "prompt": prompt,
                        "negative_prompt": NEGATIVE_PROMPT,
                        "controlnet_conditioning_scale": controlnet_conditioning_scale,
                        "num_inference_steps": 10,
                        "guidance_scale": guidance_scale,
                        "height": 384,
                        "width": 512,
                        "generator": torch.Generator(device=device).manual_seed(42 + idx),
                    }
                    if conditioning_map is not None:
                        retry_kwargs["image"] = conditioning_map.resize((512, 384), Image.Resampling.LANCZOS)
                    if ip_adapter_loaded and ip_adapter_image is not None:
                        retry_kwargs["ip_adapter_image"] = ip_adapter_image
                    
                    result = pipe(**retry_kwargs)
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

