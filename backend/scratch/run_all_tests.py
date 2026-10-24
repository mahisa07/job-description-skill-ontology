import sys
import unittest
from backend.test_real_authentication import test_real_authentication_system
from backend.test_notification_workflow import test_hr_to_user_explicit_review_workflow

if __name__ == "__main__":
    print("=== RUNNING SYSTEM DIAGNOSTICS & VERIFICATION ===")
    try:
        test_real_authentication_system()
        print("\n--- AUTHENTICATION SYSTEM VERIFIED OK ---")
        test_hr_to_user_explicit_review_workflow()
        print("\n--- NOTIFICATION WORKFLOW VERIFIED OK ---")
        print("\nALL BACKEND & API TESTS PASSED SUCCESSFULLY!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
