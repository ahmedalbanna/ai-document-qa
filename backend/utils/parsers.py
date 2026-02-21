"""Document parsers for various file formats"""
import io
import logging
from typing import Dict, Any
from pathlib import Path

import PyPDF2
from docx import Document
import pandas as pd
from pptx import Presentation
import markdown
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class DocumentParser:
    """Parse various document formats into text"""
    
    @staticmethod
    async def parse(file_content: bytes, filename: str, file_type: str) -> Dict[str, Any]:
        """
        Parse document based on file type
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            file_type: MIME type or extension
            
        Returns:
            Dict with 'text' and 'metadata'
        """
        extension = Path(filename).suffix.lower()
        
        parsers = {
            '.pdf': DocumentParser._parse_pdf,
            '.txt': DocumentParser._parse_txt,
            '.docx': DocumentParser._parse_docx,
            '.doc': DocumentParser._parse_docx,
            '.md': DocumentParser._parse_markdown,
            '.csv': DocumentParser._parse_csv,
            '.xlsx': DocumentParser._parse_excel,
            '.xls': DocumentParser._parse_excel,
            '.pptx': DocumentParser._parse_pptx,
            '.ppt': DocumentParser._parse_pptx,
            '.html': DocumentParser._parse_html,
            '.htm': DocumentParser._parse_html,
            '.json': DocumentParser._parse_json,
        }
        
        parser = parsers.get(extension)
        if not parser:
            raise ValueError(f"Unsupported file type: {extension}")
        
        try:
            text = await parser(file_content)
            metadata = {
                'filename': filename,
                'file_type': extension,
                'size': len(file_content)
            }
            return {'text': text, 'metadata': metadata}
        except Exception as e:
            logger.error(f"Error parsing {filename}: {str(e)}")
            raise
    
    @staticmethod
    async def _parse_pdf(content: bytes) -> str:
        """Parse PDF files"""
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_parts = []
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if text.strip():
                text_parts.append(f"[Page {page_num + 1}]\n{text}")
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    async def _parse_txt(content: bytes) -> str:
        """Parse text files"""
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode('utf-8', errors='ignore')
    
    @staticmethod
    async def _parse_docx(content: bytes) -> str:
        """Parse DOCX files"""
        doc_file = io.BytesIO(content)
        doc = Document(doc_file)
        
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = ' | '.join(cell.text.strip() for cell in row.cells)
                if row_text.strip():
                    text_parts.append(row_text)
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    async def _parse_markdown(content: bytes) -> str:
        """Parse Markdown files"""
        md_text = content.decode('utf-8')
        # Convert to HTML then extract text for better formatting
        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator='\n\n')
    
    @staticmethod
    async def _parse_csv(content: bytes) -> str:
        """Parse CSV files"""
        csv_file = io.BytesIO(content)
        df = pd.read_csv(csv_file)
        
        # Convert to readable text format
        text_parts = [f"CSV Data with {len(df)} rows and {len(df.columns)} columns\n"]
        text_parts.append(f"Columns: {', '.join(df.columns)}\n")
        
        # Add data in text format
        text_parts.append(df.to_string(index=False))
        
        return "\n".join(text_parts)
    
    @staticmethod
    async def _parse_excel(content: bytes) -> str:
        """Parse Excel files"""
        excel_file = io.BytesIO(content)
        
        # Read all sheets
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        text_parts = []
        for sheet_name, df in excel_data.items():
            text_parts.append(f"=== Sheet: {sheet_name} ===")
            text_parts.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
            text_parts.append(f"Columns: {', '.join(df.columns)}")
            text_parts.append(df.to_string(index=False))
            text_parts.append("")
        
        return "\n".join(text_parts)
    
    @staticmethod
    async def _parse_pptx(content: bytes) -> str:
        """Parse PowerPoint files"""
        pptx_file = io.BytesIO(content)
        prs = Presentation(pptx_file)
        
        text_parts = []
        for slide_num, slide in enumerate(prs.slides):
            text_parts.append(f"=== Slide {slide_num + 1} ===")
            
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text_parts.append(shape.text)
            
            text_parts.append("")
        
        return "\n".join(text_parts)
    
    @staticmethod
    async def _parse_html(content: bytes) -> str:
        """Parse HTML files"""
        html = content.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        return soup.get_text(separator='\n\n')
    
    @staticmethod
    async def _parse_json(content: bytes) -> str:
        """Parse JSON files"""
        data = json.loads(content.decode('utf-8'))
        
        # Convert JSON to readable text
        return json.dumps(data, indent=2, ensure_ascii=False)
