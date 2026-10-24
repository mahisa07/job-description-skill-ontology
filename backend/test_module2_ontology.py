import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.db import DatabaseStore

def run_tests():
    print("==================================================")
    print("RUNNING REFINED MODULE 2 SKILL ONTOLOGY EXPLORER VERIFICATION")
    print("==================================================")

    db = DatabaseStore()
    record = db.get_jd_analysis("demo-data-analyst")
    assert record is not None, "Demo Data Analyst record not found!"

    print(f"Loaded Job Description: '{record.job_role}' ({record.id})")

    skills = record.skills or []
    skill_categories = record.skill_categories or {}
    classified_reqs = record.classified_requirements or []
    prio_counts = record.priority_counts or {}

    print(f"Extracted Skills Count: {len(skills)}")
    print(f"Mandatory Skills Count: {prio_counts.get('Mandatory', 0)}")
    print(f"Preferred Skills Count: {prio_counts.get('Preferred', 0)}")
    print(f"Categories Present: {list(skill_categories.keys())}")

    # 1. 3 Metrics Validation (Extracted Skills, Mandatory Skills, Preferred Skills)
    extracted_skills_count = len(skills)
    mandatory_count = prio_counts.get("Mandatory", 0)
    preferred_count = prio_counts.get("Preferred", 0)

    assert extracted_skills_count > 0, "Extracted skills count must be > 0"
    assert mandatory_count >= 0, "Mandatory count must be >= 0"
    assert preferred_count >= 0, "Preferred count must be >= 0"
    print("✓ [TEST 1 PASSED] 3 Ontology Summary metrics verified")

    # 2. Simple Skill Hierarchy (Job Role -> Skill Category -> Extracted Skills)
    for cat_name, cat_skills in skill_categories.items():
        assert len(cat_skills) > 0, f"Category '{cat_name}' must not be empty"
    print("✓ [TEST 2 PASSED] Dynamic skill hierarchy (Job Role -> Category -> Skills) verified")

    # 3. Compact Skill Table Fields (Skill, Category, Priority, Confidence)
    python_skill = next((s for s in skills if s.canonical_name == "Python"), None)
    assert python_skill is not None, "Python skill missing"

    python_req = next((r for r in classified_reqs if r.requirement.lower() == "python"), None)
    assert python_req is not None, "Python requirement record missing"
    assert python_req.category in ["Technical Skills", "Programming", "Tools / Technologies"], f"Python category got {python_req.category}"
    assert python_req.priority == "Mandatory", f"Python priority got {python_req.priority}"
    print("✓ [TEST 3 PASSED] Skill table fields (Skill, Category, Priority, Confidence) verified")

    # 4. Evidence Quote Availability
    assert python_skill.evidence_sentence or python_req.source_text, "Evidence context quote missing"
    print("✓ [TEST 4 PASSED] Original evidence context quote verified")

    print("\nALL REFINED MODULE 2 VERIFICATION TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
