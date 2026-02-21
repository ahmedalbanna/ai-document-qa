"""Embedding generation service using Ollama"""
import logging
from typing import List
import httpx
import asyncio

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Generate embeddings using Ollama"""
    
    def __init__(self, base_url: str, model: str = "nomic-embed-text"):
        """
        Initialize embedding service
        
        Args:
            base_url: Ollama API base URL
            model: Embedding model name
        """
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            data = response.json()
            return data['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process concurrently
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Generate embeddings concurrently for batch
            tasks = [self.generate_embedding(text) for text in batch]
            batch_embeddings = await asyncio.gather(*tasks)
            embeddings.extend(batch_embeddings)
            
            logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        return embeddings
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
