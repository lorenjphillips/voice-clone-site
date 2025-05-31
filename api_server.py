#!/usr/bin/env python3
import os
import io
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import uvicorn

# Set environment for compatibility
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Initialize FastAPI app
app = FastAPI(
    title="Chatterbox TTS API",
    description="Simple TTS API using Chatterbox",
    version="1.0.0"
)

# Add CORS middleware for web app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "voice-clone-site-lmj808t4l-lorenphillips-protonmailcs-projects.vercel.app",  # Production
        "http://localhost:3000",  # Local development
        "http://localhost:8080",  # Local development  
        "http://127.0.0.1:3000",  # Local development
        "http://127.0.0.1:8080",  # Local development
        "null"  # For file:// protocol when opening HTML directly
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None

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

@app.on_event("startup")
async def startup_event():
    """Load model when server starts"""
    success = load_model()
    if not success:
        print("⚠️  Warning: Model failed to load on startup")

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
    """Generate TTS audio from text"""
    global model
    
    # Validate input
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(request.text) > 300:
        raise HTTPException(status_code=400, detail="Text must be 300 characters or less")
    
    # Load model if not already loaded
    if model is None:
        print("Model not loaded, attempting to load...")
        success = load_model()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to load TTS model")
    
    try:
        # Set seed if provided
        if request.seed != 0:
            torch.manual_seed(request.seed)
        
        # Generate audio
        print(f"Generating TTS for: {request.text[:50]}...")
        wav = model.generate(
            request.text,
            exaggeration=request.exaggeration,
            temperature=request.temperature,
            cfg_weight=request.cfg_weight,
        )
        
        # Convert to bytes
        audio_buffer = io.BytesIO()
        ta.save(audio_buffer, wav, model.sr, format="wav")
        audio_bytes = audio_buffer.getvalue()
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        print("✅ TTS generation successful!")
        
        return TTSResponse(
            audio_base64=audio_base64,
            sample_rate=model.sr,
            message="TTS generation successful"
        )
        
    except Exception as e:
        print(f"❌ TTS generation error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

@app.get("/models/info")
async def model_info():
    """Get information about the loaded model"""
    if model is None:
        return {"loaded": False, "message": "No model loaded"}
    
    return {
        "loaded": True,
        "sample_rate": model.sr,
        "device": get_device(),
        "message": "Model is ready"
    }

if __name__ == "__main__":
    print("🚀 Starting Chatterbox TTS API Server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    ) 