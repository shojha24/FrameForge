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
from fastapi import APIRouter
from settings import API_PREFIX
from schemas import StoryboardGenerationRequest, PanelRegenerationRequest, StoryboardResponse

router = APIRouter(prefix=API_PREFIX)

@router.post("/generate", response_model=StoryboardResponse)
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

@router.post("/regenerate", response_model=StoryboardResponse)
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