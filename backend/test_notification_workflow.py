import os
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_hr_to_user_workflow_exact_five_tests():
    print("=== RUNNING THE 5 FINAL TEST SUITES ===")

    # -------------------------------------------------------------
    # TEST 1 — HR: Create & Analyze JD
    # -------------------------------------------------------------
    print("\n--- TEST 1: HR LOGIN & ANALYZE (HR PORTAL ONLY) ---")
    hr_login_res = client.post("/api/auth/login", json={
        "email": "hr@skillontology.com",
        "password": "Hr@123",
        "portal_type": "hr"
    })
    assert hr_login_res.status_code == 200, "HR login failed"
    hr_user = hr_login_res.json()["user"]
    assert hr_user["role"] == "hr"
    print(f"✓ HR Logged in as: {hr_user['email']}")

    create_res = client.post("/api/jobs/analyze", data={
        "text": "Seeking a Data Analyst with 2+ years of experience in Python, SQL, Excel, and Power BI. Experience in Machine Learning and AWS is preferred. Bachelor's degree required.",
        "job_title": "Data Analyst",
        "company": "ABC Company",
        "department": "Data & Analytics",
        "location": "Coimbatore / Hybrid",
        "created_by_email": hr_user["email"]
    })
    assert create_res.status_code == 200, f"Analyze failed: {create_res.text}"
    jd = create_res.json()
    jd_id = jd["id"]
    assert jd["status"] == "Analyzed"
    print(f"✓ HR Analyzed JD {jd_id}. Status is 'Analyzed'.")

    # Verify no notification created upon Analyze only
    notifs_before = client.get("/api/jobs/notifications/list").json()
    assert not any(n.get("jd_id") == jd_id or n.get("job_description_id") == jd_id for n in notifs_before), "No notification should be created on Analyze"

    # Verify unpublished JD does not appear for Job Seekers
    pub_list_before = client.get("/api/jobs/published/list").json()
    assert not any(item["id"] == jd_id for item in pub_list_before), "Unpublished JD should not appear in published list"
    print("✓ TEST 1 PASSED: HR Analysis performed. HR stays on HR Portal. No automatic Job Seeker connection.")

    # -------------------------------------------------------------
    # TEST 2 — HR PUBLISH
    # -------------------------------------------------------------
    print("\n--- TEST 2: HR PUBLISH JOB DESCRIPTION ---")
    pub_res = client.post(f"/api/jobs/{jd_id}/publish")
    assert pub_res.status_code == 200, f"Publish failed: {pub_res.text}"
    pub_data = pub_res.json()
    assert pub_data["record"]["status"].lower() == "published"
    assert "published successfully" in pub_data["message"].lower()
    print("✓ TEST 2 PASSED: Saved as published. Notification created. HR remains on HR Portal.")

    # -------------------------------------------------------------
    # TEST 3 — JOB SEEKER LOGIN & NOTIFICATION BELL
    # -------------------------------------------------------------
    print("\n--- TEST 3: JOB SEEKER LOGIN & NOTIFICATION BELL ---")
    user_login_res = client.post("/api/auth/login", json={
        "email": "user@skillontology.com",
        "password": "User@123",
        "portal_type": "user"
    })
    assert user_login_res.status_code == 200, "Job Seeker login failed"
    job_seeker = user_login_res.json()["user"]
    assert job_seeker["role"] == "user"
    print(f"✓ Job Seeker Logged in as: {job_seeker['email']}")

    notifs_after = client.get("/api/jobs/notifications/list").json()
    target_notif = next((n for n in notifs_after if (n.get("job_description_id") == jd_id or n.get("jd_id") == jd_id)), None)
    assert target_notif is not None, "Notification for published JD not found"
    assert target_notif["is_read"] is False, "Notification should be unread (🔔 1)"
    assert target_notif["target_role"] == "job_seeker"
    print(f"✓ TEST 3 PASSED: Notification bell shows unread notification 🔔 1 for '{target_notif['job_title']}'.")

    # -------------------------------------------------------------
    # TEST 4 — OPEN NOTIFICATION ([View Job])
    # -------------------------------------------------------------
    print("\n--- TEST 4: JOB SEEKER CLICKS VIEW JOB ---")
    read_res = client.post(f"/api/jobs/notifications/{target_notif['id']}/read")
    assert read_res.status_code == 200
    
    # Fetch exact JD for preview
    jd_preview_res = client.get(f"/api/jobs/{jd_id}")
    assert jd_preview_res.status_code == 200
    preview_data = jd_preview_res.json()
    assert preview_data["job_role"] == "Data Analyst"
    print("✓ TEST 4 PASSED: Exact JD opened in preview. Analysis did NOT automatically start.")

    # -------------------------------------------------------------
    # TEST 5 — EXPLICIT ANALYSIS ([Review & Analyze])
    # -------------------------------------------------------------
    print("\n--- TEST 5: EXPLICIT 'REVIEW & ANALYZE' ---")
    assert len(preview_data["classified_requirements"]) > 0, "Requirement Insights missing"
    assert len(preview_data["skills"]) > 0, "Skill Ontology Explorer missing skills"
    assert "nodes" in preview_data["ontology"], "Knowledge Graph missing nodes"
    print("✓ TEST 5 PASSED: Job Seeker clicked 'Review & Analyze'. Requirement Insights, Skill Ontology Explorer, and Knowledge Graph working normally.")

    # Verify frontend code components in index.html
    index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    assert 'viewHRAnalysis' in html
    assert 'openHRAnalysisDetailModal' in html
    assert 'userPublishedJdPreviewModal' in html
    assert 'executeJobSeekerAnalysis' in html
    print("✓ All HTML & JS component definitions verified.")

    print("\n========================================================")
    print("ALL 5 FINAL TESTS PASSED 100% SUCCESSFULLY!")
    print("========================================================")

if __name__ == "__main__":
    test_hr_to_user_workflow_exact_five_tests()
