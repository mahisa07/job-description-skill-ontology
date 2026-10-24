import os
from fastapi.testclient import TestClient
from backend.main import app
from backend.routes.auth import load_users

client = TestClient(app)

def test_real_authentication_system():
    print("--- TESTING REAL EMAIL & PASSWORD AUTHENTICATION ---")

    # 1. Test Seed / Demo Accounts exist
    demo_hr_res = client.post("/api/auth/login", json={
        "email": "hr@skillontology.com",
        "password": "Hr@123",
        "portal_type": "hr"
    })
    assert demo_hr_res.status_code == 200, "Demo HR account login failed"
    assert demo_hr_res.json()["user"]["role"] == "hr"
    print("✓ Demo HR account login verified.")

    demo_user_res = client.post("/api/auth/login", json={
        "email": "user@skillontology.com",
        "password": "User@123",
        "portal_type": "user"
    })
    assert demo_user_res.status_code == 200, "Demo User account login failed"
    assert demo_user_res.json()["user"]["role"] == "user"
    print("✓ Demo User account login verified.")

    # 2. Test Real HR Registration
    import uuid
    rand_id = uuid.uuid4().hex[:6]
    hr_email = f"testhr_{rand_id}@example.com"
    hr_pass = "Test@12345"

    reg_hr_res = client.post("/api/auth/register", json={
        "full_name": "Test HR Recruiter",
        "email": hr_email,
        "password": hr_pass,
        "confirm_password": hr_pass,
        "role": "hr",
        "company_name": "Acme Global HR"
    })
    assert reg_hr_res.status_code == 200, f"HR Registration failed: {reg_hr_res.text}"
    assert "Account created successfully" in reg_hr_res.json()["message"]
    print(f"✓ Registered new HR account: {hr_email}")

    # 3. Test Real HR Login with exact credentials
    login_hr_res = client.post("/api/auth/login", json={
        "email": hr_email,
        "password": hr_pass,
        "portal_type": "hr"
    })
    assert login_hr_res.status_code == 200, f"HR Login failed for registered account: {login_hr_res.text}"
    hr_user_data = login_hr_res.json()["user"]
    assert hr_user_data["role"] == "hr"
    assert hr_user_data["name"] == "Test HR Recruiter"
    assert hr_user_data["company_name"] == "Acme Global HR"
    print(f"✓ Successfully logged in with real HR account: {hr_email} (Role: {hr_user_data['role']})")

    # 4. Test Real Normal User Registration
    user_email = f"testuser_{rand_id}@example.com"
    user_pass = "Test@12345"

    reg_user_res = client.post("/api/auth/register", json={
        "full_name": "Test Candidate User",
        "email": user_email,
        "password": user_pass,
        "confirm_password": user_pass,
        "role": "user"
    })
    assert reg_user_res.status_code == 200, f"Normal User Registration failed: {reg_user_res.text}"
    print(f"✓ Registered new Normal User account: {user_email}")

    # 5. Test Real Normal User Login with exact credentials
    login_user_res = client.post("/api/auth/login", json={
        "email": user_email,
        "password": user_pass,
        "portal_type": "user"
    })
    assert login_user_res.status_code == 200, f"User Login failed for registered account: {login_user_res.text}"
    user_data = login_user_res.json()["user"]
    assert user_data["role"] == "user"
    assert user_data["name"] == "Test Candidate User"
    print(f"✓ Successfully logged in with real Normal User account: {user_email} (Role: {user_data['role']})")

    # 6. Test Case-Insensitive Email Login (Uppercase TESTUSER@EXAMPLE.COM)
    login_case_res = client.post("/api/auth/login", json={
        "email": "TESTUSER@EXAMPLE.COM",
        "password": user_pass
    })
    assert login_case_res.status_code == 200, "Case-insensitive email login failed"
    print("✓ Case-insensitive email login verified.")

    # 7. Test Duplicate Email Prevention
    dup_res = client.post("/api/auth/register", json={
        "full_name": "Duplicate User",
        "email": "TestUser@Example.com",
        "password": "Password123",
        "confirm_password": "Password123",
        "role": "user"
    })
    assert dup_res.status_code == 400, "Duplicate email registration was not blocked"
    assert "already exists" in dup_res.json()["detail"]
    print("✓ Duplicate email prevention verified.")

    # 8. Test Incorrect Password Handling
    wrong_pass_res = client.post("/api/auth/login", json={
        "email": user_email,
        "password": "WrongPassword!99"
    })
    assert wrong_pass_res.status_code == 401, "Wrong password was not rejected"
    assert wrong_pass_res.json()["detail"] == "Invalid email or password."
    print("✓ Incorrect password error handling verified.")

    # 9. Verify users.json persistence file exists
    users_json = os.path.join(os.path.dirname(__file__), "database", "users.json")
    assert os.path.exists(users_json), "users.json file not created for persistence"
    print("✓ Persistent user storage file users.json verified.")

    print("\nALL AUTHENTICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_real_authentication_system()
