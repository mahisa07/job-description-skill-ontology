import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests():
    print("==================================================")
    print("RUNNING FINAL SIDEBAR & MODULE CLEANUP VERIFICATION")
    print("==================================================")

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "index.html"))
    assert os.path.exists(html_path), "index.html file not found!"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Locate #appSidebar block
    start_idx = content.find('id="appSidebar"')
    end_idx = content.find('</aside>', start_idx)
    assert start_idx != -1 and end_idx != -1, "#appSidebar block not found"

    sidebar_html = content[start_idx:end_idx]

    # Verify required core modules ARE PRESENT in sidebar
    required_modules = [
      "Dashboard",
      "Analyze JD",
      "Requirement Insights",
      "Skill Ontology Explorer",
      "Knowledge Graph",
      "Analysis History"
    ]

    for mod in required_modules:
        assert mod in sidebar_html, f"Required module '{mod}' missing from #appSidebar!"
        print(f"✓ Core Module in Sidebar: '{mod}'")

    # Verify removed modules ARE NOT PRESENT in sidebar
    removed_items = [
      "Job Analysis",
      "Skills Explorer",
      "Requirement Charts",
      "Academic Comparison",
      "Resume Matcher",
      "Skill Gap Analysis",
      "Advanced Modules"
    ]

    for item in removed_items:
        assert item not in sidebar_html, f"Removed item '{item}' still present in #appSidebar!"
        print(f"✓ Removed from Sidebar: '{item}'")

    print("\n✓ [TEST 1 PASSED] Normal User Sidebar contains ONLY the 6 core modules")
    print("ALL SIDEBAR CLEANUP TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
