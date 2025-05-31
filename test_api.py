#!/usr/bin/env python3
import requests
import base64
import io
import time

def test_api():
    """Test the TTS API locally"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Chatterbox TTS API...")
    
    # Test health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running!")
        print("Run: python3 api_server.py")
        return False
    
    # Test TTS generation
    print("\n2. Testing TTS generation...")
    tts_request = {
        "text": "Hello! This is a test of the API.",
        "exaggeration": 0.7,
        "temperature": 0.8,
        "cfg_weight": 0.5,
        "seed": 42
    }
    
    try:
        print("Sending TTS request...")
        start_time = time.time()
        
        response = requests.post(f"{base_url}/tts", json=tts_request)
        
        if response.status_code == 200:
            end_time = time.time()
            data = response.json()
            
            print(f"✅ TTS generation successful!")
            print(f"⏱️  Generation time: {end_time - start_time:.2f} seconds")
            print(f"📊 Sample rate: {data['sample_rate']} Hz")
            print(f"💬 Message: {data['message']}")
            
            # Decode and save audio
            audio_data = base64.b64decode(data['audio_base64'])
            with open("api_test_output.wav", "wb") as f:
                f.write(audio_data)
            print(f"💾 Audio saved to: api_test_output.wav")
            
            return True
        else:
            print(f"❌ TTS generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def test_model_info():
    """Test the model info endpoint"""
    base_url = "http://localhost:8000"
    
    print("\n3. Testing model info endpoint...")
    try:
        response = requests.get(f"{base_url}/models/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info: {data}")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print("Make sure the API server is running: python3 api_server.py")
    print("-" * 50)
    
    # Run tests
    health_ok = test_api()
    info_ok = test_model_info()
    
    print("\n" + "=" * 50)
    if health_ok and info_ok:
        print("🎉 All tests passed! API is working correctly.")
        print("\n📡 API Endpoints:")
        print("• GET  /          - Health check")
        print("• GET  /health    - Detailed health")
        print("• POST /tts       - Generate TTS")
        print("• GET  /models/info - Model information")
        print("\n🌐 API Documentation: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Check the errors above.") 