# Chatterbox TTS Setup Guide for Mac ARM64

This guide documents the complete process to get the Chatterbox TTS Gradio example working on Mac ARM64 (Apple Silicon M1/M2/M3/M4).

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Understanding the Project](#understanding-the-project)
3. [Dependency Issues and Solutions](#dependency-issues-and-solutions)
4. [Installing Dependencies](#installing-dependencies)
5. [Creating Mac-Optimized Files](#creating-mac-optimized-files)
6. [Testing and Verification](#testing-and-verification)
7. [Running the Gradio App](#running-the-gradio-app)
8. [Troubleshooting](#troubleshooting)

---

## Initial Setup

### Prerequisites
- Mac with Apple Silicon (M1/M2/M3/M4)
- Python 3.8+ (we used Python 3.9.6)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/resemble-ai/chatterbox.git
cd chatterbox
```

### 2. Check Python Version
```bash
python3 --version
# Should show Python 3.8 or higher
```

---

## Understanding the Project

### 3. Explore Project Structure
First, we examined the project structure to understand what we're working with:

```bash
ls -la
```

Key files identified:
- `pyproject.toml` - Project dependencies and configuration
- `gradio_tts_app.py` - Original Gradio TTS interface
- `example_tts.py` - Basic TTS example
- `example_for_mac.py` - Mac-specific example with device handling
- `README.md` - Project documentation

### 4. Read Project Documentation
We examined:
- `README.md` for installation instructions and usage
- `pyproject.toml` for dependency requirements
- Existing example files to understand the API

---

## Dependency Issues and Solutions

### 5. Initial Dependency Problems
The original `pyproject.toml` had strict version requirements that weren't available for Mac ARM64:

**Original problematic dependencies:**
```toml
"torch==2.6.0",
"torchaudio==2.6.0",
```

**Issue:** PyTorch 2.6.0 wasn't available for our Python/Mac combination.

### 6. Fix Dependencies
We modified `pyproject.toml` to use flexible versions:

```toml
# Changed from:
"torch==2.6.0",
"torchaudio==2.6.0",

# To:
"torch>=2.2.0",
"torchaudio>=2.2.0",
```

This allows the installer to use compatible versions already available.

---

## Installing Dependencies

### 7. Install Gradio
```bash
pip3 install gradio
```

### 8. Install Project in Editable Mode
```bash
pip3 install -e .
```

This installs the chatterbox-tts package with our modified dependencies.

**Expected warnings:** You may see dependency conflicts with jupyter packages and torchvision - these don't affect core TTS functionality.

---

## Creating Mac-Optimized Files

### 9. Device Compatibility Issues
The original code had issues with Mac's MPS (Metal Performance Shaders) backend:
- MPS doesn't support all PyTorch operations needed by the TTS model
- Specific error: `'aten::_fft_r2c' is not currently implemented for the MPS device`

### 10. Create Mac-Specific Test Script

Created `test_tts_mac.py`:

```python
#!/usr/bin/env python3
import os
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

# Set environment variable for better compatibility
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

def test_tts():
    print("🎙️ Testing Chatterbox TTS on Mac ARM64...")
    
    # Device detection with fallback to CPU for compatibility
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        # Using CPU for better compatibility with all operations
        device = "cpu"
        print("ℹ️  MPS available but using CPU for maximum compatibility")
    else:
        device = "cpu"
    
    print(f"📱 Using device: {device}")
    
    try:
        print("📥 Loading Chatterbox TTS model...")
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✅ Model loaded successfully!")
        
        # Test text
        text = "Hello! This is a test of the Chatterbox TTS system running on Mac."
        print(f"🗣️  Generating speech for: '{text}'")
        
        # Generate audio
        wav = model.generate(text)
        print("✅ Audio generated successfully!")
        
        # Save the output
        output_file = "test_output_mac.wav"
        ta.save(output_file, wav, model.sr)
        print(f"💾 Audio saved to: {output_file}")
        
        print("🎉 Test completed successfully!")
        print(f"🔊 You can play the audio file: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_tts()
    if success:
        print("\n✅ TTS is working! You can now run the Gradio app.")
    else:
        print("\n❌ TTS test failed. Please check the error above.")
```

### 11. Create Mac-Optimized Gradio App

Created `gradio_tts_app_mac.py` with the following key improvements:

**Device Selection Strategy:**
```python
# Set environment variable for MPS fallback before importing torch
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Detect device - use CPU for better compatibility on Mac
if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    # For now, use CPU instead of MPS due to compatibility issues
    DEVICE = "cpu"
    print("MPS is available but using CPU for better compatibility")
else:
    DEVICE = "cpu"
```

**Enhanced Error Handling:**
```python
def load_model():
    try:
        print("Loading Chatterbox TTS model...")
        model = ChatterboxTTS.from_pretrained(device=DEVICE)
        print("Model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
```

**Improved UI:**
- Added device information display
- Better labeling and tooltips
- Usage tips section
- Mac-specific optimizations

---

## Testing and Verification

### 12. Test Basic TTS Functionality
```bash
python3 test_tts_mac.py
```

**Expected output:**
```
🎙️ Testing Chatterbox TTS on Mac ARM64...
ℹ️  MPS available but using CPU for maximum compatibility
📱 Using device: cpu
📥 Loading Chatterbox TTS model...
✅ Model loaded successfully!
🗣️  Generating speech for: 'Hello! This is a test of the Chatterbox TTS system running on Mac.'
✅ Audio generated successfully!
💾 Audio saved to: test_output_mac.wav
🎉 Test completed successfully!
🔊 You can play the audio file: test_output_mac.wav
```

### 13. Verify Audio File Creation
```bash
ls -la test_output_mac.wav
# Should show a file around 300-400KB
```

---

## Running the Gradio App

### 14. Launch the Gradio Interface
```bash
python3 gradio_tts_app_mac.py
```

**Expected startup output:**
```
Starting Chatterbox TTS Gradio App...
MPS is available but using CPU for better compatibility
Using device: cpu
Loading Chatterbox TTS model...
Model loaded successfully!
Running on local URL:  http://127.0.0.1:7860
```

### 15. Access the Web Interface
- The app will automatically open in your browser
- Or manually navigate to: `http://localhost:7860`
- The interface should show "🎙️ Chatterbox TTS - Mac Version"

### 16. Using the Interface
1. **Enter text** (up to 300 characters)
2. **Adjust settings:**
   - **Exaggeration**: 0.5 for neutral, higher for more expressive
   - **CFG/Pace**: 0.5 default, lower for slower speech
   - **Temperature**: 0.8 for natural variation
3. **Optional:** Upload reference audio for voice cloning
4. **Click "🎙️ Generate Audio"**
5. **Listen to or download** the generated audio

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: MPS Device Errors
**Error:** `'aten::_fft_r2c' is not currently implemented for the MPS device`
**Solution:** The code automatically falls back to CPU for compatibility.

#### Issue: PyTorch Version Conflicts
**Error:** `Could not find a version that satisfies the requirement torch==2.6.0`
**Solution:** We modified dependencies to use flexible versions (`torch>=2.2.0`).

#### Issue: Gradio App Won't Start
**Solution:** 
1. Kill any existing processes: `pkill -f gradio_tts_app`
2. Restart the app: `python3 gradio_tts_app_mac.py`

#### Issue: Model Loading Errors
**Solution:** Ensure you have sufficient RAM (model requires ~4GB) and stable internet for initial download.

### Expected Warnings (Safe to Ignore)
- pkg_resources deprecation warnings
- torchvision image extension loading failures
- Various dependency conflicts with jupyter packages

---

## Key Differences for Mac ARM64

### Device Selection
- **Original:** Uses CUDA if available, otherwise CPU
- **Mac Version:** Prioritizes CPU over MPS for stability

### Environment Variables
- Added `PYTORCH_ENABLE_MPS_FALLBACK=1` for broader operation support

### Error Handling
- Enhanced try-catch blocks
- Better user feedback
- Graceful fallbacks

### UI Improvements
- Device information display
- Mac-specific tips and guidance
- Better parameter explanations

---

## Files Created During Setup

1. **Modified `pyproject.toml`** - Fixed dependency versions
2. **`test_tts_mac.py`** - Test script for verification
3. **`gradio_tts_app_mac.py`** - Mac-optimized Gradio interface
4. **`test_output_mac.wav`** - Sample generated audio file

---

## Summary

This setup process:
1. ✅ Fixed PyTorch version compatibility issues
2. ✅ Addressed Mac ARM64 MPS device limitations
3. ✅ Created robust error handling
4. ✅ Provided comprehensive testing
5. ✅ Delivered a working Gradio interface

The result is a fully functional Chatterbox TTS system optimized for Mac ARM64 that can generate high-quality speech with emotion control through an easy-to-use web interface. 