import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests():
    print("==================================================")
    print("RUNNING WHITE & PURPLE THEME REFINEMENT VERIFICATION")
    print("==================================================")

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "index.html"))
    assert os.path.exists(html_path), "index.html file not found!"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Verify CSS variables for White + Purple theme
    assert "--primary: #7c3aed" in content or "--primary: #6d28d9" in content, "Primary purple color missing in CSS root"
    assert "--card-bg: #ffffff" in content, "White card background missing in CSS root"
    assert "--card-border: #e9e5f5" in content, "Lavender card border missing in CSS root"
    assert "--text-main: #1e1b4b" in content, "Dark purple/navy main text color missing in CSS root"

    print("✓ [TEST 1 PASSED] Root CSS variables configured for White + Light Lavender + Purple theme")

    # 2. Verify Card and Body Styles
    assert "background: var(--bg-gradient);" in content, "Body gradient missing"
    assert "box-shadow: 0 4px 16px" in content or "box-shadow: 0 4px 14px" in content, "Soft card shadows present"
    print("✓ [TEST 2 PASSED] White cards, lavender borders, and soft shadows verified")

    # 3. Verify Sidebar and Buttons
    assert ".sidebar {" in content, "Sidebar CSS rules present"
    assert "background: #ffffff;" in content, "White sidebar background present"
    assert "btn-primary" in content and "btn-secondary" in content, "Button styling rules present"
    print("✓ [TEST 3 PASSED] Clean White & Purple sidebar and button rules verified")

    # 4. Verify Knowledge Graph Canvas Styling
    assert "background: #fcfbfe;" in content or "background: #f8f7fc;" in content, "Light graph canvas background present"
    assert "ctx.fillStyle = '#1e1b4b';" in content, "High contrast node text fill color verified"
    print("✓ [TEST 4 PASSED] Knowledge Graph canvas styling updated for light theme")

    print("\nALL WHITE & PURPLE THEME REFINEMENT TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
