"""Qdrant vector store service"""
import logging
from typing import List, Dict, Any, Optional
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue
)
from qdrant_client.http import models

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for managing vector embeddings in Qdrant"""
    
    COLLECTION_NAME = "documents"
    VECTOR_SIZE = 768  # Default for many embedding models
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        """Initialize Qdrant client"""
        self.host = host
        self.port = port
        self.client: Optional[QdrantClient] = None
    
    async def initialize(self):
        """Initialize connection and create collection"""
        logger.info(f"Connecting to Qdrant at {self.host}:{self.port}")
        
        self.client = QdrantClient(
            host=self.host,
            port=self.port,
            timeout=30
        )
        
        # Create collection if it doesn't exist
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.COLLECTION_NAME not in collection_names:
            logger.info(f"Creating collection: {self.COLLECTION_NAME}")
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
        else:
            logger.info(f"Collection {self.COLLECTION_NAME} already exists")
    
    async def add_documents(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        document_id: str
    ) -> int:
        """
        Add document chunks with embeddings to vector store
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
            embeddings: List of embedding vectors
            document_id: Unique document identifier
            
        Returns:
            Number of chunks added
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            
            payload = {
                'text': chunk['text'],
                'document_id': document_id,
                'chunk_id': chunk['metadata'].get('chunk_id', i),
                'filename': chunk['metadata'].get('filename', ''),
                'file_type': chunk['metadata'].get('file_type', ''),
                **chunk['metadata']
            }
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=batch
            )
        
        logger.info(f"Added {len(points)} chunks for document {document_id}")
        return len(points)
    
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        document_id: Optional[str] = None,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            document_id: Optional filter by document ID
            score_threshold: Minimum similarity score
            
        Returns:
            List of matching chunks with scores
        """
        search_filter = None
        if document_id:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
        
        results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            query_filter=search_filter,
            score_threshold=score_threshold
        )
        
        chunks = []
        for result in results:
            chunks.append({
                'text': result.payload.get('text', ''),
                'score': result.score,
                'metadata': {
                    'document_id': result.payload.get('document_id', ''),
                    'filename': result.payload.get('filename', ''),
                    'chunk_id': result.payload.get('chunk_id', 0),
                    'file_type': result.payload.get('file_type', '')
                }
            })
        
        logger.info(f"Found {len(chunks)} matching chunks")
        return chunks
    
    async def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks for a document
        
        Args:
            document_id: Document identifier
            
        Returns:
            Number of chunks deleted
        """
        # Get count before deletion
        search_result = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            ),
            limit=10000
        )
        
        count = len(search_result[0])
        
        # Delete points
        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
        )
        
        logger.info(f"Deleted {count} chunks for document {document_id}")
        return count
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get list of all unique documents
        
        Returns:
            List of document metadata
        """
        # Scroll through all points
        scroll_result = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            limit=10000
        )
        
        # Deduplicate by document_id
        documents_map = {}
        for point in scroll_result[0]:
            doc_id = point.payload.get('document_id')
            if doc_id and doc_id not in documents_map:
                documents_map[doc_id] = {
                    'document_id': doc_id,
                    'filename': point.payload.get('filename', ''),
                    'file_type': point.payload.get('file_type', ''),
                    'size': point.payload.get('size', 0)
                }
        
        return list(documents_map.values())
    
    async def health_check(self) -> bool:
        """Check if Qdrant is healthy"""
        collections = self.client.get_collections()
        return True
    
    async def close(self):
        """Close connection"""
        if self.client:
            self.client.close()
            logger.info("Qdrant connection closed")
