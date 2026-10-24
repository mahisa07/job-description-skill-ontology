from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from backend.services.document_parser import DocumentParserService
from backend.services.requirement_extractor import RequirementExtractorService

router = APIRouter(prefix="/api/resume", tags=["Resume Processing"])

@router.post("/parse")
async def parse_resume(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    resume_text = ""
    if file:
        file_bytes = await file.read()
        filename = file.filename.lower()
        if filename.endswith(".pdf"):
            resume_text = DocumentParserService.parse_pdf(file_bytes)
        elif filename.endswith(".docx") or filename.endswith(".doc"):
            resume_text = DocumentParserService.parse_docx(file_bytes)
        elif filename.endswith(".txt"):
            resume_text = DocumentParserService.parse_plain_text(file_bytes.decode("utf-8", errors="ignore"))
    elif text and text.strip():
        resume_text = DocumentParserService.parse_plain_text(text)

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from resume.")

    skills = RequirementExtractorService.extract_all_skills(resume_text)
    edu = RequirementExtractorService.extract_education(resume_text)
    exp = RequirementExtractorService.extract_experience(resume_text)

    return {
        "raw_text_length": len(resume_text),
        "detected_experience": exp,
        "detected_education": edu,
        "extracted_skills": skills
    }
