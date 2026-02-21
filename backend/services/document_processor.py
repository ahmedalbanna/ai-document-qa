"""Document processing service"""
import logging
from typing import Dict, Any, List
import uuid
from datetime import datetime

from utils.parsers import DocumentParser
from utils.chunking import TextChunker
from services.embeddings import EmbeddingService
from services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process and index documents"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize document processor
        
        Args:
            embedding_service: Service for generating embeddings
            vector_store: Vector store service
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=chunk_overlap)
        self.parser = DocumentParser()
    
    async def process_document(
        self,
        file_content: bytes,
        filename: str,
        file_type: str
    ) -> Dict[str, Any]:
        """
        Process a document end-to-end
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            file_type: MIME type
            
        Returns:
            Processing result with document_id and stats
        """
        logger.info(f"Processing document: {filename}")
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Parse document
        parsed = await self.parser.parse(file_content, filename, file_type)
        text = parsed['text']
        metadata = parsed['metadata']
        metadata['document_id'] = document_id
        metadata['uploaded_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Parsed {len(text)} characters from {filename}")
        
        # Chunk text
        chunks = self.chunker.chunk_text(text, metadata)
        
        if not chunks:
            raise ValueError("No chunks generated from document")
        
        logger.info(f"Created {len(chunks)} chunks")
        
        # Generate embeddings
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = await self.embedding_service.generate_embeddings(chunk_texts)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Store in vector database
        num_stored = await self.vector_store.add_documents(
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id
        )
        
        logger.info(f"Successfully processed document {document_id}")
        
        return {
            'document_id': document_id,
            'filename': filename,
            'chunks': len(chunks),
            'characters': len(text),
            'stored': num_stored,
            'metadata': metadata
        }
    
    async def search_documents(
        self,
        query: str,
        top_k: int = 5,
        document_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search documents using semantic search
        
        Args:
            query: Search query
            top_k: Number of results to return
            document_id: Optional filter by document
            
        Returns:
            List of relevant chunks
        """
        logger.info(f"Searching for: {query}")
        
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Search vector store
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            limit=top_k,
            document_id=document_id
        )
        
        return results
