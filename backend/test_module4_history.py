import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.db import DatabaseStore

def run_tests():
    print("==================================================")
    print("RUNNING MODULE 4 ANALYSIS HISTORY VERIFICATION")
    print("==================================================")

    db = DatabaseStore()
    history = db.get_all_records()
    assert len(history) > 0, "No records found in database store!"

    print(f"Total analysis history records retrieved: {len(history)}")

    for rec in history:
        assert hasattr(rec, "id") and rec.id, "Record ID missing"
        assert hasattr(rec, "job_role") and rec.job_role, "Job role missing"
        assert hasattr(rec, "timestamp") and rec.timestamp, "Timestamp missing"
        assert hasattr(rec, "total_skills_count"), "Total skills count missing"
        assert hasattr(rec, "priority_counts"), "Priority counts missing"

        mand_cnt = rec.priority_counts.get("Mandatory", 0) if rec.priority_counts else 0
        pref_cnt = rec.priority_counts.get("Preferred", 0) if rec.priority_counts else 0

        print(f"Record: '{rec.job_role}' | Date: '{rec.timestamp}' | Skills: {rec.total_skills_count} | Mand: {mand_cnt} | Pref: {pref_cnt}")

    print("\n✓ [TEST 1 PASSED] Analysis History Persistence & Data Model verified")
    print("ALL MODULE 4 ANALYSIS HISTORY TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
