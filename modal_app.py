"""
🎤 Chatterbox TTS API on Modal
Serverless TTS with automatic scaling and GPU support
"""

import modal
import io
import base64
import tempfile
import os
from typing import Optional

# Create Modal app
app = modal.App("chatterbox-tts-api")

# Define the container image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "fastapi>=0.115.0",
        "uvicorn>=0.32.0", 
        "python-multipart>=0.0.6",
        "chatterbox-tts",
        "torch",
        "torchaudio", 
        "numpy",
        "pydantic>=2.0.0"
    ])
    .env({"PYTORCH_ENABLE_MPS_FALLBACK": "1"})
)

# Global model - will be loaded once per container
model = None

def load_model():
    """Load ChatterboxTTS model (runs once per container)"""
    global model
    if model is None:
        print("🚀 Loading ChatterboxTTS model...")
        from chatterbox.tts import ChatterboxTTS
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = ChatterboxTTS.from_pretrained(device=device)
        print(f"✅ Model loaded on {device}")
    return model

@app.function(
    image=image,
    gpu=modal.gpu.T4(),  # GPU for faster inference
    memory=8192,  # 8GB memory 
    timeout=300,  # 5 minute timeout
    container_idle_timeout=60,  # Keep warm for 1 minute
)
@modal.web_endpoint(method="POST")
def generate_tts(
    text: str,
    exaggeration: float = 0.5,
    temperature: float = 0.8,
    cfg_weight: float = 0.5,
    seed: int = 0
):
    """🎤 Generate TTS audio (JSON endpoint)"""
    
    # Input validation
    if not text or len(text.strip()) == 0:
        return {"error": "Text cannot be empty"}, 400
    
    if len(text) > 500:
        return {"error": "Text must be 500 characters or less"}, 400
    
    try:
        # Load model (cached after first call)
        model = load_model()
        
        # Set seed if provided
        if seed != 0:
            import torch
            torch.manual_seed(seed)
        
        print(f"🎤 Generating TTS for: {text[:50]}...")
        
        # Generate audio
        import torch
        with torch.inference_mode():
            wav = model.generate(
                text=text,
                exaggeration=exaggeration,
                temperature=temperature,
                cfg_weight=cfg_weight
            )
        
        # Convert to base64
        import torchaudio as ta
        audio_buffer = io.BytesIO()
        ta.save(audio_buffer, wav, model.sr, format="wav")
        audio_bytes = audio_buffer.getvalue()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        print("✅ TTS generation successful!")
        
        return {
            "audio_base64": audio_base64,
            "sample_rate": model.sr,
            "message": "TTS generation successful"
        }
        
    except Exception as e:
        print(f"❌ TTS generation error: {e}")
        return {"error": f"TTS generation failed: {str(e)}"}, 500

@app.function(image=image, memory=512)
@modal.web_endpoint(method="GET") 
def health():
    """🏥 Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Chatterbox TTS API",
        "platform": "Modal",
        "gpu_available": True
    }

@app.function(image=image, memory=512)
@modal.web_endpoint(method="GET")
def root():
    """🏠 Root endpoint"""
    return {
        "message": "🎤 Chatterbox TTS API on Modal!",
        "platform": "serverless",
        "gpu": "T4 available",
        "endpoints": {
            "tts": "/generate_tts",
            "health": "/health"
        }
    }

# CLI for local testing
@app.local_entrypoint()
def test():
    """Test the TTS function locally"""
    result = generate_tts.remote("Hello, this is a test of the TTS system!")
    print("Test result:", result)

if __name__ == "__main__":
    # For local development
    test() 