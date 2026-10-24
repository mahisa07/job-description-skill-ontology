import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.routes.auth import login, register, LoginRequest, RegisterRequest

async def run_tests():
    print("==================================================")
    print("TESTING MULTI-PORTAL & ROLE-BASED AUTHENTICATION")
    print("==================================================")

    # 1. Normal User Login
    res1 = await login(LoginRequest(email="user@skillontology.com", password="User@123"))
    assert res1["user"]["role"] == "user", f"Expected role 'user', got '{res1['user']['role']}'"
    print("✓ [PASSED] Normal User Login -> Role: user")

    # 2. HR Manager Login
    res2 = await login(LoginRequest(email="hr@skillontology.com", password="Hr@123", portal_type="hr"))
    assert res2["user"]["role"] == "hr", f"Expected role 'hr', got '{res2['user']['role']}'"
    assert res2["user"]["company_name"] == "Acme Tech Solutions", "Company name mismatch"
    print(f"✓ [PASSED] HR Manager Login -> Role: hr | Company: {res2['user']['company_name']}")

    # 3. Recruiter Login
    res3 = await login(LoginRequest(email="recruiter@skillontology.com", password="Recruiter@123", portal_type="hr"))
    assert res3["user"]["role"] == "recruiter", f"Expected role 'recruiter', got '{res3['user']['role']}'"
    assert res3["user"]["company_name"] == "Global Talent Recruitment", "Company name mismatch"
    print(f"✓ [PASSED] Recruiter Login -> Role: recruiter | Company: {res3['user']['company_name']}")

    # 4. Create New HR Account
    reg_hr = RegisterRequest(
        full_name="Elena Rostova",
        email="elena@techcorp.io",
        password="Pass@123",
        confirm_password="Pass@123",
        role="hr",
        company_name="TechCorp AI"
    )
    res4 = await register(reg_hr)
    assert res4["user"]["role"] == "hr"
    print("✓ [PASSED] HR Account Creation -> Success")

    # 5. Login with newly created HR account
    res5 = await login(LoginRequest(email="elena@techcorp.io", password="Pass@123"))
    assert res5["user"]["role"] == "hr"
    assert res5["user"]["company_name"] == "TechCorp AI"
    print(f"✓ [PASSED] Created HR Account Login -> Role: {res5['user']['role']} | Company: {res5['user']['company_name']}")

    print("\nALL ROLE-BASED AUTHENTICATION TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
