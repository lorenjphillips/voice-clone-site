# Imprint AI - Create Your Digital Twin

A complete voice cloning and AI persona creation platform that combines state-of-the-art voice synthesis with intelligent knowledge base capabilities. Create a digital version of yourself or anyone else with their voice, knowledge, and personality.

## 🌟 Features

### Voice Cloning
- **Zero-shot voice cloning** - Clone any voice with just 3-5 seconds of audio
- **Ultra-low latency** - Sub-200ms generation time
- **High quality** - 44.1kHz audio output
- **Multiple formats** - Support for WAV and MP3

### Knowledge Base
- **Document upload** - Support for TXT, MD, CSV, JSON, PDF, DOC, DOCX
- **Intelligent retrieval** - Powered by Stella EN 1.5B embeddings
- **RAG integration** - Context-aware responses using your documents
- **Conversation memory** - Maintains context across chat sessions

### AI Persona
- **Customizable personality** - Define age, occupation, interests, and more
- **Speaking style** - Configure how your AI twin communicates
- **Background & expertise** - Give your AI detailed knowledge areas
- **Character consistency** - AI stays in character throughout conversations

### User Interface
- **Voice-to-voice chat** - Speak to your AI and hear responses
- **Real-time streaming** - Instant playback of generated audio
- **Progress tracking** - Visual feedback for document processing
- **Modern design** - Clean, intuitive interface with dark/light modes

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- 8GB RAM minimum
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice-clone-site
   ```

2. **Set up environment variables**
   ```bash
   # Create .env file in root directory
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   pip install sentence-transformers chromadb openai python-dotenv
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   python3 enhanced_api_server.py
   ```
   The API will be available at http://localhost:8000

2. **Start the frontend (in a new terminal)**
   ```bash
   cd frontend
   npm run dev
   ```
   The UI will be available at http://localhost:5173

3. **Access the application**
   Open your browser and navigate to http://localhost:5173

## 📖 User Guide

### Creating Your Digital Twin

#### Step 1: Upload Knowledge Base
1. Click on "Upload Knowledge" tab
2. Drag and drop documents or click to browse
   - Supported formats: TXT, MD, CSV, JSON, PDF, DOC, DOCX
   - Maximum 10 documents, 10MB each
3. Alternatively, paste text directly
4. (Optional) Upload a 3-5 second voice sample for cloning

#### Step 2: Configure Persona
1. Click "Next: Configure Persona"
2. Fill in personality details:
   - **Name**: Your AI's name
   - **Age**: Helps define maturity of responses
   - **Occupation**: Professional background
   - **Personality**: Key traits (friendly, analytical, etc.)
   - **Background**: Education and experience
   - **Speaking Style**: How they communicate
   - **Interests**: Topics they're passionate about
   - **Expertise**: Areas of deep knowledge

3. Click "Create AI Twin" to process documents

#### Step 3: Chat with Your AI
1. Type a message or click the microphone to speak
2. Your AI will respond using:
   - The uploaded knowledge base
   - The configured personality
   - The cloned voice (if provided)
3. Responses show how many knowledge sources were used

### Voice Interaction

#### Voice Input (Speech-to-Text)
- Click the microphone button to start recording
- Speak your message clearly
- Click again to stop and send

#### Voice Output (Text-to-Speech)
- Responses are automatically played if voice is configured
- Click "Play" button to replay any message
- Audio uses your uploaded voice sample or default voice

### Tips for Best Results

#### Voice Cloning
- Use clean audio with minimal background noise
- Speak naturally and clearly
- 3-5 seconds is optimal, longer samples don't improve quality
- WAV format preferred over MP3

#### Knowledge Base
- Break large documents into focused topics
- Use clear, well-structured text
- Include diverse content for comprehensive knowledge
- Update regularly to keep information current

#### Persona Configuration
- Be specific about personality traits
- Include relevant professional background
- Define clear areas of expertise
- Consider the speaking style for your use case

## 🛠️ Technical Details

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI    │────▶│  Knowledge  │
│    React    │     │   Server     │     │    Base     │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │ ChatterboxTTS│     │   Stella    │
                    │    Model     │     │ Embeddings  │
                    └──────────────┘     └─────────────┘
```

### Technology Stack

#### Backend
- **FastAPI** - High-performance web framework
- **ChatterboxTTS** - Voice synthesis model
- **Stella EN 1.5B v5** - State-of-the-art embeddings
- **ChromaDB** - Vector database for knowledge storage
- **OpenAI API** - Response generation

#### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **shadcn/ui** - Component library

### API Endpoints

#### Knowledge Base
- `POST /chat-with-knowledge` - Chat with AI using knowledge base
- `POST /add-knowledge` - Add documents to knowledge base
- `POST /upload-text-file` - Upload file for processing
- `GET /knowledge-stats` - Get knowledge base statistics
- `DELETE /reset-knowledge` - Clear knowledge base

#### Voice Synthesis
- `POST /tts` - Generate speech with default voice
- `POST /tts-with-voice` - Generate speech with cloned voice

#### System
- `GET /health` - Check API health status

### Configuration

Edit `kb_config.py` to customize:

```python
# OpenAI Model Selection
OPENAI_MODEL = "gpt-4o-mini"  # or "gpt-4" for better quality

# Embedding Configuration
EMBEDDING_DIMENSION = 1024  # Balance of speed vs accuracy

# Retrieval Settings
TOP_K_RESULTS = 5  # Number of documents to retrieve
SIMILARITY_THRESHOLD = 0.7  # Minimum relevance score
```

## 🧪 Testing

### Run Test Suite
```bash
# Basic functionality test
python3 test_knowledge_base.py

# Detailed debugging test
python3 test_detailed.py

# Voice cloning scenario
python3 test_voice_clone_scenario.py

# Usage examples
python3 usage_examples.py
```

### Manual Testing
1. Upload a text file with personal information
2. Configure a persona matching the content
3. Ask questions about the uploaded content
4. Verify responses use the knowledge base
5. Test voice input/output functionality

## 🚨 Troubleshooting

### Common Issues

#### "API Disconnected" Error
- Ensure backend server is running
- Check port 8000 is not in use: `lsof -i :8000`
- Verify Python environment has all dependencies

#### No Documents Retrieved
- Lower `SIMILARITY_THRESHOLD` in `kb_config.py`
- Ensure documents are properly formatted
- Check query relevance to document content

#### Voice Not Working
- Verify microphone permissions in browser
- Check audio file format (WAV/MP3 only)
- Ensure file size is under 10MB

#### Slow Performance
- First startup downloads Stella model (~6GB)
- Reduce `EMBEDDING_DIMENSION` for faster search
- Consider using GPU if available

### Performance Optimization

#### Memory Usage
- Stella model: ~6GB RAM
- ChromaDB: Variable based on documents
- Recommended: 8GB+ available RAM

#### Processing Speed
- Document embedding: 1-2 seconds per document
- Query response: 2-3 seconds average
- Voice generation: <200ms

## 🔒 Security & Privacy

### Data Storage
- Documents stored locally in `./knowledge_db`
- No data sent to external servers except OpenAI
- Voice samples processed locally

### API Keys
- Store in `.env` file (never commit)
- Use environment variables in production
- Rotate keys regularly

### Best Practices
- Don't upload sensitive personal information
- Use local deployment for private data
- Clear knowledge base after testing

## 📦 Deployment

### Local Deployment
Current setup is optimized for local use. To deploy:

1. **Production Build**
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve with PM2**
   ```bash
   pm2 start enhanced_api_server.py --interpreter python3
   pm2 serve frontend/dist 3000
   ```

### Cloud Deployment
For production deployment, consider:
- Docker containerization
- Redis for caching
- PostgreSQL instead of ChromaDB
- CDN for frontend assets
- SSL certificates
- Rate limiting
- Authentication system

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project uses multiple open-source components:
- **ChatterboxTTS**: MIT License
- **Stella EN 1.5B v5**: MIT License
- **ChromaDB**: Apache 2.0 License
- **Frontend Components**: MIT License

## 🙏 Acknowledgments

- **ChatterboxTTS Team** - For the amazing voice synthesis model
- **Nova Search** - For Stella embeddings
- **OpenAI** - For GPT models
- **Open Source Community** - For all the amazing tools

## 📞 Support

For issues and questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Open an issue on GitHub
- Review existing documentation

---

Built with ❤️ for creating intelligent, voice-enabled AI companions 