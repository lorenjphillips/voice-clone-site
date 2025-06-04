#!/usr/bin/env python3
"""
Simple MPS test with fallback enabled
"""

import torch
import os
import time

# Enable MPS fallback BEFORE importing anything else
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
print("🔧 MPS fallback enabled globally")

def test_mps_with_fallback():
    """Test MPS with automatic CPU fallback for unsupported operations"""
    print("🍎 Testing MPS with CPU Fallback")
    print("=" * 50)
    
    # Check MPS availability
    if not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
        print("❌ MPS not available on this system")
        return False
    
    print("✅ MPS is available")
    
    # Test basic MPS operations
    print("\n1. Testing basic MPS operations...")
    try:
        x = torch.randn(3, 3, device='mps')
        y = torch.randn(3, 3, device='mps')
        z = torch.matmul(x, y)
        print(f"   ✅ Matrix multiplication works: {z.device}")
    except Exception as e:
        print(f"   ❌ Basic operations failed: {e}")
        return False
    
    # Test FFT operation (the problematic one)
    print("\n2. Testing FFT operations (problematic for MPS)...")
    try:
        # This should automatically fall back to CPU with PYTORCH_ENABLE_MPS_FALLBACK=1
        signal = torch.randn(100, device='mps')
        fft_result = torch.fft.fft(signal)
        print(f"   ✅ FFT with fallback works: input={signal.device}, output={fft_result.device}")
    except Exception as e:
        print(f"   ❌ FFT operations failed: {e}")
        return False
    
    # Test ChatterboxTTS model loading
    print("\n3. Testing ChatterboxTTS model loading...")
    try:
        from chatterbox.tts import ChatterboxTTS
        start_time = time.time()
        model = ChatterboxTTS.from_pretrained(device="mps")
        load_time = time.time() - start_time
        print(f"   ✅ Model loaded on MPS: {load_time:.2f}s")
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False
    
    # Test audio generation with fallback
    print("\n4. Testing audio generation with MPS + CPU fallback...")
    try:
        start_time = time.time()
        text = "Testing MPS with automatic CPU fallback for unsupported operations."
        
        # This should use MPS where possible and CPU for FFT operations
        wav = model.generate(text, temperature=0.7, exaggeration=0.5)
        gen_time = time.time() - start_time
        
        print(f"   ✅ Audio generation successful!")
        print(f"   ⏱️  Generation time: {gen_time:.2f}s")
        print(f"   📊 Audio shape: {wav.shape}")
        
        # Save the audio
        import torchaudio as ta
        ta.save("mps_fallback_test.wav", wav.cpu(), model.sr)
        print(f"   💾 Audio saved to: mps_fallback_test.wav")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Audio generation failed: {e}")
        print(f"   📝 Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Simple MPS Test with CPU Fallback")
    print("🔧 PYTORCH_ENABLE_MPS_FALLBACK=1 is set")
    print("-" * 50)
    
    success = test_mps_with_fallback()
    
    if success:
        print("\n🎉 MPS with CPU fallback works!")
        print("✅ ChatterboxTTS can use MPS acceleration with automatic fallback")
        print("📝 This gives you the best of both worlds:")
        print("   • Supported operations run on Apple GPU (faster)")
        print("   • Unsupported operations fall back to CPU (compatible)")
    else:
        print("\n❌ MPS with fallback failed")
        print("💡 The application will continue to use CPU-only mode") 