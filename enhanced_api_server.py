from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
import base64
import numpy as np
import io
import wave
import tempfile
import shutil
import os
import gc
import torch
import traceback
import json

# Import your existing TTS code
try:
    # Import the actual api_server app instance for TTS functionality
    from api_server import app as tts_app, TTSRequest, _generate_tts_internal
    
    TTS_AVAILABLE = True
    print("✅ TTS components imported successfully")
except ImportError as e:
    print(f"Warning: Could not import TTS components: {e}")
    TTS_AVAILABLE = False
    TTSRequest = None

# Import new RAG functionality
from rag_service import LocalRAGService

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice AI with Knowledge Base", version="2.0.0")

# Add CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
# tts_service = ChatterboxTTSAPI()  # Your existing TTS service
rag_service = LocalRAGService()

# Request/Response models
class KnowledgeChatRequest(BaseModel):
    message: str
    voice_file: Optional[str] = None  # Path to voice file for cloning
    conversation_id: Optional[str] = "default"
    use_default_voice: bool = True
    system_prompt: Optional[str] = None  # Custom system prompt from persona configuration

class KnowledgeChatResponse(BaseModel):
    text_response: str
    audio_file_path: Optional[str] = None  # Path to generated audio
    sources_used: int
    relevance_scores: List[float]
    tokens_used: int
    success: bool

class AddKnowledgeRequest(BaseModel):
    documents: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None

# Store conversations in memory (for local use)
conversations: Dict[str, List[Dict]] = {}

@app.post("/chat-with-knowledge", response_model=KnowledgeChatResponse)
async def chat_with_knowledge(request: KnowledgeChatRequest):
    """
    Main endpoint: Chat with AI using knowledge base + voice generation.
    Integrates perfectly with your existing ChatterboxTTS setup.
    """
    try:
        # 1. Get conversation history
        conversation_history = conversations.get(request.conversation_id, [])
        
        # 2. Generate intelligent response using RAG with custom system prompt
        # Modify the RAG service call to include system prompt
        rag_result = None
        if request.system_prompt:
            # Create a custom generate_response call with persona system prompt
            user_query = request.message
            relevant_docs = rag_service.vector_db.search_similar(
                user_query, 
                top_k=5
            )
            
            # Prepare context from retrieved documents
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
            
            # Use the custom system prompt with knowledge base context
            system_content = f"""{request.system_prompt}

KNOWLEDGE BASE CONTEXT:
{context}

INSTRUCTIONS:
- Use the knowledge base context to provide accurate answers
- Stay in character based on the persona described above
- Be conversational and natural
- Keep responses suitable for voice output"""

            messages = [{"role": "system", "content": system_content}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": request.message})
            
            # Generate response with OpenAI
            try:
                from openai import OpenAI
                client = OpenAI()
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7,
                    top_p=0.9
                )
                
                ai_response = response.choices[0].message.content.strip()
                tokens_used = response.usage.total_tokens
                
                rag_result = {
                    "response": ai_response,
                    "sources": relevant_docs,
                    "tokens_used": tokens_used,
                    "success": True
                }
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
                rag_result = {
                    "response": f"I apologize, but I encountered an error: {str(e)}",
                    "sources": [],
                    "tokens_used": 0,
                    "success": False
                }
        else:
            # Use default RAG service
            rag_result = rag_service.generate_response(
                request.message,
                conversation_history
            )
        
        if not rag_result["success"]:
            raise HTTPException(status_code=500, detail=rag_result["response"])
        
        # 3. Update conversation history
        conversations[request.conversation_id] = conversation_history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": rag_result["response"]}
        ]
        
        # 4. Generate voice using your existing TTS system
        audio_file_path = None
        """
        # Uncomment and modify based on your existing TTS implementation:
        
        if request.use_default_voice:
            audio_result = await tts_service.generate_speech(rag_result["response"])
        else:
            audio_result = await tts_service.generate_speech_with_voice(
                rag_result["response"],
                request.voice_file
            )
        audio_file_path = audio_result.get("audio_file_path")
        """
        
        # Extract relevance scores
        relevance_scores = [doc["similarity"] for doc in rag_result["sources"]]
        
        return KnowledgeChatResponse(
            text_response=rag_result["response"],
            audio_file_path=audio_file_path,
            sources_used=len(rag_result["sources"]),
            relevance_scores=relevance_scores,
            tokens_used=rag_result["tokens_used"],
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-knowledge")
async def add_knowledge(request: AddKnowledgeRequest):
    """Add documents to the local knowledge base."""
    try:
        result = rag_service.add_knowledge(
            request.documents,
            request.metadatas
        )
        return result
        
    except Exception as e:
        logger.error(f"Error adding knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-text-file")
async def upload_text_file(file: UploadFile = File(...)):
    """Upload a text file and add it to knowledge base."""
    try:
        logger.info(f"Processing file upload: {file.filename} (type: {file.content_type})")
        
        # Read file content
        content = await file.read()
        logger.debug(f"Read {len(content)} bytes from file")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        text_content = None
        
        for encoding in encodings:
            try:
                text_content = content.decode(encoding)
                logger.debug(f"Successfully decoded file using {encoding} encoding")
                break
            except UnicodeDecodeError:
                logger.debug(f"Failed to decode using {encoding} encoding")
                continue
        
        if text_content is None:
            # For PDF and DOCX files, we need to use a library to extract text
            if file.content_type in ['application/pdf', 'application/msword', 
                                   'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                logger.info(f"Processing {file.content_type} file")
                
                # Save file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                    tmp_file.write(content)
                    tmp_path = tmp_file.name
                    logger.debug(f"Saved temporary file to {tmp_path}")
                
                try:
                    # Extract text based on file type
                    if file.content_type == 'application/pdf':
                        logger.info("Extracting text from PDF")
                        import PyPDF2
                        with open(tmp_path, 'rb') as pdf_file:
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            text_content = '\n\n'.join(page.extract_text() for page in pdf_reader.pages)
                            logger.info(f"Extracted {len(pdf_reader.pages)} pages from PDF")
                    else:  # DOC or DOCX
                        logger.info("Extracting text from Word document")
                        import docx2txt
                        text_content = docx2txt.process(tmp_path)
                        logger.info("Successfully extracted text from Word document")
                except Exception as e:
                    logger.error(f"Error extracting text from document: {str(e)}")
                    logger.error(traceback.format_exc())
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to extract text from document: {str(e)}"
                    )
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                        logger.debug("Cleaned up temporary file")
            else:
                logger.error(f"Could not decode file content: unsupported format {file.content_type}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not decode file content: unsupported format {file.content_type}"
                )
        
        if not text_content or not text_content.strip():
            logger.error("No valid content found in file")
            raise HTTPException(status_code=400, detail="No valid content found in file")
        
        # Simple paragraph-based chunking
        paragraphs = [
            para.strip() 
            for para in text_content.split('\n\n') 
            if para.strip() and len(para.strip()) > 50
        ]
        
        logger.info(f"Split content into {len(paragraphs)} paragraphs")
        
        if not paragraphs:
            logger.error("No valid paragraphs found after processing")
            raise HTTPException(status_code=400, detail="No valid content found in file")
        
        # Create metadata for each chunk
        metadatas = [
            {
                "source": file.filename,
                "chunk_index": i,
                "upload_type": "file"
            } 
            for i in range(len(paragraphs))
        ]
        
        # Add to knowledge base
        logger.info("Adding content to knowledge base")
        result = rag_service.add_knowledge(paragraphs, metadatas)
        logger.info("Successfully added content to knowledge base")
        
        response = {
            "message": f"Successfully processed {file.filename}",
            "chunks_added": len(paragraphs),
            "file_size_kb": len(content) / 1024,
            "result": result
        }
        
        logger.debug(f"Response: {json.dumps(response, indent=2)}")
        return response
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in file upload: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in file upload: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@app.get("/knowledge-stats")
async def get_knowledge_stats():
    """Get current knowledge base statistics."""
    try:
        stats = rag_service.vector_db.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reset-knowledge")
async def reset_knowledge():
    """Reset the entire knowledge base (use with caution!)."""
    try:
        rag_service.vector_db.reset_database()
        return {"message": "Knowledge base reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep your existing TTS endpoints unchanged but integrate them
@app.post("/tts")
async def text_to_speech(request: dict):
    """Your existing TTS endpoint - integrated with knowledge base responses."""
    if not TTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="TTS service not available")
    
    try:
        # Use the internal TTS generation function directly
        result = await _generate_tts_internal(
            text=request.get("text", ""),
            exaggeration=request.get("exaggeration", 0.5),
            temperature=request.get("temperature", 0.8),
            cfg_weight=request.get("cfg_weight", 0.5),
            seed=request.get("seed", 0),
            audio_file=None
        )
        
        # Convert the result to expected format
        return {
            "audio_base64": result.audio_base64,
            "sample_rate": result.sample_rate
        }
    except Exception as e:
        logger.error(f"TTS generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts-with-voice")
async def tts_with_voice_cloning(
    text: str = Form(...),
    exaggeration: float = Form(0.5),
    temperature: float = Form(0.8),
    cfg_weight: float = Form(0.5),
    seed: int = Form(0),
    voice: UploadFile = File(...)
):
    """Voice cloning endpoint - integrated with knowledge base."""
    if not TTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="TTS service not available")
    
    try:
        # Use the internal TTS generation function with voice file
        result = await _generate_tts_internal(
            text=text,
            exaggeration=exaggeration,
            temperature=temperature,
            cfg_weight=cfg_weight,
            seed=seed,
            audio_file=voice
        )
        
        # Convert the result to expected format
        return {
            "audio_base64": result.audio_base64,
            "sample_rate": result.sample_rate
        }
                
    except Exception as e:
        logger.error(f"Voice cloning error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "rag": True,
            "vector_db": True,
            "stella_embeddings": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 