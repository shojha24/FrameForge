# 🚀 START HERE - Get Running in 5 Minutes

## Step 1: Open 3 Terminal Windows

```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│  Terminal 1         │  Terminal 2         │  Terminal 3         │
│  Backend            │  Frontend           │  Browser            │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

---

## Step 2: Get API Keys

If you don't have them:
- **OpenRouter API Key**: https://openrouter.ai/keys
- **HuggingFace Token**: https://huggingface.co/settings/tokens

---

## Step 3: Create .env File

In your **project root** (where `backend/`, `frontend/`, `ml_pipeline/` folders are):

```bash
cat > .env << 'EOF'
OPENROUTER_API_KEY=sk_your_actual_key_here
HUGGING_FACE_HUB_TOKEN=hf_your_actual_token_here
EOF
```

**On Windows (PowerShell):**
```powershell
@"
OPENROUTER_API_KEY=sk_your_actual_key_here
HUGGING_FACE_HUB_TOKEN=hf_your_actual_token_here
"@ | Out-File -Encoding UTF8 .env
```

---

## Step 4: Start Everything

### Terminal 1️⃣ — Backend (Copy & Paste)

```bash
cd path/to/FrameForge
python run_server.py
```

**Wait for this output:**
```
[FrameForge] Starting backend server...
INFO:     Uvicorn running on http://127.0.0.1:8000
[Startup] Initializing diffusion pipeline...
[Startup] ✅ Pipeline ready!
```

✅ **WHEN YOU SEE `✅ Pipeline ready!` → MOVE TO TERMINAL 2**

---

### Terminal 2️⃣ — Frontend (Copy & Paste)

```bash
cd path/to/FrameForge/frontend
npm start
```

**Wait for this output:**
```
Compiled successfully!

You can now view frameforge in the browser.

  Local:            http://localhost:3000
```

✅ **WHEN YOU SEE `Compiled successfully!` → MOVE TO TERMINAL 3**

---

### Terminal 3️⃣ — Browser (Just Click)

**Open in your web browser:**
```
http://localhost:3000
```

You should see:
- FrameForge title/header
- Text input for scene description
- Button to upload character image
- Generate button
- No red errors in console (F12)

✅ **WHEN PAGE LOADS → YOU'RE READY TO TEST**

---

## Step 5: Quick 2-Minute Test

### In Browser:

**1. Type this scene:**
```
A warrior stands on a cliff. 
Dark clouds approach. 
She draws her sword. 
Lightning crashes.
```

**2. Upload a character image** (any portrait photo)

**3. Click "Generate Storyboard"**

**4. Watch Terminal 1 for this log cascade:**

```
================================================================================
[LLM Decomposer] Scene Decomposition Request
================================================================================
[LLM Call] Calling OpenRouter...
[LLM Response] ✅ Successfully parsed 2 panels

================================================================================
[Pipeline Orchestrator] Full Generation Request
================================================================================
[Pipeline] ✅ LLM generated 2 panels
[Pipeline] ✅ Loaded character reference: (512, 512)
[Pipeline] Starting image generation for 2 panels...

[Diffusion] Starting generation of 2 panels
[Diffusion] Canvas: 1024×1024
[Diffusion] Parameters: steps=25, guidance=7.5, controlnet=0.6

────────────────────────────────────────────────────────────────────────────────
[Diffusion] PANEL 1/2
────────────────────────────────────────────────────────────────────────────────
[SDXL Prompt]
  wide shot, full body and environment, eye level, ...

[Diffusion] ✅ Panel generated in 18.2 seconds

────────────────────────────────────────────────────────────────────────────────
[Diffusion] PANEL 2/2
────────────────────────────────────────────────────────────────────────────────
[SDXL Prompt]
  ...

[Diffusion] ✅ Panel generated in 19.1 seconds

================================================================================
[Pipeline Orchestrator] Generation Complete
================================================================================
```

**5. Back in browser:**
- See 2 generated images appear
- Each has a label (WS, CU, etc.)
- Each has a caption

✅ **IF YOU SEE IMAGES → SUCCESS!** 🎉

---

## ❓ What If Something Goes Wrong?

### Backend Won't Start

```
Error: ModuleNotFoundError: No module named 'ml_pipeline'
```

**Fix:** Make sure you're in the **project root**, not in a subfolder:

```bash
# ❌ WRONG - don't do this
cd path/to/FrameForge/backend
python run_server.py

# ✅ RIGHT - do this
cd path/to/FrameForge
python run_server.py
```

---

### No API Key Error

```
ERROR: OPEN_ROUTER_API_KEY environment variable is not set
```

**Fix:** Create `.env` file in project root with your actual keys:

```bash
cat > .env << 'EOF'
OPENROUTER_API_KEY=sk_your_ACTUAL_key_not_example
HUGGING_FACE_HUB_TOKEN=hf_your_ACTUAL_token_not_example
EOF
```

Then restart Terminal 1 backend.

---

### CORS Error in Browser

```
Access to XMLHttpRequest ... blocked by CORS policy
```

**Fix:** Restart backend (close Terminal 1, run `python run_server.py` again)

---

### Images Take Forever (>30 seconds)

This is **normal** on first run - models are downloading.
- First panel: 20-30 seconds
- Subsequent panels: 15-20 seconds each

On slower GPUs:
- RTX 2080: 25-30 seconds/panel
- GTX 1080: 30-40 seconds/panel

---

### Nothing Appears

**Check:**
1. Terminal 1 showing errors? (Look for ❌)
2. Backend still running? (Did you close Terminal 1?)
3. Frontend compiled? (Terminal 2 showing errors?)
4. Browser on http://localhost:3000? (Not localhost:3001)

---

## ✅ What You Should See

### Terminal 1 Output (Most Important!)
```
✅ [Startup] Pipeline ready!  ← Backend ready
✅ [LLM Decomposer]           ← LLM parsing scene
✅ [Pipeline Orchestrator]    ← Coordinating generation
✅ [Diffusion] Canvas         ← Confirming parameters
✅ Panel generated in X.X s   ← Each panel complete
✅ Generation Complete        ← All done
```

### Browser (Visual)
```
┌────────────────────────────────────────────────┐
│  [Generated Image 1]   [Generated Image 2]    │
│  WS                    CU                      │
│  Warrior on cliff      Enemy army arrives     │
└────────────────────────────────────────────────┘
```

### No Errors
```
Browser Console (F12) → Should be clean (no red errors)
```

---

## 🎯 Success = All 3 Green

```
Terminal 1: [Startup] ✅ Pipeline ready!
Terminal 2: Compiled successfully!
Browser:    2 images with captions appear
```

---

## 📊 Performance: What's Normal

| Task | Time | Status |
|------|------|--------|
| Backend startup | 10-30s | ✅ Normal |
| Frontend compile | 20-40s | ✅ Normal |
| LLM scene decompose | 5-10s | ✅ Normal |
| Generate 1 image | 15-25s | ✅ Normal |
| Generate 2 images | 40-60s | ✅ Normal |

**If takes much longer:** Check GPU memory (Task Manager)

---

## 🎓 Next Steps (Optional)

### Try More Features

1. **Edit a panel:**
   - Click on an image
   - Edit the custom prompt in the sidebar
   - Click Regenerate
   - Only that panel updates

2. **Drag panels:**
   - Click and drag Panel 1 to position 2
   - Panels reorder

3. **Export PDF:**
   - Click Export button
   - PDF downloads
   - Should show 2-3 panels per row

### Try Different Inputs

1. **Different character types:**
   - Realistic portrait
   - Anime character
   - Stylized illustration
   - 3D render

2. **Different scenes:**
   - Fantasy adventure
   - Mystery thriller
   - Sci-fi action
   - Drama dialogue

3. **Different styles:**
   - Cinematic
   - Comic Book
   - Other presets

---

## 📚 Full Documentation

**If something isn't working:**
- `QUICK_START.md` → Quick reference
- `BACKEND_STARTUP.md` → Startup issues
- `TESTING_WEBSITE.md` → Feature walkthrough
- `LOGGING_AND_PARAMETERS.md` → What logs mean

---

## 🎉 You're Ready!

```
1. Create .env with API keys      ← 1 minute
2. Terminal 1: python run_server.py    ← wait 30s
3. Terminal 2: npm start           ← wait 30s  
4. Terminal 3: Open browser        ← instant
5. Type scene, upload image, click Generate  ← instant

Total: ~5 minutes to first images! 🎬
```

---

## 💡 Pro Tips

1. **Terminal 1 is your dashboard** — watch it during generation
2. **All important info appears in logs** — if confused, check Terminal 1
3. **First generation is slowest** — models are caching, gets faster after
4. **Images improve with detail** — longer, more specific prompts = better results
5. **Custom prompts override everything** — regenerate to get exact results you want

---

**Ready? Start with Terminal 1! 🚀**

```bash
cd path/to/FrameForge
python run_server.py
```

Questions? Check the docs. Issues? Look at Terminal 1 logs first!
