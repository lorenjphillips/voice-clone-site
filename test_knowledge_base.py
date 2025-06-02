import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_knowledge_system():
    """Test the complete knowledge base system."""
    
    print("🧪 Testing Knowledge Base System")
    print("=" * 50)
    
    # 1. Add some test knowledge
    print("📚 Adding test knowledge...")
    test_docs = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
        "FastAPI is a modern web framework for building APIs with Python, known for its speed and automatic documentation."
    ]
    
    response = requests.post(f"{BASE_URL}/add-knowledge", json={
        "documents": test_docs,
        "metadatas": [{"topic": "tech"} for _ in test_docs]
    })
    
    if response.status_code == 200:
        print("✅ Knowledge added successfully")
        print(f"📊 {response.json()}")
    else:
        print(f"❌ Failed to add knowledge: {response.text}")
        return
    
    # 2. Test chat
    print("\n💬 Testing intelligent chat...")
    test_queries = [
        "What is Python?",
        "Tell me about machine learning",
        "What can you tell me about FastAPI?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        response = requests.post(f"{BASE_URL}/chat-with-knowledge", json={
            "message": query,
            "use_default_voice": True
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {result['text_response'][:100]}...")
            print(f"📊 Sources used: {result['sources_used']}")
            print(f"🎯 Relevance scores: {result['relevance_scores']}")
        else:
            print(f"❌ Error: {response.text}")
    
    # 3. Check stats
    print("\n📈 Knowledge base stats:")
    response = requests.get(f"{BASE_URL}/knowledge-stats")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_knowledge_system() 