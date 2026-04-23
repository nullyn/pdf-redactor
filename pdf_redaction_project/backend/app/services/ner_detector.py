"""
app/services/ner_detector.py
Entity detection using spaCy NER and regex patterns
"""

import spacy
import re
from typing import List, Dict, Set
from app.utils.constants import EntityType, REGEX_PATTERNS, NER_LABEL_MAPPING
import logging

logger = logging.getLogger(__name__)

class EntityDetector:
    """Detects PII entities using NER and regex patterns"""

    def __init__(self, spacy_model: str = "en_core_web_lg"):
        """Initialize spaCy model"""
        try:
            self.nlp = spacy.load(spacy_model)
            logger.info(f"Loaded spaCy model: {spacy_model}")
        except OSError:
            logger.error(f"spaCy model '{spacy_model}' not found.")
            raise

    def detect_entities(self, text: str) -> List[Dict]:
        """Detect PII entities in text using NER and regex."""
        entities = []
        entities.extend(self._detect_ner_entities(text))
        entities.extend(self._detect_regex_entities(text))
        entities = self._deduplicate_entities(entities)
        return entities

    def _detect_ner_entities(self, text: str) -> List[Dict]:
        """Detect entities using spaCy NER"""
        entities = []
        doc = self.nlp(text)

        for ent in doc.ents:
            entity_type = NER_LABEL_MAPPING.get(ent.label_)
            if entity_type:
                entities.append({
                    "type": entity_type,
                    "text": ent.text.strip(),
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "source": "NER",
                    "confidence": 0.85,
                })

        return entities

    def _detect_regex_entities(self, text: str) -> List[Dict]:
        """Detect entities using regex patterns"""
        entities = []

        for entity_type, patterns in REGEX_PATTERNS.items():
            for pattern in patterns:
                try:
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        matched_text = match.group(0)
                        if match.groups():
                            matched_text = match.group(1)

                        entities.append({
                            "type": entity_type,
                            "text": matched_text.strip(),
                            "start": match.start(),
                            "end": match.end(),
                            "source": "REGEX",
                            "confidence": 0.95,
                        })
                except re.error as e:
                    logger.warning(f"Regex error for {entity_type}: {e}")

        return entities

    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicate entities"""
        entities = sorted(entities, key=lambda e: (e["start"], e["end"]))
        deduplicated = []
        seen_positions = set()

        for entity in entities:
            pos_key = (entity["start"], entity["end"], entity["type"])

            if pos_key not in seen_positions:
                deduplicated.append(entity)
                seen_positions.add(pos_key)

        return deduplicated

    def detect_entities_by_page(self, pages_data: List[Dict]) -> Dict[int, List[Dict]]:
        """Detect entities in all pages."""
        entities_by_page = {}

        for page_data in pages_data:
            page_num = page_data["page_num"]
            text = page_data["text"]
            entities = self.detect_entities(text)
            entities_by_page[page_num] = entities
            logger.info(f"Page {page_num}: Found {len(entities)} entities")

        return entities_by_page
