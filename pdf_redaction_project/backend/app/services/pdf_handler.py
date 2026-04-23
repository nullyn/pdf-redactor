"""
app/services/pdf_handler.py
Core PDF handling operations using PyMuPDF
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Tuple
import uuid
import logging

logger = logging.getLogger(__name__)

class PDFHandler:
    """Handles PDF reading, text extraction, and coordinate mapping"""

    @staticmethod
    def extract_text_with_coords(pdf_path: str) -> List[Dict]:
        """Extract text from all pages with character-level coordinates."""
        doc = fitz.open(pdf_path)
        pages_data = []

        try:
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                blocks = page.get_text("blocks")

                pages_data.append({
                    "page_num": page_num,
                    "text": text,
                    "blocks": blocks,
                    "page_width": page.rect.width,
                    "page_height": page.rect.height,
                })

            logger.info(f"Extracted text from {len(pages_data)} pages")
            return pages_data

        finally:
            doc.close()

    @staticmethod
    def find_text_coordinates(pdf_path: str, search_text: str, page_num: int) -> List[fitz.Rect]:
        """Find all bounding boxes for a given text on a specific page."""
        doc = fitz.open(pdf_path)
        try:
            if page_num >= len(doc):
                return []

            page = doc[page_num]
            rects = page.search_for(search_text)

            return rects
        finally:
            doc.close()

    @staticmethod
    def apply_redactions(pdf_path: str, output_path: str, redactions: List[Dict]) -> None:
        """Apply permanent redactions to PDF."""
        doc = fitz.open(pdf_path)

        try:
            redactions_by_page = {}
            for redaction in redactions:
                page_num = redaction["page"]
                if page_num not in redactions_by_page:
                    redactions_by_page[page_num] = []
                redactions_by_page[page_num].append(redaction)

            for page_num, page_redactions in redactions_by_page.items():
                if page_num >= len(doc):
                    continue

                page = doc[page_num]

                for redaction in page_redactions:
                    rect = fitz.Rect(redaction["rect"])
                    page.add_redact_annot(rect, fill=(0, 0, 0))

                page.apply_redactions()

            doc.save(output_path, incremental=False)
            logger.info(f"Redacted PDF saved to {output_path}")

        finally:
            doc.close()

    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """Get total number of pages in PDF"""
        doc = fitz.open(pdf_path)
        try:
            return len(doc)
        finally:
            doc.close()

    @staticmethod
    def validate_pdf(pdf_path: str) -> Tuple[bool, str]:
        """Validate that file is a proper PDF."""
        try:
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                return False, "PDF has no pages"
            doc.close()
            return True, ""
        except Exception as e:
            return False, str(e)
