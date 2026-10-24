import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.requirement_priority_service import RequirementPriorityService
from backend.services.requirement_classifier import RequirementClassifierService
from backend.services.requirement_extractor import RequirementExtractorService

def run_tests():
    print("==================================================")
    print("RUNNING FEATURE 2 REQUIREMENT PRIORITY TESTS")
    print("==================================================")

    test_cases = [
        ("Python", "Technical Skills", "Candidates must have Python and SQL skills.", "Mandatory"),
        ("SQL", "Technical Skills", "Candidates must have Python and SQL skills.", "Mandatory"),
        ("Power BI", "Tools / Technologies", "Experience with Power BI is preferred.", "Preferred"),
        ("AWS Certification", "Certifications", "AWS certification is an added advantage.", "Preferred"),
        ("Bachelor's degree in Computer Science", "Education", "Bachelor's degree in Computer Science is required.", "Mandatory"),
        ("Communication", "Soft Skills", "Excellent communication skills are essential.", "Mandatory"),
        ("Tableau", "Tools / Technologies", "Knowledge of Tableau is nice to have.", "Preferred"),
        ("2+ years of experience", "Experience", "2+ years of experience is mandatory.", "Mandatory"),
        ("Docker", "Tools / Technologies", "Knowledge of Docker would be a plus.", "Preferred"),
        ("Office presence", "Other Requirements", "Candidates should be comfortable working in an office.", "Unknown")
    ]

    passed = 0
    for req_text, category, context, expected_priority in test_cases:
        res = RequirementPriorityService.detect_priority(
            requirement_text=req_text,
            category=category,
            context_sentence=context
        )
        status = "PASSED" if res["priority"] == expected_priority else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] Req: '{req_text}' | Priority: {res['priority']} (Expected: {expected_priority})")
        print(f"         Confidence: {res['priority_confidence']*100:.0f}% | Evidence: {res['priority_evidence']}")
        print("-" * 50)

    print(f"\nUNIT TEST RESULTS: {passed}/{len(test_cases)} tests passed.")
    assert passed == len(test_cases), f"Only {passed} out of {len(test_cases)} passed."

    print("\n==================================================")
    print("TESTING FULL SAMPLE JD PIPELINE")
    print("==================================================")
    sample_jd = (
        "We are looking for a Data Analyst.\n"
        "Candidates must have strong Python and SQL skills.\n"
        "A Bachelor's degree in Computer Science or a related field is required.\n"
        "2+ years of experience in data analytics is mandatory.\n"
        "Experience with Power BI is preferred.\n"
        "Knowledge of Tableau is nice to have.\n"
        "AWS certification is an added advantage.\n"
        "Excellent communication and teamwork skills are essential.\n"
        "Experience with Docker would be a plus.\n"
        "Responsibilities:\n"
        "Analyze business data.\n"
        "Build dashboards.\n"
        "Prepare reports."
    )

    skills = RequirementExtractorService.extract_all_skills(sample_jd)
    edu = RequirementExtractorService.extract_education(sample_jd)
    exp = RequirementExtractorService.extract_experience(sample_jd)
    certs = RequirementExtractorService.extract_certifications(sample_jd)
    resp = RequirementExtractorService.extract_responsibilities(sample_jd)

    classified, cat_counts, priority_counts = RequirementClassifierService.classify_full_jd(
        raw_text=sample_jd,
        skills=skills,
        education=edu,
        experience=exp,
        certifications=certs,
        responsibilities=resp
    )

    print(f"Total Extracted Classified Requirements: {len(classified)}")
    print(f"Priority Counts: {priority_counts}")
    print(f"Category Counts: {cat_counts}")

    print("\nClassified Items Sample:")
    for item in classified[:10]:
        print(f" - [{item.priority.upper()}] {item.requirement} ({item.category}) | Evidence: {item.priority_evidence}")

    print("\nAll Feature 2 Requirement Priority Tests PASSED successfully!\n")

if __name__ == "__main__":
    run_tests()
