"""
API Routing and Schema Definitions for FrameForge.

This module uses FastAPI and Pydantic to define the strict contracts for input
and output data. It exposes the primary endpoints for full storyboard generation
and isolated panel regeneration.
"""

import sys
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image
import json
import httpx
import base64
import io

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.settings import API_PREFIX, OPEN_ROUTER_API_KEY, SYSTEM_PROMPT, HUGGING_FACE_HUB_TOKEN
from backend.schemas import StoryboardGenerationRequest, PanelRegenerationRequest, StoryboardResponse
from ml_pipeline import pipeline

router = APIRouter(prefix=API_PREFIX)


def _normalize_panel_fields_to_camel_case(panels: list[dict]) -> list[dict]:
    """
    Convert panel JSON field names from snake_case to camelCase for frontend compatibility.
    
    Mapping:
      shot_type → shotType
      camera_angle → cameraAngle
      lighting_mood → lightingMood
      action_note → actionNote
    """
    normalized = []
    for panel in panels:
        normalized_panel = {}
        for key, value in panel.items():
            if key == "shot_type":
                normalized_panel["shotType"] = value
            elif key == "camera_angle":
                normalized_panel["cameraAngle"] = value
            elif key == "lighting_mood":
                normalized_panel["lightingMood"] = value
            elif key == "action_note":
                normalized_panel["actionNote"] = value
            elif key == "pose_query":
                normalized_panel["poseQuery"] = value
            elif key == "position":
                normalized_panel["position"] = value
            else:
                normalized_panel[key] = value
        normalized.append(normalized_panel)
    return normalized


@router.post("/generate")
async def generate_storyboard(
    scene_prompt: str = Form(...),
    num_panels: int = Form(default=5),
    visual_style: str = Form(default="cinematic, photorealistic"),
    character_reference: UploadFile = File(None)
):
    """
    Generate a complete storyboard from scene description.
    
    Args:
        scene_prompt (str): Plain English scene description
        num_panels (int): Number of panels to generate (default 5)
        visual_style (str): Visual style for image generation
        character_image (UploadFile, optional): Character reference image (PNG/JPG)
    
    Returns:
        dict: Contains panels, generated_images (base64), sdxl_prompts
    """
    try:
        ip_image_data = None
        if character_reference:
            try:
                image_bytes = await character_reference.read()  # read once
                # Validate by opening — don't call verify()
                img = Image.open(io.BytesIO(image_bytes))
                img.load()  # actually loads pixels, safe validation
                # Encode the bytes we already have
                ip_image_data = base64.b64encode(image_bytes).decode("utf-8")
                print(f"[API] Character reference image loaded: {len(image_bytes)} bytes")
            except Exception as e:
                print(f"[API] WARNING: Invalid character image: {e}")
                return JSONResponse(
                    status_code=400,
                    content={"detail": f"Character image is invalid: {e}"}
                )

        
        # Call pipeline
        result = await pipeline.run_full_generation(
            scene_prompt=scene_prompt,
            num_panels=num_panels,
            ip_image_data=ip_image_data,
            visual_style=visual_style,
            hf_token=HUGGING_FACE_HUB_TOKEN
        )
        
        # Normalize field names for frontend
        result["panels"] = _normalize_panel_fields_to_camel_case(result["panels"])
        
        # Add visual_style to panels
        for panel in result["panels"]:
            panel["visualStyle"] = visual_style
        
        print(f"[API] /generate completed: {len(result['generated_images'])} images")
        return result
        
    except Exception as e:
        print(f"[API] ERROR in /generate: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Generation failed: {str(e)}"}
        )


@router.post("/regenerate")
async def regenerate_panel(
    panel_json: str = Form(...),
    custom_prompt: str = Form(default=""),
    scene_bible: str = Form(default=""),
    character_image: UploadFile = File(None)
):
    """
    Regenerate a single panel with edited metadata and global context.
    
    Args:
        panel_json (str): JSON string of edited panel metadata
        custom_prompt (str, optional): Custom SDXL prompt for generation (for backward compatibility)
        scene_bible (str, optional): Global context string for visual consistency
        character_image (UploadFile, optional): Character reference image
    
    Returns:
        dict: Contains panel, sdxl_prompt (the prompt used), generated_image (base64)
    """
    try:
        print(f"[API] /regenerate: panel editing requested")
        if scene_bible:
            print(f"[API] Scene context: {scene_bible[:60]}...")
        
        # Parse panel JSON
        try:
            panel_data = json.loads(panel_json)
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=400,
                content={"detail": f"Invalid panel JSON: {e}"}
            )
        
        # Convert camelCase back to snake_case
        panel_data_snake = {}
        for key, value in panel_data.items():
            if key == "shotType":
                panel_data_snake["shot_type"] = value
            elif key == "cameraAngle":
                panel_data_snake["camera_angle"] = value
            elif key == "lightingMood":
                panel_data_snake["lighting_mood"] = value
            elif key == "actionNote":
                panel_data_snake["action_note"] = value
            elif key == "poseQuery":
                panel_data_snake["pose_query"] = value
            else:
                panel_data_snake[key] = value
        
        # Decode character image if provided
        ip_image_data = None
        if character_image:
            try:
                image_bytes = await character_image.read()
                img = Image.open(io.BytesIO(image_bytes))
                img.load()  # validate without verify()
                ip_image_data = base64.b64encode(image_bytes).decode("utf-8")
            except Exception as e:
                print(f"[API] WARNING: Invalid character image: {e}")
        
        # Call pipeline with scene_bible
        result = await pipeline.run_panel_regeneration(
            panel_json=panel_data_snake,
            custom_prompt=custom_prompt,
            ip_image_data=ip_image_data,
            scene_bible=scene_bible,
            hf_token=HUGGING_FACE_HUB_TOKEN
        )
        
        # Normalize panel fields for frontend
        result["panel"] = _normalize_panel_fields_to_camel_case([result["panel"]])[0]
        
        print(f"[API] /regenerate completed")
        return result
        
    except Exception as e:
        print(f"[API] ERROR in /regenerate: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Regeneration failed: {str(e)}"}
        )