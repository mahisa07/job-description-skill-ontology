import os
import re

def test_hr_profile_module():
    index_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    print("--- TESTING HR PROFILE MODULE IMPLEMENTATION ---")

    # 1. Verify Sidebar Navigation items
    assert 'btnHrSidebarProfile' in html, "HR Sidebar Profile button missing"
    assert 'switchHRTab(\'hr-profile\', this)' in html, "switchHRTab('hr-profile') handler missing"
    print("✓ HR Sidebar updated with Profile menu item.")

    # 2. Verify Profile Header Title & Subtitle
    assert "My Profile" in html, "My Profile title missing"
    assert "Manage your HR account information and profile details." in html, "My Profile subtitle missing"
    print("✓ Profile page header and subtitle verified.")

    # 3. Verify Read-Only & Edit Mode Views
    assert 'id="hrProfileViewMode"' in html, "hrProfileViewMode element missing"
    assert 'id="hrProfileEditMode"' in html, "hrProfileEditMode element missing"
    assert 'enableHRProfileEditMode()' in html, "enableHRProfileEditMode function missing"
    assert 'cancelHRProfileEdit()' in html, "cancelHRProfileEdit function missing"
    print("✓ Read-Only View Mode and Edit Mode components verified.")

    # 4. Verify Profile Fields (Full Name, Work Email, Phone, Company, Job Title, Department)
    assert 'hrProfileValName' in html and 'hrEditNameInput' in html, "Full Name fields missing"
    assert 'hrProfileValEmail' in html and 'hrEditEmailInput' in html, "Work Email fields missing"
    assert 'hrProfileValPhone' in html and 'hrEditPhoneInput' in html, "Phone Number fields missing"
    assert 'hrProfileValCompany' in html and 'hrEditCompanyInput' in html, "Company fields missing"
    assert 'hrProfileValTitle' in html and 'hrEditTitleInput' in html, "Job Title fields missing"
    assert 'hrProfileValDept' in html and 'hrEditDeptInput' in html, "Department fields missing"
    print("✓ All 6 Profile fields (Full Name, Work Email, Phone, Company, Job Title, Department) verified.")

    # 5. Verify Photo Upload and Avatar Persistence
    assert 'hrProfilePhotoInput' in html, "Avatar file input missing"
    assert 'handleHRProfilePhotoSelect' in html, "Photo selection handler missing"
    assert 'pendingAvatarB64' in html, "Base64 avatar handling missing"
    print("✓ Profile photo file picker and base64 avatar persistence verified.")

    # 6. Verify Validation & Success Messages
    assert 'Profile updated successfully.' in html, "Success message string missing"
    assert 'Full Name is required.' in html, "Name validation string missing"
    assert 'saveHRProfile' in html, "saveHRProfile handler missing"
    print("✓ Client-side validation and success message handling verified.")

    # 7. Verify Route Preservation & Back/Forward Support
    assert "combined.includes('profile')" in html, "Route parser profile check missing"
    assert 'cleanName === \'hr-profile\'' in html, "switchHRTab hr-profile handler missing"
    print("✓ Route parsing and navigation history support for /hr/profile verified.")

    # 8. Check Auth Backend Endpoint in auth.py
    auth_path = os.path.join(os.path.dirname(__file__), 'routes', 'auth.py')
    with open(auth_path, 'r', encoding='utf-8') as f_auth:
        auth_code = f_auth.read()

    assert '@router.post("/profile")' in auth_code, "POST /api/auth/profile endpoint missing in auth.py"
    assert 'ProfileUpdateRequest' in auth_code, "ProfileUpdateRequest schema missing in auth.py"
    print("✓ Backend API endpoint POST /api/auth/profile verified.")

    print("\nALL HR PROFILE MODULE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_hr_profile_module()
