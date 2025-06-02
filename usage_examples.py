"""
Examples of how to use the knowledge base system.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def add_company_knowledge():
    """Example: Add company-specific knowledge."""
    company_docs = [
        "Our company was founded in 2020 and specializes in AI voice technology.",
        "We offer voice cloning services with less than 200ms latency.",
        "Our main product is ChatterboxTTS, an open-source text-to-speech system.",
        "Customer support is available Monday through Friday, 9 AM to 5 PM PST."
    ]
    
    response = requests.post(f"{BASE_URL}/add-knowledge", json={
        "documents": company_docs,
        "metadatas": [{"type": "company_info"} for _ in company_docs]
    })
    
    print("Company knowledge added:", response.json())

def chat_about_company():
    """Example: Chat about company information."""
    queries = [
        "When was the company founded?",
        "What is ChatterboxTTS?",
        "What are your support hours?"
    ]
    
    for query in queries:
        response = requests.post(f"{BASE_URL}/chat-with-knowledge", json={
            "message": query
        })
        
        result = response.json()
        print(f"\nQ: {query}")
        print(f"A: {result['text_response']}")
        print(f"Sources: {result['sources_used']}")

def upload_documentation():
    """Example: Upload a documentation file."""
    # Create a sample file
    with open("sample_docs.txt", "w") as f:
        f.write("""
Voice Cloning Technology

Our voice cloning technology uses advanced neural networks to replicate human speech patterns. The system can clone a voice from just a few seconds of audio input.

Key Features:
- Real-time voice cloning
- High-quality audio output
- Minimal latency (under 200ms)
- Support for multiple languages

The ChatterboxTTS model is based on a 0.5B parameter architecture and has been trained on 500K hours of clean audio data.
        """)
    
    # Upload the file
    with open("sample_docs.txt", "rb") as f:
        response = requests.post(f"{BASE_URL}/upload-text-file", files={"file": f})
    
    print("File upload result:", response.json())

if __name__ == "__main__":
    # Run examples
    add_company_knowledge()
    chat_about_company()
    upload_documentation() 