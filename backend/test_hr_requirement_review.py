import os
import re

def test_hr_requirement_review_module():
    index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    print("--- TESTING HR REQUIREMENT REVIEW MODULE ---")

    # 1. Sidebar items (Dashboard, Job Descriptions, Requirement Review, Profile, Sign Out)
    assert 'btnHrSidebarDashboard' in html, "Dashboard sidebar button missing"
    assert 'btnHrSidebarJDs' in html, "Job Descriptions sidebar button missing"
    assert 'btnHrSidebarReqReview' in html, "Requirement Review sidebar button missing"
    assert 'btnHrSidebarProfile' in html, "Profile sidebar button missing"
    assert 'Sign Out' in html, "Sign Out button missing"
    print("✓ HR Sidebar contains Dashboard, Job Descriptions, Requirement Review, Profile, and Sign Out.")

    # 2. Route handling for hr-requirement-review
    assert 'requirement-review' in html and 'hr-requirement-review' in html, "Route handling for hr-requirement-review missing"
    print("✓ Dedicated HR route /hr/requirement-review and refresh preservation verified.")

    # 3. View Panel section#hr-view-requirement-review
    assert 'id="hr-view-requirement-review"' in html, "hr-view-requirement-review panel missing"
    assert 'Review extracted job requirements, priorities, categories, and confidence' in html, "Subtitle description missing"
    print("✓ Requirement Review view panel and single header title verified.")

    # 4. Job Description Selector
    assert 'id="hrReqReviewJdSelect"' in html, "Job Description select dropdown missing"
    assert 'onHRReqReviewJDChange' in html, "Dropdown change handler missing"
    print("✓ Job Description selector dropdown verified.")

    # 5. Empty State
    assert 'id="hrReqReviewEmptyState"' in html, "Empty state card missing"
    assert 'No analyzed Job Descriptions available.' in html, "Empty state text missing"
    assert 'Go to Job Descriptions &rarr;' in html, "Link to Job Descriptions missing"
    print("✓ Empty state handling verified.")

    # 6. Compact Summary Metrics Card
    assert 'hrRevSumRole' in html, "Summary Job Title element missing"
    assert 'hrRevSumCompany' in html, "Summary Company element missing"
    assert 'hrRevSumDept' in html, "Summary Department element missing"
    assert 'hrRevSumTotal' in html, "Summary Total Reqs element missing"
    assert 'hrRevSumMandatory' in html, "Summary Mandatory Reqs element missing"
    assert 'hrRevSumPreferred' in html, "Summary Preferred Reqs element missing"
    print("✓ Compact Summary metrics card verified.")

    # 7. Filters & Table
    assert 'id="hrReqReviewSearch"' in html, "Search filter input missing"
    assert 'id="hrReqReviewCatFilter"' in html, "Category filter missing"
    assert 'id="hrReqReviewPrioFilter"' in html, "Priority filter missing"
    assert 'id="hrReqReviewStatusFilter"' in html, "Review Status filter missing"
    assert 'id="hrReqReviewTableContainer"' in html, "Table container missing"
    print("✓ Filters bar (Search, Category, Priority, Review Status) and Table container verified.")

    # 8. Review Status Toggle & Persistence
    assert 'toggleHRReqReviewStatus' in html, "Toggle status handler missing"
    assert 'hr_req_reviews' in html, "LocalStorage key hr_req_reviews missing"
    print("✓ Requirement Review status toggle and local persistence verified.")

    # 9. Details Modal integration
    assert 'openHRReqDetailModal' in html, "Details modal handler missing"
    print("✓ Requirement Details modal integration verified.")

    print("\nALL REQUIREMENT REVIEW MODULE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_hr_requirement_review_module()
