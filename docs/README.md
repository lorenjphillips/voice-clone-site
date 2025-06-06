<img width="1200" alt="imprint-ai-banner" src="https://github.com/user-attachments/assets/ac385d5c-ff10-490a-88da-336e5787b70d" />

# Imprint AI - Create Your Digital Twin

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://your-demo-url.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Chatterbox TTS](https://img.shields.io/badge/Powered%20by-Chatterbox%20TTS-red)](https://github.com/resemble-ai/chatterbox)

_A complete voice cloning and AI persona creation platform that lets you create a digital version of yourself or anyone else with their voice, knowledge, and personality._

## ✨ Features

### 🎙️ Voice Cloning
- **Zero-shot voice cloning** with just 3-5 seconds of audio
- **High-quality synthesis** using Chatterbox TTS
- **Real-time generation** with ultra-low latency
- **Multiple audio formats** (WAV, MP3, M4A)

### 🧠 Knowledge Base Integration
- **Document upload** - Support for TXT, PDF, DOC, DOCX, MD, CSV, JSON
- **Intelligent RAG** - Powered by Stella EN 1.5B embeddings
- **Context-aware responses** using your personal documents
- **Vector search** with ChromaDB for fast retrieval

### 🤖 AI Persona Creation
- **Customizable personality** - Define age, occupation, interests
- **Speaking style configuration** - Natural conversation patterns
- **Background & expertise** - Detailed knowledge areas
- **Character consistency** - Maintains persona throughout chats

### 💬 Interactive Chat
- **Voice-to-voice conversations** - Speak and hear responses
- **Real-time streaming** - Instant audio playback
- **Progress tracking** - Visual feedback for all steps
- **Modern UI** - Clean interface with dark/light modes

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- 8GB RAM minimum
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/voice-clone-site.git
   cd voice-clone-site
   ```

2. **Set up environment**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

3. **Install dependencies**
   ```bash
   # Backend dependencies
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd frontend && npm install && cd ..
   ```

4. **Start the application**
   ```bash
   # Start backend (Terminal 1)
   python3 enhanced_api_server.py
   
   # Start frontend (Terminal 2)
   cd frontend && npm run dev
   ```

5. **Access the app**
   Open http://localhost:5173 in your browser

## 📖 How It Works

### Step 1: Upload Knowledge Base
- Upload documents or paste text to create your AI's knowledge foundation
- Supports up to 10 documents, 10MB each
- Documents are processed using state-of-the-art embeddings

### Step 2: Clone Your Voice (Optional)
- Upload a 3-5 second clear audio sample
- System generates a voice clone for realistic speech
- Test with custom text before proceeding

### Step 3: Configure AI Persona
- Define personality traits, background, and expertise
- Set speaking style and communication preferences
- Create a consistent character for conversations

### Step 4: Chat with Your Digital Twin
- Have natural conversations using text or voice
- AI responds using your knowledge base and personality
- Hear responses in your cloned voice

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance API framework
- **Chatterbox TTS** - State-of-the-art voice synthesis
- **Stella EN 1.5B v5** - Advanced text embeddings
- **ChromaDB** - Vector database for knowledge storage
- **OpenAI GPT** - Intelligent response generation

### Frontend  
- **React + TypeScript** - Modern UI framework
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Beautiful component library
- **Vite** - Fast build tool

## 📊 Performance

- **Voice generation**: <200ms latency
- **Knowledge retrieval**: <1 second
- **Document processing**: 1-2 seconds per document
- **Memory usage**: ~8GB for full model
- **Audio quality**: 44.1kHz broadcast quality

## 🎯 Use Cases

- **Content Creation** - Generate voiceovers for videos
- **Personal AI Assistant** - Create an AI version of yourself
- **Customer Service** - Build branded voice experiences
- **Education** - Create talking tutors with specific knowledge
- **Entertainment** - Voice characters for games and media

## 🔧 Configuration

Key settings in `kb_config.py`:

```python
# OpenAI Model
OPENAI_MODEL = "gpt-4o-mini"  # Balance of quality and cost

# Embedding Dimension  
EMBEDDING_DIMENSION = 1024  # Speed vs accuracy tradeoff

# Retrieval Settings
TOP_K_RESULTS = 5  # Documents to retrieve
SIMILARITY_THRESHOLD = 0.7  # Relevance threshold
```

## 📱 API Integration

The system provides RESTful APIs for all functionality:

```bash
# Chat with knowledge base
curl -X POST "http://localhost:8000/chat-with-knowledge" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, tell me about yourself"}'

# Generate voice with cloning
curl -X POST "http://localhost:8000/tts-with-voice" \
  -F "text=Hello world!" \
  -F "audio_file=@voice_sample.wav"
```

## 🧪 Testing

Run comprehensive tests:

```bash
# Basic functionality
python3 test_knowledge_base.py

# Voice cloning scenarios  
python3 test_voice_clone_scenario.py

# Usage examples
python3 usage_examples.py
```

## 🚀 Deployment

### Local Development
```bash
python start_dev.py  # Starts both backend and frontend
```

### Production
Ready for deployment on:
- **Render** (Backend)
- **Vercel** (Frontend) 
- **Docker** containers
- **AWS/GCP/Azure** cloud platforms

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Chatterbox TTS**: MIT License
- **Stella EN 1.5B v5**: MIT License  
- **ChromaDB**: Apache 2.0 License
- **React Components**: MIT License

## 🙏 Acknowledgments

- **[Resemble AI](https://resemble.ai)** - For Chatterbox TTS
- **Nova Search** - For Stella embeddings
- **OpenAI** - For GPT models
- **Open Source Community** - For amazing tools and libraries

## 📞 Support

- 📖 **Documentation**: Check the `/docs` folder for detailed guides
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Start a discussion
- 💬 **Community**: Join our Discord server

---

**Built with ❤️ for creating intelligent, voice-enabled AI companions**

*Transform your knowledge and voice into an interactive AI experience*
