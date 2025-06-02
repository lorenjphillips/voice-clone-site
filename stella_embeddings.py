import torch
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from kb_config import KBConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StellaEmbeddingService:
    def __init__(self):
        """Initialize Stella embedding model for local use."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Stella model on {self.device}...")
        
        # Load Stella model - will auto-download first time (~6GB)
        self.model = SentenceTransformer(
            KBConfig.EMBEDDING_MODEL,
            device=self.device,
            trust_remote_code=True
        )
        
        # Configure for optimal performance
        self.model.max_seq_length = 512
        logger.info("Stella model loaded successfully")
    
    def encode_documents(self, texts: List[str]) -> np.ndarray:
        """
        Encode documents for storage in knowledge base.
        Uses s2p (search to passage) prompt format.
        """
        if not texts:
            return np.array([])
        
        logger.info(f"Encoding {len(texts)} documents...")
        
        # For documents, we don't need special formatting - they are the passages
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            batch_size=8,  # Conservative batch size for local deployment
            show_progress_bar=True
        )
        
        # Use Matryoshka dimension truncation
        embeddings = embeddings[:, :KBConfig.EMBEDDING_DIMENSION]
        
        logger.info(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode user query for retrieval.
        Uses s2s (search to search) prompt format.
        """
        # Format with Stella's recommended s2p_query prompt for search queries
        formatted_query = f"Instruct: Given a web search query, retrieve relevant passages that answer the query.\nQuery: {query}"
        
        embedding = self.model.encode(
            [formatted_query],
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        
        # Truncate to configured dimension
        return embedding[0][:KBConfig.EMBEDDING_DIMENSION]
    
    def clear_gpu_cache(self):
        """Clear GPU cache to free memory."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache() 