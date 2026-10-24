import re
from typing import Tuple

class SkillClassifierService:
    REQUIRED_PATTERNS = [
        r'\bmust\s+have\b', r'\brequired\b', r'\bessential\b', r'\bmandatory\b',
        r'\bstrong\s+knowledge\b', r'\bstrong\s+experience\b', r'\bproficient\s+in\b',
        r'\bexpertise\s+in\b', r'\bminimum\b', r'\bneeds?\s+to\b', r'\bproven\s+track\s+record\b'
    ]

    PREFERRED_PATTERNS = [
        r'\bpreferred\b', r'\bdesirable\b', r'\bgood\s+to\s+have\b', r'\badvantage\b',
        r'\bideal\b', r'\bexperience\s+with.*is\s+a\s+plus\b', r'\bplus\s+point\b'
    ]

    OPTIONAL_PATTERNS = [
        r'\bis\s+a\s+plus\b', r'\bnice\s+to\s+have\b', r'\bfamiliarity\s+with\b',
        r'\bknowledge\s+of\b', r'\boptional\b', r'\bexposure\s+to\b', r'\bbasic\s+understanding\b'
    ]

    @classmethod
    def classify_requirement_and_importance(cls, sentence: str) -> Tuple[str, str]:
        """
        Analyzes surrounding sentence text to determine requirement level and importance.
        Returns: (requirement_level, importance)
        """
        text_lower = sentence.lower()

        # Check OPTIONAL / PLUS patterns first if specific phrase "is a plus" or "nice to have"
        for pat in cls.OPTIONAL_PATTERNS:
            if re.search(pat, text_lower):
                return "OPTIONAL", "Low"

        # Check PREFERRED patterns
        for pat in cls.PREFERRED_PATTERNS:
            if re.search(pat, text_lower):
                return "PREFERRED", "Medium"

        # Check REQUIRED patterns
        for pat in cls.REQUIRED_PATTERNS:
            if re.search(pat, text_lower):
                return "REQUIRED", "High"

        # Default classification if no explicit modifier in sentence
        return "REQUIRED", "High"
