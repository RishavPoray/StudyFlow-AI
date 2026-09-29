"""
PDF Service for StudyFlow AI
Extracts text and metadata using pypdf.
"""
import io
from typing import Dict, Any
from pypdf import PdfReader


def extract_pdf_data(file_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
    """
    Extracts text and page count from raw PDF bytes using pypdf.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            extracted_pages.append(page_text.strip())
            
        full_text = "\n\n".join([p for p in extracted_pages if p])
        
        # Clean excessive newlines/spaces
        cleaned_text = " ".join(full_text.split())
        
        # Build text preview (first 500-1000 characters)
        preview_length = 800
        preview = full_text[:preview_length].strip()
        if len(full_text) > preview_length:
            preview += "\n..."

        return {
            "success": True,
            "filename": filename,
            "pages": total_pages,
            "text": full_text,
            "text_preview": preview,
            "char_count": len(full_text),
            "word_count": len(cleaned_text.split())
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract PDF: {str(e)}",
            "filename": filename,
            "pages": 0,
            "text": "",
            "text_preview": ""
        }
