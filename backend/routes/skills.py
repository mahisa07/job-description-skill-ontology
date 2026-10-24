from fastapi import APIRouter, Query
from typing import List, Dict, Any
from backend.services.skill_normalizer import SkillNormalizerService

router = APIRouter(prefix="/api/skills", tags=["Skill Taxonomy & Normalization"])

@router.get("/search")
async def search_skills(q: str = Query(..., description="Query term (e.g. python, ml, sql)")):
    query_lower = q.strip().lower()
    matches = []

    for raw, canonical in SkillNormalizerService.CANONICAL_MAP.items():
        if query_lower in raw or query_lower in canonical.lower():
            category = SkillNormalizerService.CATEGORY_MAP.get(canonical, "Tools & Other")
            related = SkillNormalizerService.get_related_skills(canonical)
            matches.append({
                "alias": raw,
                "canonical_name": canonical,
                "category": category,
                "related_skills": related
            })
            if len(matches) >= 15:
                break

    return {
        "query": q,
        "count": len(matches),
        "results": matches
    }

@router.get("/categories")
async def get_all_categories() -> Dict[str, List[str]]:
    categories: Dict[str, List[str]] = {}
    for skill, cat in SkillNormalizerService.CATEGORY_MAP.items():
        categories.setdefault(cat, []).append(skill)
    return categories
