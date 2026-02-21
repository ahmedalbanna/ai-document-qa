from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
from contextlib import asynccontextmanager

from api.upload import router as upload_router
from api.chat import router as chat_router
from api.documents import router as documents_router
from services.vector_store import VectorStoreService
from services.llm import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
vector_store: Optional[VectorStoreService] = None
llm_service: Optional[LLMService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services"""
    global vector_store, llm_service
    
    logger.info("Starting up services...")
    
    # Initialize Qdrant
    vector_store = VectorStoreService(
        host=os.getenv("QDRANT_HOST", "qdrant"),
        port=int(os.getenv("QDRANT_PORT", "6333"))
    )
    await vector_store.initialize()
    
    # Initialize Ollama
    llm_service = LLMService(
        host=os.getenv("OLLAMA_HOST", "ollama"),
        port=int(os.getenv("OLLAMA_PORT", "11434"))
    )
    await llm_service.initialize()
    
    logger.info("Services initialized successfully")
    
    yield
    
    logger.info("Shutting down services...")
    if vector_store:
        await vector_store.close()
    if llm_service:
        await llm_service.close()

# Create FastAPI app
app = FastAPI(
    title="AI Document QA System",
    description="RAG-based document question answering with Ollama",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(documents_router, prefix="/api", tags=["documents"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Document QA System",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "api": "healthy",
        "qdrant": "unknown",
        "ollama": "unknown"
    }
    
    try:
        if vector_store:
            await vector_store.health_check()
            health_status["qdrant"] = "healthy"
    except Exception as e:
        health_status["qdrant"] = f"unhealthy: {str(e)}"
    
    try:
        if llm_service:
            await llm_service.health_check()
            health_status["ollama"] = "healthy"
    except Exception as e:
        health_status["ollama"] = f"unhealthy: {str(e)}"
    
    return health_status

# Make services available to routers
def get_vector_store() -> VectorStoreService:
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    return vector_store

def get_llm_service() -> LLMService:
    if llm_service is None:
        raise HTTPException(status_code=503, detail="LLM service not initialized")
    return llm_service

# Export for use in routers
app.state.get_vector_store = get_vector_store
app.state.get_llm_service = get_llm_service
