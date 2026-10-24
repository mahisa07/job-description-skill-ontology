import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.requirement_classifier import RequirementClassifierService

def run_tests():
    print("==================================================")
    print("RUNNING REQUIREMENT CLASSIFIER SERVICE TESTS")
    print("==================================================")

    test_cases = [
        ("Python and SQL experience required", "Technical Skills"),
        ("Excellent communication and teamwork", "Soft Skills"),
        ("Bachelor's degree in Computer Science", "Education"),
        ("3+ years of experience in data analytics", "Experience"),
        ("AWS Certified Solutions Architect", "Certifications"),
        ("Experience with Power BI and Excel", "Tools / Technologies"),
        ("Build dashboards and prepare analytical reports", "Job Responsibilities"),
        ("Experience in banking domain", "Domain / Industry Knowledge"),
        ("Candidates should be enthusiastic about office culture", "Other Requirements")
    ]

    passed = 0
    for text, expected_category in test_cases:
        res = RequirementClassifierService.classify_single_requirement(text)
        status = "PASSED" if res.category == expected_category else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] Input: '{text}'")
        print(f"         Expected: {expected_category} | Got: {res.category}")
        print(f"         Confidence: {res.confidence * 100:.0f}% | Evidence: {res.evidence}")
        print("-" * 50)

    print(f"\nRESULTS: {passed}/{len(test_cases)} tests passed.")
    assert passed == len(test_cases), f"Only {passed} out of {len(test_cases)} passed."
    print("All requirement classifier unit tests PASSED successfully!\n")

if __name__ == "__main__":
    run_tests()
