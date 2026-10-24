import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests():
    print("==================================================")
    print("RUNNING POPULATED HR DASHBOARD & JD MANAGEMENT TESTS")
    print("==================================================")

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "index.html"))
    assert os.path.exists(html_path), "index.html file not found!"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # --- PART 1 — HR DASHBOARD TESTS ---
    assert "HR Dashboard" in content, "HR Dashboard header missing"
    assert "Welcome," in content, "Dynamic welcome message missing"
    assert "Manage Job Descriptions and analyze their requirements and skills." in content, "Dashboard header subtitle missing"

    # 4 Summary Cards
    assert 'id="hrKpiTotalJDs"' in content, "Total Job Descriptions metric missing"
    assert 'id="hrKpiDrafts"' in content, "Drafts metric missing"
    assert 'id="hrKpiAnalyzedJDs"' in content, "Analyzed metric missing"
    assert 'id="hrKpiTotalSkills"' in content, "Extracted Skills metric missing"

    # Quick Action Button
    assert "navigateToCreateJD()" in content, "Quick Action navigateToCreateJD button missing"

    # Recent Job Descriptions Table (Top 3)
    assert 'id="hrRecentJdTableContainer"' in content, "Recent JDs container missing"
    assert "records.reverse().slice(0, 3)" in content or "slice(0, 3)" in content, "Top 3 recent JDs slicing missing"
    assert "Create your first Job Description &rarr;" in content, "Dashboard empty state button missing"

    print("✓ [TEST 1 PASSED] HR Dashboard (Header, 4 Cards, Quick Action, Top 3 Recent JDs, Empty State) verified")

    # --- PART 2 — JOB DESCRIPTIONS PAGE TESTS ---
    assert "Job Descriptions" in content, "Job Descriptions page title missing"
    assert "Create, manage, and analyze your Job Descriptions." in content, "Job Descriptions page subtitle missing"
    assert "Search by Job Title or Department..." in content, "Search input placeholder missing"

    # Management Table Columns
    assert "Job Title" in content, "Job Title column missing"
    assert "Department" in content, "Department column missing"
    assert "Location" in content, "Location column missing"
    assert "Created Date" in content, "Created Date column missing"
    assert "Status" in content, "Status column missing"
    assert "Action" in content, "Action column missing"

    # Form Fields & Dual Actions
    assert 'id="hrModalRoleInput"' in content, "Job Title input missing"
    assert 'id="hrModalDeptInput"' in content, "Department input missing"
    assert 'id="hrModalLocationInput"' in content, "Location input missing"
    assert 'id="hrModalTextInput"' in content, "Job Description text area missing"
    assert "Save Draft" in content, "Save Draft button missing"
    assert "Analyze Job Description" in content, "Analyze Job Description button missing"

    # Existing JD Actions & Details Modal
    assert 'id="hrJdDetailsModal"' in content, "Job Description Details modal missing"
    assert "openHRJdDetailsModal" in content, "openHRJdDetailsModal function missing"
    assert "View Requirement Insights &rarr;" in content, "View Requirement Insights button missing"
    assert "deleteHRJd" in content, "deleteHRJd function missing"

    print("✓ [TEST 2 PASSED] Job Descriptions Page (Search, Table, Form, Dual Buttons, Details Modal, Actions) verified")

    # --- SIDEBAR & THEME TESTS ---
    assert "HR Portal" in content, "HR Portal sidebar label missing"
    assert "Sign Out" in content, "Sign Out button missing"
    assert "#6D28D9" in content, "Professional Purple theme color verified"

    print("✓ [TEST 3 PASSED] HR Sidebar & Theme consistency verified")

    print("\nALL POPULATED HR DASHBOARD AND JOB DESCRIPTIONS TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
