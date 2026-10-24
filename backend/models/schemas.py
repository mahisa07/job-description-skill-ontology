from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SkillMention(BaseModel):
    original_mention: str
    canonical_name: str
    category: str
    requirement_level: str  # REQUIRED, PREFERRED, OPTIONAL
    importance: str         # High, Medium, Low
    evidence_sentence: Optional[str] = ""

class ClassifiedRequirement(BaseModel):
    requirement: str
    category: str
    priority: str = "Unknown"  # "Mandatory", "Preferred", "Optional", "Unknown"
    confidence: float = 0.50   # Category confidence
    priority_confidence: float = 0.50 # Priority confidence
    evidence: str = ""
    priority_evidence: str = ""
    source_text: str = ""

class RequirementBreakdown(BaseModel):
    job_role: str
    experience: str
    education: List[str] = []
    certifications: List[str] = []
    technical_skills: List[SkillMention] = []
    soft_skills: List[SkillMention] = []
    responsibilities: List[str] = []
    other_requirements: List[str] = []

class OntologyNode(BaseModel):
    id: str
    label: str
    type: str  # role, category, skill, related_skill
    category: Optional[str] = None
    requirement_level: Optional[str] = None
    importance: Optional[str] = None

class OntologyEdge(BaseModel):
    source: str
    target: str
    relation: str  # requires, belongs_to, is_related_to

class OntologyGraph(BaseModel):
    nodes: List[OntologyNode]
    edges: List[OntologyEdge]

class VerificationCheckItem(BaseModel):
    check_name: str
    category: str  # company, recruiter, job_posting, risk
    status: str    # VERIFIED, UNCONFIRMED, MISMATCH, UNAVAILABLE, WARNING
    details: str
    evidence_url: Optional[str] = None
    source_name: Optional[str] = None

class TrustVerificationResult(BaseModel):
    verification_status: str  # "Verified", "Partially Verified", "Unverified", "High Risk"
    verified_at: str
    summary_reason: str
    trust_score: Optional[int] = None
    indicative_trust_score: Optional[int] = None
    score_disclaimer: str
    disclaimer: Optional[str] = None
    company_name: Optional[str] = ""
    company_domain: Optional[str] = ""
    company_verified: bool = False
    company_website_url: Optional[str] = None
    recruiter_name: Optional[str] = ""
    recruiter_email: Optional[str] = ""
    recruiter_profile_url: Optional[str] = None
    recruiter_affiliation_status: str  # CONFIRMED, GENERIC_EMAIL, MISMATCH, NOT_PROVIDED, HIGH_RISK, UNCONFIRMED
    job_posting_url: Optional[str] = None
    job_posting_status: str  # MATCHED, EXTERNAL_SOURCE, NOT_FOUND, NOT_PROVIDED, UNCONFIRMED
    checks: List[VerificationCheckItem] = []
    detailed_checks: Optional[List[VerificationCheckItem]] = []
    risk_indicators: List[str] = []
    positive_indicators: List[str] = []
    limitations_and_disclaimers: List[str] = []
    company_verification: Optional[Dict[str, Any]] = None
    recruiter_verification: Optional[Dict[str, Any]] = None
    posting_verification: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None

class TrustVerificationRequest(BaseModel):
    jd_id: Optional[str] = None
    raw_text: Optional[str] = ""
    job_role: Optional[str] = ""
    company: Optional[str] = ""
    company_url: Optional[str] = ""
    recruiter_name: Optional[str] = ""
    recruiter_email: Optional[str] = ""
    recruiter_profile_url: Optional[str] = ""
    job_posting_url: Optional[str] = ""

class JDAnalysisResponse(BaseModel):
    id: str
    timestamp: str
    raw_text: str
    job_role: str
    experience: str
    education: List[str]
    certifications: List[str]
    responsibilities: List[str]
    total_skills_count: int
    required_skills_count: int
    preferred_skills_count: int
    optional_skills_count: int
    skills: List[SkillMention]
    skill_categories: Dict[str, List[str]]
    ontology: OntologyGraph
    traditional_vs_ontology: Dict[str, Any]
    classified_requirements: Optional[List[ClassifiedRequirement]] = []
    requirement_category_counts: Optional[Dict[str, int]] = {}
    priority_counts: Optional[Dict[str, int]] = {}
    created_by_email: Optional[str] = ""
    company: Optional[str] = ""
    department: Optional[str] = ""
    location: Optional[str] = ""
    employment_type: Optional[str] = ""
    application_deadline: Optional[str] = ""
    publisher_name: Optional[str] = ""
    published_at: Optional[str] = ""
    required_skills_summary: Optional[str] = ""
    status: Optional[str] = "Analyzed"
    trust_verification: Optional[TrustVerificationResult] = None

class JDDraftRequest(BaseModel):
    id: Optional[str] = None
    job_title: str
    department: Optional[str] = ""
    location: Optional[str] = ""
    raw_text: str
    created_by_email: Optional[str] = ""
    company: Optional[str] = ""
    experience_level: Optional[str] = ""
    employment_type: Optional[str] = ""
    application_deadline: Optional[str] = ""
    required_skills: Optional[str] = ""

class HRPublishJobRequest(BaseModel):
    id: Optional[str] = None
    job_title: str
    company_name: Optional[str] = ""
    department: Optional[str] = ""
    location: Optional[str] = ""
    experience_level: Optional[str] = ""
    employment_type: Optional[str] = ""
    application_deadline: Optional[str] = ""
    required_skills: Optional[str] = ""
    raw_text: Optional[str] = ""
    job_description: Optional[str] = ""
    created_by_email: Optional[str] = ""
    publisher_email: Optional[str] = ""
    publisher_name: Optional[str] = ""

class NotificationItem(BaseModel):
    id: str
    notification_id: str
    recipient_id: str
    recipient_email: str
    recipient_name: Optional[str] = ""
    published_job_id: str
    job_description_id: str
    jd_id: str
    title: str = "New Job Posted!"
    job_title: str
    company: str
    publisher_name: Optional[str] = ""
    department: Optional[str] = ""
    message: str
    created_at: str
    is_read: bool = False

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    target_jd_id: Optional[str] = None

class SkillMatchItem(BaseModel):
    skill_name: str
    category: str
    status: str  # MATCHED, PARTIAL_MATCH, MISSING
    matched_resume_skill: Optional[str] = None
    note: Optional[str] = None

class ResumeMatchResponse(BaseModel):
    jd_id: str
    job_role: str
    total_required_skills: int
    matched_count: int
    partial_count: int
    missing_count: int
    match_percentage: float
    matched_skills: List[SkillMatchItem]
    partial_skills: List[SkillMatchItem]
    missing_skills: List[SkillMatchItem]
    skill_gap_insights: List[str]
