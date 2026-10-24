import re
from typing import List, Dict, Tuple, Optional
from backend.models.schemas import ClassifiedRequirement, SkillMention
from backend.services.nlp_service import NLPService
from backend.services.requirement_priority_service import RequirementPriorityService

class RequirementClassifierService:
    CATEGORIES = [
        "Technical Skills",
        "Soft Skills",
        "Education",
        "Experience",
        "Certifications",
        "Tools / Technologies",
        "Job Responsibilities",
        "Domain / Industry Knowledge",
        "Other Requirements"
    ]

    # Noise / Stopwords to explicitly reject as standalone requirements
    STOPWORDS = {
        "be", "to", "in", "a", "an", "or", "of", "the", "and", "with", "for", "is", "are",
        "have", "has", "do", "does", "by", "on", "at", "as", "from", "it", "this", "that"
    }

    TECHNICAL_SKILLS_KEYWORDS = {
        "python", "java", "c++", "c#", "javascript", "typescript", "sql", "r", "go", "ruby", "php",
        "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
        "data analysis", "data science", "data engineering", "statistics", "algorithms", "data structures",
        "neural networks", "artificial intelligence", "ai", "ml", "dl", "backend", "frontend", "full stack",
        "pandas", "numpy", "scikit-learn", "scikit learn", "tensorflow", "pytorch", "keras"
    }

    SOFT_SKILLS_KEYWORDS = {
        "communication", "teamwork", "leadership", "problem solving", "problem-solving",
        "collaboration", "time management", "adaptability", "critical thinking", "analytical thinking",
        "interpersonal", "presentation", "negotiation", "flexibility", "self-motivated", "creativity"
    }

    TOOLS_TECHNOLOGIES_KEYWORDS = {
        "excel", "ms excel", "power bi", "powerbi", "tableau", "qlik", "looker",
        "git", "github", "docker", "kubernetes", "k8s", "aws", "azure", "microsoft azure", "google cloud", "gcp",
        "mongodb", "postgresql", "postgres", "mysql", "oracle", "redis", "jira", "confluence"
    }

    DOMAIN_KEYWORDS = {
        "banking", "finance", "financial", "healthcare", "health", "retail", "e-commerce", "ecommerce",
        "cybersecurity", "security", "supply chain", "telecom", "telecommunications", "insurance",
        "fintech", "pharma", "pharmaceuticals", "automotive", "logistics", "saas", "technology"
    }

    EDU_PATTERNS = [
        r"\b(bachelor\'?s(?:\s+degree)?|master\'?s(?:\s+degree)?|b\.?e\.?|b\.?tech|m\.?e\.?|m\.?tech|ph\.?d|doctorate|degree|b\.?c\.?a|m\.?c\.?a|b\.?s\.?|m\.?s\.?)\b"
    ]

    EXP_PATTERNS = [
        r"\b(\d+\+?\s*-\s*\d+\s*(?:years?|yrs?)(?:\s+of\s+experience)?|\d+\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?|entry\s+level|fresher|freshers|minimum\s+\d+\s+years?)\b"
    ]

    CERT_PATTERNS = [
        r"\b(certifi\w+|pmp|scrum\s+master|cissp|cka|aws\s+certified|azure\s+certified|gcp\s+certified|cisco)\b"
    ]

    RESPONSIBILITY_ACTION_VERBS = {
        "collect", "clean", "develop", "design", "build", "analyze", "create", "maintain", "manage", "lead", "implement",
        "deploy", "collaborate", "deliver", "optimize", "query", "prepare", "evaluate", "monitor", "write", "work"
    }

    @classmethod
    def is_valid_requirement(cls, text: str) -> bool:
        """Filters out noise, stopwords, and short fragments."""
        clean = text.strip().lower()
        if not clean or clean in cls.STOPWORDS:
            return False
        if len(clean) <= 2 and clean not in {"ai", "ml", "r", "go", "ip", "ui", "ux", "qa"}:
            return False
        return True

    @classmethod
    def classify_single_requirement(
        cls,
        requirement_text: str,
        context_sentence: Optional[str] = None,
        skill_level_hint: Optional[str] = None,
        full_jd_text: Optional[str] = None
    ) -> Optional[ClassifiedRequirement]:
        """
        Classifies a single requirement text into Feature 1 Categories and Feature 2 Priorities.
        Returns None if the requirement is noise/stopword.
        """
        text_clean = requirement_text.strip()
        if not cls.is_valid_requirement(text_clean):
            return None

        text_lower = text_clean.lower()
        context = context_sentence or requirement_text

        category = "Other Requirements"
        confidence = 0.45
        evidence = "Requirement contains general specifications not fitting distinct technical or educational patterns."

        # 1. Education Check First (To prevent classifying "Bachelor's degree in Data Science" as Experience)
        for pat in cls.EDU_PATTERNS:
            if re.search(pat, text_lower) or "degree" in text_lower:
                category = "Education"
                confidence = 0.98
                evidence = "Requirement explicitly specifies an academic qualification or degree."
                break

        # 2. Experience Check (Only if not Education)
        if category == "Other Requirements":
            for pat in cls.EXP_PATTERNS:
                if re.search(pat, text_lower) or ("years" in text_lower and any(char.isdigit() for char in text_lower)):
                    category = "Experience"
                    confidence = 0.96
                    evidence = "Requirement specifies career experience duration or seniority level."
                    break

        # 3. Certifications Check
        if category == "Other Requirements":
            for pat in cls.CERT_PATTERNS:
                if re.search(pat, text_lower):
                    category = "Certifications"
                    confidence = 0.97
                    evidence = "Requirement lists a recognized professional certification or credential."
                    break

        # 4. Soft Skills Check
        if category == "Other Requirements":
            for kw in cls.SOFT_SKILLS_KEYWORDS:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    category = "Soft Skills"
                    confidence = 0.94
                    evidence = f"'{kw.title()}' is identified as a behavioral or interpersonal soft skill."
                    break

        # 5. Tools & Technologies Check
        if category == "Other Requirements":
            for kw in cls.TOOLS_TECHNOLOGIES_KEYWORDS:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    category = "Tools / Technologies"
                    confidence = 0.95
                    evidence = f"'{kw.title()}' is identified as a software tool, platform, or framework."
                    break

        # 6. Technical Skills Check
        if category == "Other Requirements":
            for kw in cls.TECHNICAL_SKILLS_KEYWORDS:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    category = "Technical Skills"
                    confidence = 0.96
                    evidence = f"'{kw.title()}' is identified as a technical programming language, library, or core competency."
                    break

        # 7. Domain Check
        if category == "Other Requirements":
            for kw in cls.DOMAIN_KEYWORDS:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    category = "Domain / Industry Knowledge"
                    confidence = 0.92
                    evidence = f"Requirement requires domain expertise in the {kw.title()} industry sector."
                    break

        # 8. Responsibilities Check (Action verbs duty sentences)
        if category == "Other Requirements":
            first_word = text_lower.split()[0] if text_lower.split() else ""
            if first_word in cls.RESPONSIBILITY_ACTION_VERBS or any(v in text_lower for v in ["responsible for", "duties include", "will be required to", "will design", "will build", "will analyze", "prepare regular"]):
                category = "Job Responsibilities"
                confidence = 0.92
                evidence = "Statement outlines a primary job duty or operational responsibility."

        # Feature 2: Priority Detection with Full JD Context
        priority_res = RequirementPriorityService.detect_priority(
            requirement_text=text_clean,
            category=category,
            context_sentence=context,
            skill_level_hint=skill_level_hint,
            full_jd_text=full_jd_text
        )

        return ClassifiedRequirement(
            requirement=text_clean,
            category=category,
            priority=priority_res["priority"],
            confidence=confidence,
            priority_confidence=priority_res["priority_confidence"],
            evidence=evidence,
            priority_evidence=priority_res["priority_evidence"],
            source_text=priority_res["source_text"]
        )

    @classmethod
    def classify_full_jd(
        cls,
        raw_text: str,
        skills: List[SkillMention],
        education: List[str],
        experience: str,
        certifications: List[str],
        responsibilities: List[str]
    ) -> Tuple[List[ClassifiedRequirement], Dict[str, int], Dict[str, int]]:
        """
        Classifies all extracted components of a JD and returns structured items, category count statistics, and priority count statistics.
        """
        classified_list: List[ClassifiedRequirement] = []
        seen_requirements = set()

        def add_item(item: Optional[ClassifiedRequirement]):
            if not item:
                return
            key = (item.requirement.lower().strip(), item.category)
            if key not in seen_requirements:
                seen_requirements.add(key)
                classified_list.append(item)

        # 1. Experience
        if experience:
            add_item(cls.classify_single_requirement(experience, context_sentence=raw_text, full_jd_text=raw_text))

        # 2. Education
        for edu in education:
            add_item(cls.classify_single_requirement(edu, context_sentence=raw_text, full_jd_text=raw_text))

        # 3. Certifications
        for cert in certifications:
            add_item(cls.classify_single_requirement(cert, context_sentence=raw_text, full_jd_text=raw_text))

        # 4. Skills (Technical, Soft Skills, Tools)
        for s in skills:
            req_name = s.canonical_name
            context_sent = s.evidence_sentence
            item = cls.classify_single_requirement(
                req_name,
                context_sentence=context_sent,
                skill_level_hint=s.requirement_level,
                full_jd_text=raw_text
            )

            if item:
                # Refine category taxonomy mapping
                if s.category in ["Soft Skills"]:
                    item.category = "Soft Skills"
                    item.confidence = max(item.confidence, 0.94)
                elif s.category in ["DevOps & Tools", "Data Visualization", "Database"] and item.category not in ["Technical Skills", "Tools / Technologies"]:
                    item.category = "Tools / Technologies"
                    item.confidence = max(item.confidence, 0.93)
                elif s.category in ["Programming", "AI & Machine Learning", "Data Analysis", "Cloud Platforms"]:
                    item.category = "Technical Skills"
                    item.confidence = max(item.confidence, 0.96)

                add_item(item)

        # 5. Responsibilities
        for resp in responsibilities:
            add_item(cls.classify_single_requirement(resp, context_sentence=resp, full_jd_text=raw_text))

        # Build category count summary dictionary for all 9 categories
        category_counts: Dict[str, int] = {cat: 0 for cat in cls.CATEGORIES}
        priority_counts: Dict[str, int] = {
            RequirementPriorityService.MANDATORY: 0,
            RequirementPriorityService.PREFERRED: 0,
            RequirementPriorityService.OPTIONAL: 0,
            RequirementPriorityService.UNKNOWN: 0
        }

        for item in classified_list:
            if item.category in category_counts:
                category_counts[item.category] += 1
            else:
                category_counts["Other Requirements"] += 1

            if item.priority in priority_counts:
                priority_counts[item.priority] += 1
            else:
                priority_counts[RequirementPriorityService.UNKNOWN] += 1

        return classified_list, category_counts, priority_counts
