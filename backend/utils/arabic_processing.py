"""Arabic text processing utilities for Islamic content"""
import re
from typing import Dict, List, Optional
import unicodedata
import logging

logger = logging.getLogger(__name__)

class ArabicTextProcessor:
    """Process and normalize Arabic text"""
    
    # Arabic diacritics (Tashkeel)
    ARABIC_DIACRITICS = [
        '\u064B',  # Fathatan
        '\u064C',  # Dammatan
        '\u064D',  # Kasratan
        '\u064E',  # Fatha
        '\u064F',  # Damma
        '\u0650',  # Kasra
        '\u0651',  # Shadda
        '\u0652',  # Sukun
        '\u0653',  # Maddah
        '\u0654',  # Hamza above
        '\u0655',  # Hamza below
        '\u0656',  # Subscript alef
        '\u0657',  # Inverted damma
        '\u0658',  # Mark noon ghunna
        '\u0670',  # Superscript alef
    ]
    
    # Arabic letter variations
    ARABIC_NORMALIZATIONS = {
        'أ': 'ا',  # Alef with hamza above
        'إ': 'ا',  # Alef with hamza below
        'آ': 'ا',  # Alef with madda
        'ٱ': 'ا',  # Alef wasla
        'ى': 'ي',  # Alef maksura
        'ة': 'ه',  # Taa marbuta
    }
    
    # Common Islamic terms and their variations
    ISLAMIC_TERM_EXPANSIONS = {
        'صبر': ['الصبر', 'صابر', 'صابرين', 'صابرون', 'صبروا', 'اصبر', 'اصبروا'],
        'إيمان': ['الإيمان', 'مؤمن', 'مؤمنون', 'مؤمنين', 'آمن', 'آمنوا', 'يؤمن'],
        'صلاة': ['الصلاة', 'صلى', 'يصلي', 'صلوا', 'مصل', 'مصلين'],
        'زكاة': ['الزكاة', 'زكى', 'يزكي', 'تزكية'],
        'حج': ['الحج', 'حاج', 'حجاج', 'يحج'],
        'جهاد': ['الجهاد', 'جاهد', 'مجاهد', 'مجاهدون', 'يجاهد'],
        'توحيد': ['التوحيد', 'موحد', 'موحدون', 'وحد'],
        'تقوى': ['التقوى', 'تقي', 'متقي', 'متقون', 'اتقى', 'اتقوا'],
        'رحمة': ['الرحمة', 'رحيم', 'رحمن', 'ارحم', 'ترحم'],
        'عبادة': ['العبادة', 'عبد', 'عابد', 'عابدون', 'اعبد', 'اعبدوا'],
    }
    
    def __init__(self):
        """Initialize the processor"""
        self.diacritics_pattern = re.compile('[' + ''.join(self.ARABIC_DIACRITICS) + ']')
    
    def remove_diacritics(self, text: str) -> str:
        """
        Remove all Arabic diacritics from text
        
        Args:
            text: Arabic text with diacritics
            
        Returns:
            Text without diacritics
        """
        return self.diacritics_pattern.sub('', text)
    
    def normalize_arabic(self, text: str, remove_diacritics: bool = True) -> str:
        """
        Normalize Arabic text for better matching
        
        Args:
            text: Arabic text to normalize
            remove_diacritics: Whether to remove diacritical marks
            
        Returns:
            Normalized text
        """
        normalized = text
        
        # Remove diacritics if requested
        if remove_diacritics:
            normalized = self.remove_diacritics(normalized)
        
        # Normalize letter variations
        for original, replacement in self.ARABIC_NORMALIZATIONS.items():
            normalized = normalized.replace(original, replacement)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def preserve_diacritics(self, text: str) -> str:
        """
        Ensure diacritics are preserved (for display/storage)
        
        Args:
            text: Arabic text
            
        Returns:
            Text with Unicode normalization
        """
        # Use NFC normalization to preserve diacritics properly
        return unicodedata.normalize('NFC', text)
    
    def extract_root_words(self, text: str) -> List[str]:
        """
        Extract potential Arabic root words (simplified)
        
        Note: This is a basic implementation. For production,
        consider using libraries like CAMeL Tools or PyArabic
        
        Args:
            text: Arabic text
            
        Returns:
            List of potential root words
        """
        # Remove diacritics and normalize
        normalized = self.normalize_arabic(text)
        
        # Split into words
        words = normalized.split()
        
        # Remove common prefixes and suffixes (simplified)
        roots = []
        for word in words:
            if len(word) < 3:
                continue
            
            # Remove common prefixes
            prefixes = ['ال', 'و', 'ف', 'ب', 'ل', 'ك']
            for prefix in prefixes:
                if word.startswith(prefix) and len(word) > len(prefix) + 2:
                    word = word[len(prefix):]
                    break
            
            # Remove common suffixes
            suffixes = ['ون', 'ين', 'ات', 'ان', 'تي', 'كم', 'هم', 'ها', 'ة', 'ي']
            for suffix in suffixes:
                if word.endswith(suffix) and len(word) > len(suffix) + 2:
                    word = word[:-len(suffix)]
                    break
            
            if len(word) >= 3:
                roots.append(word)
        
        return roots
    
    def expand_islamic_term(self, term: str) -> List[str]:
        """
        Expand an Islamic term to include common variations
        
        Args:
            term: Islamic term in Arabic
            
        Returns:
            List including original term and variations
        """
        normalized_term = self.normalize_arabic(term)
        
        # Check if we have predefined expansions
        for base_term, expansions in self.ISLAMIC_TERM_EXPANSIONS.items():
            if normalized_term in self.normalize_arabic(base_term):
                return [term] + expansions
            for expansion in expansions:
                if normalized_term in self.normalize_arabic(expansion):
                    return [term, base_term] + [e for e in expansions if e != expansion]
        
        # If no predefined expansion, return original
        return [term]
    
    def detect_arabic_script(self, text: str) -> bool:
        """
        Check if text contains Arabic script
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains Arabic characters
        """
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')
        return bool(arabic_pattern.search(text))
    
    def get_text_direction(self, text: str) -> str:
        """
        Determine text direction (RTL for Arabic, LTR otherwise)
        
        Args:
            text: Text to analyze
            
        Returns:
            'rtl' or 'ltr'
        """
        if self.detect_arabic_script(text):
            return 'rtl'
        return 'ltr'
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        Split Arabic text into sentences
        
        Arabic uses different punctuation than English
        
        Args:
            text: Arabic text
            
        Returns:
            List of sentences
        """
        # Arabic sentence delimiters
        # Note: Arabic uses different punctuation marks
        delimiters = [
            '.',   # Period
            '!',   # Exclamation
            '?',   # Question mark
            '؟',   # Arabic question mark
            '.',   # Arabic full stop (same as Latin)
            '؛',   # Arabic semicolon
            '\n',  # Newline
        ]
        
        # Create pattern
        pattern = '|'.join(re.escape(d) for d in delimiters)
        sentences = re.split(f'({pattern})', text)
        
        # Recombine sentences with their delimiters
        result = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ''
            combined = (sentence + delimiter).strip()
            if combined:
                result.append(combined)
        
        # Add last sentence if exists
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())
        
        return result
    
    def clean_arabic_text(self, text: str) -> str:
        """
        Clean Arabic text for processing
        
        - Removes extra whitespace
        - Fixes common encoding issues
        - Normalizes line breaks
        
        Args:
            text: Raw Arabic text
            
        Returns:
            Cleaned text
        """
        # Remove zero-width characters
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\u200c', '')  # Zero-width non-joiner
        text = text.replace('\u200d', '')  # Zero-width joiner
        text = text.replace('\ufeff', '')  # Zero-width no-break space
        
        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalize line breaks
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def format_for_display(self, text: str, add_rtl_mark: bool = True) -> str:
        """
        Format Arabic text for proper display
        
        Args:
            text: Arabic text
            add_rtl_mark: Add RTL mark for proper rendering
            
        Returns:
            Formatted text
        """
        # Preserve diacritics
        formatted = self.preserve_diacritics(text)
        
        # Add RTL mark if requested
        if add_rtl_mark and self.detect_arabic_script(formatted):
            formatted = '\u202B' + formatted + '\u202C'  # RTL embedding
        
        return formatted
    
    def highlight_quranic_text(self, text: str) -> str:
        """
        Add special markers for Qur'anic text
        
        Args:
            text: Text that may contain Qur'anic verses
            
        Returns:
            Text with Qur'anic portions marked
        """
        # Look for bismillah
        text = re.sub(
            r'(بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ)',
            r'🕌 \1 🕌',
            text,
            flags=re.UNICODE
        )
        
        # Look for verse numbers in special brackets
        text = re.sub(
            r'﴿(\d+)﴾',
            r'📖[\1]',
            text,
            flags=re.UNICODE
        )
        
        return text
    
    def create_search_variations(self, query: str) -> List[str]:
        """
        Create search variations for better matching
        
        Args:
            query: Search query in Arabic
            
        Returns:
            List of query variations
        """
        variations = [query]
        
        # Add normalized version
        normalized = self.normalize_arabic(query)
        if normalized != query:
            variations.append(normalized)
        
        # Add version with diacritics removed
        no_diacritics = self.remove_diacritics(query)
        if no_diacritics not in variations:
            variations.append(no_diacritics)
        
        # Extract and add root words
        roots = self.extract_root_words(query)
        for root in roots:
            if root not in variations and len(root) >= 3:
                variations.append(root)
        
        # Add term expansions for Islamic terms
        words = query.split()
        for word in words:
            expansions = self.expand_islamic_term(word)
            for expansion in expansions[:3]:  # Limit to top 3 expansions
                if expansion not in variations:
                    variations.append(expansion)
        
        return variations[:10]  # Limit to 10 variations
    
    def enhance_query(self, query: str) -> str:
        """
        Enhance query with Islamic context
        
        Args:
            query: User's search query
            
        Returns:
            Enhanced query
        """
        # Detect if query is asking about Islamic topics
        islamic_keywords = [
            'ما حكم',  # What is the ruling
            'ما معنى',  # What does it mean
            'من هو',  # Who is
            'كيف',  # How
            'لماذا',  # Why
            'متى',  # When
            'أين',  # Where
        ]
        
        enhanced = query
        
        # If query starts with question word, keep as is
        for keyword in islamic_keywords:
            if query.startswith(keyword):
                return enhanced
        
        # Otherwise, add helpful context
        if not any(keyword in query for keyword in islamic_keywords):
            # Check if asking about a topic
            if len(query.split()) <= 3:
                enhanced = f"ما يقوله الإسلام عن {query}"  # What Islam says about...
        
        return enhanced
