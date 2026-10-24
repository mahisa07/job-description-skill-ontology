import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests():
    print("==================================================")
    print("RUNNING WHITE + PROFESSIONAL PURPLE THEME VERIFICATION")
    print("==================================================")

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "index.html"))
    assert os.path.exists(html_path), "index.html file not found!"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Verify CSS variables for Professional Purple theme
    assert "--primary: #6D28D9" in content, "Primary Professional Purple color (#6D28D9) missing in CSS root"
    assert "--card-bg: #FFFFFF" in content, "White card background missing in CSS root"
    assert "--card-border: #E9E5F5" in content, "Light lavender divider border missing in CSS root"
    assert "--text-main: #1F2937" in content, "Dark charcoal main text color (#1F2937) missing in CSS root"
    assert "--bg-gradient: #FCFBFF" in content, "Bleach white background (#FCFBFF) missing in CSS root"

    print("✓ [TEST 1 PASSED] Root CSS variables configured for Professional Purple (#6D28D9) + Bleach White (#FCFBFF)")

    # 2. Verify Absence of Barbie Pink
    assert "#E0218A" not in content, "Barbie pink (#E0218A) completely removed"
    assert "#F48FB1" not in content, "Barbie soft pink (#F48FB1) completely removed"
    print("✓ [TEST 2 PASSED] Pink accents completely removed and replaced with purple family")

    # 3. Verify Hero Title & Heading Size Refinements
    assert "Understand Job Requirements. Discover Skills. Explore Their Relationships." in content, "Updated Hero title text present"
    assert "Build Better Career Matches" not in content, "Unrelated career matching phrasing removed from hero section"
    assert "font-size: 2.1rem;" in content, "Hero title font size reduced to 2.1rem for professional application feel"
    print("✓ [TEST 3 PASSED] Hero section title & compact font size verified")

    # 4. Verify Sidebar and Buttons
    assert ".sidebar {" in content, "Sidebar CSS rules present"
    assert "background: #FCFBFF;" in content, "White/off-white sidebar background present"
    assert "background: #6D28D9;" in content or "background: var(--primary);" in content, "Primary purple button styling rules present"
    print("✓ [TEST 4 PASSED] Clean Bleach White & Professional Purple sidebar and button rules verified")

    # 5. Verify Knowledge Graph Canvas Styling
    assert "background: #FCFBFF;" in content, "Bleach white graph canvas background present"
    assert "ctx.fillStyle = '#1F2937';" in content, "High contrast dark charcoal node text fill color verified"
    assert "ctx.fillStyle = n.type === 'role' ? '#6D28D9'" in content, "Professional Purple role node styling verified"
    print("✓ [TEST 5 PASSED] Knowledge Graph canvas styling updated for Professional Purple theme")

    print("\nALL WHITE + PROFESSIONAL PURPLE THEME TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_tests()
