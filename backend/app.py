import sys
import os

# Add project root to path so ml_pipeline imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from backend.settings import PROJECT_NAME, ORIGINS
from backend.api import router
from ml_pipeline import diffusion, pose_search

app = FastAPI(title=PROJECT_NAME)

# Initialize diffusion pipeline at startup
@app.on_event("startup")
async def startup():
    print("[Startup] Initializing diffusion pipeline...")
    diffusion.initialize_pipeline()
    print("[Startup] Initializing pose search...")
    pose_search.initialize()
    print("[Startup] ✅ Pipeline ready!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,            # List of allowed origins
    allow_credentials=True,           # Allow cookies/auth headers
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)

app.include_router(router)