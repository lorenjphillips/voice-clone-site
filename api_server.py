#!/usr/bin/env python3
"""
Minimal Chatterbox TTS API Server
Direct integration with chatterbox-tts package
Optimized with lazy loading for Render (2GB RAM plan)
"""

import os
import io
import base64
import tempfile
import shutil
import asyncio
import gc
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import torchaudio as ta

# CRITICAL FIX: Patch torch.load to always use CPU mapping
# This fixes "Attempting to deserialize object on a CUDA device" error
_original_torch_load = torch.load
def _cpu_safe_load(*args, **kwargs):
    """Ensure all torch.load calls map to CPU for compatibility"""
    kwargs['map_location'] = 'cpu'
    return _original_torch_load(*args, **kwargs)

# Apply the global patch
torch.load = _cpu_safe_load
print("🔧 Applied CPU-safe torch.load patch for local development")

# Global model instance - will be loaded lazily on first request
model = None
model_loading = False
model_load_time = None

# Set environment for better compatibility
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['OMP_NUM_THREADS'] = '2'  # Allow more threads with 2GB RAM
os.environ['MKL_NUM_THREADS'] = '2'

def get_device():
    """Determine best device - prefer CPU for stability, allow CUDA if available"""
    # With 2GB RAM, we can be more flexible about device selection
    if torch.cuda.is_available():
        print("🎮 CUDA detected, using GPU for better performance")
        return "cuda"
    else:
        print("🖥️  Using CPU for inference")
        return "cpu"

async def load_model_async():
    """
    🔥 LAZY LOADING: Load the ChatterboxTTS model only when first needed
    This prevents startup crashes and lets the server bind to port immediately
    """
    global model, model_loading, model_load_time
    
    # If model already loaded, return immediately
    if model is not None:
        return True
        
    # If another request is already loading, wait for it
    if model_loading:
        print("⏳ Model already loading, waiting...")
        while model_loading and model is None:
            await asyncio.sleep(0.1)
        return model is not None
    
    # Start loading process
    model_loading = True
    start_time = time.time()
    
    try:
        print("📦 LAZY LOADING: Loading ChatterboxTTS model on first request...")
        from chatterbox.tts import ChatterboxTTS
        
        device = get_device()
        print(f"🚀 Loading model on device: {device}")
        
        # Force garbage collection before loading
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Load model - the global torch.load patch handles CPU mapping automatically
        model = ChatterboxTTS.from_pretrained(device=device)
        
        # Force garbage collection after loading
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        model_load_time = time.time() - start_time
        print(f"✅ ChatterboxTTS model loaded successfully in {model_load_time:.2f}s!")
        model_loading = False
        return True
        
    except Exception as e:
        print(f"❌ Error loading ChatterboxTTS model: {e}")
        model_loading = False
        model_load_time = None
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    🎯 LAZY LOADING LIFESPAN: Don't load model here!
    This ensures fast startup and immediate port binding
    """
    print("🚀 Starting Chatterbox TTS API Server...")
    print("📝 LAZY LOADING: Model will load on first TTS request")
    print("🏥 Server will be healthy immediately for Render detection")
    yield
    # Shutdown cleanup
    print("👋 Shutting down Chatterbox TTS API Server...")
    global model
    if model is not None:
        print("🧹 Cleaning up model from memory...")
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# Initialize FastAPI app
app = FastAPI(
    title="Chatterbox TTS API",
    description="Lazy-loaded TTS API using ChatterboxTTS (2GB RAM optimized)",
    version="1.1.0",
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
    """Root endpoint - always responds fast due to lazy loading"""
    return {
        "message": "🎤 Chatterbox TTS API is running!",
        "model_loaded": model is not None,
        "model_loading": model_loading,
        "model_load_time": f"{model_load_time:.2f}s" if model_load_time else "N/A",
        "device": get_device() if model is not None else "TBD",
        "optimization": "lazy-loaded for 2GB RAM plan",
        "status": "🟢 Ready for requests"
    }

@app.get("/health")
async def health_check():
    """Health check - always healthy due to lazy loading"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_loading": model_loading,
        "device": get_device() if model is not None else "TBD",
        "torch_version": torch.__version__,
        "lazy_loading": "✅ enabled"
    }

@app.post("/warm-up")
async def warm_up():
    """
    🔥 Warm up endpoint: Manually trigger model loading
    Call this after deployment to pre-load the model
    """
    success = await load_model_async()
    if success:
        return {
            "message": "🔥 Model warmed up successfully!",
            "device": get_device(),
            "load_time": f"{model_load_time:.2f}s"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to warm up model")

@app.post("/tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    """
    🗣️ Generate TTS audio from text (JSON API)
    First call will trigger lazy loading
    """
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
    """
    🎭 Generate TTS audio with optional voice cloning (Form API)
    First call will trigger lazy loading
    """
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
    """
    🎯 Internal TTS generation with lazy loading
    """
    global model
    
    # Validate input
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Increased limit for 2GB RAM plan
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Text must be 500 characters or less")
    
    # 🔥 LAZY LOADING: Load model only when first TTS request comes in
    if model is None:
        print("🔥 LAZY LOADING: First TTS request - loading model now...")
        success = await load_model_async()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to load TTS model")
        print("✅ Model loaded, proceeding with TTS generation...")
    
    audio_prompt_path = None
    
    try:
        # Memory optimization
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Handle audio file upload for voice cloning
        if audio_file and audio_file.size > 0:
            print(f"🎵 Processing uploaded audio file: {audio_file.filename}")
            
            # Increased limit for 2GB RAM plan
            if audio_file.size > 15 * 1024 * 1024:  # 15MB limit
                raise HTTPException(status_code=400, detail="Audio file too large (max 15MB)")
            
            # Check file extension
            allowed_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
            if not any(audio_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                raise HTTPException(status_code=400, detail="Unsupported audio format")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                shutil.copyfileobj(audio_file.file, tmp_file)
                audio_prompt_path = tmp_file.name
                print(f"💾 Saved audio file to: {audio_prompt_path}")
        
        # Set seed if provided
        if seed != 0:
            torch.manual_seed(seed)
        
        # Generate audio using ChatterboxTTS
        print(f"🎤 Generating TTS for: {text[:50]}...")
        
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
        
        # Generate with memory optimization
        with torch.inference_mode():
            wav = model.generate(**generate_args)
        
        # Memory cleanup after generation
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Convert to bytes
        audio_buffer = io.BytesIO()
        ta.save(audio_buffer, wav, model.sr, format="wav")
        audio_bytes = audio_buffer.getvalue()
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        print("✅ TTS generation successful!")
        
        device_info = get_device() if model is not None else "unknown"
        message = f"TTS generation successful ({device_info})"
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
                print(f"🧹 Cleaned up temporary file: {audio_prompt_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not delete temporary file: {e}")
        
        # Final memory cleanup
        gc.collect()

@app.get("/models/info")
async def model_info():
    """Get detailed model information"""
    global model, model_load_time
    
    if model is None:
        return {
            "loaded": False,
            "device": "TBD",
            "load_time": "N/A",
            "message": "🔥 Model not loaded yet - will lazy load on first TTS request",
            "lazy_loading": "✅ enabled"
        }
    
    return {
        "loaded": True,
        "sample_rate": model.sr,
        "device": get_device(),
        "load_time": f"{model_load_time:.2f}s" if model_load_time else "N/A",
        "message": "🎤 ChatterboxTTS model is ready!",
        "lazy_loading": "✅ enabled"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (for Render deployment)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting lazy-loaded server on port {port}")
    print(f"💾 Memory plan: 2GB RAM")
    print(f"🔥 Lazy loading: Model loads on first TTS request")
    
    # Run with optimized settings for 2GB plan
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        workers=1,  # Single worker for memory efficiency
        timeout_keep_alive=60,  # Longer timeout for model loading
        access_log=True  # Re-enable access logs with more memory
    ) 