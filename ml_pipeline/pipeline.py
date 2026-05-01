"""
Pipeline Orchestrator.

This module coordinates the data flow between the API routing layer (`api.py`), 
the LLM decomposer (`panel_gen.py`), and the diffusion engine (`diffusion.py`). 
It handles data formatting, error catching, and the separation of logic between 
full batch generation and single-panel regeneration.
"""

def run_full_generation(scene_prompt: str, visual_style: str, num_panels: int, ip_image_data: str = None) -> dict:
    """
    Orchestrates the end-to-end creation of a completely new storyboard.
    
    Steps:
    1. Passes the raw text to `panel_gen.decompose_scene()`.
    2. Decodes the base64 `ip_image_data` into a PIL Image.
    3. Passes the resulting JSON array and PIL image to `diffusion.generate_panels()`.
    4. Gathers the returned images, compiles the exact text prompts used, and 
       formats everything into a dictionary ready for the API to return.
       
    Args:
        scene_prompt (str): Raw scene text.
        visual_style (str): Chosen aesthetic.
        num_panels (int): Number of panels to generate.
        ip_image_data (str, optional): Base64 encoded character reference.
        
    Returns:
        dict: A payload containing lists of `panel_jsons`, `sdxl_prompts`, and `generated_images`.
    """
    pass

def run_panel_regeneration(panel_json: dict, custom_prompt: str, ip_image_data: str = None) -> dict:
    """
    Orchestrates the targeted regeneration of a single edited panel.
    
    Bypasses the LLM generation step (`panel_gen.py`). Parses the edited `panel_json` 
    to generate a fresh spatial layout map. Overrides the auto-prompt generator with 
    the `custom_prompt` provided by the user. Feeds the data directly to the 
    diffusion pipeline.
    
    Args:
        panel_json (dict): The user-edited metadata for the specific panel.
        custom_prompt (str): The exact prompt to use for generation.
        ip_image_data (str, optional): Base64 encoded character reference.
        
    Returns:
        dict: A payload containing the single new `panel_json`, `custom_prompt`, 
              and the single new `generated_image`.
    """
    pass