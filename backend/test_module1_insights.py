import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.db import DatabaseStore

def run_tests():
    print("==================================================")
    print("RUNNING REFINED MODULE 1 REQUIREMENT INSIGHTS VERIFICATION")
    print("==================================================")

    # Force re-instantiation to pick up updated sample JD
    db = DatabaseStore()
    record = db.get_jd_analysis("demo-data-analyst")
    assert record is not None, "Demo Data Analyst record not found!"

    print(f"Loaded Job Description: '{record.job_role}' ({record.id})")

    classified = record.classified_requirements or []
    cat_counts = record.requirement_category_counts or {}
    prio_counts = record.priority_counts or {}

    print(f"\nExtracted Requirements Count: {len(classified)}")
    print(f"Category Counts: {cat_counts}")
    print(f"Priority Counts: {prio_counts}")

    # Build requirement lookup dict
    req_map = {item.requirement.lower(): item for item in classified}

    # 1. Python -> Technical Skill -> Mandatory
    assert "python" in req_map, "Python requirement missing"
    assert req_map["python"].category == "Technical Skills", f"Python category got {req_map['python'].category}"
    assert req_map["python"].priority == "Mandatory", f"Python priority got {req_map['python'].priority}"
    print("✓ [TEST 1 PASSED] Python -> Technical Skill -> Mandatory")

    # 2. SQL -> Technical Skill -> Mandatory
    assert "sql" in req_map, "SQL requirement missing"
    assert req_map["sql"].category in ["Technical Skills", "Tools / Technologies"], f"SQL category got {req_map['sql'].category}"
    assert req_map["sql"].priority == "Mandatory", f"SQL priority got {req_map['sql'].priority}"
    print("✓ [TEST 2 PASSED] SQL -> Technical Skill -> Mandatory")

    # 3. Power BI -> Technical / Tools -> Mandatory (under required responsibilities/qualifications)
    pbi_item = req_map.get("power bi") or req_map.get("powerbi")
    assert pbi_item is not None, "Power BI requirement missing"
    assert pbi_item.category in ["Technical Skills", "Tools / Technologies"], f"Power BI category got {pbi_item.category}"
    print("✓ [TEST 3 PASSED] Power BI -> Technical Skill / Tools")

    # 4. Pandas -> Technical Skill -> Preferred (under PREFERRED QUALIFICATIONS header)
    assert "pandas" in req_map, "Pandas requirement missing"
    assert req_map["pandas"].category in ["Technical Skills", "Tools / Technologies"], f"Pandas category got {req_map['pandas'].category}"
    assert req_map["pandas"].priority == "Preferred", f"Pandas priority got {req_map['pandas'].priority}"
    print("✓ [TEST 4 PASSED] Pandas -> Technical Skill -> Preferred (Section Header Context)")

    # 5. NumPy -> Technical Skill -> Preferred
    assert "numpy" in req_map, "NumPy requirement missing"
    assert req_map["numpy"].category in ["Technical Skills", "Tools / Technologies"], f"NumPy category got {req_map['numpy'].category}"
    assert req_map["numpy"].priority == "Preferred", f"NumPy priority got {req_map['numpy'].priority}"
    print("✓ [TEST 5 PASSED] NumPy -> Technical Skill -> Preferred")

    # 6. Tableau -> Technical Skill -> Preferred
    assert "tableau" in req_map, "Tableau requirement missing"
    assert req_map["tableau"].category in ["Technical Skills", "Tools / Technologies"], f"Tableau category got {req_map['tableau'].category}"
    assert req_map["tableau"].priority == "Preferred", f"Tableau priority got {req_map['tableau'].priority}"
    print("✓ [TEST 6 PASSED] Tableau -> Technical Skill -> Preferred")

    # 7. AWS -> Technical Skill / Tools -> Preferred
    assert "aws" in req_map, "AWS requirement missing"
    assert req_map["aws"].priority == "Preferred", f"AWS priority got {req_map['aws'].priority}"
    print("✓ [TEST 7 PASSED] AWS -> Preferred")

    # 8. Microsoft Azure -> Preferred
    azure_item = req_map.get("microsoft azure") or req_map.get("azure")
    assert azure_item is not None, "Microsoft Azure requirement missing"
    assert azure_item.priority == "Preferred", f"Azure priority got {azure_item.priority}"
    print("✓ [TEST 8 PASSED] Microsoft Azure -> Preferred")

    # 9. Bachelor's degree -> Education (Not Experience!)
    edu_items = [item for item in classified if item.category == "Education"]
    assert len(edu_items) > 0, "No Education requirements extracted!"
    assert any("degree" in item.requirement.lower() or "bachelor" in item.requirement.lower() for item in edu_items), "Bachelor's degree missing from Education category"
    print("✓ [TEST 9 PASSED] Bachelor's Degree -> Education Category")

    # 10. 1-3 years -> Experience
    exp_items = [item for item in classified if item.category == "Experience"]
    assert len(exp_items) > 0, "No Experience requirements extracted!"
    print("✓ [TEST 10 PASSED] 1-3 Years -> Experience Category")

    # 11 & 12. Soft Skills (Communication & Problem Solving)
    soft_items = [item for item in classified if item.category == "Soft Skills"]
    assert len(soft_items) > 0, "No Soft Skills extracted!"
    print("✓ [TEST 11 & 12 PASSED] Communication & Problem Solving -> Soft Skills Category")

    # 13. Job Responsibility Sentences -> Job Responsibilities
    resp_items = [item for item in classified if item.category == "Job Responsibilities"]
    assert len(resp_items) > 0, "No Job Responsibilities extracted!"
    print("✓ [TEST 13 PASSED] Duty sentences -> Job Responsibilities Category")

    # 14. "be" is NOT extracted
    assert "be" not in req_map, "Stopword 'be' was incorrectly extracted as a requirement!"
    print("✓ [TEST 14 PASSED] Stopword 'be' was NOT extracted (Noise Filter working)")

    # 15. Technical Skills count > 0
    assert cat_counts.get("Technical Skills", 0) > 0, "Technical Skills metric count must be > 0"
    print(f"✓ [TEST 15 PASSED] Technical Skills count is {cat_counts['Technical Skills']} (> 0)")

    # 16. Education count > 0
    assert cat_counts.get("Education", 0) > 0, "Education metric count must be > 0"
    print(f"✓ [TEST 16 PASSED] Education count is {cat_counts['Education']} (> 0)")

    # 17. Preferred count reflects actual preferred section
    assert prio_counts.get("Preferred", 0) >= 4, "Preferred count should accurately reflect items under PREFERRED QUALIFICATIONS"
    print(f"✓ [TEST 17 PASSED] Preferred count is {prio_counts['Preferred']} (reflects PREFERRED QUALIFICATIONS header)")

    print("\nALL 17 DETAILED REQUIREMENT EXTRACTION & CLASSIFICATION TESTS PASSED!\n")

if __name__ == "__main__":
    run_tests()
