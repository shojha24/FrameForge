"""
LLM Scene Decomposition Module.

Handles LLM calls to decompose scenes into structured panel JSON arrays.
"""

import json
import httpx
import sys
import os

# Ensure backend is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from settings import OPEN_ROUTER_API_KEY, SYSTEM_PROMPT


async def decompose_scene(scene_prompt: str, num_panels: int, visual_style: str) -> list[dict]:
    """
    Call OpenRouter LLM to decompose scene into panel JSON array.
    
    Args:
        scene_prompt (str): Plain English scene description
        num_panels (int): Number of panels to generate
        visual_style (str): Visual style for generation
    
    Returns:
        list[dict]: Array of panel objects with fields:
          - caption, shot_type, camera_angle, characters, pose_query,
            lighting_mood, background, action_note
    
    Raises:
        Exception: If LLM returns invalid JSON or API call fails
    """
    async with httpx.AsyncClient() as client:
        user_prompt = f"Panel Count: {num_panels} Scene Description: {scene_prompt} Visual Style: {visual_style}"
        
        print(f"\n{'='*80}")
        print(f"[LLM Decomposer] Scene Decomposition Request")
        print(f"{'='*80}")
        print(f"[Input]")
        print(f"  Scene: {scene_prompt[:100]}{'...' if len(scene_prompt) > 100 else ''}")
        print(f"  Target Panels: {num_panels}")
        
        try:
            print(f"\n[LLM Call] Calling OpenRouter (nvidia/nemotron-3-nano-30b-a3b:free)...")
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
                timeout=60.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content
            content = data['choices'][0]['message']['content']
            
            # Parse JSON
            panel_jsons = json.loads(content)
            print(f"\n[LLM Response] ✅ Successfully parsed {len(panel_jsons)} panels")

            if panel_jsons:
                protagonist_name = (
                    panel_jsons[0].get("characters", [{}])[0].get("name", "")
                )
                if protagonist_name:
                    for panel in panel_jsons[1:]:
                        chars = panel.get("characters", [])
                        if chars:
                            chars[0]["name"] = protagonist_name  # overwrite drift
            
            # Log each panel
            print(f"\n[Panels Generated]")
            for idx, panel in enumerate(panel_jsons, 1):
                print(f"  Panel {idx}:")
                print(f"    Caption: {panel.get('caption', 'N/A')[:60]}")
                print(f"    Shot Type: {panel.get('shot_type', 'N/A')}")
                print(f"    Camera Angle: {panel.get('camera_angle', 'N/A')}")
                print(f"    Characters: {panel.get('characters', [])}")
                print(f"    Pose Query: {panel.get('pose_query', 'N/A')[:60]}...")
                print(f"    Lighting: {panel.get('lighting_mood', 'N/A')}")
                print(f"    Background: {panel.get('background', 'N/A')[:50]}...")
                print(f"    Action Note: {panel.get('action_note', 'N/A')[:50]}...")
            
            print(f"\n{'='*80}")
            return panel_jsons
            
        except json.JSONDecodeError as e:
            print(f"\n[LLM Response] ❌ Invalid JSON received: {e}")
            print(f"[LLM Response] Raw content (first 200 chars): {content[:200]}")
            # Retry once with a simpler prompt
            try:
                print(f"\n[LLM Decomposer] Retrying with simplified prompt...")
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a JSON generator. Return ONLY a valid JSON array. No markdown, no explanation."
                            },
                            {
                                "role": "user",
                                "content": f"Generate exactly {num_panels} JSON panel objects with these exact fields: caption (string), shot_type (ECU|CU|MS|WS|ELS|OTS|POV), camera_angle (Eye Level|High Angle|Low Angle|Bird's-Eye View|Worm's-Eye View|Dutch Angle|Ground Level), characters (array of {{name, position}}), pose_query (string), lighting_mood (string), background (string), action_note (string). Scene: {scene_prompt}"
                            }
                        ],
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data['choices'][0]['message']['content']
                panel_jsons = json.loads(content)
                print(f"[LLM Decomposer] ✅ Retry succeeded! Generated {len(panel_jsons)} panels")
                return panel_jsons
            except Exception as retry_error:
                print(f"[LLM Decomposer] ❌ Retry also failed: {retry_error}")
                raise
                
        except Exception as e:
            print(f"[LLM Decomposer] ❌ API Error: {e}")
            raise