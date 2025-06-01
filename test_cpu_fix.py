#!/usr/bin/env python3
"""
Test script to verify the CPU torch.load patch fix
"""

import torch

# Apply the same CPU-safe patch as in api_server.py
_original_torch_load = torch.load
def _cpu_safe_load(*args, **kwargs):
    """Ensure all torch.load calls map to CPU for compatibility"""
    kwargs['map_location'] = 'cpu'
    return _original_torch_load(*args, **kwargs)

# Apply the global patch
torch.load = _cpu_safe_load
print("🔧 Applied CPU-safe torch.load patch")

def test_cpu_model_loading():
    print("🧪 Testing CPU Model Loading Fix")
    print("=" * 50)
    
    # Test 1: Import
    print("1. Testing import...")
    try:
        from chatterbox.tts import ChatterboxTTS
        print("   ✅ Import successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Model loading with CPU device
    print("2. Testing model loading with CPU device...")
    try:
        model = ChatterboxTTS.from_pretrained(device="cpu")
        print(f"   ✅ Model loaded successfully!")
        print(f"   📍 Sample rate: {model.sr}")
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False
    
    # Test 3: Quick generation test
    print("3. Testing quick audio generation...")
    try:
        text = "Hello! CPU loading is working perfectly."
        wav = model.generate(text, exaggeration=0.5, temperature=0.8)
        print(f"   ✅ Audio generated: shape={wav.shape}, dtype={wav.dtype}")
    except Exception as e:
        print(f"   ❌ Audio generation failed: {e}")
        return False
    
    print("\n🎉 All CPU loading tests passed!")
    print("✅ The torch.load patch successfully fixes the CUDA device error")
    return True

if __name__ == "__main__":
    success = test_cpu_model_loading()
    exit(0 if success else 1) 