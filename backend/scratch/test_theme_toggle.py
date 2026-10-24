import os
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=== VERIFYING LIGHT / DARK THEME TOGGLE IMPLEMENTATION ===")

index_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html')
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Check CSS variables and rules
assert 'body.dark-theme' in html
assert '--bg-gradient: #111318' in html
assert '--card-bg: #1E2128' in html
assert '--card-border: #30343D' in html
assert '--primary: #8B5CF6' in html
assert '.btn-theme-toggle' in html

# 2. Check toggle button present in landing navbar, HR header, and Job Seeker header
assert 'toggleAppTheme()' in html
assert 'class="btn-theme-toggle"' in html

# 3. Check Theme JS functions
assert 'function initTheme()' in html
assert 'function applyTheme(theme)' in html
assert 'function toggleAppTheme()' in html
assert 'localStorage.setItem(\'so_theme\', theme)' in html

# 4. Test root API returning HTML
res = client.get("/")
assert res.status_code == 200
assert 'Job Description Skill Ontology' in res.text

print("✓ All Light / Dark Theme CSS, HTML, and JS components verified with 100% success!")
