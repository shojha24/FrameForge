# test_fal.py
import asyncio
from PIL import Image
import fal_client
from fal_client.client import FalClientHTTPError
import os
import sys
import httpx
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_pipeline import build_map
from dotenv import load_dotenv

load_dotenv("backend/.env", override=True)
os.environ["FAL_KEY"] = os.getenv("FAL_KEY")


async def _upload_image_to_fal(img: Image.Image) -> str:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    url = await fal_client.upload_async(buffered.read(), "image/png")
    return url


async def test():
    result = await fal_client.run_async(
        "fal-ai/flux/dev",
        arguments={
            "prompt": "cinematic storyboard, medium shot, detective in a rainy alley",
            "image_size": {"width": 1280, "height": 768},
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
        }
    )
    print(result["images"][0]["url"])


async def test_controlnet():
    conditioning_map = build_map.get_conditioning_map(
        pose_query="person standing upright, arms at sides",
        position_keyword="center midground",
        camera_angle="Eye Level",
        canvas_width=1024,
        canvas_height=1024,
    )

    pose_url = await _upload_image_to_fal(conditioning_map)
    print(f"Pose map uploaded: {pose_url}")

    async with httpx.AsyncClient() as client:
        r = await client.get(pose_url)
        print(f"URL check: status={r.status_code}, size={len(r.content)} bytes")

    try:
        result = await fal_client.run_async(
            "fal-ai/flux-general",
            arguments={
                "prompt": "cinematic storyboard, medium shot, detective in a rainy alley",
                "image_size": {"width": 1024, "height": 1024},
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "seed": 42,
                "loras": [],
                "controlnets": [],
                "controlnet_unions": [
                    {
                        "path": "InstantX/FLUX.1-dev-Controlnet-Union",
                        "controls": [
                            {
                                "control_image_url": pose_url,
                                "control_mode": "pose",
                            }
                        ],
                    }
                ],
            }
        )
        print(result["images"][0]["url"])
    except FalClientHTTPError as e:
        print("=== FAL ERROR ===")
        print("Message:", e)
        if hasattr(e, "response") and e.response is not None:
            print("Status:", e.response.status_code)
            print("Body:", e.response.text)
        raise


async def test_controlnet_with_ip_adapter(character_image_path: str):
    conditioning_map = build_map.get_conditioning_map(
        pose_query="person standing upright, arms at sides, facing camera",
        position_keyword="center midground",
        camera_angle="Eye Level",
        canvas_width=1024,
        canvas_height=1024,
    )

    pose_url = await _upload_image_to_fal(conditioning_map)
    print(f"Pose map uploaded: {pose_url}")

    character_image = Image.open(character_image_path).convert("RGB").resize((512, 512))
    ip_adapter_url = await _upload_image_to_fal(character_image)

    print(f"Character reference uploaded: {ip_adapter_url}")

    try:
        result = await fal_client.run_async(
            "fal-ai/flux-general",
            arguments={
                # Removed "85mm portrait lens" and forced a wider camera angle
                "prompt": "FACE VISIBLE, highly realistic, detective standing in an alley in the morning, bareheaded, thick dark curly hair visible, direct eye contact with camera, sharp facial features",
                "image_size": {"width": 1024, "height": 1024},
                "num_inference_steps": 28,
                "guidance_scale": 3.5, 
                "seed": 69,
                "loras": [],
                "controlnets": [],
                "controlnet_unions": [
                    {
                        "path": "InstantX/FLUX.1-dev-Controlnet-Union",
                        "controls": [
                            {
                                "control_image_url": pose_url,
                                "control_mode": "pose",
                            }
                        ],
                    }
                ],
                "enable_safety_checker": True,
                "ip_adapters": [
                    {
                        # Swapped back to XLabs to reduce Composition Leak
                        "path": "XLabs-AI/flux-ip-adapter",
                        "image_encoder_path": "openai/clip-vit-large-patch14", # XLabs uses CLIP
                        "weight_name": "ip_adapter.safetensors",               
                        "image_url": ip_adapter_url,
                        "scale": 0.65,  # 0.65 is the sweet spot for XLabs face retention
                    }
                ],
            }
        )
        print(result["images"][0]["url"])
    except FalClientHTTPError as e:
        print("=== FAL ERROR ===")
        print("Message:", e)
        if hasattr(e, "response") and e.response is not None:
            print("Status:", e.response.status_code)
            print("Body:", e.response.text)
        raise


# Run whichever test you need:
# asyncio.run(test_controlnet())
# asyncio.run(test())
asyncio.run(test_controlnet_with_ip_adapter("ml_pipeline/me.png"))