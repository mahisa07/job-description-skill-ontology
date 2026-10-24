import os
import json
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=== VERIFYING MASTER REQUIREMENT TABLE UPDATE ===")

# 1. Verify index.html contains all new elements and functions
index_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html')
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Three small summary cards
assert 'id="prioCardMandatory"' in html, "Missing prioCardMandatory"
assert 'id="prioCardPreferred"' in html, "Missing prioCardPreferred"
assert 'id="prioCardUnknown"' in html, "Missing prioCardUnknown"

assert 'id="prioCountMandatory"' in html, "Missing prioCountMandatory"
assert 'id="prioCountPreferred"' in html, "Missing prioCountPreferred"
assert 'id="prioCountUnknown"' in html, "Missing prioCountUnknown"

assert 'selectMasterPriority(\'Mandatory\')' in html, "Missing selectMasterPriority('Mandatory')"
assert 'selectMasterPriority(\'Preferred\')' in html, "Missing selectMasterPriority('Preferred')"
assert 'selectMasterPriority(\'Unknown\')' in html, "Missing selectMasterPriority('Unknown')"

# 2. CSS Styles for cards and dark theme
assert '.priority-summary-box' in html, "Missing .priority-summary-box style"
assert '.active-prio-mandatory' in html, "Missing .active-prio-mandatory style"
assert '.active-prio-preferred' in html, "Missing .active-prio-preferred style"
assert '.active-prio-unknown' in html, "Missing .active-prio-unknown style"
assert 'body.dark-theme .priority-summary-box' in html, "Missing dark theme for summary box"
assert '.req-item-row' in html, "Missing .req-item-row style"
assert 'body.dark-theme .req-item-row' in html, "Missing dark theme for req-item-row"

# 3. List container and JavaScript functions
assert 'id="insightsRequirementsList"' in html, "Missing insightsRequirementsList container"
assert 'function selectMasterPriority(prio)' in html, "Missing selectMasterPriority function"
assert 'function filterInsightsTable()' in html, "Missing filterInsightsTable function"
assert 'openReqDetailModal(' in html, "Missing openReqDetailModal call in requirements list"
assert 'id="activePrioListLabel"' in html, "Missing activePrioListLabel"
assert 'id="activePrioListBadge"' in html, "Missing activePrioListBadge"

print("✓ All HTML, CSS, and JS components verified in index.html!")

# 2. Verify backend endpoints and database records
res = client.get("/")
assert res.status_code == 200, "Root API failed"

res_job = client.get("/api/jobs/demo-data-analyst")
assert res_job.status_code == 200, "demo-data-analyst API failed"
data = res_job.json()
reqs = data.get("classified_requirements", [])
mandatory = [r for r in reqs if (r.get("priority") or "").strip().lower() == "mandatory"]
preferred = [r for r in reqs if (r.get("priority") or "").strip().lower() == "preferred"]
unknown = [r for r in reqs if (r.get("priority") or "").strip().lower() == "unknown"]

print(f"✓ Data Analyst requirements: Mandatory={len(mandatory)}, Preferred={len(preferred)}, Unknown={len(unknown)}")
assert len(mandatory) == 9, f"Expected 9 mandatory requirements, got {len(mandatory)}"
assert len(preferred) == 6, f"Expected 6 preferred requirements, got {len(preferred)}"
assert len(unknown) == 3, f"Expected 3 unknown requirements, got {len(unknown)}"

# Check ML Engineer
res_ml = client.get("/api/jobs/demo-ml-engineer")
assert res_ml.status_code == 200
data_ml = res_ml.json()
reqs_ml = data_ml.get("classified_requirements", [])
ml_mandatory = [r for r in reqs_ml if (r.get("priority") or "").strip().lower() == "mandatory"]
ml_preferred = [r for r in reqs_ml if (r.get("priority") or "").strip().lower() == "preferred"]
ml_unknown = [r for r in reqs_ml if (r.get("priority") or "").strip().lower() == "unknown"]
print(f"✓ ML Engineer requirements: Mandatory={len(ml_mandatory)}, Preferred={len(ml_preferred)}, Unknown={len(ml_unknown)}")

print("\nALL MASTER REQUIREMENT TABLE TESTS PASSED SUCCESSFULLY!")
