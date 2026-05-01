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

class StoryboardGenerationRequest(BaseModel):
    """
    Schema for the initial full storyboard generation request.
    
    Attributes:
        scene_prompt (str): The plain-English description of the scene.
        visual_style (str): The requested cinematic style keyword (e.g., "noir", "anime").
        ip_adapter_image (str): Base64 encoded image or URL of the protagonist reference face.
        num_panels (int): The number of panels to generate for this scene.
    """
    pass

class PanelRegenerationRequest(BaseModel):
    """
    Schema for an isolated panel regeneration request.
    
    Attributes:
        panel_json (dict): The edited or original structured metadata for a single panel.
        custom_prompt (str): The manually overridden SDXL text prompt.
        ip_adapter_image (str): Base64 encoded image or URL of the protagonist reference face.
    """
    pass

class StoryboardResponse(BaseModel):
    """
    Schema for the successful return of storyboard data to the frontend.
    
    Attributes:
        panel_jsons (List[dict]): The LLM-generated structural metadata for each panel.
        sdxl_prompts (List[str]): The exact text prompts fed into the diffusion model.
        generated_images (List[str]): Base64 encoded strings of the final output images.
    """
    pass

@app.post("/generate", response_model=StoryboardResponse)
async def generate_storyboard(request: StoryboardGenerationRequest):
    """
    Initializes the full scene-to-storyboard generation pipeline.
    
    Validates the incoming scene text and reference imagery, then passes the 
    data to the orchestrator (`pipeline.py`). Returns the structured metadata, 
    the prompts used, and the generated images.
    
    Args:
        request (StoryboardGenerationRequest): The user's scene and style inputs.
        
    Returns:
        StoryboardResponse: The fully generated storyboard payload.
    """
    pass

@app.post("/regenerate", response_model=StoryboardResponse)
async def regenerate_panel(request: PanelRegenerationRequest):
    """
    Regenerates a single specific panel without affecting the rest of the storyboard.
    
    Bypasses the LLM scene decomposer and feeds the user's updated panel JSON 
    and prompt directly into the diffusion pipeline via the orchestrator.
    
    Args:
        request (PanelRegenerationRequest): The updated constraints for the target panel.
        
    Returns:
        StoryboardResponse: A payload containing just the single regenerated image 
                            and its associated metadata.
    """
    pass