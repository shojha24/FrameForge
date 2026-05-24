import sys
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Add project root to path so ml_pipeline imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Change to project root directory
os.chdir(project_root)

from backend.app import app