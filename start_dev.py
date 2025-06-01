#!/usr/bin/env python3
"""
Development startup script for Chatterbox TTS
Starts both the Python backend API and React frontend
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def check_and_fix_rollup():
    """Check and fix rollup architecture issues"""
    frontend_dir = Path.cwd() / "frontend"
    rollup_x64_path = frontend_dir / "node_modules" / "@rollup" / "rollup-darwin-x64"
    rollup_arm64_path = frontend_dir / "node_modules" / "@rollup" / "rollup-darwin-arm64"
    
    if rollup_x64_path.exists() and not rollup_arm64_path.exists():
        print("🔧 Detected Rollup architecture mismatch, fixing...")
        try:
            subprocess.run([
                "npm", "install", "@rollup/rollup-darwin-arm64", "--save-dev"
            ], cwd=frontend_dir, check=True, capture_output=True)
            print("✅ Rollup ARM64 binary installed")
        except subprocess.CalledProcessError:
            print("⚠️  Could not auto-fix Rollup issue")

def run_backend():
    """Start the Python API server"""
    print("🚀 Starting Python API server...")
    try:
        subprocess.run([
            sys.executable, "api_server.py"
        ], cwd=Path.cwd())
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")

def run_frontend():
    """Start the React development server"""
    print("⚛️  Starting React frontend...")
    try:
        # Force ARM64 architecture to fix Rollup binary detection
        subprocess.run([
            "arch", "-arm64", "npm", "run", "dev"
        ], cwd=Path.cwd() / "frontend", check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Frontend failed to start with error code {e.returncode}")
        print("💡 Try running 'npm run dev' directly in the frontend directory")
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")

def main():
    print("🎙️ Starting Chatterbox TTS Development Environment")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api_server.py").exists():
        print("❌ Error: api_server.py not found. Make sure you're in the project root.")
        sys.exit(1)
    
    if not Path("frontend/package.json").exists():
        print("❌ Error: frontend/package.json not found. Make sure the frontend is set up.")
        sys.exit(1)
    
    print("📦 Dependencies checked ✅")
    
    # Check and fix rollup issues
    check_and_fix_rollup()
    
    print("🌐 Backend will run on: http://localhost:8000")
    print("⚛️  Frontend will run on: http://localhost:5173")
    print("=" * 50)
    
    # Start both servers in separate threads
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    
    try:
        backend_thread.start()
        time.sleep(2)  # Give backend a moment to start
        frontend_thread.start()
        
        print("\n✅ Both servers starting...")
        print("🎯 Open http://localhost:5173 in your browser")
        print("📡 API health: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop both servers")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down development servers...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 