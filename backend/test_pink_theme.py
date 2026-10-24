import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests():
    print("==================================================")
    print("RUNNING WHITE & SOFT PINK THEME REFINEMENT VERIFICATION")
    print("==================================================")

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "index.html"))
    assert os.path.exists(html_path), "index.html file not found!"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Verify CSS variables for White + Soft Pink theme
    assert "--primary: #e11d48" in content, "Primary soft deep pink color missing in CSS root"
    assert "--card-bg: #ffffff" in content, "White card background missing in CSS root"
    assert "--card-border: #f3e2e5" in content, "Light blush border missing in CSS root"
    assert "--text-main: #1f2937" in content, "Dark charcoal main text color missing in CSS root"

    print("✓ [TEST 1 PASSED] Root CSS variables configured for White + Soft Pink + Light Blush theme")

    # 2. Verify Card and Body Styles
    assert "background: var(--bg-gradient);" in content, "Body gradient missing"
    assert "box-shadow: 0 4px 16px rgba(225, 29, 72, 0.03)" in content or "box-shadow: 0 4px 14px" in content, "Soft pink shadows present"
    print("✓ [TEST 2 PASSED] White cards, blush borders, and soft pink shadows verified")

    # 3. Verify Sidebar and Buttons
    assert ".sidebar {" in content, "Sidebar CSS rules present"
    assert "background: #ffffff;" in content, "White sidebar background present"
    assert "btn-primary" in content and "btn-secondary" in content, "Button styling rules present"
    print("✓ [TEST 3 PASSED] Clean White & Pink sidebar and button rules verified")

    # 4. Verify Knowledge Graph Canvas Styling
    assert "background: #fdf8f9;" in content, "Light blush graph canvas background present"
    assert "ctx.fillStyle = '#1f2937';" in content, "High contrast dark charcoal node text fill color verified"
    print("✓ [TEST 4 PASSED] Knowledge Graph canvas styling updated for light blush theme")

    print("\nALL WHITE & SOFT PINK THEME REFINEMENT TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
