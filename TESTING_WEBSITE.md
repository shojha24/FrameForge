# FrameForge: Website UI Testing Guide

Complete walkthrough of testing the FrameForge website (React frontend) from start to finish.

---

## Setup: Start All Services

Open **3 separate terminal windows**:

### Terminal 1: Backend API
```bash
cd path/to/FrameForge
python backend/main.py
```

Wait for:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Frontend Dev Server
```bash
cd path/to/FrameForge/frontend
npm start
```

Wait for:
```
Compiled successfully!

You can now view frameforge in the browser.

  Local:            http://localhost:3000
```

### Terminal 3: Log Monitor (Optional)
Keep this terminal ready to monitor backend logs (watch Terminal 1 here).

---

## Part 1: First-Time Setup & Validation

### Step 1: Open the Website

In your browser, navigate to:
```
http://localhost:3000
```

**Expected to see:**
- FrameForge header/title
- Text input field labeled "Scene Description"
- Button to upload character reference image
- Style preset dropdown (Cinematic, Comic Book, etc.)
- "Generate Storyboard" button
- Area for generated panels below
- "Export to PDF" button (initially disabled)

**Check browser console (F12) for errors:**
- Should be clean (no red errors)
- May have warnings (normal for dev server)

### Step 2: Verify API Connection

The website should auto-detect the backend at startup.

**Check:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh the page
4. Look for a request to `http://localhost:8000/frame-forge/api/health`
5. Status should be `200 OK`

If you see CORS error:
```
Access to XMLHttpRequest ... has been blocked by CORS policy
```
→ Backend CORS isn't configured for `http://localhost:3000`. Fix in `backend/settings.py`:
```python
ORIGINS = [
    "http://localhost:3000",
]
```

---

## Part 2: Basic Generation Flow

### Step 3: Enter Scene Description

Click in the text area and type a detailed scene (3-4 sentences):

**Example 1 (Cinematic):**
```
A warrior stands atop a cliff overlooking a vast kingdom. 
Dark clouds gather above as an enemy army approaches from the distance. 
The warrior draws their sword with determination. 
Thunder crashes as they prepare for battle.
```

**Example 2 (Mystery):**
```
A detective walks into a dimly lit warehouse late at night.
Shadows dance across the walls from a flickering neon sign.
She notices fresh footprints in the dust on the floor.
A mysterious silhouette appears in the darkness ahead.
```

**Example 3 (Fantasy):**
```
A young apprentice discovers a hidden portal in the forest.
Magical runes glow softly around the entrance.
Strange creatures peek curiously from the trees.
The apprentice takes a deep breath and steps through.
```

**Expected behavior:**
- Text appears in input field
- No validation errors
- Character count shows (optional)

### Step 4: Upload Character Reference Image

Click **"Upload Character Reference"** button.

**File dialog opens:**
- Select any portrait image (JPEG, PNG, or WebP)
- Recommended: 512×512 to 1024×1024 pixels
- Any person or character (realistic, stylized, anime, etc.)

**Expected:**
- File name appears in UI
- Thumbnail preview shows (if implemented)
- No "Invalid image" error

**Try with different character types:**
1. Realistic portrait (e.g., actor photo)
2. Stylized illustration (e.g., animated character)
3. Anime character art
4. Fantasy character (drawn)

Note the differences in how IP-Adapter scale adapts!

### Step 5: Select Style Preset

Click the **"Style Preset"** dropdown.

**Options should include:**
- Cinematic (default)
- Comic Book
- Storyboard (maybe)
- Others based on your implementation

**Select:** "Cinematic" for now

**Expected:**
- Dropdown closes
- Selected style shows

### Step 6: Request Number of Panels

In the UI, there should be a control for **"Number of Panels"** (or similar).

**Try:**
- Start with 2 panels (fastest to test)
- Later try 3-5 panels

**Expected:**
- Input accepts 1-10 (or your defined range)
- No validation errors

### Step 7: Click "Generate Storyboard"

Click the **"Generate Storyboard"** button.

**Expected immediately:**
- Button becomes disabled
- Loading spinner appears
- Status message: "Generating panels..." (or similar)

**In Terminal 1 (Backend), watch for:**
```
================================================================================
[LLM Decomposer] Scene Decomposition Request
================================================================================
[Input]
  Scene: A warrior stands atop a cliff...
  Target Panels: 2

[LLM Call] Calling OpenRouter...

[LLM Response] ✅ Successfully parsed 2 panels

[Panels Generated]
  Panel 1:
    Caption: Warrior prepares for battle
    Shot Type: WS
    Camera Angle: Eye Level
    Characters: [{'name': 'Warrior', 'position': 'center'}]
    Pose Query: A warrior standing upright with sword raised...
    ...

================================================================================
[Pipeline Orchestrator] Full Generation Request
================================================================================
...
```

Keep watching as generation progresses!

---

## Part 3: Monitor Generation Progress

### Watch Terminal 1 for All Stages

As generation runs, you should see in order:

**Stage 1: LLM Decomposition** (5-10 seconds)
```
[LLM Decomposer] Scene Decomposition Request
[LLM Response] ✅ Successfully parsed N panels
[Panels Generated]
```

**Stage 2: Pipeline Orchestration Starts** (0-1 seconds)
```
[Pipeline Orchestrator] Full Generation Request
[Request Summary]
  Scene: ...
  Panels: 2
  Character Reference: Yes
[Pipeline] ✅ LLM generated 2 panels
[Pipeline] ✅ Loaded character reference: (512, 512)
```

**Stage 3: Image Generation** (30-60 seconds for 2 panels)
```
[Pipeline] Starting image generation for 2 panels...

[Diffusion] Starting generation of 2 panels
[Diffusion] Canvas: 1024×1024
[Diffusion] Parameters: steps=25, guidance=7.5, controlnet=0.6
[Diffusion] Character reference: Yes

────────────────────────────────────────────────────────────────────────────────
[Diffusion] PANEL 1/2
────────────────────────────────────────────────────────────────────────────────
[Panel Metadata]
  Caption: Warrior prepares for battle
  Shot Type: WS
  Camera Angle: Eye Level
  Characters: [{'name': 'Warrior', 'position': 'center'}]
  Position: center midground

[SDXL Prompt]
  wide shot, full body and environment, eye level, character: Warrior standing upright with sword raised, lighting: golden dawn, background: cliff overlooking kingdom, Warrior in center, A warrior stands with confidence at the edge of the cliff. Thunder crashes around him., cinematic storyboard panel, highly detailed, professional lighting, vibrant colors

[Pose Retrieval]
  Query: A warrior standing upright with sword raised above head...
  Position: center
  Camera Angle: Eye Level
  Conditioning map ready: (1024, 1024)

[Generation Parameters]
  IP-Adapter Scale: 0.4
  ControlNet Scale: 0.6
  Inference Steps: 25
  Guidance Scale: 7.5
  Canvas Size: 1024×1024

[Diffusion] ✅ Panel generated in 18.2 seconds

────────────────────────────────────────────────────────────────────────────────
[Diffusion] PANEL 2/2
────────────────────────────────────────────────────────────────────────────────
[Panel Metadata]
  Caption: Enemy army approaches
  Shot Type: ELS
  Camera Angle: High Angle
  Characters: [{'name': 'Warrior', 'position': 'center'}, {'name': 'Enemy Army', 'position': 'background'}]
  Position: center background

[SDXL Prompt]
  ...

[Diffusion] ✅ Panel generated in 19.1 seconds

[Pipeline] ✅ Generated 2 images

================================================================================
[Pipeline Orchestrator] Generation Complete
================================================================================
```

### Key Things to Verify in Logs:

✅ **Canvas Size:** Should be `1024×1024` (not 768×512)
✅ **Inference Steps:** Should be `25`
✅ **ControlNet Scale:** Should be `0.6`
✅ **IP-Adapter Scale:** Should be `0.4` (or per-panel override)
✅ **Guidance Scale:** Should be `7.5`
✅ **Timing:** Each panel ~15-25 seconds (depends on GPU)
✅ **SDXL Prompts:** Full sentences, specific framing and character details
✅ **Character Consistency:** Character names correct, positions logical

---

## Part 4: View Generated Panels in UI

### After Generation Completes

**In browser, you should see:**

1. **Panel Grid** appears below input
   - 2 panels displayed (in your case)
   - Each has a generated image
   - Shot type label below each (e.g., "WS", "ELS")
   - Caption below label (e.g., "Warrior prepares for battle")

2. **Generate button re-enables**

3. **Export to PDF button becomes enabled**

**Expected panel layout:**
```
┌─────────────────────────────────────────────────────────┐
│  [Generated Image 1]      [Generated Image 2]           │
│                                                         │
│  WS                       ELS                           │
│  Warrior prepares         Enemy army approaches         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Inspect Image Quality

Look at the generated images:

**Good signs:**
- ✅ Character is recognizable from reference image
- ✅ Character pose matches the pose_query description
- ✅ Shot type is honored (wide shot shows full body + environment)
- ✅ Lighting/mood matches the description
- ✅ Background matches the scene description
- ✅ Colors are vibrant, not washed out

**Issues to report:**
- ❌ Character is distorted or unrecognizable
- ❌ Pose is completely wrong (e.g., standing when should be kneeling)
- ❌ Image is blurry or low quality
- ❌ Background doesn't match description
- ❌ Text/watermarks present (should be clean)

---

## Part 5: Test Drag-to-Reorder Panels

### Click and Drag Panel 1 to Position 2

1. **Hover over Panel 1 image** — should see visual hint (highlight or drag handle)
2. **Click and hold on Panel 1**
3. **Drag it to the right, over Panel 2**
4. **Release mouse**

**Expected:**
- ✅ Panels swap order
- ✅ Panel 1 becomes Panel 2, Panel 2 becomes Panel 1
- ✅ Both panels still have correct images and labels

**Try again:**
- Drag Panel 2 back to position 1 to restore original order

---

## Part 6: Test Single Panel Regeneration

### Click on a Panel Image to Open Editor

1. **Click on Panel 1 image**

**Expected:**
- Sidebar or drawer opens on the right
- Shows panel metadata:
  - Caption (editable)
  - Shot Type selector (editable)
  - Camera Angle selector
  - Custom Prompt field (editable text area)
  - Other fields

### Edit the Custom Prompt

In the prompt field, replace or add to the auto-generated prompt:

**Example override:**
```
A massive warrior standing defiantly on a windswept cliff, 
extreme close-up on determined face, 
dramatic storm clouds gathering behind, 
golden lightning illuminating features, 
intense cinematic lighting, 
photorealistic style, 
4K quality, 
highly detailed
```

### Click "Regenerate" Button

**In browser:**
- Sidebar shows "Regenerating..."
- Loading spinner appears

**In Terminal 1 (Backend), watch for:**
```
================================================================================
[Pipeline Orchestrator] Panel Regeneration Request
================================================================================
[Panel Metadata]
  Caption: Warrior prepares for battle
  Shot Type: WS
  Camera Angle: Eye Level
  Characters: [{'name': 'Warrior', 'position': 'center'}]

[Custom Prompt Override]
  A massive warrior standing defiantly on a windswept cliff...

[Pipeline] ✅ Loaded character reference: (512, 512)

[Pipeline] Regenerating single panel...

[Diffusion] Starting generation of 1 panel
  ────────────────────────────────────────────────────────
  [Diffusion] PANEL 1/1
  ────────────────────────────────────────────────────────
  [SDXL Prompt]
    A massive warrior standing defiantly on a windswept cliff...

  [Diffusion] ✅ Panel generated in 18.5 seconds

[Pipeline Orchestrator] Regeneration Complete
================================================================================
```

### Verify Only Panel 1 Updated

**Expected:**
- ✅ Only Panel 1 image changes
- ✅ Panel 2 image remains unchanged
- ✅ Both panels still visible in grid

**Try editing Panel 2:**
- Click on Panel 2
- Change its prompt
- Regenerate
- Verify only Panel 2 updates

---

## Part 7: Test Style Preset Changes

### Regenerate Same Panels with Different Style

1. **Go back to input area**
2. **Change Style Preset to "Comic Book"** (or alternative)
3. **Click "Generate Storyboard" again** with same scene and character

**Expected:**
- New generation starts
- Images have comic book style (bolder colors, more illustrative, comic panel borders maybe)
- Same character, different visual treatment
- Logging shows new generation cycle

**Try with:**
- Cinematic (default)
- Comic Book (bold, stylized)
- Storyboard (flat, simple)
- Any other presets you implemented

---

## Part 8: Test With Different Character References

### Upload New Character Image

1. **Click "Change Character Reference"** (or re-upload)
2. **Select a different person/character** (anime, realistic, illustration, etc.)
3. **Generate with same scene**

**Expected:**
- Images show different character
- Character is still consistent across panels
- Same character type used in both panels

**Try with:**
- Realistic portrait (human actor/photo)
- Anime character
- Stylized illustration
- 3D rendered character

**Monitor IP-Adapter scale in logs:**
- Realistic human: should be 0.4 (default)
- If LLM specified different scale (0.5-0.6), logs show per-panel override

---

## Part 9: Test PDF Export

### Generate Final Storyboard

1. **Generate a 3-4 panel storyboard** with your preferred settings
2. Wait for all panels to complete

### Click "Export to PDF"

**Expected:**
- File download starts
- Downloads to your Downloads folder as `storyboard.pdf` (or similar)
- No errors in browser console

### Open the PDF

**Expected layout:**
- Title page with scene description
- Generation date/time
- 2-3 panels per row
- Each panel shows:
  - Generated image
  - Shot type label (WS, CU, etc.)
  - Caption
  - Action note
- Page breaks as needed for multiple rows
- Professional looking layout

**Verify:**
- ✅ All panels present
- ✅ All images render in PDF
- ✅ Text is readable
- ✅ Layout doesn't have text overlaps
- ✅ File size reasonable (~5-20MB depending on resolution)

---

## Part 10: Test Edge Cases

### Test 1: Clear and Regenerate

1. **Clear the scene text** (empty input)
2. **Try to generate**

**Expected:**
- Either validation error: "Please enter a scene"
- Or graceful handling without crash

### Test 2: Generate Without Character Reference

1. **Remove character reference** (or skip upload)
2. **Generate storyboard**

**Expected:**
- ✅ Generation succeeds
- ✅ Images generated anyway (no character consistency focus)
- ✅ In logs: `[Diffusion] Character reference: No`
- ✅ Images may be less consistent across panels but still valid

### Test 3: Rapid Successive Requests

1. **Generate 2 panels**
2. **While generating, click Generate again** (don't wait for first to finish)

**Expected:**
- Second request queues or first completes before second starts
- No crash or weird behavior
- Backend handles gracefully

### Test 4: Very Long Scene Description

1. **Paste a very long scene** (5+ paragraphs)
2. **Generate**

**Expected:**
- ✅ Accepted (may truncate in logs but works)
- ✅ Generation completes
- ✅ LLM handles long context

### Test 5: Unicode/Special Characters

1. **Scene with emoji or special characters:**
   ```
   A warrior ⚔️ stands on a cliff facing an army 🪖. 
   Dark clouds & thunder storm approaching. 
   The hero must decide: fight or flee?
   ```
2. **Generate**

**Expected:**
- ✅ Works without Unicode errors
- ✅ Logs show characters correctly
- ✅ Images generate fine

---

## Part 11: Monitor Performance

### Measure Full Generation Time

**Time from click Generate to all panels complete:**

**Example (2 panels):**
```
19:23:15 - Click Generate
19:23:22 - LLM response (7 seconds)
19:23:25 - Character image loaded
19:23:43 - Panel 1 done (18 seconds)
19:23:62 - Panel 2 done (19 seconds)
19:24:03 - PDF export ready
─────────────────────────────
Total: ~48 seconds ✅ (reasonable)
```

**Expected times by panel count:**
- 2 panels: 40-60 seconds
- 3 panels: 60-90 seconds
- 4 panels: 80-120 seconds
- 5 panels: 100-150 seconds

### Monitor GPU Memory

While generation is running, open Task Manager (Windows) or Activity Monitor (Mac):

**Expected VRAM usage:**
- During generation: 8-10 GB (RTX 3080+)
- Peak: ~11-12 GB
- After generation: Stays ~8-10 GB (models cached in memory)

---

## Part 12: Browser Developer Tools Inspection

### Network Tab

During generation:

1. **Open F12 → Network tab**
2. **Click Generate**
3. **Watch requests:**
   - POST to `/frame-forge/api/decompose` (5-10 sec) → Response: panel array
   - POST to `/frame-forge/api/generate` (30-60 sec) → Response: images + prompts

**Expected:**
- ✅ Status 200 for all
- ✅ Response includes base64 images (large payloads)
- ✅ No CORS errors
- ✅ No timeout errors

### Console Tab

During generation:

1. **Open F12 → Console tab**
2. **Click Generate**
3. **Watch for logs:**

**Expected:**
- ✅ No red errors
- ✅ Maybe some warnings (normal)
- ✅ May see debug logs if implemented: `[FrameForge] Request sent to /generate`

**If you see CORS error:**
```
Access to XMLHttpRequest at 'http://localhost:8000/frame-forge/api/generate' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```
→ Fix in `backend/settings.py` and restart backend

### Storage Tab

Check localStorage/sessionStorage:

1. **Open F12 → Application → Storage → Local Storage**
2. **Should have entries for:**
   - `frameforge_scene` (last scene)
   - `frameforge_panels` (cached panels)
   - `frameforge_style_preset` (user preference)

---

## Part 13: Complete Test Checklist

Before saying "everything works", verify:

- [ ] Website loads at http://localhost:3000
- [ ] No CORS errors in browser console
- [ ] Can type scene description
- [ ] Can upload character image
- [ ] Can select style preset
- [ ] Can set number of panels
- [ ] Click Generate starts request
- [ ] Backend logs appear in Terminal 1
- [ ] All logging sections present (LLM, Pipeline, Diffusion)
- [ ] Parameters logged: canvas=1024×1024, steps=25, controlnet=0.6, ip_adapter=0.4, guidance=7.5
- [ ] Panels appear in UI after generation
- [ ] Images look reasonable (character consistent, proper framing)
- [ ] Can drag panels to reorder
- [ ] Can click panel to open editor
- [ ] Can edit custom prompt
- [ ] Can regenerate single panel (only that panel updates)
- [ ] Custom prompt override logged in Terminal 1
- [ ] Can export to PDF
- [ ] PDF opens with proper layout (2-3 panels per row)
- [ ] Can test with different character references
- [ ] Can test with different style presets
- [ ] No crashes with edge cases
- [ ] Network tab shows 200 responses
- [ ] Generation takes reasonable time (2-3 min for 3-4 panels)

---

## Troubleshooting During Website Testing

### Website Won't Load

```
Problem: ERR_CONNECTION_REFUSED when opening http://localhost:3000
Solution: 
  - Check Terminal 2: `npm start` must be running
  - Check port 3000 isn't blocked by firewall
  - Try http://127.0.0.1:3000 instead
```

### Generate Button Doesn't Work

```
Problem: Click Generate, nothing happens
Check:
  - Is Backend running? (Terminal 1 should show requests)
  - Check browser console (F12) for errors
  - Check Network tab for failed requests
  - Is API key set in .env?
  - Is scene text empty? (might need text first)
```

### Images Take Forever to Generate

```
Problem: Stuck on "Generating..." for 10+ minutes
Check:
  - GPU memory? (nvidia-smi or Task Manager)
  - Is model downloading? (first run takes longer)
  - Check Terminal 1 for errors (❌ marks)
  - Is pose retrieval stuck? (look for [Pose Retrieval] section)
```

### Images Don't Look Good

```
Problem: Character unrecognizable, pose wrong, quality poor
Check:
  - Character reference image: is it clear and facing forward?
  - Scene description: is pose_query detailed enough?
  - Prompt: does [SDXL Prompt] section show specific details?
  - Parameters: are controlnet=0.6 and ip_adapter=0.4 logged?
  - Try regenerating with custom prompt to override
```

### PDF Export Doesn't Work

```
Problem: Export button doesn't do anything or file won't open
Check:
  - Are all panels generated? (no failed ones?)
  - Browser console errors?
  - File downloaded but corrupted? (try again)
  - PDF viewer installed?
```

---

## Success - You Know It's Working When:

✅ **You can describe a scene in plain English**
✅ **Upload a character image**
✅ **Click Generate**
✅ **See logging flow through Terminal 1**
✅ **Watch beautiful, consistent storyboard panels appear**
✅ **Drag panels around**
✅ **Regenerate individual panels with custom prompts**
✅ **Export to a PDF**
✅ **All parameters (canvas, steps, scales) logged correctly**
✅ **Generation takes 2-5 minutes for 3-4 panels**
✅ **Zero errors in browser console or backend logs**

**If all that works → FrameForge MVP is ready! 🚀**

---

## Next: Production Deployment

Once you've validated the website works locally:

1. Build frontend: `npm run build`
2. Serve built frontend from backend
3. Deploy both to cloud/server
4. Update `ORIGINS` in `backend/settings.py` for production domain
5. Monitor `/frame-forge/api/health` in production
6. Check server logs for same logging sections

Happy testing! 🎬
