#!/usr/bin/env python3
"""
Test script to verify MPS (Metal Performance Shaders) functionality
"""

import torch
import os
import time

# Set environment for MPS fallback
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Apply the same CPU-safe patch as in api_server.py for fallback
_original_torch_load = torch.load
def _cpu_safe_load(*args, **kwargs):
    """Ensure all torch.load calls have fallback for compatibility"""
    if 'map_location' not in kwargs:
        kwargs['map_location'] = 'cpu'
    return _original_torch_load(*args, **kwargs)

# Apply the global patch
torch.load = _cpu_safe_load
print("🔧 Applied torch.load patch with MPS fallback enabled")

def test_device_availability():
    """Test what devices are available"""
    print("🖥️  Device Availability Check")
    print("=" * 50)
    
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if hasattr(torch.backends, 'mps'):
        mps_available = torch.backends.mps.is_available()
        print(f"MPS available: {mps_available}")
        if mps_available:
            print("🍎 Apple Silicon GPU detected!")
        else:
            print("🚫 MPS not available on this system")
        return mps_available
    else:
        print("MPS backend not supported in this PyTorch version")
        return False

def test_mps_model_loading():
    """Test loading ChatterboxTTS model with MPS"""
    print("\n🧪 Testing MPS Model Loading")
    print("=" * 50)
    
    # Check if MPS is available
    if not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
        print("❌ MPS not available, cannot test")
        return False
    
    # Test 1: Import
    print("1. Testing import...")
    try:
        from chatterbox.tts import ChatterboxTTS
        print("   ✅ Import successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Model loading with MPS device
    print("2. Testing model loading with MPS device...")
    start_time = time.time()
    try:
        model = ChatterboxTTS.from_pretrained(device="mps")
        load_time = time.time() - start_time
        print(f"   ✅ Model loaded successfully on MPS!")
        print(f"   ⏱️  Load time: {load_time:.2f} seconds")
        print(f"   📍 Sample rate: {model.sr}")
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        print(f"   🔄 This might be due to unsupported operations on MPS")
        return False
    
    # Test 3: Simple tensor operations on MPS
    print("3. Testing basic MPS tensor operations...")
    try:
        test_tensor = torch.randn(2, 2, device="mps")
        result = test_tensor * 2
        print(f"   ✅ Basic MPS operations work: {result.device}")
    except Exception as e:
        print(f"   ❌ MPS tensor operations failed: {e}")
        return False
    
    # Test 4: Audio generation test
    print("4. Testing audio generation with MPS...")
    generation_start = time.time()
    try:
        text = "Hello! This is a test of MPS acceleration with Apple Silicon."
        wav = model.generate(text, exaggeration=0.5, temperature=0.8)
        generation_time = time.time() - generation_start
        print(f"   ✅ Audio generated: shape={wav.shape}, dtype={wav.dtype}")
        print(f"   ⏱️  Generation time: {generation_time:.2f} seconds")
        
        # Save test audio
        import torchaudio as ta
        ta.save("mps_test_output.wav", wav.cpu(), model.sr)
        print(f"   💾 Audio saved to: mps_test_output.wav")
        
    except Exception as e:
        print(f"   ❌ Audio generation failed: {e}")
        print(f"   📝 Error details: {str(e)}")
        return False
    
    print("\n🎉 All MPS tests passed!")
    print("✅ MPS acceleration is working with ChatterboxTTS!")
    return True

def test_performance_comparison():
    """Compare CPU vs MPS performance if both are available"""
    print("\n🏁 Performance Comparison")
    print("=" * 50)
    
    if not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
        print("❌ MPS not available, skipping performance comparison")
        return
    
    try:
        from chatterbox.tts import ChatterboxTTS
        test_text = "This is a performance test for voice synthesis."
        
        # Test CPU
        print("Testing CPU performance...")
        cpu_start = time.time()
        cpu_model = ChatterboxTTS.from_pretrained(device="cpu")
        cpu_load_time = time.time() - cpu_start
        
        cpu_gen_start = time.time()
        cpu_wav = cpu_model.generate(test_text)
        cpu_gen_time = time.time() - cpu_gen_start
        
        print(f"CPU - Load: {cpu_load_time:.2f}s, Generate: {cpu_gen_time:.2f}s")
        
        # Test MPS
        print("Testing MPS performance...")
        mps_start = time.time()
        mps_model = ChatterboxTTS.from_pretrained(device="mps")
        mps_load_time = time.time() - mps_start
        
        mps_gen_start = time.time()
        mps_wav = mps_model.generate(test_text)
        mps_gen_time = time.time() - mps_gen_start
        
        print(f"MPS - Load: {mps_load_time:.2f}s, Generate: {mps_gen_time:.2f}s")
        
        # Compare
        load_speedup = cpu_load_time / mps_load_time if mps_load_time > 0 else 0
        gen_speedup = cpu_gen_time / mps_gen_time if mps_gen_time > 0 else 0
        
        print(f"\n📊 Performance Results:")
        print(f"Load speedup: {load_speedup:.2f}x")
        print(f"Generation speedup: {gen_speedup:.2f}x")
        
        if gen_speedup > 1.1:
            print("🚀 MPS provides significant acceleration!")
        elif gen_speedup > 0.9:
            print("⚖️  MPS and CPU performance are similar")
        else:
            print("🐌 CPU might be faster for this model")
            
    except Exception as e:
        print(f"❌ Performance comparison failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting MPS Testing...")
    print("🍎 Testing Apple Metal Performance Shaders with ChatterboxTTS")
    print("-" * 60)
    
    # Run tests
    devices_ok = test_device_availability()
    
    if devices_ok:
        model_ok = test_mps_model_loading()
        if model_ok:
            test_performance_comparison()
    else:
        print("\n❌ MPS not available on this system")
        print("This test requires an Apple Silicon Mac (M1/M2/M3)")
    
    print("\n" + "=" * 60)
    print("🏁 MPS testing complete!") 