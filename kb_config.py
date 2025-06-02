import os
from dotenv import load_dotenv

load_dotenv()

class KBConfig:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4o-mini"  # Cheaper option, or use "gpt-4" for best quality
    
    # Stella Embedding Model
    EMBEDDING_MODEL = "NovaSearch/stella_en_1.5B_v5"
    EMBEDDING_DIMENSION = 1024  # Good balance of performance vs storage
    
    # Local Vector Database
    CHROMA_PERSIST_DIRECTORY = "./knowledge_db"
    COLLECTION_NAME = "local_knowledge"
    
    # RAG Settings
    TOP_K_RESULTS = 5
    SIMILARITY_THRESHOLD = 0.3
    MAX_CONTEXT_LENGTH = 4000
    
    # Your existing TTS settings
    TTS_MODEL_PATH = "./models/chatterbox"  # Keep your existing path 