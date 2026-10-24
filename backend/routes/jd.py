from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header, Query
from typing import Optional, List
from backend.database.db import db_store
from backend.services.document_parser import DocumentParserService
from backend.models.schemas import (
    JDAnalysisResponse,
    JDDraftRequest,
    HRPublishJobRequest,
    TrustVerificationRequest,
    TrustVerificationResult
)
from backend.services.trust_verification_service import TrustVerificationService

router = APIRouter(prefix="/api/jobs", tags=["Job Description Analysis"])

def verify_hr_authorization(email: Optional[str] = None) -> dict:
    if not email or not email.strip():
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in as HR or Recruiter.")
    from backend.routes.auth import load_users
    users = load_users()
    user = users.get(email.strip().lower())
    if not user:
        raise HTTPException(status_code=401, detail="Authenticated account not found.")
    role = (user.get("role") or "").strip().lower()
    if role not in ["hr", "recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden. Only HR or Recruiter accounts have permission to publish job descriptions.")
    return user

@router.post("/analyze", response_model=JDAnalysisResponse)
async def analyze_job_description(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    created_by_email: Optional[str] = Form(""),
    company: Optional[str] = Form(""),
    department: Optional[str] = Form(""),
    location: Optional[str] = Form(""),
    job_title: Optional[str] = Form(""),
    jd_id: Optional[str] = Form(None),
    company_url: Optional[str] = Form(""),
    recruiter_name: Optional[str] = Form(""),
    recruiter_email: Optional[str] = Form(""),
    recruiter_profile_url: Optional[str] = Form(""),
    job_posting_url: Optional[str] = Form("")
):
    extracted_text = ""

    if file:
        file_bytes = await file.read()
        filename = file.filename.lower()
        if filename.endswith(".pdf"):
            extracted_text = DocumentParserService.parse_pdf(file_bytes)
        elif filename.endswith(".docx") or filename.endswith(".doc"):
            extracted_text = DocumentParserService.parse_docx(file_bytes)
        elif filename.endswith(".txt"):
            extracted_text = DocumentParserService.parse_plain_text(file_bytes.decode("utf-8", errors="ignore"))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT.")
    elif text and text.strip():
        extracted_text = DocumentParserService.parse_plain_text(text)
    else:
        raise HTTPException(status_code=400, detail="Please provide a valid Job Description via text or file upload.")

    if not extracted_text or len(extracted_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Unable to extract meaningful text content from the input.")

    record = db_store.save_jd_analysis(
        raw_text=extracted_text,
        created_by_email=created_by_email,
        company=company,
        department=department,
        location=location,
        custom_id=jd_id,
        override_role=job_title if job_title and job_title.strip() else None,
        company_url=company_url,
        recruiter_name=recruiter_name,
        recruiter_email=recruiter_email,
        recruiter_profile_url=recruiter_profile_url,
        job_posting_url=job_posting_url
    )
    return record

@router.post("/verify-trust", response_model=TrustVerificationResult)
async def verify_trust_endpoint(req: TrustVerificationRequest):
    """Run standalone or updated Trust & Verification audit on a job posting."""
    text_to_audit = req.raw_text or ""
    role_to_audit = req.job_role or ""
    company_to_audit = req.company or ""

    if req.jd_id and not text_to_audit:
        rec = db_store.get_jd_analysis(req.jd_id)
        if rec:
            text_to_audit = rec.raw_text
            role_to_audit = role_to_audit or rec.job_role
            company_to_audit = company_to_audit or rec.company

    if not text_to_audit and not req.company and not req.recruiter_email:
        raise HTTPException(status_code=400, detail="Please provide Job Description text or verification parameters.")

    result = TrustVerificationService.perform_verification(
        raw_text=text_to_audit,
        job_role=role_to_audit,
        company=company_to_audit,
        company_url=req.company_url,
        recruiter_name=req.recruiter_name,
        recruiter_email=req.recruiter_email,
        recruiter_profile_url=req.recruiter_profile_url,
        job_posting_url=req.job_posting_url
    )

    if req.jd_id:
        db_store.update_trust_verification(req.jd_id, result)

    return result

@router.post("/{jd_id}/verify-trust", response_model=TrustVerificationResult)
async def verify_jd_trust_by_id(jd_id: str, req: Optional[TrustVerificationRequest] = None):
    """Run Trust & Verification for an existing job description by ID."""
    rec = db_store.get_jd_analysis(jd_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Job analysis with ID '{jd_id}' not found.")

    comp = (req.company if req and req.company else None) or rec.company
    comp_url = (req.company_url if req else "") or ""
    rec_name = (req.recruiter_name if req else "") or ""
    rec_email = (req.recruiter_email if req else "") or ""
    rec_profile = (req.recruiter_profile_url if req else "") or ""
    job_url = (req.job_posting_url if req else "") or ""

    result = TrustVerificationService.perform_verification(
        raw_text=rec.raw_text,
        job_role=rec.job_role,
        company=comp,
        company_url=comp_url,
        recruiter_name=rec_name,
        recruiter_email=rec_email,
        recruiter_profile_url=rec_profile,
        job_posting_url=job_url
    )

    db_store.update_trust_verification(jd_id, result)
    return result

@router.post("/draft", response_model=JDAnalysisResponse)
async def save_job_description_draft(
    draft_req: JDDraftRequest,
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    if not draft_req.job_title or not draft_req.job_title.strip():
        raise HTTPException(status_code=400, detail="Job Title is required to save a draft.")
    if not draft_req.raw_text or not draft_req.raw_text.strip():
        raise HTTPException(status_code=400, detail="Job Description text is required to save a draft.")

    effective_email = x_user_email or draft_req.created_by_email or ""
    record = db_store.save_draft(
        draft_id=draft_req.id,
        job_title=draft_req.job_title.strip(),
        department=draft_req.department or "",
        location=draft_req.location or "",
        raw_text=draft_req.raw_text.strip(),
        created_by_email=effective_email,
        company=draft_req.company or "",
        experience_level=draft_req.experience_level or "",
        employment_type=draft_req.employment_type or "",
        application_deadline=draft_req.application_deadline or "",
        required_skills=draft_req.required_skills or ""
    )
    return record

@router.post("/publish", response_model=JDAnalysisResponse)
async def create_and_publish_job_endpoint(
    req: HRPublishJobRequest,
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    """Directly create, analyze, and publish a new Job Description with instant job seeker notifications."""
    effective_email = x_user_email or req.created_by_email or req.publisher_email
    user = verify_hr_authorization(effective_email)

    raw_text = (req.raw_text or req.job_description or "").strip()
    if not req.job_title or not req.job_title.strip():
        raise HTTPException(status_code=400, detail="Job Title is required to publish.")
    if not raw_text:
        raise HTTPException(status_code=400, detail="Job Description text is required to publish.")

    comp_name = (req.company_name or "").strip() or user.get("company_name") or "Acme Tech Solutions"

    full_text = raw_text
    if req.required_skills and req.required_skills.strip():
        if "REQUIRED SKILLS" not in full_text.upper():
            full_text += f"\n\nREQUIRED SKILLS:\n{req.required_skills.strip()}"

    record = db_store.create_and_publish_job(
        job_title=req.job_title.strip(),
        company=comp_name,
        raw_text=full_text,
        created_by_email=user.get("email"),
        department=req.department or user.get("department") or "",
        location=req.location or "",
        experience_level=req.experience_level or "",
        employment_type=req.employment_type or "",
        application_deadline=req.application_deadline or "",
        required_skills=req.required_skills or "",
        publisher_name=user.get("name", "HR Recruiter"),
        custom_id=req.id
    )
    return record

@router.get("/history", response_model=List[JDAnalysisResponse])
async def get_analysis_history():
    return db_store.get_all_records()

@router.get("/user-history", response_model=List[JDAnalysisResponse])
async def get_user_analysis_history(email: Optional[str] = ""):
    if email:
        return db_store.get_user_records(email)
    return db_store.get_all_records()

@router.get("/published/list", response_model=List[JDAnalysisResponse])
async def get_published_job_descriptions():
    return db_store.get_published_records()

@router.get("/notifications/list")
async def get_user_notifications(
    user_email: Optional[str] = Query(None, alias="user_email"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    effective_email = x_user_email or user_email
    return db_store.get_notifications(user_email=effective_email)

@router.post("/notifications/read-all/clear")
async def mark_all_notifications_read(
    user_email: Optional[str] = Query(None, alias="user_email"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    effective_email = x_user_email or user_email
    db_store.mark_all_notifications_read(user_email=effective_email)
    return {"message": "All notifications marked as read."}

@router.post("/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: str,
    user_email: Optional[str] = Query(None, alias="user_email"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    effective_email = x_user_email or user_email
    success = db_store.mark_notification_read(notif_id, user_email=effective_email)
    if not success:
        raise HTTPException(status_code=404, detail=f"Notification '{notif_id}' not found or unauthorized.")
    return {"message": "Notification marked as read.", "id": notif_id}

@router.delete("/{jd_id}")
async def delete_job_description(jd_id: str):
    success = db_store.delete_jd(jd_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Job description '{jd_id}' not found.")
    return {"message": "Job Description deleted successfully.", "id": jd_id}

@router.post("/{jd_id}/publish")
async def publish_job_description(
    jd_id: str,
    created_by_email: Optional[str] = Form(None),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    user_email_param: Optional[str] = Query(None, alias="email")
):
    existing_rec = db_store.get_record(jd_id)
    if not existing_rec:
        raise HTTPException(status_code=404, detail=f"Job description '{jd_id}' not found.")

    effective_email = x_user_email or created_by_email or user_email_param or existing_rec.created_by_email
    user = verify_hr_authorization(effective_email)

    record = db_store.publish_jd(
        jd_id=jd_id,
        publisher_email=user.get("email"),
        publisher_name=user.get("name"),
        company_name=user.get("company_name")
    )
    if not record:
        raise HTTPException(status_code=404, detail=f"Job description '{jd_id}' not found.")
    return {
        "success": True,
        "message": "Job Description published successfully. Registered job seekers have been notified.",
        "record": record
    }

@router.get("/{jd_id}", response_model=JDAnalysisResponse)
async def get_job_analysis(jd_id: str):
    record = db_store.get_jd_analysis(jd_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Job analysis with ID '{jd_id}' not found.")
    return record

@router.get("/{jd_id}/requirements")
async def get_job_requirements(jd_id: str):
    record = db_store.get_jd_analysis(jd_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Job analysis with ID '{jd_id}' not found.")
    return {
        "job_role": record.job_role,
        "experience": record.experience,
        "education": record.education,
        "certifications": record.certifications,
        "responsibilities": record.responsibilities,
        "required_skills": [s for s in record.skills if s.requirement_level == "REQUIRED"],
        "preferred_skills": [s for s in record.skills if s.requirement_level == "PREFERRED"],
        "optional_skills": [s for s in record.skills if s.requirement_level == "OPTIONAL"],
        "classified_requirements": record.classified_requirements or [],
        "category_counts": record.requirement_category_counts or {},
        "priority_counts": record.priority_counts or {}
    }

@router.get("/{jd_id}/classified-requirements")
async def get_classified_requirements(jd_id: str):
    record = db_store.get_jd_analysis(jd_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Job analysis with ID '{jd_id}' not found.")
    return {
        "job_role": record.job_role,
        "total_requirements": len(record.classified_requirements or []),
        "category_counts": record.requirement_category_counts or {},
        "priority_counts": record.priority_counts or {},
        "classified_requirements": record.classified_requirements or []
    }
