# Chatterbox TTS Local Module
"""
Local version of Chatterbox TTS to avoid PyPI dependency conflicts
This is a deployment-compatible version for Render
"""

__version__ = "0.1.0"

from .tts import ChatterboxTTS

__all__ = ["ChatterboxTTS"] 