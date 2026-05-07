from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from settings import PROJECT_NAME
from api import router

app = FastAPI(title=PROJECT_NAME)

app.include_router(router)