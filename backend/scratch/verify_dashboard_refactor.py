import os
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=== VERIFYING DASHBOARD REFACTOR & ALL CORE MODULES ===")

# 1. Verify index.html contains all clean dashboard elements
index_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html')
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Section 1 Header
assert 'Welcome,' in html
assert 'id="dashWelcomeName"' in html
assert 'id="jdSelect"' in html
assert 'id="btnUserNotificationBell"' in html

# Section 2 Summary Cards
assert 'id="kpiRole"' in html
assert 'id="kpiExp"' in html
assert 'id="kpiReqSkills"' in html
assert 'id="kpiTotalSkills"' in html

# Section 3 Quick Actions Row
assert 'switchTabById(\'analyze\')' in html
assert 'switchTabById(\'req-insights\')' in html
assert 'switchTabById(\'ontology-explorer\')' in html
assert 'switchTabById(\'ontology\')' in html

# Section 4 Job Overview Card
assert 'id="overviewJobTitle"' in html
assert 'id="overviewDept"' in html
assert 'id="overviewCompany"' in html
assert 'id="overviewLocation"' in html
assert 'id="overviewExp"' in html
assert 'id="overviewEdu"' in html
assert 'id="overviewStatus"' in html

# Section 5 & 6 Collapsible Cards & Categories
assert 'id="dashboardPriorityCollapse"' in html
assert 'id="dashboardCategoryCollapse"' in html
assert 'toggleZeroCategories()' in html
assert 'id="btnToggleZeroCategories"' in html

# Section 7 Top Required Skills Card
assert 'id="dashboardTopSkillChips"' in html

print("✓ All 7 Job Seeker Dashboard UI Sections verified in index.html!")

# 2. Check API endpoints
r_root = client.get("/")
assert r_root.status_code == 200, "Root failed"

r_pub = client.get("/api/jobs/published/list")
assert r_pub.status_code == 200, "Published list failed"

r_notif = client.get("/api/jobs/notifications/list")
assert r_notif.status_code == 200, "Notifications list failed"

r_hist = client.get("/api/jobs/history")
assert r_hist.status_code == 200, "History failed"

print("✓ All backend API endpoints operational.")
print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
