"""Document management API endpoints"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

from services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter()

class Document(BaseModel):
    """Document model"""
    document_id: str
    filename: str
    file_type: str
    size: int = 0

class DeleteResponse(BaseModel):
    """Delete response model"""
    success: bool
    document_id: str
    chunks_deleted: int
    message: str

# Dependency to get vector store
def get_vector_store():
    """Get vector store from app state"""
    from main import app
    return app.state.get_vector_store()

@router.get("/documents", response_model=List[Document])
async def list_documents(
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    """
    List all uploaded documents
    """
    try:
        documents = await vector_store.get_all_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(
    document_id: str,
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    """
    Delete a document and all its chunks
    """
    try:
        chunks_deleted = await vector_store.delete_document(document_id)
        
        if chunks_deleted == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DeleteResponse(
            success=True,
            document_id=document_id,
            chunks_deleted=chunks_deleted,
            message=f"Successfully deleted document with {chunks_deleted} chunks"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    vector_store: VectorStoreService = Depends(get_vector_store)
):
    """
    Get document details
    """
    try:
        documents = await vector_store.get_all_documents()
        doc = next((d for d in documents if d['document_id'] == document_id), None)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
