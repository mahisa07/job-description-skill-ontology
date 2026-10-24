import sys
import os

# Add backend directory and project root to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_hr_publishing_and_notifications():
    print("\n--- 1. Testing Job Seeker Permission Restrictions (403 Forbidden) ---")
    # Job seeker attempts to publish a new job directly
    seeker_publish_payload = {
        "job_title": "Unauthorized Developer",
        "company_name": "Fake Corp",
        "job_description": "Building stuff with Python and React.",
        "publisher_email": "user@skillontology.com", # Job seeker
        "publisher_name": "Mahisa S",
        "experience_level": "1-2 Years",
        "employment_type": "Full-time",
        "location": "Remote",
        "application_deadline": "2026-12-31",
        "required_skills": "Python, React"
    }
    res = client.post("/api/jobs/publish", json=seeker_publish_payload, headers={"X-User-Email": "user@skillontology.com"})
    print(f"Seeker direct publish response: {res.status_code}")
    assert res.status_code == 403, f"Expected 403 Forbidden for job seeker, got {res.status_code}"
    print("[PASS] Job seeker cannot publish jobs directly.")

    print("\n--- 2. Testing HR Job Publishing (/api/jobs/publish) ---")
    hr_publish_payload = {
        "job_title": "Senior Data Analyst",
        "company_name": "Acme Tech Solutions",
        "department": "Analytics & Intelligence",
        "job_description": "We are seeking a Senior Data Analyst with 4+ years of experience in Python, SQL, Power BI, and Tableau. Experience with AWS Redshift and snowflake is preferred. Must have excellent analytical and communication skills. Bachelor's degree required.",
        "publisher_email": "hr@skillontology.com",
        "publisher_name": "Sarah Jenkins",
        "experience_level": "4+ Years",
        "employment_type": "Full-time",
        "location": "Boston, MA (Hybrid)",
        "application_deadline": "2026-11-30",
        "required_skills": "Python, SQL, Power BI, Tableau, Snowflake"
    }
    res = client.post("/api/jobs/publish", json=hr_publish_payload, headers={"X-User-Email": "hr@skillontology.com"})
    print(f"HR publish response status: {res.status_code}")
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    job_data = res.json()
    job_id = job_data["id"]
    print(f"Published Job ID: {job_id}")
    assert job_data["job_role"] == "Senior Data Analyst"
    assert job_data["company"] == "Acme Tech Solutions"
    assert job_data["publisher_name"] == "Sarah Jenkins"
    assert job_data["status"] == "Published"
    assert job_data["employment_type"] == "Full-time"
    assert job_data["application_deadline"] == "2026-11-30"
    assert "Python" in job_data["required_skills_summary"]
    print("[PASS] HR published job successfully with full metadata and Published status.")

    print("\n--- 3. Testing Job Seeker In-App Notifications ---")
    # Check notifications for registered job seeker
    res = client.get("/api/jobs/notifications/list?user_email=user@skillontology.com", headers={"X-User-Email": "user@skillontology.com"})
    assert res.status_code == 200
    notifications = res.json()
    print(f"Job Seeker Notifications count: {len(notifications)}")
    assert len(notifications) > 0, "Expected at least 1 notification for job seeker"

    # Find the notification for our newly published job
    matching_notifs = [n for n in notifications if n.get("published_job_id") == job_id or n.get("job_description_id") == job_id]
    assert len(matching_notifs) == 1, f"Expected exactly 1 notification for job {job_id}, found {len(matching_notifs)}"
    notif = matching_notifs[0]
    notif_id = notif["id"]

    print("Notification received:")
    print(f"  ID: {notif['id']}")
    print(f"  Title: {notif.get('title', 'New Job Posted!')}")
    print(f"  Message: {notif['message']}")
    print(f"  Company: {notif['company']}")
    print(f"  Publisher: {notif.get('publisher_name')}")
    print(f"  Created At: {notif.get('created_at')}")
    print(f"  Read Status: {notif['is_read']}")

    assert "Acme Tech Solutions has published a new job: Senior Data Analyst" in notif["message"]
    assert notif["recipient_id"] == "user@skillontology.com"
    assert notif["is_read"] == False
    print("[PASS] Notification format, recipient targeting, and unread status verified.")

    print("\n--- 4. Testing Notification Deduplication ---")
    # Retrying publish on the existing job ID should not create duplicate notifications
    retry_res = client.post(f"/api/jobs/{job_id}/publish", headers={"X-User-Email": "hr@skillontology.com"})
    assert retry_res.status_code == 200

    res = client.get("/api/jobs/notifications/list?user_email=user@skillontology.com", headers={"X-User-Email": "user@skillontology.com"})
    notifications_after_retry = res.json()
    matching_after_retry = [n for n in notifications_after_retry if n.get("published_job_id") == job_id or n.get("job_description_id") == job_id]
    assert len(matching_after_retry) == 1, f"Deduplication failed! Found {len(matching_after_retry)} duplicate notifications"
    print("[PASS] Deduplication verified: retry did not duplicate notifications.")

    print("\n--- 5. Testing Seeker Publishing Existing Job ID (403 Forbidden) ---")
    seeker_retry = client.post(f"/api/jobs/{job_id}/publish", headers={"X-User-Email": "user@skillontology.com"})
    assert seeker_retry.status_code == 403, f"Expected 403 Forbidden, got {seeker_retry.status_code}"
    print("[PASS] Job seeker cannot publish existing jobs.")

    print("\n--- 6. Testing Mark Notification as Read & Persistence ---")
    read_res = client.post(f"/api/jobs/notifications/{notif_id}/read?user_email=user@skillontology.com", headers={"X-User-Email": "user@skillontology.com"})
    assert read_res.status_code == 200

    # Fetch again to verify persistence
    res = client.get("/api/jobs/notifications/list?user_email=user@skillontology.com", headers={"X-User-Email": "user@skillontology.com"})
    updated_notifs = res.json()
    target_notif = next(n for n in updated_notifs if n["id"] == notif_id)
    assert target_notif["is_read"] == True, "Expected notification to be marked as read"
    print("[PASS] Mark notification as read verified and persisted.")

    print("\n--- 7. Testing Published Job Details Retrieval ---")
    job_res = client.get(f"/api/jobs/{job_id}")
    assert job_res.status_code == 200
    retrieved_job = job_res.json()
    assert retrieved_job["id"] == job_id
    assert retrieved_job["job_role"] == "Senior Data Analyst"
    assert retrieved_job["company"] == "Acme Tech Solutions"
    assert retrieved_job["employment_type"] == "Full-time"
    assert retrieved_job["experience"] == "4+ Years"
    assert retrieved_job["application_deadline"] == "2026-11-30"
    assert retrieved_job["publisher_name"] == "Sarah Jenkins"
    assert len(retrieved_job["classified_requirements"]) > 0
    assert "priority_counts" in retrieved_job
    print("[PASS] Published job details retrieved successfully with full ontology, skills, and classification.")

    print("\n--- 8. Testing Mark All Notifications Read ---")
    clear_res = client.post("/api/jobs/notifications/read-all/clear?user_email=user@skillontology.com", headers={"X-User-Email": "user@skillontology.com"})
    assert clear_res.status_code == 200
    res = client.get("/api/jobs/notifications/list?user_email=user@skillontology.com", headers={"X-User-Email": "user@skillontology.com"})
    all_notifs = res.json()
    assert all(n["is_read"] for n in all_notifs), "All notifications should be read after clear"
    print("[PASS] Mark all notifications read verified.")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_hr_publishing_and_notifications()
