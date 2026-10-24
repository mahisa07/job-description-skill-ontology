import os
import re

def test_no_duplicate_profile_heading():
    index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    print("--- TESTING DUPLICATE HEADING FIX ON HR PROFILE PAGE ---")

    # 1. Locate section id="hr-view-profile"
    section_match = re.search(r'<section id="hr-view-profile"[^>]*>(.*?)</section>', html, re.DOTALL)
    assert section_match, "section id='hr-view-profile' not found"

    section_content = section_match.group(1)

    # 2. Assert no <h2> tag exists inside section#hr-view-profile
    assert '<h2' not in section_content, "Found duplicate <h2> heading inside section#hr-view-profile!"
    print("✓ Inner section does NOT contain a duplicate <h2> heading.")

    # 3. Assert subtitle exists
    assert 'Manage your HR account information and profile details.' in section_content, "Subtitle text missing from section content"
    print("✓ Subtitle 'Manage your HR account information and profile details.' verified.")

    # 4. Assert profile card, view mode, edit mode, and form buttons exist
    assert 'id="hrProfileViewMode"' in section_content, "hrProfileViewMode missing"
    assert 'id="hrProfileEditMode"' in section_content, "hrProfileEditMode missing"
    assert 'enableHRProfileEditMode()' in section_content, "Edit Profile button missing"
    print("✓ Profile card, Read-Only view, Edit form, and action buttons verified.")

    print("\nALL DUPLICATE PROFILE HEADING TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_no_duplicate_profile_heading()
