"""
Pose Map Preprocessing Pipeline for FrameForge.

Implements the 2-stage pipeline from the documented specification:
Stage 1: Semantic pose retrieval via FAISS index
Stage 2: Preprocessing (tight crop, pad to square, scale by depth, place on canvas)

The final output is a 1024×1024 (or configurable size) black canvas with the
OpenPose skeleton sprite composited at the correct position and scale for
ControlNet-OpenPose conditioning.
"""

from PIL import Image
import numpy as np
from ml_pipeline import pose_search


def _tight_crop(img: Image.Image, threshold: int = 10) -> Image.Image:
    """
    Crop image to tight bounding box of non-black pixels.
    
    Uses threshold=10 to discard near-black compression artifacts.
    
    Args:
        img: Input PIL Image
        threshold: Pixel value threshold (0-255); pixels above this are "not black"
    
    Returns:
        Cropped PIL Image
    """
    img_array = np.array(img.convert("RGB"))
    # Find all non-black pixels
    nonblack_mask = np.any(img_array > threshold, axis=2)
    if not nonblack_mask.any():
        return img  # Entirely black; return as-is
    
    # Find bounding box
    rows, cols = np.where(nonblack_mask)
    y_min, y_max = rows.min(), rows.max() + 1
    x_min, x_max = cols.min(), cols.max() + 1
    
    # Crop
    cropped = img.crop((x_min, y_min, x_max, y_max))
    return cropped


def _pad_to_square(img: Image.Image) -> Image.Image:
    """
    Pad image to square with black padding (symmetric on shorter dimension).
    
    Args:
        img: Input PIL Image (already tight-cropped)
    
    Returns:
        Square PIL Image
    """
    w, h = img.size
    max_dim = max(w, h)
    
    # Calculate padding
    pad_left = (max_dim - w) // 2
    pad_right = max_dim - w - pad_left
    pad_top = (max_dim - h) // 2
    pad_bottom = max_dim - h - pad_top
    
    # Create square canvas and paste
    square = Image.new("RGB", (max_dim, max_dim), color=(0, 0, 0))
    square.paste(img, (pad_left, pad_top))
    return square


def _scale_by_depth(img: Image.Image, position_keyword: str) -> Image.Image:
    """
    Scale the skeleton sprite based on depth (foreground, midground, background).
    
    Scaling factors:
      foreground: 0.65  (large, close to camera)
      midground:  0.45  (medium)
      background: 0.28  (small, far from camera)
    
    Args:
        img: Square PIL Image from pad_to_square()
        position_keyword: Must contain 'foreground', 'midground', or 'background'
    
    Returns:
        Scaled PIL Image
    """
    position_lower = position_keyword.lower()
    
    if "foreground" in position_lower or "fg" in position_lower:
        scale = 0.65
    elif "midground" in position_lower or "mg" in position_lower:
        scale = 0.45
    elif "background" in position_lower or "bg" in position_lower:
        scale = 0.28
    else:
        scale = 0.45  # Default to midground
    
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return scaled


def _place_on_canvas(
    sprite: Image.Image,
    position_keyword: str,
    camera_angle: str,
    canvas_width: int = 640,
    canvas_height: int = 384
) -> Image.Image:
    """
    Composite the scaled skeleton sprite onto a canvas at the correct position.
    
    Position is determined by:
      - Horizontal: lateral component (left, center, right)
      - Vertical: depth component (foreground, midground, background) + camera angle shift
    
    Args:
        sprite: Scaled skeleton sprite
        position_keyword: e.g., "left foreground", "center midground"
        camera_angle: e.g., "Eye Level", "Low Angle", "High Angle"
        canvas_width: Output canvas width (default 640)
        canvas_height: Output canvas height (default 384)
    
    Returns:
        Canvas PIL Image with sprite composited
    """
    canvas = Image.new("RGB", (canvas_width, canvas_height), color=(0, 0, 0))
    
    # Determine horizontal position
    position_lower = position_keyword.lower()
    if "left" in position_lower:
        x_center = 0.25
    elif "right" in position_lower:
        x_center = 0.75
    else:  # center or default
        x_center = 0.50
    
    # Base vertical position by depth
    if "foreground" in position_lower or "fg" in position_lower:
        y_center = 0.70
    elif "background" in position_lower or "bg" in position_lower:
        y_center = 0.40
    else:  # midground or default
        y_center = 0.55
    
    # Camera angle adjustment
    camera_lower = camera_angle.lower()
    if "low" in camera_lower:
        y_shift = 0.12  # Lower in frame, more headroom above
    elif "high" in camera_lower:
        y_shift = -0.12  # Higher in frame, more floor below
    else:  # eye level or default
        y_shift = 0.0
    
    y_center += y_shift
    
    # Calculate pixel positions (center of sprite at x_center, y_center)
    x_pixel = int(x_center * canvas_width - sprite.width // 2)
    y_pixel = int(y_center * canvas_height - sprite.height // 2)
    
    # Clamp to canvas bounds
    x_pixel = max(0, min(x_pixel, canvas_width - sprite.width))
    y_pixel = max(0, min(y_pixel, canvas_height - sprite.height))
    
    # Composite
    canvas.paste(sprite, (x_pixel, y_pixel))
    return canvas


def build_pose_map(
    pose_img: Image.Image,
    position_keyword: str,
    camera_angle: str,
    canvas_width: int = 640,
    canvas_height: int = 384
) -> Image.Image:
    """
    Run the full 4-step preprocessing pipeline on a skeleton image.
    
    Steps:
    1. Tight crop (remove black padding)
    2. Pad to square
    3. Scale by depth
    4. Place on canvas
    
    Args:
        pose_img: Input OpenPose skeleton image
        position_keyword: e.g., "left foreground", "center midground"
        camera_angle: e.g., "Eye Level", "Low Angle", "High Angle"
        canvas_width: Output canvas width (default 640)
        canvas_height: Output canvas height (default 384)
    
    Returns:
        Final canvas PIL Image ready for ControlNet-OpenPose conditioning
    """
    # Step 1: Tight crop
    cropped = _tight_crop(pose_img, threshold=10)
    
    # Step 2: Pad to square
    squared = _pad_to_square(cropped)
    
    # Step 3: Scale by depth
    scaled = _scale_by_depth(squared, position_keyword)
    
    # Step 4: Place on canvas
    canvas = _place_on_canvas(scaled, position_keyword, camera_angle, canvas_width=canvas_width, canvas_height=canvas_height)
    
    return canvas


def get_conditioning_map(
    pose_query: str,
    position_keyword: str,
    camera_angle: str,
    canvas_width: int = 640,
    canvas_height: int = 384,
    hf_token: str = None
) -> Image.Image:
    """
    Convenience wrapper: retrieve pose + preprocess in one call.
    
    This is the PRIMARY ENTRY POINT called by diffusion.py.
    
    Args:
        pose_query: Naturalistic description of pose
        position_keyword: Spatial position on canvas
        camera_angle: Camera angle for vertical adjustment
        canvas_width: Output canvas width (default 640)
        canvas_height: Output canvas height (default 384)
        hf_token: HuggingFace token (required on first run)
    
    Returns:
        Final conditioning canvas ready for ControlNet-OpenPose
    """
    # Stage 1: Retrieve skeleton image via semantic search
    try:
        skeleton_img = pose_search.retrieve_pose(pose_query, top_k=1, hf_token=hf_token)
    except Exception as e:
        print(f"[Warning] Pose search failed: {e}. Skipping pose conditioning.")
        return None
    
    # Stage 2: Preprocess
    conditioning_map = build_pose_map(skeleton_img, position_keyword, camera_angle, canvas_width=canvas_width, canvas_height=canvas_height)
    
    return conditioning_map