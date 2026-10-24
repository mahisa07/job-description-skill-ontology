import re

index_path = r"C:\Users\DELL\.gemini\antigravity\scratch\job-skill-ontology\backend\static\index.html"

with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the main <script> tag content
m = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if m:
    script_text = m.group(1)
    print(f"Extracted script block: {len(script_text)} characters.")
    
    # Save to a temporary js file for node validation
    js_out = r"C:\Users\DELL\.gemini\antigravity\scratch\job-skill-ontology\backend\scratch\temp_script.js"
    with open(js_out, 'w', encoding='utf-8') as f_out:
        f_out.write(script_text)
    print("Saved script to temp_script.js")
else:
    print("No <script> tag found!")
