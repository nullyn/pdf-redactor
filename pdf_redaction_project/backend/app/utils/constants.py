"""
app/utils/constants.py
Entity types and pattern definitions for PII detection
"""

from enum import Enum
from typing import List, Dict

class EntityType(str, Enum):
    """Supported entity types for redaction"""
    # NER-based
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    GPE = "GPE"  # Geopolitical entity (countries, cities)
    ORG = "ORGANIZATION"
    DATE = "DATE"

    # Pattern-based
    DOB = "DOB"  # Date of birth (specific format)
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SSN = "SSN"  # Social Security Number (US)
    CREDIT_CARD = "CREDIT_CARD"
    ZIP_CODE = "ZIP_CODE"
    PASSPORT = "PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    MEDICAL_RECORD = "MEDICAL_RECORD"
    SEX = "SEX"  # Male/Female designation
    ADDRESS = "ADDRESS"
    IP_ADDRESS = "IP_ADDRESS"
    URL = "URL"

# Pattern definitions for regex-based detection
REGEX_PATTERNS: Dict[EntityType, List[str]] = {
    EntityType.DOB: [
        r"(?:DOB|D\.O\.B|Date of Birth)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(?:Born|b\.|b\.d\.)\s*(?:on\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{4}-\d{2}-\d{2})",
    ],
    EntityType.EMAIL: [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    ],
    EntityType.PHONE: [
        r"(?:\+\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})",
        r"\b\d{3}[-.]?\d{4}[-.]?\d{4}\b",
    ],
    EntityType.SSN: [
        r"\b\d{3}-\d{2}-\d{4}\b",
        r"\b\d{9}\b",
    ],
    EntityType.CREDIT_CARD: [
        r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
    ],
    EntityType.ZIP_CODE: [
        r"\b\d{5}(?:-\d{4})?\b",
    ],
    EntityType.PASSPORT: [
        r"(?:Passport|passport)[\s:]*([A-Z0-9]{6,9})",
    ],
    EntityType.DRIVERS_LICENSE: [
        r"(?:DL|Driver.?s License|license)[\s:]*([A-Z0-9]{5,8})",
    ],
    EntityType.MEDICAL_RECORD: [
        r"(?:MRN|Medical Record)[\s:]*([0-9]{6,10})",
    ],
    EntityType.SEX: [
        r"(?:Sex|Gender)[\s:]*(?:Male|Female|M|F|Other)",
    ],
    EntityType.IP_ADDRESS: [
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
    ],
    EntityType.URL: [
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)",
    ],
}

NER_LABEL_MAPPING = {
    "PERSON": EntityType.PERSON,
    "GPE": EntityType.GPE,
    "LOC": EntityType.LOCATION,
    "ORG": EntityType.ORG,
    "DATE": EntityType.DATE,
}
