import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
import os
from kb_config import KBConfig
from stella_embeddings import StellaEmbeddingService
import logging

logger = logging.getLogger(__name__)

class LocalVectorDB:
    def __init__(self):
        """Initialize local ChromaDB with persistence."""
        # Create directory if it doesn't exist
        os.makedirs(KBConfig.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=KBConfig.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize Stella embeddings
        self.embeddings = StellaEmbeddingService()
        
        # Get or create collection
        self._init_collection()
        
    def _init_collection(self):
        """Initialize the knowledge collection."""
        try:
            self.collection = self.client.get_collection(
                name=KBConfig.COLLECTION_NAME
            )
            count = self.collection.count()
            logger.info(f"Loaded existing collection with {count} documents")
        except:
            self.collection = self.client.create_collection(
                name=KBConfig.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Created new knowledge collection")
    
    def add_documents(self, 
                     documents: List[str], 
                     metadatas: Optional[List[Dict]] = None) -> List[str]:
        """Add documents to the local knowledge base."""
        if not documents:
            return []
        
        logger.info(f"Adding {len(documents)} documents to knowledge base...")
        
        # Generate embeddings
        embeddings = self.embeddings.encode_documents(documents)
        
        # Generate unique IDs
        ids = [str(uuid.uuid4()) for _ in documents]
        
        # Prepare metadata
        if metadatas is None:
            metadatas = [{"source": "manual", "type": "document"} for _ in documents]
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Clear GPU cache
        self.embeddings.clear_gpu_cache()
        
        logger.info(f"Successfully added {len(documents)} documents")
        return ids
    
    def search_similar(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents using Stella embeddings."""
        top_k = top_k or KBConfig.TOP_K_RESULTS
        
        logger.info(f"Searching for: '{query[:50]}...'")
        
        # Encode query
        query_embedding = self.embeddings.encode_query(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results with similarity scores
        formatted_results = []
        if results['documents'][0]:  # Check if any results
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                
                # Only include results above threshold
                if similarity >= KBConfig.SIMILARITY_THRESHOLD:
                    formatted_results.append({
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': similarity,
                        'distance': distance
                    })
        
        logger.info(f"Found {len(formatted_results)} relevant documents")
        return formatted_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": KBConfig.COLLECTION_NAME,
            "embedding_model": KBConfig.EMBEDDING_MODEL,
            "embedding_dimension": KBConfig.EMBEDDING_DIMENSION
        }
    
    def reset_database(self):
        """Reset the entire knowledge base (use carefully!)."""
        logger.warning("Resetting knowledge base...")
        self.client.delete_collection(KBConfig.COLLECTION_NAME)
        self._init_collection()
        logger.info("Knowledge base reset complete") 