import os
import re

def test_no_duplicate_job_descriptions_heading():
    index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    print("--- TESTING DUPLICATE HEADING FIX ON HR JOB DESCRIPTIONS PAGE ---")

    # 1. Locate section id="hr-view-job-descriptions"
    section_match = re.search(r'<section id="hr-view-job-descriptions"[^>]*>(.*?)</section>', html, re.DOTALL)
    assert section_match, "section id='hr-view-job-descriptions' not found"

    section_content = section_match.group(1)

    # 2. Assert no <h2> tag exists inside section#hr-view-job-descriptions
    assert '<h2' not in section_content, "Found duplicate <h2> heading inside section#hr-view-job-descriptions!"
    print("✓ Inner section does NOT contain a duplicate <h2> heading.")

    # 3. Assert subtitle exists
    assert 'Create, manage, and analyze your Job Descriptions.' in section_content, "Subtitle text missing from section content"
    print("✓ Subtitle 'Create, manage, and analyze your Job Descriptions.' verified.")

    # 4. Assert header bar has main title element and create button
    assert 'id="hrPageTitle"' in html, "Global header bar page title element #hrPageTitle missing"
    assert 'navigateToCreateJD()' in html or 'openHRCreateJDModal()' in html, "Create Job Description primary action button missing"
    print("✓ Global header bar owns single main heading and primary action button.")

    print("\nALL DUPLICATE HEADING TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_no_duplicate_job_descriptions_heading()
