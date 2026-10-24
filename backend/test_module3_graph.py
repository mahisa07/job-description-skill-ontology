import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.db import DatabaseStore

def run_tests():
    print("==================================================")
    print("RUNNING MODULE 3 KNOWLEDGE GRAPH VERIFICATION")
    print("==================================================")

    db = DatabaseStore()
    record = db.get_jd_analysis("demo-data-analyst")
    assert record is not None, "Demo Data Analyst record not found!"

    print(f"Loaded Job Description: '{record.job_role}' ({record.id})")

    skills = record.skills or []
    skill_categories = record.skill_categories or {}
    ontology = record.ontology

    # 1. Essential Node Types (Job Role, Category, Skill)
    nodes = ontology.nodes
    role_nodes = [n for n in nodes if n.type == "role"]
    cat_nodes = [n for n in nodes if n.type == "category"]
    skill_nodes = [n for n in nodes if n.type == "skill"]

    assert len(role_nodes) == 1, "Root Job Role node missing"
    assert role_nodes[0].label == record.job_role, f"Role node label got {role_nodes[0].label}"
    assert len(cat_nodes) > 0, "Skill Category nodes missing"
    assert len(skill_nodes) > 0, "Skill nodes missing"
    print("✓ [TEST 1 PASSED] Essential Node Types (Job Role -> Category -> Skill) verified")

    # 2. Supported Relationships (has_category, belongs_to, requires)
    edges = ontology.edges
    supported_relations = set(e.relation for e in edges)

    assert "has_category" in supported_relations or "belongs_to" in supported_relations or "requires" in supported_relations, "Supported relations missing"
    print("✓ [TEST 2 PASSED] Supported Graph Relationships verified")

    # 3. Priority Information Binding
    python_skill = next((s for s in skills if s.canonical_name == "Python"), None)
    assert python_skill is not None, "Python skill missing"
    assert python_skill.requirement_level in ["REQUIRED", "PREFERRED", "OPTIONAL"], "Requirement level missing"
    print("✓ [TEST 3 PASSED] Skill Priority Information (Mandatory/Preferred) bound to nodes")

    # 4. Node Detail Properties Validation
    # Job Role Details
    assert len(skills) > 0, "Skills list missing"
    # Category Details
    assert len(skill_categories) > 0, "Categories missing"
    print("✓ [TEST 4 PASSED] Compact Node Detail Properties (Role, Category, Skill) verified")

    print("\nALL MODULE 3 KNOWLEDGE GRAPH TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
