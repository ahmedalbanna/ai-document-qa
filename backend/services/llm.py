"""LLM service for question answering using Ollama"""
import logging
from typing import List, Dict, Any, AsyncGenerator
import httpx
import json

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Ollama LLM"""
    
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "llama2"):
        """
        Initialize LLM service
        
        Args:
            host: Ollama host
            port: Ollama port
            model: Model name to use
        """
        self.base_url = f"http://{host}:{port}"
        self.model = model
        self.client: httpx.AsyncClient = None
    
    async def initialize(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(timeout=120.0)
        logger.info(f"LLM service initialized with model: {self.model}")
    
    async def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Generate answer using RAG
        
        Args:
            question: User question
            context_chunks: Retrieved context chunks
            stream: Whether to stream response
            
        Yields:
            Answer text chunks if streaming
        """
        # Build context from chunks
        context = self._build_context(context_chunks)
        
        # Create prompt
        prompt = self._create_prompt(question, context)
        
        # Generate response
        if stream:
            async for chunk in self._stream_generate(prompt):
                yield chunk
        else:
            response = await self._generate(prompt)
            yield response
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context from retrieved chunks"""
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks):
            filename = chunk['metadata'].get('filename', 'Unknown')
            text = chunk['text']
            score = chunk.get('score', 0)
            
            context_parts.append(
                f"[Source {i+1}: {filename} (relevance: {score:.2f})]\n{text}"
            )
        
        return "\n\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create RAG prompt"""
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context.
Use the following context to answer the question. If the answer cannot be found in the context, say so clearly.
Always cite which source(s) you used in your answer by referring to [Source X].

Context:
{context}

Question: {question}

Answer (be accurate, professional, and cite your sources):"""
        
        return prompt
    
    async def _generate(self, prompt: str) -> str:
        """Generate non-streaming response"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            return data['response']
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _stream_generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Ollama is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Ollama health check failed: {str(e)}")
            raise
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("LLM service closed")
