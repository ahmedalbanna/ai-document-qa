"""Islamic reference detection and extraction utilities"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class QuranReference:
    """Qur'an verse reference"""
    surah_number: int
    surah_name: Optional[str]
    verse_start: int
    verse_end: Optional[int]
    raw_text: str
    
    def __str__(self):
        if self.verse_end and self.verse_end != self.verse_start:
            return f"{self.surah_name or f'Surah {self.surah_number}'}: {self.verse_start}-{self.verse_end}"
        return f"{self.surah_name or f'Surah {self.surah_number}'}: {self.verse_start}"

@dataclass
class HadithReference:
    """Hadith reference"""
    collection: str  # Bukhari, Muslim, etc.
    book: Optional[str]
    number: Optional[str]
    raw_text: str
    
    def __str__(self):
        parts = [self.collection]
        if self.book:
            parts.append(f"Book: {self.book}")
        if self.number:
            parts.append(f"#{self.number}")
        return ", ".join(parts)

class IslamicReferenceDetector:
    """Detect and extract Qur'an and Hadith references from Arabic text"""
    
    # Surah names in Arabic (1-114)
    SURAH_NAMES = {
        "الفاتحة": 1, "البقرة": 2, "آل عمران": 3, "النساء": 4, "المائدة": 5,
        "الأنعام": 6, "الأعراف": 7, "الأنفال": 8, "التوبة": 9, "يونس": 10,
        "هود": 11, "يوسف": 12, "الرعد": 13, "إبراهيم": 14, "الحجر": 15,
        "النحل": 16, "الإسراء": 17, "الكهف": 18, "مريم": 19, "طه": 20,
        "الأنبياء": 21, "الحج": 22, "المؤمنون": 23, "النور": 24, "الفرقان": 25,
        "الشعراء": 26, "النمل": 27, "القصص": 28, "العنكبوت": 29, "الروم": 30,
        "لقمان": 31, "السجدة": 32, "الأحزاب": 33, "سبأ": 34, "فاطر": 35,
        "يس": 36, "الصافات": 37, "ص": 38, "الزمر": 39, "غافر": 40,
        "فصلت": 41, "الشورى": 42, "الزخرف": 43, "الدخان": 44, "الجاثية": 45,
        "الأحقاف": 46, "محمد": 47, "الفتح": 48, "الحجرات": 49, "ق": 50,
        "الذاريات": 51, "الطور": 52, "النجم": 53, "القمر": 54, "الرحمن": 55,
        "الواقعة": 56, "الحديد": 57, "المجادلة": 58, "الحشر": 59, "الممتحنة": 60,
        "الصف": 61, "الجمعة": 62, "المنافقون": 63, "التغابن": 64, "الطلاق": 65,
        "التحريم": 66, "الملك": 67, "القلم": 68, "الحاقة": 69, "المعارج": 70,
        "نوح": 71, "الجن": 72, "المزمل": 73, "المدثر": 74, "القيامة": 75,
        "الإنسان": 76, "المرسلات": 77, "النبأ": 78, "النازعات": 79, "عبس": 80,
        "التكوير": 81, "الإنفطار": 82, "المطففين": 83, "الإنشقاق": 84, "البروج": 85,
        "الطارق": 86, "الأعلى": 87, "الغاشية": 88, "الفجر": 89, "البلد": 90,
        "الشمس": 91, "الليل": 92, "الضحى": 93, "الشرح": 94, "التين": 95,
        "العلق": 96, "القدر": 97, "البينة": 98, "الزلزلة": 99, "العاديات": 100,
        "القارعة": 101, "التكاثر": 102, "العصر": 103, "الهمزة": 104, "الفيل": 105,
        "قريش": 106, "الماعون": 107, "الكوثر": 108, "الكافرون": 109, "النصر": 110,
        "المسد": 111, "الإخلاص": 112, "الفلق": 113, "الناس": 114
    }
    
    # Hadith collections in Arabic
    HADITH_COLLECTIONS = {
        "البخاري": "Sahih al-Bukhari",
        "صحيح البخاري": "Sahih al-Bukhari",
        "مسلم": "Sahih Muslim",
        "صحيح مسلم": "Sahih Muslim",
        "أبو داود": "Sunan Abu Dawud",
        "أبي داود": "Sunan Abu Dawud",
        "الترمذي": "Jami' at-Tirmidhi",
        "النسائي": "Sunan an-Nasa'i",
        "ابن ماجه": "Sunan Ibn Majah",
        "أحمد": "Musnad Ahmad",
        "مسند أحمد": "Musnad Ahmad",
        "الموطأ": "Muwatta Malik",
        "موطأ مالك": "Muwatta Malik",
        "الدارمي": "Sunan ad-Darimi"
    }
    
    def __init__(self):
        """Initialize the detector with compiled regex patterns"""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching"""
        
        # Qur'an reference patterns
        # Pattern 1: سورة البقرة آية 255
        # Pattern 2: سورة البقرة: 255
        # Pattern 3: البقرة:255
        # Pattern 4: (البقرة: 255-256)
        # Pattern 5: [2:255]
        
        surah_names = "|".join(re.escape(name) for name in self.SURAH_NAMES.keys())
        
        self.quran_patterns = [
            # سورة [name] آية [number] or الآية [number]
            re.compile(
                rf"سورة\s*({surah_names})\s*(?:آية|الآية)\s*(\d+)(?:\s*-\s*(\d+))?",
                re.UNICODE
            ),
            # سورة [name]: [number]
            re.compile(
                rf"سورة\s*({surah_names})\s*[:\:]\s*(\d+)(?:\s*-\s*(\d+))?",
                re.UNICODE
            ),
            # [name]:[number] (without سورة)
            re.compile(
                rf"({surah_names})\s*[:\:]\s*(\d+)(?:\s*-\s*(\d+))?",
                re.UNICODE
            ),
            # [number]:[verse] format
            re.compile(
                r"[\[\(]?(\d{1,3})\s*[:\:]\s*(\d{1,3})(?:\s*-\s*(\d{1,3}))?[\]\)]?",
                re.UNICODE
            ),
            # Q [number]:[verse]
            re.compile(
                r"[Qq]\s*(\d{1,3})\s*[:\:]\s*(\d{1,3})(?:\s*-\s*(\d{1,3}))?",
                re.UNICODE
            ),
        ]
        
        # Hadith reference patterns
        collections = "|".join(re.escape(name) for name in self.HADITH_COLLECTIONS.keys())
        
        self.hadith_patterns = [
            # صحيح البخاري، كتاب الإيمان، رقم 50
            re.compile(
                rf"({collections})\s*(?:،|,)?\s*(?:كتاب\s+([^،,\d]+?))?\s*(?:،|,)?\s*(?:رقم|رقم الحديث|حديث)\s*(\d+)",
                re.UNICODE
            ),
            # رواه البخاري (رقم 50)
            re.compile(
                rf"رواه\s+({collections})\s*[\(\[]?\s*(?:رقم\s*)?(\d+)\s*[\)\]]?",
                re.UNICODE
            ),
            # أخرجه مسلم في كتاب الإيمان
            re.compile(
                rf"أخرجه\s+({collections})\s*(?:في\s+كتاب\s+([^،,\d]+))?",
                re.UNICODE
            ),
            # متفق عليه (both Bukhari and Muslim)
            re.compile(
                r"متفق\s+عليه",
                re.UNICODE
            ),
        ]
    
    def detect_quran_references(self, text: str) -> List[QuranReference]:
        """
        Detect all Qur'an references in text
        
        Args:
            text: Arabic text to search
            
        Returns:
            List of QuranReference objects
        """
        references = []
        
        for pattern in self.quran_patterns:
            for match in pattern.finditer(text):
                try:
                    ref = self._parse_quran_match(match)
                    if ref:
                        references.append(ref)
                except Exception as e:
                    logger.warning(f"Failed to parse Qur'an reference: {match.group(0)}, error: {e}")
        
        # Remove duplicates based on raw_text
        unique_refs = []
        seen_texts = set()
        for ref in references:
            if ref.raw_text not in seen_texts:
                unique_refs.append(ref)
                seen_texts.add(ref.raw_text)
        
        return unique_refs
    
    def _parse_quran_match(self, match: re.Match) -> Optional[QuranReference]:
        """Parse a regex match into a QuranReference"""
        groups = match.groups()
        raw_text = match.group(0)
        
        # Determine format and extract data
        if len(groups) >= 2:
            first = groups[0]
            
            # Check if first group is surah name
            if first in self.SURAH_NAMES:
                surah_number = self.SURAH_NAMES[first]
                surah_name = first
                verse_start = int(groups[1])
                verse_end = int(groups[2]) if len(groups) > 2 and groups[2] else None
            else:
                # Numeric format [surah:verse]
                try:
                    surah_number = int(groups[0])
                    if surah_number < 1 or surah_number > 114:
                        return None
                    surah_name = self._get_surah_name(surah_number)
                    verse_start = int(groups[1])
                    verse_end = int(groups[2]) if len(groups) > 2 and groups[2] else None
                except ValueError:
                    return None
            
            return QuranReference(
                surah_number=surah_number,
                surah_name=surah_name,
                verse_start=verse_start,
                verse_end=verse_end,
                raw_text=raw_text
            )
        
        return None
    
    def _get_surah_name(self, surah_number: int) -> Optional[str]:
        """Get surah name by number"""
        for name, num in self.SURAH_NAMES.items():
            if num == surah_number:
                return name
        return None
    
    def detect_hadith_references(self, text: str) -> List[HadithReference]:
        """
        Detect all Hadith references in text
        
        Args:
            text: Arabic text to search
            
        Returns:
            List of HadithReference objects
        """
        references = []
        
        for pattern in self.hadith_patterns:
            for match in pattern.finditer(text):
                try:
                    ref = self._parse_hadith_match(match)
                    if ref:
                        references.append(ref)
                except Exception as e:
                    logger.warning(f"Failed to parse Hadith reference: {match.group(0)}, error: {e}")
        
        # Remove duplicates
        unique_refs = []
        seen_texts = set()
        for ref in references:
            if ref.raw_text not in seen_texts:
                unique_refs.append(ref)
                seen_texts.add(ref.raw_text)
        
        return unique_refs
    
    def _parse_hadith_match(self, match: re.Match) -> Optional[HadithReference]:
        """Parse a regex match into a HadithReference"""
        groups = match.groups()
        raw_text = match.group(0)
        
        # Handle "متفق عليه" (agreed upon by Bukhari and Muslim)
        if "متفق عليه" in raw_text:
            return HadithReference(
                collection="متفق عليه (Agreed Upon)",
                book=None,
                number=None,
                raw_text=raw_text
            )
        
        if not groups or not groups[0]:
            return None
        
        collection = self.HADITH_COLLECTIONS.get(groups[0], groups[0])
        book = groups[1].strip() if len(groups) > 1 and groups[1] else None
        number = groups[2] if len(groups) > 2 and groups[2] else None
        
        return HadithReference(
            collection=collection,
            book=book,
            number=number,
            raw_text=raw_text
        )
    
    def extract_all_references(self, text: str) -> Dict[str, List]:
        """
        Extract all Islamic references from text
        
        Args:
            text: Arabic text to analyze
            
        Returns:
            Dictionary with 'quran' and 'hadith' lists
        """
        return {
            'quran': self.detect_quran_references(text),
            'hadith': self.detect_hadith_references(text)
        }
    
    def is_quran_verse(self, text: str) -> bool:
        """Check if text appears to be a Qur'an verse"""
        # Common Qur'anic phrases and patterns
        quran_indicators = [
            r"بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",  # Bismillah
            r"يَا أَيُّهَا الَّذِينَ آمَنُوا",  # O you who believe
            r"قُلْ",  # Say (common command in Quran)
            r"إِنَّ اللَّهَ",  # Indeed Allah
            r"وَاللَّهُ",  # And Allah
        ]
        
        for pattern in quran_indicators:
            if re.search(pattern, text, re.UNICODE):
                return True
        
        # Check for verse-ending markers (rare but possible)
        if re.search(r"﴿\d+﴾", text):
            return True
            
        return False
    
    def is_hadith_text(self, text: str) -> bool:
        """Check if text appears to be a Hadith"""
        # Common Hadith indicators
        hadith_indicators = [
            r"عن\s+\w+\s+قال",  # From X, he said
            r"حدثنا",  # He narrated to us
            r"أخبرنا",  # He informed us
            r"عن\s+النبي\s+صلى\s+الله\s+عليه\s+وسلم",  # From the Prophet PBUH
            r"قال\s+رسول\s+الله",  # The Messenger of Allah said
            r"عن\s+أبي\s+هريرة",  # From Abu Huraira (common narrator)
            r"عن\s+عائشة",  # From Aisha
        ]
        
        for pattern in hadith_indicators:
            if re.search(pattern, text, re.UNICODE):
                return True
        
        return False
    
    def get_content_type(self, text: str) -> str:
        """
        Determine the type of Islamic content
        
        Returns:
            'quran', 'hadith', 'commentary', or 'unknown'
        """
        if self.is_quran_verse(text):
            return 'quran'
        elif self.is_hadith_text(text):
            return 'hadith'
        elif self.detect_quran_references(text) or self.detect_hadith_references(text):
            return 'commentary'
        else:
            return 'unknown'
