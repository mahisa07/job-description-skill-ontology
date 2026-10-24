from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from backend.database.db import db_store
from backend.services.document_parser import DocumentParserService
from backend.services.matching_service import MatchingService
from backend.models.schemas import ResumeMatchResponse

router = APIRouter(prefix="/api/matching", tags=["Resume vs JD Matching & Skill Gap Analysis"])

@router.post("/analyze", response_model=ResumeMatchResponse)
async def analyze_match(
    jd_id: str = Form(...),
    resume_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    jd_record = db_store.get_jd_analysis(jd_id)
    if not jd_record:
        raise HTTPException(status_code=404, detail=f"Target Job Description with ID '{jd_id}' not found.")

    extracted_resume = ""
    if file:
        file_bytes = await file.read()
        filename = file.filename.lower()
        if filename.endswith(".pdf"):
            extracted_resume = DocumentParserService.parse_pdf(file_bytes)
        elif filename.endswith(".docx") or filename.endswith(".doc"):
            extracted_resume = DocumentParserService.parse_docx(file_bytes)
        elif filename.endswith(".txt"):
            extracted_resume = DocumentParserService.parse_plain_text(file_bytes.decode("utf-8", errors="ignore"))
    elif resume_text and resume_text.strip():
        extracted_resume = DocumentParserService.parse_plain_text(resume_text)

    if not extracted_resume:
        raise HTTPException(status_code=400, detail="Please provide resume text or upload a valid PDF/DOCX file.")

    match_response = MatchingService.compare_resume_with_jd(extracted_resume, jd_record)
    return match_response
