"""
API Routing and Schema Definitions for FrameForge.

This module uses FastAPI and Pydantic to define the strict contracts for input
and output data. It exposes the primary endpoints for full storyboard generation
and isolated panel regeneration, acting as the interface between the client UI
and the internal generation pipeline.

Dependencies:
    - FastAPI (for routing)
    - Pydantic (for input/output validation schemas)
    - typing.List, typing.Optional
"""
from pydantic import BaseModel, Base64Str

class StoryboardGenerationRequest(BaseModel):
    """
    Schema for the initial full storyboard generation request.

    Attributes:
        scene_prompt (str): The plain-English description of the scene.
        visual_style (str): The requested cinematic style keyword (e.g., "noir", "anime").
        ip_adapter_image (str): Base64 encoded image or URL of the protagonist reference face.
        num_panels (int): The number of panels to generate for this scene.
    """
    scene_prompt: str
    visual_style: str
    ip_adapter_image: Base64Str = ""
    num_panels: int


class PanelRegenerationRequest(BaseModel):
    """
    Schema for an isolated panel regeneration request.

    Attributes:
        panel_json (dict): The edited or original structured metadata for a single panel.
        custom_prompt (str): The manually overridden SDXL text prompt.
        ip_adapter_image (str): Base64 encoded image or URL of the protagonist reference face.
    """
    panel_json: dict
    custom_prompt: str
    ip_adapter_image: Base64Str = ""



class StoryboardResponse(BaseModel):
    """
    Schema for the successful return of storyboard data to the frontend.

    Attributes:
        panel_jsons (List[dict]): The LLM-generated structural metadata for each panel.
        sdxl_prompts (List[str]): The exact text prompts fed into the diffusion model.
        generated_images (List[str]): Base64 encoded strings of the final output images.
    """
    panel_jsons: list[dict]
    sdxl_prompts: list[str]
    generated_images: list[str]
