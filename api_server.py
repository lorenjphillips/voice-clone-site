#!/usr/bin/env python3
"""
Minimal Chatterbox TTS API Server
Direct integration with chatterbox-tts package
"""

import os
import io
import base64
import tempfile
import shutil
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import torchaudio as ta

# Global model instance
model = None

# Set environment for better compatibility
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

def get_device():
    """Determine the best device for inference"""
    if torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"

def load_model():
    """Load the ChatterboxTTS model"""
    global model
    try:
        from chatterbox.tts import ChatterboxTTS
        
        device = get_device()
        print(f"Loading ChatterboxTTS model on device: {device}")
        
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✅ ChatterboxTTS model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading ChatterboxTTS model: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("🚀 Starting Chatterbox TTS API Server...")
    success = load_model()
    if not success:
        print("❌ Failed to load model on startup")
        raise RuntimeError("Failed to load ChatterboxTTS model")
    yield
    # Shutdown
    print("👋 Shutting down Chatterbox TTS API Server...")

# Initialize FastAPI app
app = FastAPI(
    title="Chatterbox TTS API",
    description="Clean TTS API using ChatterboxTTS",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://voice-clone-site.vercel.app",
        "http://voice-clone-site.vercel.app",
        "https://localhost:3000",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class TTSRequest(BaseModel):
    text: str
    exaggeration: float = 0.5
    temperature: float = 0.8
    cfg_weight: float = 0.5
    seed: int = 0

class TTSResponse(BaseModel):
    audio_base64: str
    sample_rate: int
    message: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Chatterbox TTS API is running!",
        "model_loaded": model is not None,
        "device": get_device()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": get_device(),
        "torch_version": torch.__version__
    }

@app.post("/tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    """Generate TTS audio from text (JSON API)"""
    return await _generate_tts_internal(
        text=request.text,
        exaggeration=request.exaggeration,
        temperature=request.temperature,
        cfg_weight=request.cfg_weight,
        seed=request.seed,
        audio_file=None
    )

@app.post("/tts-with-voice", response_model=TTSResponse)
async def generate_tts_with_voice(
    text: str = Form(...),
    exaggeration: float = Form(0.5),
    temperature: float = Form(0.8),
    cfg_weight: float = Form(0.5),
    seed: int = Form(0),
    audio_file: Optional[UploadFile] = File(None)
):
    """Generate TTS audio with optional voice cloning (Form API)"""
    return await _generate_tts_internal(
        text=text,
        exaggeration=exaggeration,
        temperature=temperature,
        cfg_weight=cfg_weight,
        seed=seed,
        audio_file=audio_file
    )

async def _generate_tts_internal(
    text: str,
    exaggeration: float,
    temperature: float,
    cfg_weight: float,
    seed: int,
    audio_file: Optional[UploadFile]
):
    """Internal TTS generation function"""
    global model
    
    # Validate input
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(text) > 300:
        raise HTTPException(status_code=400, detail="Text must be 300 characters or less")
    
    # Ensure model is loaded
    if model is None:
        raise HTTPException(status_code=500, detail="TTS model not loaded")
    
    audio_prompt_path = None
    
    try:
        # Handle audio file upload for voice cloning
        if audio_file and audio_file.size > 0:
            print(f"Processing uploaded audio file: {audio_file.filename}")
            
            # Validate audio file
            if audio_file.size > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(status_code=400, detail="Audio file too large (max 10MB)")
            
            # Check file extension
            allowed_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
            if not any(audio_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                raise HTTPException(status_code=400, detail="Unsupported audio format")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                shutil.copyfileobj(audio_file.file, tmp_file)
                audio_prompt_path = tmp_file.name
                print(f"Saved audio file to: {audio_prompt_path}")
        
        # Set seed if provided
        if seed != 0:
            torch.manual_seed(seed)
        
        # Generate audio using ChatterboxTTS
        print(f"Generating TTS for: {text[:50]}...")
        
        # Prepare generation arguments
        generate_args = {
            "text": text,
            "exaggeration": exaggeration,
            "temperature": temperature,
            "cfg_weight": cfg_weight,
        }
        
        # Add audio prompt if provided
        if audio_prompt_path:
            generate_args["audio_prompt_path"] = audio_prompt_path
        
        # Generate with ChatterboxTTS
        wav = model.generate(**generate_args)
        
        # Convert to bytes
        audio_buffer = io.BytesIO()
        ta.save(audio_buffer, wav, model.sr, format="wav")
        audio_bytes = audio_buffer.getvalue()
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        print("✅ TTS generation successful!")
        
        message = "TTS generation successful"
        if audio_prompt_path:
            message += " with voice cloning"
        
        return TTSResponse(
            audio_base64=audio_base64,
            sample_rate=model.sr,
            message=message
        )
        
    except Exception as e:
        print(f"❌ TTS generation error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if audio_prompt_path and os.path.exists(audio_prompt_path):
            try:
                os.unlink(audio_prompt_path)
                print(f"Cleaned up temporary file: {audio_prompt_path}")
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {e}")

@app.get("/models/info")
async def model_info():
    """Get model information"""
    global model
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    return {
        "loaded": True,
        "sample_rate": model.sr,
        "device": get_device(),
        "message": "ChatterboxTTS model is ready"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (for Render deployment)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 