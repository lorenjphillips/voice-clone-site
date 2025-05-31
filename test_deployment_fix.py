#!/usr/bin/env python3
"""
Test script to verify the Chatterbox TTS deployment fix
"""

import torch
import torchaudio
from chatterbox.tts import ChatterboxTTS

def test_deployment_fix():
    print("🧪 Testing Chatterbox TTS Deployment Fix")
    print("=" * 50)
    
    # Test 1: Import
    print("1. Testing import...")
    try:
        from chatterbox.tts import ChatterboxTTS
        print("   ✅ Import successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Model loading
    print("2. Testing model loading...")
    try:
        model = ChatterboxTTS.from_pretrained(device="cpu")
        print(f"   ✅ Model loaded: {model}")
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False
    
    # Test 3: Audio generation
    print("3. Testing audio generation...")
    try:
        text = "Hello! This is a test of the deployment fix."
        wav = model.generate(text, exaggeration=0.7, temperature=0.8)
        print(f"   ✅ Audio generated: shape={wav.shape}, dtype={wav.dtype}")
    except Exception as e:
        print(f"   ❌ Audio generation failed: {e}")
        return False
    
    # Test 4: Save audio file
    print("4. Testing audio file saving...")
    try:
        output_file = "deployment_test_output.wav"
        torchaudio.save(output_file, wav, model.sr)
        print(f"   ✅ Audio saved to: {output_file}")
    except Exception as e:
        print(f"   ❌ Audio saving failed: {e}")
        return False
    
    # Test 5: PyTorch version compatibility
    print("5. Testing PyTorch compatibility...")
    try:
        torch_version = torch.__version__
        print(f"   ✅ PyTorch version: {torch_version}")
        
        # Check if it's the CPU version
        if "cpu" in torch_version or not torch.cuda.is_available():
            print("   ✅ Using CPU-compatible PyTorch (good for Render)")
        else:
            print("   ⚠️  Using CUDA PyTorch (may not work on Render)")
    except Exception as e:
        print(f"   ❌ PyTorch check failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The deployment fix is working correctly.")
    print("📦 Ready for Render deployment.")
    return True

if __name__ == "__main__":
    success = test_deployment_fix()
    exit(0 if success else 1) 