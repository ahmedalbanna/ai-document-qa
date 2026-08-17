"""Text chunking utilities for RAG"""
import logging
from typing import List, Dict, Any
import re
import os

logger = logging.getLogger(__name__)

# Import Islamic utilities if available
try:
    from backend.utils.islamic_references import IslamicReferenceDetector
    from backend.utils.arabic_processing import ArabicTextProcessor
    ISLAMIC_SUPPORT = True
except ImportError:
    try:
        from utils.islamic_references import IslamicReferenceDetector
        from utils.arabic_processing import ArabicTextProcessor
        ISLAMIC_SUPPORT = True
    except ImportError:
        ISLAMIC_SUPPORT = False
        logger.warning("Islamic utilities not available. Install for enhanced Arabic support.")

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
            
            # If a single sentence is too large, force split it
            if sentence_size > self.chunk_size:
                # Save current chunk if exists
                if current:
                    chunks.append(" ".join(current))
                    current = []
                    current_size = 0
                
                # Force split the long sentence
                for i in range(0, sentence_size, self.chunk_size - self.overlap):
                    chunk = sentence[i:i + self.chunk_size]
                    chunks.append(chunk)
                continue
            
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


class IslamicTextChunker(TextChunker):
    """
    Specialized chunker for Islamic texts (Qur'an, Hadith, scholarly works)
    
    Features:
    - Verse-aware chunking (preserves Qur'anic verses)
    - Hadith preservation (keeps chain of narration with text)
    - Citation detection and metadata enrichment
    - Arabic text handling with diacritics
    """
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200, enable_islamic_features: bool = None):
        """
        Initialize Islamic text chunker
        
        Args:
            chunk_size: Target chunk size
            overlap: Overlap between chunks
            enable_islamic_features: Enable Islamic-specific processing (auto-detect if None)
        """
        super().__init__(chunk_size, overlap)
        
        # Auto-detect Islamic mode from environment
        if enable_islamic_features is None:
            enable_islamic_features = os.getenv('ISLAMIC_MODE', 'false').lower() == 'true'
        
        self.islamic_mode = enable_islamic_features and ISLAMIC_SUPPORT
        
        if self.islamic_mode:
            self.ref_detector = IslamicReferenceDetector()
            self.arabic_processor = ArabicTextProcessor()
            logger.info("Islamic text chunker initialized with Arabic support")
        else:
            self.ref_detector = None
            self.arabic_processor = None
            if enable_islamic_features and not ISLAMIC_SUPPORT:
                logger.warning("Islamic mode requested but utilities not available")
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk Islamic text with special handling
        
        Args:
            text: Text to chunk
            metadata: Document metadata
            
        Returns:
            List of enriched chunks
        """
        if not self.islamic_mode:
            # Fall back to standard chunking
            return super().chunk_text(text, metadata)
        
        # Clean and normalize Arabic text
        text = self.arabic_processor.clean_arabic_text(text)
        
        # Detect content type
        content_type = self.ref_detector.get_content_type(text)
        metadata['content_type'] = content_type
        
        # Use specialized chunking based on content type
        if content_type == 'quran':
            chunks = self._chunk_quran_text(text, metadata)
        elif content_type == 'hadith':
            chunks = self._chunk_hadith_text(text, metadata)
        else:
            # For commentary/scholarly works, use verse-aware chunking
            chunks = self._chunk_with_verse_awareness(text, metadata)
        
        # Enrich all chunks with Islamic metadata
        enriched_chunks = []
        for chunk in chunks:
            enriched_chunk = self._enrich_chunk_metadata(chunk)
            enriched_chunks.append(enriched_chunk)
        
        logger.info(f"Created {len(enriched_chunks)} Islamic chunks from {metadata.get('filename')}")
        return enriched_chunks
    
    def _chunk_quran_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk Qur'anic text while preserving verse boundaries
        
        Qur'anic verses should not be split mid-verse
        """
        chunks = []
        
        # Split by verse markers or detect verse boundaries
        # Common patterns: ﴿١﴾ or (1) or [1]
        verse_pattern = r'(?:﴿\d+﴾|\(\d+\)|^\d+[\.\-\s])'
        
        # Try to detect verses
        verses = re.split(f'({verse_pattern})', text, flags=re.MULTILINE | re.UNICODE)
        
        current_chunk = []
        current_size = 0
        verse_numbers = []
        
        for i, segment in enumerate(verses):
            segment = segment.strip()
            if not segment:
                continue
            
            segment_size = len(segment)
            
            # Check if this is a verse number
            is_verse_num = bool(re.match(verse_pattern, segment, re.UNICODE))
            if is_verse_num:
                verse_numbers.append(segment)
                continue
            
            # If adding this verse exceeds chunk size and we have content
            if current_size + segment_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunk_meta = {
                    **metadata,
                    'verse_numbers': verse_numbers.copy(),
                    'is_complete_verses': True
                }
                chunks.append(self._create_chunk(chunk_text, chunk_meta, len(chunks)))
                
                # Start new chunk with context overlap
                if self.overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-1][-self.overlap:]
                    current_chunk = [overlap_text, segment]
                    current_size = len(overlap_text) + segment_size
                else:
                    current_chunk = [segment]
                    current_size = segment_size
                verse_numbers = []
            else:
                current_chunk.append(segment)
                current_size += segment_size
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_meta = {
                **metadata,
                'verse_numbers': verse_numbers,
                'is_complete_verses': True
            }
            chunks.append(self._create_chunk(chunk_text, chunk_meta, len(chunks)))
        
        return chunks
    
    def _chunk_hadith_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk Hadith text while preserving chain of narration (isnad)
        
        A hadith typically has:
        1. Chain of narration (isnad): عن فلان عن فلان...
        2. The actual hadith text
        """
        chunks = []
        
        # Detect hadith boundaries
        # Common patterns: حدثنا، أخبرنا، عن النبي
        hadith_starts = [
            r'حدثنا\s+\w+',
            r'أخبرنا\s+\w+',
            r'عن\s+\w+\s+قال',
            r'قال\s+رسول\s+الله',
        ]
        
        # Split into individual hadiths
        pattern = '|'.join(f'({p})' for p in hadith_starts)
        parts = re.split(pattern, text, flags=re.UNICODE)
        
        current_hadith = []
        current_size = 0
        
        for part in parts:
            if not part or not part.strip():
                continue
            
            part_size = len(part)
            
            # Check if this starts a new hadith
            is_new_hadith = any(re.match(p, part.strip(), re.UNICODE) for p in hadith_starts)
            
            # If this is a new hadith and we have accumulated content
            if is_new_hadith and current_hadith and current_size > 0:
                # Save previous hadith as one chunk
                hadith_text = ' '.join(current_hadith)
                chunk_meta = {
                    **metadata,
                    'is_complete_hadith': True
                }
                chunks.append(self._create_chunk(hadith_text, chunk_meta, len(chunks)))
                
                # Start new hadith
                current_hadith = [part]
                current_size = part_size
            else:
                current_hadith.append(part)
                current_size += part_size
                
                # If hadith becomes too large, force split
                if current_size > self.chunk_size * 1.5:
                    hadith_text = ' '.join(current_hadith)
                    chunk_meta = {
                        **metadata,
                        'is_complete_hadith': False  # Marked as incomplete
                    }
                    chunks.append(self._create_chunk(hadith_text, chunk_meta, len(chunks)))
                    current_hadith = []
                    current_size = 0
        
        # Add final hadith
        if current_hadith:
            hadith_text = ' '.join(current_hadith)
            chunk_meta = {
                **metadata,
                'is_complete_hadith': True
            }
            chunks.append(self._create_chunk(hadith_text, chunk_meta, len(chunks)))
        
        return chunks if chunks else super().chunk_text(text, metadata)
    
    def _chunk_with_verse_awareness(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk scholarly text while being aware of embedded verses
        
        This preserves Qur'an/Hadith citations within scholarly commentary
        """
        # Use standard chunking but detect verses in each chunk
        base_chunks = super().chunk_text(text, metadata)
        
        # Process each chunk to ensure verses aren't split
        refined_chunks = []
        
        for chunk_dict in base_chunks:
            chunk_text = chunk_dict['text']
            
            # Detect if there are verse references
            refs = self.ref_detector.extract_all_references(chunk_text)
            
            # If chunk contains verses, try to keep them complete
            if refs['quran'] or refs['hadith']:
                # Check if any reference is cut off at the end
                # This is a simplified check - could be enhanced
                needs_refinement = False
                
                # If the chunk ends mid-reference, extend it slightly
                for qref in refs['quran']:
                    if chunk_text.endswith(qref.raw_text[:len(qref.raw_text)//2]):
                        needs_refinement = True
                        break
                
                if not needs_refinement:
                    refined_chunks.append(chunk_dict)
                else:
                    # For now, just mark it and include as-is
                    # Advanced: could look ahead to next chunk
                    chunk_dict['metadata']['has_split_reference'] = True
                    refined_chunks.append(chunk_dict)
            else:
                refined_chunks.append(chunk_dict)
        
        return refined_chunks
    
    def _enrich_chunk_metadata(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich chunk with Islamic metadata (citations, content type, etc.)
        
        Args:
            chunk: Chunk dictionary
            
        Returns:
            Enriched chunk
        """
        text = chunk['text']
        metadata = chunk['metadata']
        
        # Detect all references
        refs = self.ref_detector.extract_all_references(text)
        
        # Add Qur'an references
        if refs['quran']:
            metadata['quran_refs'] = [
                {
                    'surah': ref.surah_number,
                    'surah_name': ref.surah_name,
                    'verse_start': ref.verse_start,
                    'verse_end': ref.verse_end,
                    'text': ref.raw_text
                }
                for ref in refs['quran']
            ]
            metadata['has_quran_citation'] = True
        
        # Add Hadith references
        if refs['hadith']:
            metadata['hadith_refs'] = [
                {
                    'collection': ref.collection,
                    'book': ref.book,
                    'number': ref.number,
                    'text': ref.raw_text
                }
                for ref in refs['hadith']
            ]
            metadata['has_hadith_citation'] = True
        
        # Detect text direction
        metadata['text_direction'] = self.arabic_processor.get_text_direction(text)
        
        # Store both original and normalized versions for better search
        metadata['text_normalized'] = self.arabic_processor.normalize_arabic(text)
        
        return chunk
