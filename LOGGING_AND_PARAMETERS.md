# FrameForge: Logging Architecture & Parameter Tuning

## Overview

This document summarizes all parameter tuning adjustments and comprehensive logging instrumentation added to the FrameForge MVP pipeline.

---

## Parameter Tuning (Team Testing)

Based on feedback from FrameForge team testing sessions, the following parameters have been calibrated:

### 1. Canvas Size (Image Generation)
- **Parameter**: `W`, `H` in `ml_pipeline/diffusion.py`
- **Value**: `1024 × 1024` (changed from `768 × 512`)
- **Rationale**: Team testing confirmed larger canvas provides better composition and detail without sacrificing speed on modern GPUs
- **File**: `ml_pipeline/diffusion.py` (lines 35-36)

### 2. IP-Adapter Scale (Character Consistency)
- **Default**: `0.4`
- **Range**: `0.3 - 0.7`
- **Location**: `ml_pipeline/diffusion.py` (line 45)
- **Per-panel Override**: Panels can specify `ip_adapter_scale` in their JSON to override default
- **Tuning Guidance**:
  - `0.3 - 0.4`: Photorealistic or naturally-proportioned human characters (default)
  - `0.5 - 0.6`: Stylized characters, anime, illustration styles
  - `0.6 - 0.7`: Highly stylized references where facial recognition is critical
- **Documented In**: `backend/settings.py` SYSTEM_PROMPT (lines 33-41)

### 3. ControlNet Conditioning Scale
- **Parameter**: `controlnet_conditioning_scale` in `ml_pipeline/diffusion.py`
- **Value**: `0.6`
- **Rationale**: Team testing showed 0.6 is the sweet spot:
  - `0.5`: Pose becomes too loose, character positioning vague
  - `0.6`: Best balance between pose fidelity and visual naturalness
  - `0.7+`: Composition becomes stiff, unnatural movement
- **File**: `ml_pipeline/diffusion.py` (line 44)

### 4. Inference Steps
- **Parameter**: `num_inference_steps` in `ml_pipeline/diffusion.py`
- **Value**: `25` (reduced from `30`)
- **Rationale**: Stress testing confirmed 25 steps produces good results without sacrificing quality; improves generation speed
- **File**: `ml_pipeline/diffusion.py` (line 46)

### 5. Guidance Scale
- **Parameter**: `guidance_scale` in `ml_pipeline/diffusion.py`
- **Value**: `7.5`
- **Rationale**: Confirmed good across all team test runs; remains unchanged
- **File**: `ml_pipeline/diffusion.py` (line 47)

---

## Comprehensive Logging Architecture

All major request stages are logged to the terminal session running the API with consistent formatting and section delimiters.

### Logging Format Conventions
- **Major Section Headers**: `[Module Name] Description` with `═` borders (80 chars wide)
- **Panel-by-panel separators**: `─` borders with `[Panel N/M]` marker
- **Status Indicators**:
  - `✅` Success
  - `❌` Error
  - `⚠️` Warning/Info

### 1. LLM Scene Decomposition (`ml_pipeline/panel_gen.py`)

**Function**: `decompose_scene()`

**Logged Data**:
```
================================================================================
[LLM Decomposer] Scene Decomposition Request
================================================================================
[Input]
  Scene: <first 100 chars of scene description>
  Target Panels: <number>

[LLM Call] Calling OpenRouter (nvidia/nemotron-3-nano-30b-a3b:free)...

[LLM Response] ✅ Successfully parsed N panels

[Panels Generated]
  Panel 1:
    Caption: <first 60 chars>
    Shot Type: <ECU|CU|MS|WS|ELS|OTS|POV>
    Camera Angle: <angle>
    Characters: [list]
    Pose Query: <first 60 chars>...
    Lighting: <mood>
    Background: <first 50 chars>...
    Action Note: <first 50 chars>...
  [Panel 2, 3, ...]

================================================================================
```

**Error Handling**:
- JSON parsing errors logged with first 200 chars of raw response
- Automatic retry with simplified prompt
- Full exception trace on final failure

### 2. Pipeline Orchestration (`ml_pipeline/pipeline.py`)

#### Full Generation (`run_full_generation()`)

**Logged Data**:
```
================================================================================
[Pipeline Orchestrator] Full Generation Request
================================================================================
[Request Summary]
  Scene: <first 100 chars>
  Panels: N
  Character Reference: Yes/No

[Pipeline] ✅ LLM generated N panels

[Pipeline] ✅ Loaded character reference: (W, H)

[Pipeline] Starting image generation for N panels...

[Pipeline] ✅ Generated N images

[Pipeline] Building SDXL prompts...
[Pipeline] ✅ Built N prompts

[Pipeline] Encoding images to base64...
[Pipeline] ✅ Encoded N images

================================================================================
[Pipeline Orchestrator] Generation Complete
================================================================================
```

#### Panel Regeneration (`run_panel_regeneration()`)

**Logged Data**:
```
================================================================================
[Pipeline Orchestrator] Panel Regeneration Request
================================================================================
[Panel Metadata]
  Caption: <first 60 chars>
  Shot Type: <type>
  Camera Angle: <angle>
  Characters: [list]

[Custom Prompt Override]
  <first 100 chars>...

[Pipeline] ✅ Loaded character reference: (W, H)

[Pipeline] Regenerating single panel...

[Pipeline] ✅ Regenerated panel successfully

================================================================================
[Pipeline Orchestrator] Regeneration Complete
================================================================================
```

### 3. Image Generation (`ml_pipeline/diffusion.py`)

**Function**: `generate_panels()`

**Global Status**:
```
================================================================================
[Diffusion] Starting generation of N panels
[Diffusion] Canvas: 1024×1024
[Diffusion] Parameters: steps=25, guidance=7.5, controlnet=0.6
[Diffusion] Character reference: Yes/No
================================================================================
```

**Per-Panel Generation**:
```
────────────────────────────────────────────────────────────────────────────────
[Diffusion] PANEL 1/N
────────────────────────────────────────────────────────────────────────────────

[Panel Metadata]
  Caption: <caption>
  Shot Type: <type>
  Camera Angle: <angle>
  Characters: [list]
  Position: <position>

[SDXL Prompt]
  <full cinematic prompt>

[Pose Retrieval]
  Query: <first 80 chars>...
  Position: <position>
  Camera Angle: <angle>
  Conditioning map ready: (1024, 1024)

[Generation Parameters]
  IP-Adapter Scale: 0.4 (or per-panel override)
  ControlNet Scale: 0.6
  Inference Steps: 25
  Guidance Scale: 7.5
  Canvas Size: 1024×1024

[Diffusion] ✅ Panel generated in 12.3 seconds

[Panel 2/N, ...]
```

**Error Handling**:
- OOM errors logged with fallback strategy
- Invalid character reference rejected with descriptive message
- Per-panel generation failures logged but don't halt entire batch

---

## Custom Prompt Override (Regeneration)

When a user regenerates a panel with a custom prompt override:

1. Frontend sends `custom_prompt` to `/frame-forge/api/regenerate`
2. Backend receives custom prompt and adds it to panel JSON as `_override_prompt`
3. `diffusion.build_sdxl_prompt()` checks for `_override_prompt` and returns it directly (bypassing auto-generation)
4. Full override prompt is logged in `[SDXL Prompt]` section

**Example**:
```
[SDXL Prompt]
  This is my custom hand-crafted prompt that I entered in the UI
```

---

## System Prompt Updates (`backend/settings.py`)

The SYSTEM_PROMPT has been updated to document the optional `ip_adapter_scale` field:

- **Lines 33-41**: New section "IP-Adapter Scale (Optional)"
- **Guidance**: When to use 0.3-0.4 vs 0.5-0.6 vs 0.6-0.7
- **Example Output**: Updated to include `ip_adapter_scale: 0.4` in sample JSON

This allows the LLM to optionally override the default scale per-panel based on the character reference type.

---

## Reading Logs During Development

When running the API locally (e.g., `python backend/main.py`), all logs appear in the terminal session:

### Full Generation Flow
```
python backend/main.py
# ... startup logs ...

# User hits /generate endpoint

[LLM Decomposer] Scene Decomposition Request
  ...

[Pipeline Orchestrator] Full Generation Request
  ...

[Diffusion] Starting generation of N panels
  PANEL 1/N
    [Panel Metadata]
    [SDXL Prompt]
    [Pose Retrieval]
    [Generation Parameters]
  PANEL 2/N
    ...

[Pipeline Orchestrator] Generation Complete
```

### Single Panel Regeneration Flow
```
# User clicks Regenerate on Panel 3

[Pipeline Orchestrator] Panel Regeneration Request
  [Panel Metadata]
  [Custom Prompt Override]

[Diffusion] Starting generation of 1 panel
  PANEL 1/1
    [SDXL Prompt]
    [Pose Retrieval]
    [Generation Parameters]

[Pipeline Orchestrator] Regeneration Complete
```

---

## Debugging Tips

### To trace a specific panel through the full pipeline:
1. Search logs for `[Panel Metadata]` → `Caption:`
2. Follow the same panel through `[Pose Retrieval]` and `[Generation Parameters]`
3. Look for `[Diffusion] ✅ Panel generated in X.X seconds`

### To verify parameter values are applied:
Search logs for `[Generation Parameters]` and confirm:
- `IP-Adapter Scale: 0.4` (or per-panel override)
- `ControlNet Scale: 0.6`
- `Inference Steps: 25`
- `Guidance Scale: 7.5`
- `Canvas Size: 1024×1024`

### To debug LLM output quality:
1. Check `[LLM Response]` section for parsing errors
2. Look at `[Panels Generated]` to see what fields the LLM actually returned
3. If characters are missing, check `[Panel Metadata]` Characters field
4. If pose is wrong, check `[Pose Retrieval]` Query field

---

## API Endpoints with Logging

### POST `/frame-forge/api/generate`
- Input: `scene_description`, `num_panels`, `character_image` (base64), `style_preset`
- Output: `panels`, `generated_images`, `sdxl_prompts`
- Logs: Full pipeline (decomposition + generation)

### POST `/frame-forge/api/regenerate`
- Input: `panel`, `custom_prompt`, `character_image` (base64)
- Output: `panel`, `custom_prompt`, `generated_image`
- Logs: Single panel regeneration with override

---

## Summary of Changes

| File | Changes | Lines |
|------|---------|-------|
| `ml_pipeline/diffusion.py` | Parameters tuned (W=1024, H=1024, controlnet=0.6, ip_adapter=0.4, steps=25), comprehensive panel-by-panel logging, _override_prompt handling in build_sdxl_prompt | 35-36, 44-47, 99-120, 174-360 |
| `ml_pipeline/panel_gen.py` | Comprehensive logging for LLM calls, JSON parsing, panel metadata | 18-103 |
| `ml_pipeline/pipeline.py` | Detailed logging for full generation and panel regeneration orchestration | 21-98, 101-157 |
| `backend/settings.py` | Updated SYSTEM_PROMPT to document optional ip_adapter_scale field | 17-68 |

All logging follows consistent formatting with section delimiters and status indicators for easy terminal visibility.
