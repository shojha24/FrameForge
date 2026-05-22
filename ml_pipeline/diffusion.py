"""
Core Image Generation Pipeline (SDXL + ControlNet + IP-Adapter).

This module manages the heavy lifting of image synthesis. It moves away from 
MiDaS depth estimation (which requires manual layout sketches) and instead relies 
on programmatic spatial mapping. 

It takes structured character positions from the LLM, encodes them into a 
color-coded PIL canvas, and uses a Semantic Segmentation ControlNet 
(or GLIGEN) to strictly enforce the composition and protagonist placement 
before generation.
"""

from PIL import Image, ImageDraw
import time

# helpers
def get_depth_map(image: Image.Image) -> Image.Image:
    """Run MiDaS on an image and return a depth map as a PIL Image."""
    image = image.convert("RGB")
    depth_out = depth_estimator(image)
    depth_np  = np.array(depth_out["depth"])
    # Normalize to 0-255
    depth_np  = (depth_np - depth_np.min()) / (depth_np.max() - depth_np.min() + 1e-8)
    depth_np  = (depth_np * 255).astype(np.uint8)
    # ControlNet expects a 3-channel image
    depth_img = Image.fromarray(depth_np).convert("RGB")
    depth_img = depth_img.resize(image.size)
    return depth_img

def get_pose_map(image: Image.Image) -> Image.Image:
    """Run OpenPose on an image and return a pose skeleton as a PIL Image."""
    image = image.convert("RGB")
    pose_img = pose_detector(image)
    return pose_img.resize(image.size)

def _encode_spatial_map(panel_json: dict, width: int = 1024, height: int = 1024) -> Image.Image:
    """
    Programmatically generates a semantic segmentation map using PIL.
    
    Reads the `characters` list and their `position_keyword` (e.g., "left foreground", 
    "center medium") from the `panel_json`. Maps these natural language keywords to 
    pre-defined bounding box coordinates on a blank black PIL canvas. Draws solid 
    colored rectangles (using standard ADE20K segmentation hex codes for "person") 
    at those coordinates.
    
    This generated map guarantees the protagonist is forced into the correct 
    compositional space by the ControlNet.
    
    Args:
        panel_json (dict): The structured data containing character positioning.
        width (int): Output map width.
        height (int): Output map height.
        
    Returns:
        Image.Image: A color-coded PIL image acting as the spatial condition map.
    """

    chars = panel_json.get("characters", [])
    ref_image = None
    for c in chars:
        if img:=c.get("reference_image"):
            ref_image = image
            break
    if ref_image = None:
        blank = Image.fromarray(np.zeros((height, width, 3), dtype=np.uint8))
        return blank, blank

    ref_image = ref_image.resize((width, height))
    depth_map = get_depth_map(ref_image)
    pose_map = get_pose_map(ref_image)
    return depth_map, pose_map


def build_sdxl_prompt(panel_json: dict, visual_style: str) -> str:
    """
    take panel JSON, turn into string (key, value)
    Translates the structural panel JSON into a comma-separated SDXL text prompt.
    
    Args:
        panel_json (dict): The metadata for a single panel.
        visual_style (str): The chosen aesthetic keyword.
        
    Returns:
        str: A highly optimized, cinematic text prompt ready for SDXL.
    """
    parts = [
        visual_style
        panel_json.get("action_note", ""),
        f"{panel_json.get('shot_type', '')} shot",
        f"{panel_json.get('camera_angle', '')} angle",
        f"background: {panel_json.get('background', '')}",
        f"lighting: {panel_json.get('lighting_mood', '')}",
    ]
    chars = panel_json.get("characters", [])
    for c in chars:
        parts.append(f"{c.get('name','character')} {c.get('position','')}")
    prompt = ", ".join(p for p in parts if p.strip(", "))
    prompt += ", cinematic storyboard panel, highly detailed"
    return prompt

def generate_panels(panel_jsons: list[dict], ip_adapter_image: Image.Image = None) -> list[Image.Image]:
    """
    Executes the diffusion generation loop for an array of panels.
    
    For each panel in the provided list:
    1. Calls `_encode_spatial_map()` to programmatically build the composition map.
    2. Calls `build_sdxl_prompt()` to construct the text conditioning.
    3. Feeds the prompt, the PIL spatial map, and the `ip_adapter_image` into the 
       SDXL + ControlNet(Seg) + IP-Adapter pipeline.
       
    Args:
        panel_jsons (list[dict]): The structural data for the batch of panels.
        ip_adapter_image (PIL.Image, optional): The reference face for the protagonist.
        
    Returns:
        list[Image.Image]: The final rendered storyboard panel images.
    """
    # pass

    # Handle IP-Adapter
    if ip_adapter_image is not None:
        pipe.set_ip_adapter_scale(ip_adapter_scale)
    else:
        pipe.set_ip_adapter_scale(0.0)
        ip_adapter_image = Image.fromarray(np.zeros((224, 224, 3), dtype=np.uint8))

    generated_panels = []
    panel_titles = []

    for i, panel_json in enumerate(panel_jsons):
        prompt = build_sdxl_prompt(panel_json, visual_style=visual_style)
        depth_map, pose_map = _encode_spatial_map(panel_json, width=W, height=H)
        print(f"\n🎨 Generating panel {i+1}/{len(panel_jsons)}...")
        print(f"   Prompt: {prompt[:80]}...")

        t0 = time.time()

        result = pipe(
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            image=[depth_map, pose_map],
            ip_adapter_image=ip_adapter_image,
            controlnet_conditioning_scale=[
                controlnet_depth_scale,
                controlnet_pose_scale,
            ],
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=W, height=H,
            generator=torch.manual_seed(42 + i),
        )

        elapsed = time.time() - t0
        img = result.images[0]
        generated_panels.append(img)

        shot_type  = panel_json.get("shot_type", "")
        camera_angle = panel_json.get("camera_angle", "")
        panel_titles.append(f"Panel {i+1}: {shot_type} / {camera_angle}")
        print(f"   ✅ Done in {elapsed:.1f}s")

    print("\n🎬 All panels generated!")
    show_panels(generated_panels, panel_titles)
    return generated_panels