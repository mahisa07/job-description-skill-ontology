from typing import List
from backend.models.schemas import JDAnalysisResponse, ResumeMatchResponse, SkillMatchItem
from backend.services.requirement_extractor import RequirementExtractorService
from backend.services.skill_normalizer import SkillNormalizerService

class MatchingService:
    @staticmethod
    def compare_resume_with_jd(resume_text: str, jd_data: JDAnalysisResponse) -> ResumeMatchResponse:
        # Extract skills from resume using extractor
        resume_skills = RequirementExtractorService.extract_all_skills(resume_text)
        resume_canonical_names = {s.canonical_name for s in resume_skills}

        matched_items: List[SkillMatchItem] = []
        partial_items: List[SkillMatchItem] = []
        missing_items: List[SkillMatchItem] = []

        required_jd_skills = [s for s in jd_data.skills if s.requirement_level in ["REQUIRED", "PREFERRED"]]

        for jd_skill in required_jd_skills:
            canon = jd_skill.canonical_name

            # 1. Direct Match
            if canon in resume_canonical_names:
                matched_items.append(SkillMatchItem(
                    skill_name=canon,
                    category=jd_skill.category,
                    status="MATCHED",
                    matched_resume_skill=canon,
                    note="Direct exact match found in resume."
                ))
            else:
                # 2. Check Related Skill match
                related_candidates = SkillNormalizerService.get_related_skills(canon)
                found_related = None
                for rel in related_candidates:
                    if rel in resume_canonical_names:
                        found_related = rel
                        break

                if found_related:
                    partial_items.append(SkillMatchItem(
                        skill_name=canon,
                        category=jd_skill.category,
                        status="PARTIAL_MATCH",
                        matched_resume_skill=found_related,
                        note=f"Resume contains related skill '{found_related}' which supports '{canon}' via ontology taxonomy."
                    ))
                else:
                    # 3. Missing Skill
                    missing_items.append(SkillMatchItem(
                        skill_name=canon,
                        category=jd_skill.category,
                        status="MISSING",
                        matched_resume_skill=None,
                        note=f"Required skill '{canon}' not detected in candidate resume."
                    ))

        total_req = len(required_jd_skills) or 1
        matched_cnt = len(matched_items)
        partial_cnt = len(partial_items)
        missing_cnt = len(missing_items)

        # Transparent system-generated formula calculation
        # Exact match = 1.0 weight, Partial match = 0.5 weight
        raw_score = ((matched_cnt * 1.0) + (partial_cnt * 0.5)) / float(total_req) * 100.0
        score = min(100.0, round(raw_score, 1))

        gap_insights = []
        if missing_cnt == 0:
            gap_insights.append("Candidate strongly satisfies all extracted core requirements!")
        else:
            top_missing = [m.skill_name for m in missing_items[:3]]
            gap_insights.append(f"Primary Skill Gap: Candidate should upskill in: {', '.join(top_missing)}.")

        if partial_cnt > 0:
            top_partial = [p.skill_name for p in partial_items[:2]]
            gap_insights.append(f"Ontology Transferability: Related knowledge demonstrated for {', '.join(top_partial)}.")

        return ResumeMatchResponse(
            jd_id=jd_data.id,
            job_role=jd_data.job_role,
            total_required_skills=total_req,
            matched_count=matched_cnt,
            partial_count=partial_cnt,
            missing_count=missing_cnt,
            match_percentage=score,
            matched_skills=matched_items,
            partial_skills=partial_items,
            missing_skills=missing_items,
            skill_gap_insights=gap_insights
        )
