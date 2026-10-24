import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests():
    print("==================================================")
    print("RUNNING BARBIE PINK + BLEACH WHITE THEME VERIFICATION")
    print("==================================================")

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "index.html"))
    assert os.path.exists(html_path), "index.html file not found!"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Verify CSS variables for Barbie Pink + Bleach White theme
    assert "--primary: #E0218A" in content, "Primary Barbie Pink color (#E0218A) missing in CSS root"
    assert "--card-bg: #FFFFFF" in content, "White card background missing in CSS root"
    assert "--card-border: #F3E2ED" in content, "Light blush divider border missing in CSS root"
    assert "--text-main: #2B2B2B" in content, "Dark charcoal main text color (#2B2B2B) missing in CSS root"
    assert "--bg-gradient: #FFFDFE" in content, "Bleach white background (#FFFDFE) missing in CSS root"

    print("✓ [TEST 1 PASSED] Root CSS variables configured for Barbie Pink (#E0218A) + Bleach White (#FFFDFE)")

    # 2. Verify Flat Design & Absence of Gradients
    assert "linear-gradient(135deg, var(--primary)" not in content, "Gradient removed from brand logo / primary buttons for flat Barbie Pink design"
    assert "backdrop-filter: blur" not in content, "Glassmorphism removed for clean software dashboard design"
    print("✓ [TEST 2 PASSED] Flat software dashboard design without gradients or neon glow verified")

    # 3. Verify Sidebar and Buttons
    assert ".sidebar {" in content, "Sidebar CSS rules present"
    assert "background: #FFFDFE;" in content, "Bleach white sidebar background present"
    assert "btn-primary" in content and "btn-secondary" in content, "Button styling rules present"
    print("✓ [TEST 3 PASSED] Clean Bleach White & Barbie Pink sidebar and button rules verified")

    # 4. Verify Knowledge Graph Canvas Styling
    assert "background: #FFFDFE;" in content, "Bleach white graph canvas background present"
    assert "ctx.fillStyle = '#2B2B2B';" in content, "High contrast dark charcoal node text fill color verified"
    assert "ctx.fillStyle = n.type === 'role' ? '#E0218A'" in content, "Barbie Pink node styling verified"
    print("✓ [TEST 4 PASSED] Knowledge Graph canvas styling updated for Barbie Pink theme")

    print("\nALL BARBIE PINK + BLEACH WHITE THEME TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
