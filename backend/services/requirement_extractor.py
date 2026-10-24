import re
from typing import List, Dict, Any
from backend.services.nlp_service import NLPService
from backend.services.skill_normalizer import SkillNormalizerService
from backend.services.skill_classifier import SkillClassifierService
from backend.models.schemas import SkillMention, RequirementBreakdown

class RequirementExtractorService:
    ROLE_PATTERNS = [
        r'\b(Data\s+Analyst)\b',
        r'\b(Data\s+Scientist)\b',
        r'\b(Machine\s+Learning\s+Engineer)\b',
        r'\b(ML\s+Engineer)\b',
        r'\b(Software\s+Engineer)\b',
        r'\b(Software\s+Developer)\b',
        r'\b(Full\s+Stack\s+Developer)\b',
        r'\b(Backend\s+Developer)\b',
        r'\b(Frontend\s+Developer)\b',
        r'\b(DevOps\s+Engineer)\b',
        r'\b(Cloud\s+Architect)\b',
        r'\b(Business\s+Analyst)\b',
        r'\b(Data\s+Engineer)\b',
        r'\b(AI\s+Engineer)\b'
    ]

    EXP_PATTERNS = [
        r'\b(\d+\+?\s*-\s*\d+\s*(?:years?|yrs?))\b',
        r'\b(\d+\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?)\b',
        r'\b(entry\s+level)\b',
        r'\b(fresher|freshers)\b',
        r'\b(minimum\s+\d+\s+years?)\b'
    ]

    EDU_PATTERNS = [
        r'\b(B\.?E\.?|B\.?Tech|Bachelor\'?s(?:\s+Degree)?)\b',
        r'\b(M\.?E\.?|M\.?Tech|Master\'?s(?:\s+Degree)?)\b',
        r'\b(Ph\.?D|Doctorate)\b',
        r'\b(B\.?C\.?A|M\.?C\.?A|B\.?S\.?|M\.?S\.?)\b',
        r'\b(Degree\s+in\s+Computer\s+Science|Data\s+Science|Engineering)\b'
    ]

    CERT_PATTERNS = [
        r'\b(AWS\s+Certifi\w+)\b',
        r'\b(Azure\s+Certifi\w+)\b',
        r'\b(Google\s+Cloud\s+Certifi\w+)\b',
        r'\b(GCP\s+Certifi\w+)\b',
        r'\b(PMP)\b',
        r'\b(Scrum\s+Master)\b',
        r'\b(CISSP)\b',
        r'\b(CKA)\b'
    ]

    @classmethod
    def extract_job_role(cls, text: str) -> str:
        first_paragraph = "\n".join(text.split("\n")[:5])
        for pat in cls.ROLE_PATTERNS:
            match = re.search(pat, first_paragraph, re.IGNORECASE)
            if match:
                return match.group(1).title()

        # Search whole text if not found in top 5 lines
        for pat in cls.ROLE_PATTERNS:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1).title()

        return "Software / Data Professional"

    @classmethod
    def extract_experience(cls, text: str) -> str:
        for pat in cls.EXP_PATTERNS:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()
        return "1+ Years"

    @classmethod
    def extract_education(cls, text: str) -> List[str]:
        results = set()
        for pat in cls.EDU_PATTERNS:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                results.add(m.strip())
        return list(results) if results else ["Bachelor's Degree in CS, IT, or relevant quantitative field"]

    @classmethod
    def extract_certifications(cls, text: str) -> List[str]:
        results = set()
        for pat in cls.CERT_PATTERNS:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                results.add(m.strip())
        return list(results)

    @classmethod
    def extract_responsibilities(cls, text: str) -> List[str]:
        sentences = NLPService.segment_sentences(text)
        resp = []
        action_verbs = ["design", "develop", "build", "analyze", "create", "maintain", "collaborate", "lead", "implement", "deploy"]
        for s in sentences:
            s_lower = s.lower()
            if any(verb in s_lower for verb in action_verbs) and len(s) > 20:
                resp.append(s.strip())
            if len(resp) >= 6:
                break
        if not resp:
            resp = [
                "Analyze structured and unstructured datasets to derive actionable insights.",
                "Design and maintain scalable pipelines and dashboard solutions.",
                "Collaborate with cross-functional teams to deliver key technical requirements."
            ]
        return resp

    @classmethod
    def extract_all_skills(cls, text: str) -> List[SkillMention]:
        sentences = NLPService.segment_sentences(text)
        detected_skills: Dict[str, SkillMention] = {}

        # Known canonical map keys to check
        all_skill_keys = list(SkillNormalizerService.CANONICAL_MAP.keys())
        # Sort keys by length descending to match multi-word phrases first
        all_skill_keys.sort(key=len, reverse=True)

        for sentence in sentences:
            sentence_lower = f" {sentence.lower()} "
            for raw_key in all_skill_keys:
                # Word boundary check for regex safety
                pattern = r'(?<![a-zA-Z0-9_#\+\-])' + re.escape(raw_key) + r'(?![a-zA-Z0-9_#\+\-])'
                if re.search(pattern, sentence_lower):
                    canonical, category = SkillNormalizerService.normalize_skill(raw_key)
                    req_level, importance = SkillClassifierService.classify_requirement_and_importance(sentence)

                    if canonical not in detected_skills:
                        detected_skills[canonical] = SkillMention(
                            original_mention=raw_key.upper() if len(raw_key) <= 3 else raw_key.title(),
                            canonical_name=canonical,
                            category=category,
                            requirement_level=req_level,
                            importance=importance,
                            evidence_sentence=sentence.strip()
                        )
                    else:
                        # Upgrade requirement level if REQUIRED found in another sentence
                        if req_level == "REQUIRED" and detected_skills[canonical].requirement_level != "REQUIRED":
                            detected_skills[canonical].requirement_level = "REQUIRED"
                            detected_skills[canonical].importance = "High"

        return list(detected_skills.values())
