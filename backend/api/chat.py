"""Chat API endpoints"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json

from services.document_processor import DocumentProcessor
from services.embeddings import EmbeddingService
from services.vector_store import VectorStoreService
from services.llm import LLMService

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    """Chat request model"""
    question: str
    document_id: Optional[str] = None
    model: Optional[str] = None  # Allow user to specify model (llama2, aya, llama3.2)
    top_k: int = 5
    stream: bool = True

class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str
    sources: List[dict]

class Source(BaseModel):
    """Source information"""
    filename: str
    chunk_id: int
    score: float
    text: str

# Dependency to get services
def get_services():
    """Get service instances from app state"""
    from main import app
    vector_store = app.state.get_vector_store()
    llm_service = app.state.get_llm_service()
    
    # Create embedding service
    ollama_host = os.getenv("OLLAMA_HOST", "ollama")
    ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
    base_url = f"http://{ollama_host}:{ollama_port}"
    
    embedding_service = EmbeddingService(
        base_url=base_url,
        model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    )
    
    # Create document processor
    processor = DocumentProcessor(
        embedding_service=embedding_service,
        vector_store=vector_store,
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200"))
    )
    
    return processor, llm_service

@router.post("/chat")
async def chat(
    request: ChatRequest,
    services: tuple = Depends(get_services)
):
    """
    Ask a question about uploaded documents
    
    Uses RAG to retrieve relevant context and generate answers
    """
    try:
        processor, llm_service = services
        
        logger.info(f"Chat request: {request.question}")
        
        # Search for relevant context
        context_chunks = await processor.search_documents(
            query=request.question,
            top_k=request.top_k,
            document_id=request.document_id
        )
        
        if not context_chunks:
            return ChatResponse(
                answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
                sources=[]
            )
        
        # Generate answer with streaming
        if request.stream:
            async def generate():
                # First send sources
                sources_data = [
                    {
                        'filename': chunk['metadata']['filename'],
                        'chunk_id': chunk['metadata']['chunk_id'],
                        'score': chunk['score'],
                        'text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
                    }
                    for chunk in context_chunks
                ]
                
                yield f"data: {json.dumps({'type': 'sources', 'data': sources_data})}\n\n"
                
                # Stream answer with selected model
                selected_model = request.model or os.getenv("LLM_MODEL", "llama2")
                async for chunk_text in llm_service.generate_answer(
                    question=request.question,
                    context_chunks=context_chunks,
                    stream=True,
                    model=selected_model
                ):
                    yield f"data: {json.dumps({'type': 'answer', 'data': chunk_text})}\n\n"
                
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        else:
            # Non-streaming response
            answer = ""
            selected_model = request.model or os.getenv("LLM_MODEL", "llama2")
            async for chunk in llm_service.generate_answer(
                question=request.question,
                context_chunks=context_chunks,
                stream=False,
                model=selected_model
            ):
                answer += chunk
            
            sources = [
                {
                    'filename': chunk['metadata']['filename'],
                    'chunk_id': chunk['metadata']['chunk_id'],
                    'score': chunk['score'],
                    'text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
                }
                for chunk in context_chunks
            ]
            
            return ChatResponse(answer=answer, sources=sources)
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
