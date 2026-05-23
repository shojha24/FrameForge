from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from settings import PROJECT_NAME, ORIGINS
from api import router

app = FastAPI(title=PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,            # List of allowed origins
    allow_credentials=True,           # Allow cookies/auth headers
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)

app.include_router(router)