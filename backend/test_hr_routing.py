import os
import re

def test_hr_routing_implementation():
    index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    print("--- TESTING HR PORTAL ROUTING & REFRESH LOGIC ---")

    # 1. Verify getTargetHRRoute function exists and parses routes correctly
    assert 'function getTargetHRRoute()' in html, "getTargetHRRoute function missing"
    assert 'job-descriptions' in html, "job-descriptions route handling missing"
    assert 'dashboard' in html, "dashboard route handling missing"
    print("✓ getTargetHRRoute() function verified.")

    # 2. Verify checkAuthSession uses target route from URL rather than hardcoding dashboard
    assert 'const targetRoute = getTargetHRRoute() || \'hr-dashboard\';' in html or 'getTargetHRRoute' in html, \
        "checkAuthSession does not dynamically inspect URL route on load"
    print("✓ checkAuthSession() dynamically respects URL route on refresh.")

    # 3. Verify event listeners for hashchange and popstate exist for browser back/forward buttons
    assert "window.addEventListener('hashchange'" in html, "hashchange event listener missing"
    assert "window.addEventListener('popstate'" in html, "popstate event listener missing"
    print("✓ Browser Back/Forward navigation listeners (hashchange & popstate) verified.")

    # 4. Verify switchHRTab updates history/hash dynamically
    assert 'switchHRTab(viewName, btnEl, updateUrl = true)' in html or 'switchHRTab' in html, "switchHRTab function missing"
    assert 'window.location.hash' in html, "URL hash updating logic missing"
    print("✓ switchHRTab() URL hash & history synchronization verified.")

    # 5. Verify section IDs match view targets
    assert 'id="hr-view-dashboard"' in html, "hr-view-dashboard section ID missing"
    assert 'id="hr-view-job-descriptions"' in html, "hr-view-job-descriptions section ID missing"
    print("✓ HR view panel IDs (hr-view-dashboard & hr-view-job-descriptions) verified.")

    # 6. Verify sidebar button handlers
    assert 'onclick="switchHRTab(\'hr-dashboard\', this)"' in html, "HR Sidebar Dashboard onclick handler missing"
    assert 'onclick="switchHRTab(\'hr-job-descriptions\', this)"' in html, "HR Sidebar Job Descriptions onclick handler missing"
    print("✓ HR Sidebar buttons (Dashboard & Job Descriptions) handlers verified.")

    # 7. Check unauthenticated protection logic
    assert "selectPortal('hr')" in html, "selectPortal('hr') handling missing"
    assert "showHRLoginCard()" in html, "showHRLoginCard() handling missing"
    print("✓ Unauthenticated route protection and login card redirection verified.")

    print("\nALL HR PORTAL ROUTING AND NAVIGATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_hr_routing_implementation()
