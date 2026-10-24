import re
from typing import Dict, Any, Optional

class RequirementPriorityService:
    MANDATORY = "Mandatory"
    PREFERRED = "Preferred"
    OPTIONAL = "Optional"
    UNKNOWN = "Unknown"

    MANDATORY_PATTERNS = [
        (r'\b(must\s+have|candidates?\s+must|applicants?\s+must)\b', "The phrase '{}' explicitly states a mandatory requirement."),
        (r'\b(is\s+mandatory|mandatory)\b', "Requirement is explicitly marked as mandatory."),
        (r'\b(is\s+required|required\s+skills?|qualifications?\s+required|required)\b', "The requirement uses the phrase '{}' indicating mandatory status."),
        (r'\b(is\s+essential|essential\s+requirement|essential)\b', "Requirement uses the term '{}' indicating it is essential."),
        (r'\b(minimum\s+qualifications?|minimum\s+years?|minimum)\b', "Requirement specifies a minimum necessary qualification."),
        (r'\b(need\s+to|should\s+have|candidates?\s+should\s+have)\b', "Requirement indicates an expected core competency.")
    ]

    PREFERRED_PATTERNS = [
        (r'\b(would\s+be\s+a\s+plus|is\s+a\s+plus|a\s+plus|plus\s+point)\b', "Requirement uses the phrase '{}' indicating a preferred/bonus skill."),
        (r'\b(added\s+advantage|additional\s+advantage|an\s+advantage)\b', "Requirement is marked as an added advantage."),
        (r'\b(is\s+preferred|preferred\s+qualification|preferred\s+skills?|preferably|preferred)\b', "Requirement explicitly uses the term '{}'."),
        (r'\b(nice\s+to\s+have|good\s+to\s+have|desirable|bonus)\b', "Requirement uses phrase '{}' representing a desirable bonus qualification.")
    ]

    OPTIONAL_PATTERNS = [
        (r'\b(is\s+optional|optional)\b', "Requirement is explicitly designated as optional."),
        (r'\b(exposure\s+to|familiarity\s+with|basic\s+understanding)\b', "Requirement indicates introductory or optional familiarity.")
    ]

    @classmethod
    def detect_section_header(cls, requirement_text: str, full_jd_text: Optional[str]) -> Optional[str]:
        """Detects if the requirement falls under a PREFERRED or REQUIRED section header in the JD."""
        if not full_jd_text or not requirement_text:
            return None

        req_lower = requirement_text.strip().lower()
        jd_lower = full_jd_text.lower()

        pos = jd_lower.find(req_lower)
        if pos == -1:
            # Try matching first word
            words = [w for w in req_lower.split() if len(w) > 2]
            if words:
                pos = jd_lower.find(words[0])

        if pos != -1:
            preceding_text = jd_lower[:pos]
            lines = [line.strip() for line in preceding_text.split('\n') if line.strip()]

            # Search backwards for nearest section header line
            for line in reversed(lines[-8:]):
                if any(h in line for h in ["preferred qualifications", "preferred skills", "nice to have", "desirable qualifications", "bonus skills"]):
                    return "PREFERRED"
                if any(h in line for h in ["required qualifications", "basic qualifications", "mandatory requirements", "minimum qualifications", "requirements:"]):
                    return "REQUIRED"

        return None

    @classmethod
    def detect_priority(
        cls,
        requirement_text: str,
        category: str,
        context_sentence: Optional[str] = None,
        skill_level_hint: Optional[str] = None,
        full_jd_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines whether a requirement is Mandatory, Preferred, Optional, or Unknown.
        Evaluates section header context first, then local clause patterns, then fallback hints.
        """
        req_clean = requirement_text.strip()
        sentence = (context_sentence or req_clean).strip()
        sent_lower = sentence.lower()

        # Step 1: Check Section Header Context (e.g. PREFERRED QUALIFICATIONS header)
        sec_header = cls.detect_section_header(req_clean, full_jd_text or context_sentence)
        if sec_header == "PREFERRED":
            return {
                "priority": cls.PREFERRED,
                "priority_confidence": 0.96,
                "priority_evidence": "Requirement appears under the 'PREFERRED QUALIFICATIONS' section of the Job Description.",
                "source_text": sentence
            }
        elif sec_header == "REQUIRED":
            return {
                "priority": cls.MANDATORY,
                "priority_confidence": 0.97,
                "priority_evidence": "Requirement appears under the 'REQUIRED QUALIFICATIONS' section of the Job Description.",
                "source_text": sentence
            }

        # Step 2: Clause-aware PREFERRED indicators
        clauses = re.split(r'[,;]|\bwhile\b|\bwhereas\b|\bbut\b|\band\s+a\b', sent_lower)
        target_clause = sent_lower
        for clause in clauses:
            if req_clean.lower() in clause:
                target_clause = clause
                break

        for pattern, ev_template in cls.PREFERRED_PATTERNS:
            match = re.search(pattern, target_clause) or re.search(pattern, sent_lower)
            if match:
                phrase = match.group(1)
                return {
                    "priority": cls.PREFERRED,
                    "priority_confidence": 0.94,
                    "priority_evidence": ev_template.format(phrase),
                    "source_text": sentence
                }

        # Step 3: Clause-aware MANDATORY indicators
        for pattern, ev_template in cls.MANDATORY_PATTERNS:
            match = re.search(pattern, target_clause) or re.search(pattern, sent_lower)
            if match:
                phrase = match.group(1)
                return {
                    "priority": cls.MANDATORY,
                    "priority_confidence": 0.97,
                    "priority_evidence": ev_template.format(phrase),
                    "source_text": sentence
                }

        # Step 4: Check OPTIONAL indicators
        for pattern, ev_template in cls.OPTIONAL_PATTERNS:
            match = re.search(pattern, target_clause) or re.search(pattern, sent_lower)
            if match:
                phrase = match.group(1)
                return {
                    "priority": cls.OPTIONAL,
                    "priority_confidence": 0.88,
                    "priority_evidence": ev_template.format(phrase),
                    "source_text": sentence
                }

        # Step 5: Fallback to skill level hint from extractor
        if skill_level_hint:
            if skill_level_hint.upper() == "REQUIRED":
                return {
                    "priority": cls.MANDATORY,
                    "priority_confidence": 0.85,
                    "priority_evidence": "Requirement classified as Mandatory based on default NLP sentence modifier analysis.",
                    "source_text": sentence
                }
            elif skill_level_hint.upper() == "PREFERRED":
                return {
                    "priority": cls.PREFERRED,
                    "priority_confidence": 0.85,
                    "priority_evidence": "Requirement classified as Preferred based on default NLP sentence modifier analysis.",
                    "source_text": sentence
                }

        # Step 6: Fallback to Mandatory if in core required list or default Unknown
        return {
            "priority": cls.MANDATORY if category in ["Technical Skills", "Education", "Experience"] else cls.UNKNOWN,
            "priority_confidence": 0.65 if category in ["Technical Skills", "Education", "Experience"] else 0.50,
            "priority_evidence": "Core qualification specification without explicit modifier.",
            "source_text": sentence
        }
