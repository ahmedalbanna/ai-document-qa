"""Text chunking utilities for RAG"""
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class TextChunker:
    """Split text into chunks for embedding"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            metadata: Document metadata
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Split by paragraphs first
        paragraphs = self._split_paragraphs(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            # If single paragraph exceeds chunk size, split it
            if para_size > self.chunk_size:
                # Save current chunk if not empty
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append(self._create_chunk(chunk_text, metadata, len(chunks)))
                    current_chunk = []
                    current_size = 0
                
                # Split large paragraph
                sub_chunks = self._split_large_paragraph(para)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk(sub_chunk, metadata, len(chunks)))
            
            # If adding paragraph exceeds chunk size, save current chunk
            elif current_size + para_size > self.chunk_size and current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(self._create_chunk(chunk_text, metadata, len(chunks)))
                
                # Start new chunk with overlap
                if self.overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-1][-self.overlap:] if len(current_chunk[-1]) > self.overlap else current_chunk[-1]
                    current_chunk = [overlap_text, para]
                    current_size = len(overlap_text) + para_size
                else:
                    current_chunk = [para]
                    current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(self._create_chunk(chunk_text, metadata, len(chunks)))
        
        logger.info(f"Created {len(chunks)} chunks from document {metadata.get('filename')}")
        return chunks
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines or multiple newlines
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """Split a large paragraph into smaller chunks"""
        # Try to split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        chunks = []
        current = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > self.chunk_size and current:
                chunks.append(" ".join(current))
                # Keep overlap
                if self.overlap > 0 and current:
                    overlap = current[-1][-self.overlap:] if len(current[-1]) > self.overlap else current[-1]
                    current = [overlap, sentence]
                    current_size = len(overlap) + sentence_size
                else:
                    current = [sentence]
                    current_size = sentence_size
            else:
                current.append(sentence)
                current_size += sentence_size
        
        if current:
            chunks.append(" ".join(current))
        
        return chunks
    
    def _create_chunk(self, text: str, metadata: Dict[str, Any], chunk_id: int) -> Dict[str, Any]:
        """Create a chunk dictionary"""
        return {
            'text': text,
            'metadata': {
                **metadata,
                'chunk_id': chunk_id,
                'chunk_size': len(text)
            }
        }
