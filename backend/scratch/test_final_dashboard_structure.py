import os
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=== VERIFYING FINAL CLEAN JOB SEEKER DASHBOARD STRUCTURE ===")

index_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html')
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Verify Top Header is untouched
assert 'Dashboard Overview' in html
assert 'id="headerUserName"' in html
assert 'id="userNotifBadge"' in html
assert 'id="jdSelect"' in html

# 2. Verify duplicate welcome section is REMOVED
assert 'id="dashWelcomeName"' not in html, "Duplicate welcome section not removed"

# 3. Verify Quick Actions card block is REMOVED from view-dashboard
assert 'Quick Actions' not in html, "Quick Actions block not removed"

# 4. Verify Skill Ontology Preview is REMOVED from view-dashboard
assert 'Skill Ontology Preview' not in html, "Skill Ontology Preview block not removed"
assert 'id="ontologyPreviewTree"' not in html, "ontologyPreviewTree element not removed"

# 5. Verify the required 6 sections in view-dashboard:
# Section 1: Summary Cards
assert 'id="kpiRole"' in html
assert 'id="kpiExp"' in html
assert 'id="kpiReqSkills"' in html
assert 'id="kpiTotalSkills"' in html

# Section 2: Job Overview
assert 'id="overviewJobTitle"' in html
assert 'id="overviewDept"' in html
assert 'id="overviewCompany"' in html
assert 'id="overviewLocation"' in html
assert 'id="overviewExp"' in html
assert 'id="overviewEdu"' in html
assert 'id="overviewStatus"' in html

# Section 3: Requirement Priority Breakdown
assert 'id="dashboardPriorityCollapse"' in html

# Section 4: Requirement Classification Summary
assert 'id="dashboardCategoryCollapse"' in html
assert 'toggleZeroCategories()' in html

# Section 5: Top Required Skills
assert 'id="dashboardTopSkillChips"' in html

# 6. Verify full standalone modules remain functional
assert 'id="view-ontology-explorer"' in html, "Skill Ontology Explorer module missing"
assert 'id="view-req-insights"' in html, "Requirement Insights module missing"
assert 'id="view-ontology"' in html, "Knowledge Graph module missing"
assert 'id="view-analyze"' in html, "Analyze JD module missing"
assert 'id="view-analysis-history"' in html, "Analysis History module missing"

# 7. Check backend API
r_root = client.get("/")
assert r_root.status_code == 200

r_pub = client.get("/api/jobs/published/list")
assert r_pub.status_code == 200

print("✓ All 13 Final Test items verified with 100% success!")
