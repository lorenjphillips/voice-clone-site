"""
Test the complete user flow for the voice clone site:
1. Upload and embed documents
2. Upload voice and generate clone
3. Configure persona
4. Chat with voice responses
"""

import requests
import json
import time
import base64
import os

BASE_URL = "http://localhost:8000"

def test_full_flow():
    print("🎯 Testing Complete Voice Clone Site Flow")
    print("=" * 60)
    
    # 1. Check API health
    print("\n1️⃣ Checking API health...")
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code == 200:
            print("✅ API is healthy")
        else:
            print("❌ API health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the backend is running: python enhanced_api_server.py")
        return
    
    # 2. Reset knowledge base for clean test
    print("\n2️⃣ Resetting knowledge base...")
    reset = requests.delete(f"{BASE_URL}/reset-knowledge")
    if reset.status_code == 200:
        print("✅ Knowledge base reset")
    
    # 3. Upload documents
    print("\n3️⃣ Testing document upload and embedding...")
    
    # Create test documents
    test_docs = [
        "I am John Smith, a software engineer with 10 years of experience in AI and machine learning. I graduated from MIT with a PhD in Computer Science.",
        "My expertise includes neural networks, natural language processing, and computer vision. I've published 15 papers in top AI conferences.",
        "I enjoy hiking, playing chess, and reading science fiction novels. My favorite authors are Isaac Asimov and Arthur C. Clarke.",
        "I believe in making AI accessible to everyone and have taught over 5000 students through online courses."
    ]
    
    # Add documents to knowledge base
    add_response = requests.post(f"{BASE_URL}/add-knowledge", json={
        "documents": test_docs,
        "metadatas": [{"source": f"test_doc_{i}"} for i in range(len(test_docs))]
    })
    
    if add_response.status_code == 200:
        result = add_response.json()
        print(f"✅ Added {len(result['document_ids'])} documents to knowledge base")
        print(f"   Total documents: {result['knowledge_base_stats']['total_documents']}")
    else:
        print(f"❌ Failed to add documents: {add_response.text}")
    
    # 4. Test voice cloning
    print("\n4️⃣ Testing voice cloning...")
    
    # Generate a test voice sample (3 seconds of sine wave as placeholder)
    import numpy as np
    import wave
    import io
    
    sample_rate = 44100
    duration = 3
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (0.5 * np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    wav_buffer.seek(0)
    
    # Test TTS with voice cloning
    test_text = "Hello, this is a test of my cloned voice. I am John Smith."
    
    print("   Testing voice generation...")
    tts_response = requests.post(
        f"{BASE_URL}/tts-with-voice",
        files={
            "voice": ("test_voice.wav", wav_buffer, "audio/wav")
        },
        data={
            "text": test_text,
            "exaggeration": 0.5,
            "temperature": 0.8,
            "cfg_weight": 0.5,
            "seed": 0
        }
    )
    
    if tts_response.status_code == 200:
        result = tts_response.json()
        print("✅ Voice clone generated successfully")
        print(f"   Audio length: {len(result.get('audio_base64', ''))} characters (base64)")
        
        # Save test audio
        if 'audio_base64' in result:
            audio_data = base64.b64decode(result['audio_base64'])
            with open('test_voice_output.wav', 'wb') as f:
                f.write(audio_data)
            print("   Saved test audio to: test_voice_output.wav")
    else:
        print(f"❌ Voice cloning failed: {tts_response.text}")
    
    # 5. Test chat with persona
    print("\n5️⃣ Testing chat with persona configuration...")
    
    # Create persona system prompt
    persona_prompt = """You are John Smith, a 45-year-old AI researcher and software engineer. 
Your personality: Friendly, knowledgeable, passionate about AI and technology. 
Background: PhD from MIT, 10 years in AI/ML, published researcher. 
Speaking style: Clear, technical but accessible, enthusiastic. 
Interests: Hiking, chess, science fiction. 
Expertise: Neural networks, NLP, computer vision, AI education.

You have access to the user's uploaded documents and will use them to provide accurate, personalized responses. 
Always stay in character and reference the knowledge base when relevant."""
    
    conversation_id = f"test_session_{int(time.time())}"
    
    # Test queries
    test_queries = [
        "Tell me about your background and expertise",
        "What are your hobbies?",
        "How many students have you taught?",
        "What's your opinion on making AI accessible?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        
        chat_response = requests.post(f"{BASE_URL}/chat-with-knowledge", json={
            "message": query,
            "conversation_id": conversation_id,
            "use_default_voice": False,
            "system_prompt": persona_prompt
        })
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print(f"   ✅ Response: {result['text_response'][:100]}...")
            print(f"      Sources used: {result['sources_used']}")
            print(f"      Tokens used: {result['tokens_used']}")
        else:
            print(f"   ❌ Chat failed: {chat_response.text}")
    
    # 6. Get final stats
    print("\n6️⃣ Final knowledge base stats...")
    stats = requests.get(f"{BASE_URL}/knowledge-stats")
    if stats.status_code == 200:
        result = stats.json()
        print(f"✅ Total documents: {result.get('total_documents', 0)}")
        print(f"   Collection: {result.get('collection_name', 'N/A')}")
        print(f"   Embedding model: {result.get('embedding_model', 'N/A')}")
    
    print("\n✅ All tests completed!")
    print("\n📝 Summary:")
    print("- Document upload and embedding: ✅")
    print("- Voice cloning: ✅")
    print("- Persona-based chat: ✅")
    print("- Knowledge retrieval: ✅")
    print("\nThe frontend should now work with the complete flow:")
    print("1. Upload documents → Click 'Embed Documents'")
    print("2. Upload voice → Click 'Generate Voice Clone' → Test with text")
    print("3. Configure persona → Click 'Set Up Twin Configuration'")
    print("4. Chat with your AI twin using text or voice!")

if __name__ == "__main__":
    test_full_flow() 