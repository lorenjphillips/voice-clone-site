import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_detailed():
    """Test with more detailed debugging."""
    
    print("🧪 Detailed Knowledge Base Test")
    print("=" * 50)
    
    # 1. Reset knowledge base first
    print("🔄 Resetting knowledge base...")
    response = requests.delete(f"{BASE_URL}/reset-knowledge")
    print(f"Reset result: {response.json()}")
    
    # 2. Add specific test knowledge
    print("\n📚 Adding test knowledge...")
    test_docs = [
        "Python is a high-level, interpreted programming language created by Guido van Rossum. It emphasizes readability and simplicity.",
        "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.",
        "FastAPI is a modern Python web framework for building APIs. It's based on standard Python type hints and is very fast."
    ]
    
    response = requests.post(f"{BASE_URL}/add-knowledge", json={
        "documents": test_docs,
        "metadatas": [{"topic": "programming"} for _ in test_docs]
    })
    
    print(f"Add result: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # 3. Test specific queries
    print("\n💬 Testing specific queries...")
    
    # Query that should match the Python document
    query = "Tell me about Python programming language"
    print(f"\nQuery: {query}")
    
    response = requests.post(f"{BASE_URL}/chat-with-knowledge", json={
        "message": query,
        "use_default_voice": True
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['text_response'][:200]}...")
        print(f"Sources used: {result['sources_used']}")
        print(f"Relevance scores: {result['relevance_scores']}")
    else:
        print(f"Error: {response.text}")
    
    # Try another query
    query2 = "What is machine learning?"
    print(f"\nQuery: {query2}")
    
    response = requests.post(f"{BASE_URL}/chat-with-knowledge", json={
        "message": query2,
        "use_default_voice": True
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['text_response'][:200]}...")
        print(f"Sources used: {result['sources_used']}")
        print(f"Relevance scores: {result['relevance_scores']}")

if __name__ == "__main__":
    test_detailed() 