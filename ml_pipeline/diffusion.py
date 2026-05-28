import fal_client
import asyncio
import httpx
import os
import io
from PIL import Image

os.environ["FAL_KEY"] = os.getenv("FAL_KEY")

NEGATIVE_PROMPT = (
    "text, watermark, extra limbs, blurry, low quality, deformed, "
    "disconnected limbs, floating limbs, disfigured, poorly drawn, "
    "photorealistic, photograph, 3d render"
)

CONTROLNET_CONDITIONING_SCALE = 0.55
NUM_INFERENCE_STEPS = 28
GUIDANCE_SCALE = 3.5
W = 1280
H = 768


# ============================================================================
# PROMPT BUILDER
# ============================================================================

def build_flux_prompt(panel: dict, style: str, scene_bible: str) -> tuple[str, str]:
    shot_language = {
        "ECU": "extreme close-up, face filling the entire frame",
        "CU":  "close-up shot, head and shoulders only",
        "MS":  "medium shot, subject from waist up",
        "WS":  "wide shot, full body visible with environment",
        "ELS": "extreme long shot, small figure in vast environment",
        "OTS": "over-the-shoulder shot, partial back of head in foreground",
        "POV": "first-person point of view shot",
    }
    angle_language = {
        "Eye Level":                  "eye level camera angle",
        "High Angle":                 "high angle shot looking down at subject",
        "Low Angle":                  "dramatic low angle shot looking up",
        "Bird's-Eye View / Top-Down": "overhead bird's-eye view, looking straight down",
        "Worm's-Eye View":            "extreme low worm's-eye view",
        "Dutch Angle / Canted Angle": "dutch angle, tilted frame suggesting unease",
        "Ground Level":               "ground level camera, floor perspective",
    }

    shot  = shot_language.get(panel.get("shot_type", "MS"), "medium shot")
    angle = angle_language.get(panel.get("camera_angle", "Eye Level"), "eye level")

    prompt = (
        f"{style.upper()} illustration style. "
        f"{shot.upper()}, {angle}. "
        f"{panel.get('action_note', '')}. "
        f"Setting: {panel.get('background', '')}. "
        f"{panel.get('lighting_mood', '')} lighting atmosphere. "
        f"{scene_bible}. "
        f"storyboard frame, professional concept art, "
        f"high detail, single character."
    )

    negative = (
        "multiple characters, crowd, text, watermark, blurry, "
        "low quality, deformed, extra limbs, photorealistic photograph, "
        "3d render, poorly drawn hands"
    )

    return prompt, negative


# ============================================================================
# CONTINUITY CONTEXT
# ============================================================================

def extract_panel_context(panel: dict) -> str:
    parts = []
    bg = panel.get("background", "")
    if bg:
        parts.append(f"environment: {bg}")
    lighting = panel.get("lighting_mood", "")
    if lighting:
        parts.append(f"lighting: {lighting}")
    action = panel.get("action_note", "")
    if action:
        parts.append(f"action: {action[:50]}")
    return "; ".join(parts)


def build_panel_sequence_context(panel_jsons: list[dict]) -> list[dict]:
    for idx, panel in enumerate(panel_jsons):
        panel["_panel_index"] = idx
        panel["_total_panels"] = len(panel_jsons)
        if idx > 0:
            panel["_previous_context"] = extract_panel_context(panel_jsons[idx - 1])
    return panel_jsons


# ============================================================================
# FAL UPLOAD
# ============================================================================

async def _upload_image_to_fal(img: Image.Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    url = await fal_client.upload_async(buffered.read(), "image/png")
    return url


# ============================================================================
# SINGLE PANEL GENERATION
# ============================================================================

async def _generate_single_panel(
    panel_json: dict,
    pose_url: str,
    ip_adapter_url: str | None,
    style: str,
    scene_bible: str,
    panel_idx: int
) -> str:
    prompt, _ = build_flux_prompt(panel_json, style, scene_bible)  # discard negative

    shot_type = panel_json.get("shot_type", "MS")
    disable_controlnet_shots = {"CU", "ECU"}  # Close-up and Extreme close-up
    use_controlnet = shot_type not in disable_controlnet_shots

    arguments = {
        "prompt": prompt,
        "image_size": {"width": W, "height": H},
        "num_inference_steps": NUM_INFERENCE_STEPS,
        "guidance_scale": GUIDANCE_SCALE,
        "seed": 42 + panel_idx,
        "loras": [],
        "controlnets": [],
    }

    if use_controlnet:
        arguments["controlnet_unions"] = [
            {
                "path": "InstantX/FLUX.1-dev-Controlnet-Union",
                "controls": [
                    {
                        "control_image_url": pose_url,
                        "control_mode": "pose",
                        # no conditioning_scale here — omit entirely
                    }
                ],
            }
        ]

    if ip_adapter_url is not None:
        arguments["ip_adapters"] = [
            {
                "path": "XLabs-AI/flux-ip-adapter",
                "image_encoder_path": "openai/clip-vit-large-patch14",  # required for XLabs
                "weight_name": "ip_adapter.safetensors",                 # required for XLabs
                "image_url": ip_adapter_url,
                "scale": panel_json.get("ip_adapter_scale", 0.65),      # 0.65 = tested sweet spot
            }
            #    {
            #       "path": "InstantX/FLUX.1-dev-IP-Adapter",
            #       "image_encoder_path": "google/siglip-so400m-patch14-384", # <-- The exact SigLIP model
            #       "weight_name": "ip-adapter.bin",                          # <-- InstantX uses .bin
            #       "image_url": ip_adapter_url,
            #       "scale": panel_json.get("ip_adapter_scale", 0.65),  
            #    }
        ]

    result = await fal_client.run_async(
        "fal-ai/flux-general",
        arguments=arguments
    )

    return result["images"][0]["url"]


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def generate_panels(
    panel_jsons: list[dict],
    ip_adapter_image: Image.Image = None,
    hf_token: str = None,
    scene_bible: str = ""
) -> list[Image.Image]:

    print(f"[Diffusion] Generating {len(panel_jsons)} panels via Flux ControlNet")
    print(f"[Diffusion] Resolution: {W}×{H}")
    print(f"[Diffusion] IP-Adapter character pass: {'enabled' if ip_adapter_image else 'disabled'}")

    panel_jsons = build_panel_sequence_context(panel_jsons)

    # Upload character reference once upfront if provided
    ip_adapter_url = None
    if ip_adapter_image is not None:
        print("[Diffusion] Uploading character reference...")
        ip_adapter_url = await _upload_image_to_fal(
            ip_adapter_image.convert("RGB").resize((512, 512))
        )
        print(f"[Diffusion] Character reference ready: {ip_adapter_url}")

    # Build pose conditioning maps using your existing pipeline
    print("[Diffusion] Building pose conditioning maps...")
    from ml_pipeline import build_map

    conditioning_maps = []
    for idx, panel in enumerate(panel_jsons):
        pose_query = panel.get("pose_query", "person standing upright facing camera")
        camera_angle = panel.get("camera_angle", "Eye Level")

        # Extract position from characters array (where LLM puts it)
        characters = panel.get("characters", [])
        position = (
            characters[0].get("position", "center midground")
            if characters else "center midground"
        )

        conditioning_map = build_map.get_conditioning_map(
            pose_query=pose_query,
            position_keyword=position,
            camera_angle=camera_angle,
            canvas_width=W,
            canvas_height=H,
            hf_token=hf_token
        )
        conditioning_maps.append(conditioning_map)
        print(f"  Panel {idx + 1}: pose map ready — {pose_query[:60]}...")

    # Upload all pose maps concurrently
    print("[Diffusion] Uploading pose maps to fal...")
    valid_pairs = [
        (idx, panel, cm)
        for idx, (panel, cm) in enumerate(zip(panel_jsons, conditioning_maps))
        if cm is not None
    ]

    pose_urls = await asyncio.gather(*[
        _upload_image_to_fal(cm) for _, _, cm in valid_pairs
    ])
    print(f"[Diffusion] {len(pose_urls)} pose maps uploaded")

    # Generate all panels concurrently
    style = panel_jsons[0].get("visual_style", "cinematic storyboard") if panel_jsons else ""

    print("[Diffusion] Launching parallel generation...")
    image_urls = await asyncio.gather(*[
        _generate_single_panel(
            panel_json=panel,
            pose_url=pose_urls[i],
            ip_adapter_url=ip_adapter_url,
            style=style,
            scene_bible=scene_bible,
            panel_idx=idx
        )
        for i, (idx, panel, _) in enumerate(valid_pairs)
    ])
    print(f"[Diffusion] All {len(image_urls)} panels generated")

    # Download final images
    print("[Diffusion] Downloading images...")
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(*[
            client.get(url) for url in image_urls
        ])

    images = [
        Image.open(io.BytesIO(r.content)).convert("RGB")
        for r in responses
    ]

    print(f"[Diffusion] Done — {len(images)} images ready")
    return images