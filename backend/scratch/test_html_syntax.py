import re
import os

index_path = r"C:\Users\DELL\.gemini\antigravity\scratch\job-skill-ontology\backend\static\index.html"

with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Total size: {len(content)} chars")

# Extract script blocks
scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
print(f"Found {len(scripts)} inline script blocks.")

for idx, script in enumerate(scripts):
    try:
        compile(script, f'<script_{idx}>', 'exec')
        print(f"Script block {idx} compiled as Python (syntax check approximation)")
    except Exception as e:
        print(f"Script block {idx} compilation error: {e}")

# Check for unclosed divs or html tags
open_divs = len(re.findall(r'<div', content, re.IGNORECASE))
close_divs = len(re.findall(r'</div>', content, re.IGNORECASE))
print(f"Open <div>: {open_divs}, Close </div>: {close_divs}")

open_section = len(re.findall(r'<section', content, re.IGNORECASE))
close_section = len(re.findall(r'</section>', content, re.IGNORECASE))
print(f"Open <section>: {open_section}, Close </section>: {close_section}")

open_button = len(re.findall(r'<button', content, re.IGNORECASE))
close_button = len(re.findall(r'</button>', content, re.IGNORECASE))
print(f"Open <button>: {open_button}, Close </button>: {close_button}")
