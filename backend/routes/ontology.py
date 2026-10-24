from fastapi import APIRouter, HTTPException
from backend.database.db import db_store
from backend.models.schemas import OntologyGraph

router = APIRouter(prefix="/api/ontology", tags=["Skill Ontology Knowledge Graph"])

@router.get("/{jd_id}", response_model=OntologyGraph)
async def get_job_ontology(jd_id: str):
    record = db_store.get_jd_analysis(jd_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Job analysis with ID '{jd_id}' not found.")
    return record.ontology

@router.get("/{jd_id}/academic-comparison")
async def get_academic_comparison(jd_id: str):
    record = db_store.get_jd_analysis(jd_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Job analysis with ID '{jd_id}' not found.")
    return record.traditional_vs_ontology
