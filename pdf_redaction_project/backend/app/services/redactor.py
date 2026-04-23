"""
app/services/redactor.py
Core redaction coordination
"""

from typing import List, Dict
from app.services.pdf_handler import PDFHandler
from app.services.ner_detector import EntityDetector
import fitz
import logging

logger = logging.getLogger(__name__)

class RedactionService:
    """Coordinates detection and redaction of PII in PDFs"""

    def __init__(self):
        self.pdf_handler = PDFHandler()
        self.entity_detector = EntityDetector()

    def detect_pii_in_pdf(self, pdf_path: str) -> Dict:
        """Detect all PII in a PDF file."""
        pages_data = self.pdf_handler.extract_text_with_coords(pdf_path)
        entities_by_page = self.entity_detector.detect_entities_by_page(pages_data)
        matched_entities = self._map_entities_to_pdf_coords(pdf_path, pages_data, entities_by_page)

        return {
            "page_count": len(pages_data),
            "matches": matched_entities,
        }

    def _map_entities_to_pdf_coords(
        self, pdf_path: str, pages_data: List[Dict], entities_by_page: Dict[int, List[Dict]]
    ) -> List[Dict]:
        """Map detected text entities to PDF bounding boxes."""
        matched_entities = []

        for page_num, entities in entities_by_page.items():
            for entity in entities:
                rects = self.pdf_handler.find_text_coordinates(
                    pdf_path, entity["text"], page_num
                )

                if rects:
                    for rect in rects:
                        matched_entities.append({
                            "page": page_num,
                            "text": entity["text"],
                            "type": entity["type"],
                            "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
                            "source": entity.get("source", "UNKNOWN"),
                            "confidence": entity.get("confidence", 0.0),
                        })
                else:
                    logger.warning(f"Could not find coordinates for '{entity['text']}' on page {page_num}")

        logger.info(f"Mapped {len(matched_entities)} entities to PDF coordinates")
        return matched_entities

    def apply_redactions(
        self, input_path: str, output_path: str, redactions: List[Dict]
    ) -> bool:
        """Apply selected redactions to PDF and save."""
        try:
            self.pdf_handler.apply_redactions(input_path, output_path, redactions)
            logger.info(f"Applied {len(redactions)} redactions to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply redactions: {e}")
            raise
