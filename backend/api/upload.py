"""File upload API endpoints"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os

from services.document_processor import DocumentProcessor
from services.embeddings import EmbeddingService
from services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter()

class UploadResponse(BaseModel):
    """Upload response model"""
    success: bool
    document_id: str
    filename: str
    chunks: int
    characters: int
    message: str

# Dependency to get services
def get_services():
    """Get service instances from app state"""
    from main import app
    vector_store = app.state.get_vector_store()
    
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
    
    return processor

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    processor: DocumentProcessor = Depends(get_services)
):
    """
    Upload and process a document
    
    Supports: PDF, TXT, DOCX, MD, CSV, XLSX, PPTX, HTML, JSON
    """
    try:
        logger.info(f"Receiving file: {file.filename}")
        
        # Validate file type
        allowed_extensions = {
            '.pdf', '.txt', '.docx', '.doc', '.md', 
            '.csv', '.xlsx', '.xls', '.pptx', '.ppt',
            '.html', '.htm', '.json'
        }
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported types: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Process document
        result = await processor.process_document(
            file_content=content,
            filename=file.filename,
            file_type=file.content_type or file_ext
        )
        
        return UploadResponse(
            success=True,
            document_id=result['document_id'],
            filename=result['filename'],
            chunks=result['chunks'],
            characters=result['characters'],
            message=f"Successfully processed {result['filename']}"
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
