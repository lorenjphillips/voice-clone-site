# Voice Clone Service with Local Knowledge Base

This implementation adds an intelligent knowledge base to your voice cloning service using **Stella EN 1.5B v5** embeddings, ChromaDB for local vector storage, and OpenAI for response generation.

## Features

- 🧠 **Local Knowledge Base**: Store and retrieve information using state-of-the-art Stella embeddings
- 🎯 **Intelligent RAG**: Retrieval-Augmented Generation for context-aware responses
- 🗣️ **Voice Integration**: Seamlessly integrates with your existing ChatterboxTTS system
- 📚 **Document Management**: Add, search, and manage knowledge documents
- 💬 **Conversational AI**: Maintains conversation context across interactions
- 🚀 **Fast Performance**: Sub-second retrieval with local vector database

## System Requirements

- Python 3.9+
- 8GB RAM minimum (for Stella model)
- ~6GB disk space for model storage
- OpenAI API key

## Installation

1. **Install dependencies:**
   ```bash
   pip install sentence-transformers chromadb openai python-dotenv
   ```

2. **Set up environment variables:**
   Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Quick Start

1. **Start the API server:**
   ```bash
   python3 enhanced_api_server.py
   ```

2. **Test the system:**
   ```bash
   python3 test_knowledge_base.py
   ```

3. **Access API documentation:**
   Open http://localhost:8000/docs in your browser

## API Endpoints

### Knowledge Base Endpoints

#### `POST /chat-with-knowledge`
Chat with AI using the knowledge base.

```json
{
  "message": "What is voice cloning?",
  "voice_file": null,
  "conversation_id": "default",
  "use_default_voice": true
}
```

Response:
```json
{
  "text_response": "Voice cloning is a technology that...",
  "audio_file_path": null,
  "sources_used": 2,
  "relevance_scores": [0.85, 0.78],
  "tokens_used": 245,
  "success": true
}
```

#### `POST /add-knowledge`
Add documents to the knowledge base.

```json
{
  "documents": [
    "ChatterboxTTS supports multiple languages...",
    "Voice cloning requires 3-5 seconds of audio..."
  ],
  "metadatas": [
    {"category": "features"},
    {"category": "requirements"}
  ]
}
```

#### `POST /upload-text-file`
Upload a text file to the knowledge base.

```bash
curl -X POST "http://localhost:8000/upload-text-file" \
  -F "file=@documentation.txt"
```

#### `GET /knowledge-stats`
Get knowledge base statistics.

#### `DELETE /reset-knowledge`
Reset the entire knowledge base (use with caution!).

### Existing TTS Endpoints

Your existing endpoints remain unchanged:
- `POST /tts` - Text-to-speech with default voice
- `POST /tts-with-voice` - Text-to-speech with voice cloning

## Usage Examples

### Adding Company Knowledge

```python
import requests

# Add company-specific information
docs = [
    "Our company specializes in AI voice technology",
    "We offer voice cloning with <200ms latency",
    "Support available Mon-Fri, 9 AM - 5 PM PST"
]

response = requests.post("http://localhost:8000/add-knowledge", json={
    "documents": docs,
    "metadatas": [{"type": "company_info"} for _ in docs]
})
```

### Intelligent Chat with Voice

```python
# Ask a question that uses the knowledge base
response = requests.post("http://localhost:8000/chat-with-knowledge", json={
    "message": "What are your support hours?",
    "use_default_voice": true
})

print(response.json()["text_response"])
# Output: "Support available Monday through Friday, 9 AM to 5 PM PST"
```

### Maintaining Conversations

```python
# First message
response1 = requests.post("http://localhost:8000/chat-with-knowledge", json={
    "message": "I want to clone my voice",
    "conversation_id": "user123"
})

# Follow-up message (maintains context)
response2 = requests.post("http://localhost:8000/chat-with-knowledge", json={
    "message": "How long will it take?",
    "conversation_id": "user123"
})
```

## Configuration

Edit `kb_config.py` to customize:

```python
class KBConfig:
    # OpenAI settings
    OPENAI_MODEL = "gpt-4o-mini"  # or "gpt-4" for better quality
    
    # Embedding settings
    EMBEDDING_DIMENSION = 1024  # Reduce for faster search, increase for better accuracy
    
    # Search settings
    TOP_K_RESULTS = 5  # Number of documents to retrieve
    SIMILARITY_THRESHOLD = 0.7  # Minimum similarity score (0-1)
```

## How It Works

1. **Document Storage**: When you add documents, they're encoded using Stella embeddings and stored in ChromaDB
2. **Query Processing**: User queries are encoded and compared against stored documents
3. **Context Retrieval**: Most relevant documents are retrieved based on cosine similarity
4. **Response Generation**: OpenAI uses the retrieved context to generate accurate responses
5. **Voice Synthesis**: The response can be converted to speech using your ChatterboxTTS system

## Performance

- **First startup**: ~30 seconds (Stella model download)
- **Subsequent startups**: ~10 seconds
- **Document addition**: 1-2 seconds per document
- **Query response**: 2-3 seconds (retrieval + generation)
- **Memory usage**: ~8GB RAM

## Testing

Run the comprehensive test suite:

```bash
# Basic functionality test
python3 test_knowledge_base.py

# Detailed test with debugging
python3 test_detailed.py

# Voice cloning scenario test
python3 test_voice_clone_scenario.py

# Usage examples
python3 usage_examples.py
```

## Integration with Your Voice System

To integrate with your existing ChatterboxTTS:

1. Import your TTS module in `enhanced_api_server.py`
2. Uncomment the TTS integration code
3. The text responses from RAG will automatically be passed to your voice generation

Example:
```python
# In enhanced_api_server.py
from your_existing_tts_module import ChatterboxTTSAPI

# Initialize
tts_service = ChatterboxTTSAPI()

# In the chat endpoint, uncomment:
if request.use_default_voice:
    audio_result = await tts_service.generate_speech(rag_result["response"])
```

## Best Practices

1. **Knowledge Organization**: Group related documents with metadata
2. **Document Quality**: Add clear, concise information for better retrieval
3. **Regular Updates**: Keep knowledge base current with new information
4. **Context Length**: Keep documents focused on single topics
5. **Testing**: Test queries to ensure proper retrieval

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Ensure all dependencies are installed
- Check Python version (3.9+ required)

### No documents retrieved
- Lower the SIMILARITY_THRESHOLD in kb_config.py
- Ensure documents are properly added
- Check if queries match document content

### Slow performance
- Reduce EMBEDDING_DIMENSION for faster search
- Use CPU if GPU issues occur
- Consider batch processing for large documents

## Future Enhancements

When ready for production:
- Add Redis caching for embeddings
- Implement user authentication
- Add rate limiting
- Set up monitoring and logging
- Deploy with Docker
- Add backup/restore functionality

## License

This implementation uses:
- Stella EN 1.5B v5 (MIT License)
- ChromaDB (Apache 2.0)
- OpenAI API (Commercial)

Your existing ChatterboxTTS license remains unchanged. 