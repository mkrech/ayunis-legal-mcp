#!/usr/bin/env python3
"""
Start script for the Legal MCP Store API
Automatically sets up the correct Python path for local development
"""
import sys
import os
from pathlib import Path

# Add store directory to Python path
store_path = Path(__file__).parent / "store"
sys.path.insert(0, str(store_path))

# Change working directory to store for .env loading
os.chdir(store_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(store_path / "app")]
    )
