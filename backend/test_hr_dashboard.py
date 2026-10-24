import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests():
    print("==================================================")
    print("RUNNING HR MODULE 1 — HR DASHBOARD VERIFICATION")
    print("==================================================")

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "index.html"))
    assert os.path.exists(html_path), "index.html file not found!"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Verify HR Header
    assert "HR Dashboard" in content, "HR Dashboard header title missing"
    assert "Welcome, <strong id=\"hrHeaderUserName\"" in content or "Welcome, <strong id='hrHeaderUserName'" in content, "Dynamic HR welcome header missing"

    print("✓ [TEST 1 PASSED] HR Dashboard header and dynamic welcome message verified")

    # 2. Verify 4 Summary Cards
    assert "Total Job Descriptions" in content, "Total Job Descriptions metric card missing"
    assert "Analyzed Job Descriptions" in content, "Analyzed Job Descriptions metric card missing"
    assert "Total Extracted Skills" in content, "Total Extracted Skills metric card missing"
    assert "Recent JD" in content, "Recent JD metric card missing"

    print("✓ [TEST 2 PASSED] 4 essential HR summary cards verified")

    # 3. Verify 2 Main HR Actions
    assert "Create Job Description" in content, "Create Job Description action button missing"
    assert "View Job Descriptions" in content, "View Job Descriptions action button missing"

    print("✓ [TEST 3 PASSED] 2 primary HR actions verified")

    # 4. Verify Empty State
    assert "No Job Descriptions yet" in content, "HR empty state title missing"
    assert "Create your first Job Description to begin requirement and skill analysis." in content, "HR empty state subtitle missing"

    print("✓ [TEST 4 PASSED] HR user empty state verified")

    # 5. Verify HR Sidebar Navigation Items
    assert "switchHRTab('hr-dashboard'" in content, "HR Sidebar Dashboard nav link missing"
    assert "switchHRTab('hr-job-descriptions'" in content, "HR Sidebar Job Descriptions nav link missing"
    assert "btn-logout" in content, "HR Sidebar Sign Out nav link missing"

    print("✓ [TEST 5 PASSED] HR sidebar navigation clean & focused")

    # 6. Verify User-Scoped Backend Route
    jd_route_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "routes", "jd.py"))
    with open(jd_route_path, "r", encoding="utf-8") as f:
        jd_code = f.read()

    assert "/user-history" in jd_code, "User-scoped backend history endpoint missing in routes/jd.py"

    print("✓ [TEST 6 PASSED] User-scoped backend endpoint verified")

    print("\nALL HR MODULE 1 — HR DASHBOARD TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
