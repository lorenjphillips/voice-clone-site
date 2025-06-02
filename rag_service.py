import openai
from openai import OpenAI
from typing import List, Dict, Any, Optional
from kb_config import KBConfig
from local_vector_db import LocalVectorDB
import logging

logger = logging.getLogger(__name__)

class LocalRAGService:
    def __init__(self):
        """Initialize RAG service with local vector database."""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=KBConfig.OPENAI_API_KEY)
        if not KBConfig.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize local vector database
        self.vector_db = LocalVectorDB()
        
        logger.info("RAG service initialized successfully")
    
    def generate_response(self, 
                         user_query: str, 
                         conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate intelligent response using RAG (Retrieval-Augmented Generation).
        Perfect for integration with your voice cloning system.
        """
        logger.info(f"Processing query: '{user_query}'")
        
        # 1. Retrieve relevant knowledge
        relevant_docs = self.vector_db.search_similar(
            user_query, 
            top_k=KBConfig.TOP_K_RESULTS
        )
        
        # 2. Prepare context from retrieved documents
        if relevant_docs:
            context_parts = []
            for i, doc in enumerate(relevant_docs, 1):
                similarity_percent = int(doc['similarity'] * 100)
                context_parts.append(
                    f"[Source {i} - {similarity_percent}% relevant]: {doc['document']}"
                )
            context = "\n\n".join(context_parts)
        else:
            context = "No specific information found in knowledge base."
        
        # 3. Build conversation messages
        system_prompt = f"""You are a helpful AI assistant with access to a local knowledge base.

KNOWLEDGE BASE CONTEXT:
{context}

INSTRUCTIONS:
- Use the knowledge base context to provide accurate, helpful answers
- If the context doesn't fully answer the question, supplement with your general knowledge
- Be conversational and friendly - this will be converted to speech
- Keep responses concise but informative (good for voice output)
- If you reference the knowledge base, mention it naturally
- If unsure about something, acknowledge the uncertainty"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user query
        messages.append({"role": "user", "content": user_query})
        
        # 4. Generate response with OpenAI
        try:
            response = self.client.chat.completions.create(
                model=KBConfig.OPENAI_MODEL,
                messages=messages,
                max_tokens=800,  # Good for voice responses
                temperature=0.7,
                top_p=0.9
            )
            
            ai_response = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens
            
            logger.info(f"Generated response ({tokens_used} tokens)")
            
            return {
                "response": ai_response,
                "sources": relevant_docs,
                "tokens_used": tokens_used,
                "model_used": KBConfig.OPENAI_MODEL,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "sources": [],
                "tokens_used": 0,
                "model_used": None,
                "success": False
            }
    
    def add_knowledge(self, 
                     documents: List[str], 
                     metadatas: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Add new documents to the local knowledge base."""
        try:
            doc_ids = self.vector_db.add_documents(documents, metadatas)
            stats = self.vector_db.get_stats()
            
            return {
                "success": True,
                "message": f"Successfully added {len(doc_ids)} documents",
                "document_ids": doc_ids,
                "knowledge_base_stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to add documents: {str(e)}",
                "document_ids": [],
                "knowledge_base_stats": {}
            } 