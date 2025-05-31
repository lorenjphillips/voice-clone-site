#!/usr/bin/env python3
"""
Local development server for Chatterbox TTS
Run this to test your voice clone site locally
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import torch
        import torchaudio
        import fastapi
        import uvicorn
        from chatterbox.tts import ChatterboxTTS
        print("✅ All required packages are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("📦 Please install requirements: pip install -r requirements.txt")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Chatterbox TTS API Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("🌐 Frontend will be available at: http://localhost:8000/static")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Set environment variables
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    
    # Import and run the server
    try:
        from api_server import app
        import uvicorn
        
        # Add static file serving for the frontend
        from fastapi.staticfiles import StaticFiles
        
        # Serve index.html as static content
        if Path("index.html").exists():
            app.mount("/static", StaticFiles(directory=".", html=True), name="static")
            print("📄 Frontend will be served at: http://localhost:8000/static/index.html")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False  # Disable reload for stability
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    print("🎙️ Chatterbox TTS - Local Development Server")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api_server.py").exists():
        print("❌ Please run this script from the voice-clone-site directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main() 