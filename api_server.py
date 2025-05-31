#!/usr/bin/env python3
import os
import io
import base64
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import uvicorn
import tempfile
import shutil

# Set environment for compatibility
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Global model variable
model = None

def get_device():
    """Get the best available device with fallback to CPU for compatibility"""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        # Use CPU for better compatibility
        return "cpu"
    else:
        return "cpu"

def load_model():
    """Load the TTS model once on startup"""
    global model
    try:
        device = get_device()
        print(f"Loading Chatterbox TTS model on device: {device}")
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✅ Model loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("🚀 Starting Chatterbox TTS API Server...")
    success = load_model()
    if not success:
        print("⚠️  Warning: Model failed to load on startup")
    yield
    # Shutdown
    print("👋 Shutting down Chatterbox TTS API Server...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Chatterbox TTS API",
    description="Simple TTS API using Chatterbox with voice cloning support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for web app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://voice-clone-site-lmj808t4l-lorenphillips-protonmailcs-projects.vercel.app",  # Production HTTPS
        "http://voice-clone-site-lmj808t4l-lorenphillips-protonmailcs-projects.vercel.app",   # Production HTTP
        "https://voice-clone-site.vercel.app",  # Main Vercel domain
        "http://voice-clone-site.vercel.app",   # Main Vercel domain HTTP
        "https://localhost:3000",  # Local development HTTPS
        "http://localhost:3000",   # Local development HTTP
        "http://localhost:8080",   # Local development  
        "http://127.0.0.1:3000",   # Local development
        "http://127.0.0.1:8080",   # Local development
        "*"  # Allow all origins for now (can be restricted later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
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
    """Health check endpoint"""
    return {
        "message": "Chatterbox TTS API is running!",
        "model_loaded": model is not None,
        "device": get_device()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
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
    """Generate TTS audio from text with optional voice cloning (Form API)"""
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
    
    # Load model if not already loaded
    if model is None:
        print("Model not loaded, attempting to load...")
        success = load_model()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to load TTS model")
    
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
                raise HTTPException(status_code=400, detail="Unsupported audio format. Use WAV, MP3, FLAC, M4A, or OGG")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                shutil.copyfileobj(audio_file.file, tmp_file)
                audio_prompt_path = tmp_file.name
                print(f"Saved audio file to: {audio_prompt_path}")
        
        # Set seed if provided
        if seed != 0:
            torch.manual_seed(seed)
        
        # Generate audio
        print(f"Generating TTS for: {text[:50]}...")
        wav = model.generate(
            text,
            audio_prompt_path=audio_prompt_path,
            exaggeration=exaggeration,
            temperature=temperature,
            cfg_weight=cfg_weight,
        )
        
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
    """Get information about the loaded model"""
    if model is None:
        return {"loaded": False, "message": "No model loaded"}
    
    return {
        "loaded": True,
        "sample_rate": model.sr,
        "device": get_device(),
        "model_status": str(model),
        "message": "Model is ready"
    }

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting Chatterbox TTS API Server on port {port}...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    ) 