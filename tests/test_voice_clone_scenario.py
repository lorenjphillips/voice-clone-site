"""
Test scenario: Voice Clone Service with Knowledge Base
This demonstrates how the knowledge base enhances voice cloning responses.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def setup_voice_clone_knowledge():
    """Set up comprehensive voice cloning knowledge base."""
    
    print("🎙️ Voice Clone Service - Knowledge Base Demo")
    print("=" * 60)
    
    # 1. Reset and add voice cloning specific knowledge
    print("📚 Setting up voice cloning knowledge base...")
    
    voice_clone_docs = [
        # Technical specifications
        "ChatterboxTTS is a state-of-the-art voice cloning system with a 0.5B parameter model trained on 500K hours of clean audio data. It achieves sub-200ms latency for real-time voice generation.",
        
        # Voice cloning process
        "To clone a voice, you need at least 3-5 seconds of clean audio recording. The system analyzes the speaker's unique vocal characteristics including pitch, tone, timbre, and speaking rhythm.",
        
        # Supported features
        "ChatterboxTTS supports multiple languages including English, Spanish, French, German, and Mandarin. It can handle various speaking styles: conversational, narrative, emotional, and professional presentations.",
        
        # Audio quality specs
        "The system outputs high-quality 44.1kHz audio with support for both WAV and MP3 formats. Advanced noise reduction ensures crystal-clear voice synthesis even from imperfect source recordings.",
        
        # API usage
        "Voice cloning API endpoints: POST /tts for text-to-speech with default voice, POST /tts-with-voice for custom voice cloning. Both endpoints accept JSON with 'text' field and optional 'voice_file' path.",
        
        # Best practices
        "For optimal voice cloning results: Use high-quality source audio (minimal background noise), speak naturally in the recording, provide diverse speech samples covering different tones and emotions.",
        
        # Limitations
        "Current limitations: Maximum text length is 5000 characters per request. Voice cloning works best with adult voices (age 18-65). Heavily accented speech may require additional training samples.",
        
        # Use cases
        "Popular use cases include: audiobook narration, video game character voices, corporate training materials, accessibility tools for visually impaired users, and personalized virtual assistants."
    ]
    
    response = requests.post(f"{BASE_URL}/add-knowledge", json={
        "documents": voice_clone_docs,
        "metadatas": [{"category": "voice_cloning"} for _ in voice_clone_docs]
    })
    
    print(f"✅ Added {len(voice_clone_docs)} voice cloning documents")
    print(f"📊 Total documents in KB: {response.json()['knowledge_base_stats']['total_documents']}")
    
    # 2. Test various voice cloning queries
    print("\n💬 Testing Voice Cloning Queries with Knowledge Base...")
    
    test_queries = [
        {
            "query": "How much audio do I need to clone a voice?",
            "context": "User wants to know minimum requirements"
        },
        {
            "query": "What languages does the voice cloning support?",
            "context": "User asking about language capabilities"
        },
        {
            "query": "Can you explain the technical specs of ChatterboxTTS?",
            "context": "Technical user wanting details"
        },
        {
            "query": "What's the best way to record audio for voice cloning?",
            "context": "User needs recording tips"
        },
        {
            "query": "What are the API endpoints for voice cloning?",
            "context": "Developer integration question"
        }
    ]
    
    for test in test_queries:
        print(f"\n{'='*60}")
        print(f"📢 Query: {test['query']}")
        print(f"📝 Context: {test['context']}")
        
        response = requests.post(f"{BASE_URL}/chat-with-knowledge", json={
            "message": test['query'],
            "use_default_voice": True
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 Response: {result['text_response']}")
            print(f"\n📊 Metrics:")
            print(f"  - Sources used: {result['sources_used']}")
            print(f"  - Relevance scores: {[f'{score:.2%}' for score in result['relevance_scores']]}")
            print(f"  - Tokens used: {result['tokens_used']}")
        else:
            print(f"❌ Error: {response.text}")
    
    # 3. Demonstrate a conversation flow
    print(f"\n\n{'='*60}")
    print("🗣️ Simulating a Customer Conversation...")
    
    conversation_id = "customer_001"
    conversation_flow = [
        "I want to create an audiobook with my own voice. Can your system help?",
        "That sounds great! How long does it take to clone my voice?",
        "What format should I record my voice sample in?",
        "Perfect, I'll prepare a recording. Can I use this for commercial purposes?"
    ]
    
    for i, message in enumerate(conversation_flow, 1):
        print(f"\n👤 Customer: {message}")
        
        response = requests.post(f"{BASE_URL}/chat-with-knowledge", json={
            "message": message,
            "conversation_id": conversation_id,
            "use_default_voice": True
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 Assistant: {result['text_response']}")
            if result['sources_used'] > 0:
                print(f"   📎 (Using {result['sources_used']} knowledge sources)")

if __name__ == "__main__":
    setup_voice_clone_knowledge() 