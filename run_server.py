#!/usr/bin/env python3
"""
FrameForge Backend Startup Script

Run from project root:
  python run_server.py

Or with custom host/port:
  python run_server.py --host 0.0.0.0 --port 8000
"""

import sys
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Ensure project root is in path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import and run
if __name__ == "__main__":
    import uvicorn
    from backend.app import app
    
    print("="*80)
    print("[FrameForge] Starting backend server...")
    print("="*80)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
