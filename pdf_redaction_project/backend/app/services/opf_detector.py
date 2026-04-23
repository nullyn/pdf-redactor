"""
app/services/opf_detector.py
Entity detection using OpenAI Privacy Filter (OPF) CLI.

Drop-in replacement for ner_detector.py. Requires `opf` on PATH:
    pip install openai-privacy-filter

Device selection: defaults to cpu. Override with OPF_DEVICE env var.
"""

import json
import os
import shutil
import subprocess
from typing import Dict, List

from app.utils.constants import EntityType, OPF_LABEL_MAPPING
import logging

logger = logging.getLogger(__name__)


def _opf_device() -> str:
    return os.environ.get("OPF_DEVICE", "cpu")


def _opf_path() -> str:
    path = shutil.which("opf")
    if not path:
        raise RuntimeError(
            "OpenAI Privacy Filter (opf) is not installed or not on PATH.\n"
            "Install it with: pip install openai-privacy-filter"
        )
    return path


class OPFDetector:
    """Detects PII entities using OpenAI Privacy Filter (OPF) CLI."""

    def detect_entities(self, text: str, timeout: int = 120) -> List[Dict]:
        """Run OPF on text; return list of entity dicts matching the original schema."""
        if not text.strip():
            return []

        cmd = [
            _opf_path(), "redact",
            "--format", "json",
            "--device", _opf_device(),
            "--no-print-color-coded-text",
        ]

        try:
            proc = subprocess.run(
                cmd,
                input=text,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            logger.error("OPF timed out after %ds", timeout)
            return []

        if proc.returncode != 0:
            logger.error("OPF exited %d: %s", proc.returncode, proc.stderr.strip())
            return []

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            logger.error("OPF returned non-JSON: %s", proc.stdout[:200])
            return []

        entities = []
        for span in data.get("detected_spans", []):
            opf_label = span.get("label", "")
            entity_type: EntityType = OPF_LABEL_MAPPING.get(opf_label)
            if entity_type is None:
                logger.debug("Unmapped OPF label: %s", opf_label)
                continue

            entities.append({
                "type": entity_type,
                "text": span.get("text", ""),
                "start": span.get("start", 0),
                "end": span.get("end", 0),
                "source": "OPF",
                "confidence": 0.96,
            })

        logger.debug("OPF found %d entities", len(entities))
        return entities

    def detect_entities_by_page(self, pages_data: List[Dict]) -> Dict[int, List[Dict]]:
        """Detect entities in each page independently."""
        entities_by_page: Dict[int, List[Dict]] = {}

        for page_data in pages_data:
            page_num = page_data["page_num"]
            text = page_data["text"]
            entities = self.detect_entities(text)
            entities_by_page[page_num] = entities
            logger.info("Page %d: found %d entities", page_num, len(entities))

        return entities_by_page
