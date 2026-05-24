# FrameForge Quick Reference Card

## 🚀 Start Everything (3 Commands)

```bash
# Terminal 1: Backend
python run_server.py

# Terminal 2: Frontend  
cd frontend && npm start

# Terminal 3: Browser
# Open http://localhost:3000
```

---

## 📝 Expected Console Output

**Backend Terminal (after startup):**
```
[FrameForge] Starting backend server...
INFO:     Uvicorn running on http://127.0.0.1:8000
[Startup] Initializing diffusion pipeline...
[Startup] ✅ Pipeline ready!
```

**Frontend Terminal (after startup):**
```
Compiled successfully!
You can now view frameforge in the browser.
Local:            http://localhost:3000
```

---

## ⚙️ Environment Setup

### Create `.env` in project root:
```
OPENROUTER_API_KEY=sk_your_key_here
HUGGING_FACE_HUB_TOKEN=hf_your_token_here
```

### Verify dependencies:
```bash
# Python packages
python test_backend_imports.py

# Node packages
cd frontend && npm list react react-dom
```

---

## 🧪 Testing Checklist

### Phase 1: Backend API
- [ ] `python run_server.py` starts without errors
- [ ] `curl http://localhost:8000/frame-forge/api/health` returns 200
- [ ] Logs show `[Startup] ✅ Pipeline ready!`

### Phase 2: Frontend
- [ ] `npm start` compiles successfully
- [ ] Page loads at `http://localhost:3000`
- [ ] No errors in browser console (F12)
- [ ] Can type scene description

### Phase 3: Generation
- [ ] Click Generate
- [ ] Watch Terminal 1 for logging cascade:
  - `[LLM Decomposer]` (5-10s)
  - `[Pipeline Orchestrator]` (0-1s)
  - `[Diffusion]` with panel-by-panel updates (30-60s)
- [ ] Panels appear in browser
- [ ] Images look reasonable

### Phase 4: Features
- [ ] Can drag panels to reorder
- [ ] Can click panel to edit
- [ ] Can regenerate with custom prompt
- [ ] Can export to PDF
- [ ] PDF opens correctly

### Phase 5: Verify Parameters
In Terminal 1 logs, look for:
```
Canvas: 1024×1024 ✅
Inference Steps: 25 ✅
ControlNet Scale: 0.6 ✅
IP-Adapter Scale: 0.4 ✅
Guidance Scale: 7.5 ✅
```

---

## 📋 Key Files to Know

| File | Purpose |
|------|---------|
| `run_server.py` | Start backend (DO THIS FIRST) |
| `frontend/src/App.tsx` | Main React component |
| `backend/api.py` | API endpoints (/generate, /regenerate) |
| `ml_pipeline/pipeline.py` | Orchestrator (LLM → Diffusion) |
| `ml_pipeline/diffusion.py` | Image generation (SDXL + ControlNet + IP-Adapter) |
| `.env` | Your API keys |

---

## 🔍 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'ml_pipeline'` | Run `python run_server.py` from **project root** (not from backend/) |
| CORS error in browser | Restart backend after updating `.env` |
| Port 8000 already in use | Kill process: `taskkill /PID <PID> /F` |
| Slow generation | Normal! 2-5 min for 3-4 panels is expected |
| Images look bad | Check character reference image is clear; try regenerating with custom prompt |

---

## 📁 Directory Structure (Remember This)

```
FrameForge/  ← You are here when running commands
├── backend/           (API server)
├── frontend/          (React UI)
├── ml_pipeline/       (Image generation)
├── run_server.py      ← Run this
├── .env               ← Put API keys here
└── TESTING_WEBSITE.md (Complete walkthrough)
```

---

## 🎯 Full Workflow Example

```bash
# 1. Project root setup
cd path/to/FrameForge
cat > .env << 'EOF'
OPENROUTER_API_KEY=sk_...
HUGGING_FACE_HUB_TOKEN=hf_...
EOF

# 2. Terminal 1: Backend
python run_server.py
# Wait for: [Startup] ✅ Pipeline ready!

# 3. Terminal 2: Frontend
cd frontend && npm start
# Wait for: Compiled successfully!

# 4. Terminal 3: Browser
# Open http://localhost:3000

# 5. In browser:
# - Type scene: "A detective finds a clue in a dark warehouse"
# - Upload character image
# - Click Generate
# - Wait 30-60 seconds
# - See storyboard panels
# - Drag to reorder
# - Click panel to edit
# - Regenerate with custom prompt
# - Export to PDF

# Done! ✅
```

---

## 📊 Performance Expectations

| Task | Time |
|------|------|
| Backend startup | 10-30 seconds |
| Frontend compile | 20-40 seconds |
| LLM decomposition | 5-10 seconds |
| Image generation (1 panel) | 15-25 seconds |
| Full flow (2 panels) | 40-60 seconds |
| Full flow (3 panels) | 60-90 seconds |

---

## 🛠️ Debugging Commands

```bash
# Check Python path
python -c "import sys; print(sys.path[0])"

# Verify API key loaded
python -c "from backend.settings import OPEN_ROUTER_API_KEY; print(f'API Key: {bool(OPEN_ROUTER_API_KEY)}')"

# Test API endpoint manually
curl -X POST http://localhost:8000/frame-forge/api/decompose \
  -H "Content-Type: application/json" \
  -d '{"scene_description": "test", "num_panels": 1}'

# Check GPU memory
nvidia-smi  # NVIDIA
```

---

## ✅ Success Criteria

You know everything works when:
1. ✅ Backend starts cleanly
2. ✅ Frontend compiles without errors
3. ✅ Can generate a 2-panel storyboard
4. ✅ All 5 parameters logged correctly
5. ✅ Images look good and character is consistent
6. ✅ Custom prompt regeneration works
7. ✅ PDF exports with proper layout
8. ✅ No errors in browser console or backend logs

---

## 📖 Full Guides

- **TESTING_GUIDE.md** — Detailed testing for every component
- **TESTING_WEBSITE.md** — Complete UI walkthrough
- **BACKEND_STARTUP.md** — Backend setup troubleshooting
- **LOGGING_AND_PARAMETERS.md** — What to expect in logs
- **PARAMETER_TUNING_CHECKLIST.md** — Parameter verification

---

**Happy testing! 🚀** When in doubt, check Terminal 1 logs for the full story.
