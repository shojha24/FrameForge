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
from fastapi import APIRouter, HTTPException
import json
import httpx

from settings import API_PREFIX, OPEN_ROUTER_API_KEY, SYSTEM_PROMPT
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

    panel_jsons = await generate_storyboard_panel_json(request.scene_prompt, request.num_panels, request.visual_style)

    return StoryboardResponse(panel_jsons=panel_jsons)

async def generate_storyboard_panel_json(prompt: str = "", num_panels: int = 1, visual_style: str = "None"):
    async with httpx.AsyncClient() as client:
        print("Calling Scene Decomposer LLM...")
        user_prompt = f"Panel Count: {num_panels} Scene Description: {prompt}"

        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "nvidia/nemotron-3-nano-30b-a3b:free",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                },
                timeout=60.0  # LLMs take time, don't let it timeout too early
            )

            response.raise_for_status()
            data = response.json()

            # Extract content
            content = data['choices'][0]['message']['content']

            # Convert JSON string to List of Dicts
            panel_jsons = json.loads(content)
            for panel in panel_jsons:
                panel["style"] = visual_style
            print("Panels Created Successfully")
            return panel_jsons
        except json.JSONDecodeError:
            # LLMs sometimes hallucinate text around the JSON
            print("Error: LLM returned invalid JSON")
            raise HTTPException(status_code=500, detail="LLM output was not valid JSON")
        except Exception as e:
            print(f"API Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

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