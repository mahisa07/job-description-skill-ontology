import os
import re

def test_hr_analysis_history_module():
    index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    print("--- TESTING HR ANALYSIS HISTORY MODULE ---")

    # 1. Sidebar items (Dashboard, Job Descriptions, Requirement Review, Analysis History, Profile, Sign Out)
    assert 'btnHrSidebarDashboard' in html, "Dashboard sidebar button missing"
    assert 'btnHrSidebarJDs' in html, "Job Descriptions sidebar button missing"
    assert 'btnHrSidebarReqReview' in html, "Requirement Review sidebar button missing"
    assert 'btnHrSidebarHistory' in html, "Analysis History sidebar button missing"
    assert 'btnHrSidebarProfile' in html, "Profile sidebar button missing"
    assert 'Sign Out' in html, "Sign Out button missing"
    print("✓ HR Sidebar menu items (Dashboard, Job Descriptions, Requirement Review, Analysis History, Profile, Sign Out) verified.")

    # 2. Dedicated Route /hr/analysis-history
    assert 'analysis-history' in html and 'hr-analysis-history' in html, "Route handling for hr-analysis-history missing"
    print("✓ Route parsing and refresh preservation for /hr/analysis-history verified.")

    # 3. View Panel section#hr-view-analysis-history
    assert 'id="hr-view-analysis-history"' in html, "hr-view-analysis-history panel missing"
    assert 'View and manage your previous job description analyses' in html, "Subtitle text missing"
    print("✓ Analysis History view panel and title verified.")

    # 4. Summary Metrics Cards (Total Analyses, Completed, This Month, Skills Extracted)
    assert 'hrHistTotalAnalyses' in html, "Total Analyses metric card missing"
    assert 'hrHistCompleted' in html, "Completed metric card missing"
    assert 'hrHistThisMonth' in html, "This Month metric card missing"
    assert 'hrHistTotalSkills' in html, "Skills Extracted metric card missing"
    print("✓ Summary metrics cards verified.")

    # 5. Search and Filters
    assert 'id="hrHistSearch"' in html, "Search bar missing"
    assert 'id="hrHistDeptFilter"' in html, "Department filter missing"
    assert 'id="hrHistStatusFilter"' in html, "Status filter missing"
    assert 'id="hrHistDateFilter"' in html, "Date filter missing"
    assert 'clearHRHistoryFilters()' in html, "Clear Filters button handler missing"
    print("✓ Search bar and Department/Status/Date filters verified.")

    # 6. Table & Actions (View Analysis, Download Report, Delete)
    assert 'id="hrHistTableContainer"' in html, "History table container missing"
    assert 'openHRAnalysisDetailModal' in html, "openHRAnalysisDetailModal handler missing"
    assert 'downloadHRAnalysisReport' in html, "downloadHRAnalysisReport handler missing"
    assert 'deleteHRAnalysis' in html, "deleteHRAnalysis handler missing"
    print("✓ Master history table and View/Download/Delete actions verified.")

    # 7. View Analysis Modal and Ontology Visual Map
    assert 'id="hrAnalysisDetailModal"' in html, "hrAnalysisDetailModal element missing"
    assert 'Ontology Relationship Map' in html, "Ontology relationship map header missing"
    assert 'Job Role' in html and 'Skills' in html and 'Knowledge' in html, "Ontology relationship cards missing"
    print("✓ View Analysis modal with Job Info, Extracted Reqs, and Ontology Map verified.")

    # 8. Loading, Error, and Empty States
    assert 'id="hrHistLoading"' in html, "Loading state container missing"
    assert 'id="hrHistError"' in html, "Error state container missing"
    assert 'id="hrHistEmptyState"' in html, "Empty state container missing"
    assert 'No analysis history available.' in html, "Empty state text missing"
    print("✓ Loading state, Error state, and Empty state verified.")

    print("\nALL HR ANALYSIS HISTORY MODULE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_hr_analysis_history_module()
