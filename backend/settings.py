import os

from distlib.util import PROJECT_NAME_AND_VERSION
from dotenv import load_dotenv

# Load env
load_dotenv(override=True)

# Project Settings
PROJECT_NAME = "FrameForge"
API_PREFIX = "/frame-forge/api"

# Secret Keys
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
