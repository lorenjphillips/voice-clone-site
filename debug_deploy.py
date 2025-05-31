#!/usr/bin/env python3
"""
Debug script for deployment issues
"""
import os
import sys

def check_environment():
    print("🔍 Environment Check")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check environment variables
    env_vars = [
        'PYTORCH_ENABLE_MPS_FALLBACK',
        'PORT',
        'RENDER',
        'RENDER_SERVICE_NAME'
    ]
    
    print("\n📋 Environment Variables:")
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")

def check_imports():
    print("\n📦 Import Check")
    print("=" * 50)
    
    imports_to_check = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'uvicorn'),
        ('torch', 'PyTorch'),
        ('torchaudio', 'torchaudio'),
        ('transformers', 'transformers'),
        ('diffusers', 'diffusers'),
        ('chatterbox.tts', 'ChatterboxTTS')
    ]
    
    for module, name in imports_to_check:
        try:
            if module == 'chatterbox.tts':
                from chatterbox.tts import ChatterboxTTS
                print(f"  ✅ {name}: Available")
            else:
                __import__(module)
                print(f"  ✅ {name}: Available")
        except ImportError as e:
            print(f"  ❌ {name}: Failed - {e}")
        except Exception as e:
            print(f"  ⚠️  {name}: Error - {e}")

def check_torch_device():
    print("\n🖥️  Device Check")
    print("=" * 50)
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if hasattr(torch.backends, 'mps'):
            print(f"MPS available: {torch.backends.mps.is_available()}")
        else:
            print("MPS: Not supported on this platform")
            
        # Test device selection
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "cpu"  # Use CPU for compatibility
        else:
            device = "cpu"
            
        print(f"Selected device: {device}")
        
        # Test tensor creation
        test_tensor = torch.randn(2, 2, device=device)
        print(f"✅ Device test passed: {test_tensor.device}")
        
    except Exception as e:
        print(f"❌ PyTorch device check failed: {e}")

def check_model_loading():
    print("\n🤖 Model Loading Check")
    print("=" * 50)
    
    try:
        # Set environment for compatibility
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        
        from chatterbox.tts import ChatterboxTTS
        print("✅ ChatterboxTTS import successful")
        
        # Test device detection
        import torch
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
            
        print(f"Using device: {device}")
        
        # Try to load model (this might take a while)
        print("⏳ Attempting to load model...")
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✅ Model loaded successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def main():
    print("🚀 Voice Clone Site - Deployment Debug")
    print("=" * 50)
    
    check_environment()
    check_imports()
    check_torch_device()
    
    # Only try model loading if basic checks pass
    print("\n⚠️  Model loading test (may take 2-3 minutes)...")
    user_input = input("Proceed with model loading test? (y/N): ").lower()
    
    if user_input == 'y':
        success = check_model_loading()
        if success:
            print("\n🎉 All checks passed! Deployment should work.")
        else:
            print("\n❌ Model loading failed. Check the error above.")
    else:
        print("\n⏭️  Skipped model loading test.")
    
    print("\n📋 Debug complete!")

if __name__ == "__main__":
    main() 