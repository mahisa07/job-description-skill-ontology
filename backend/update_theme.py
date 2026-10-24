import re
import os

filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "index.html"))

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace CSS Variables
old_vars = """    :root {
      --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
      --card-bg: rgba(30, 41, 59, 0.7);
      --card-border: rgba(255, 255, 255, 0.1);
      --card-hover-border: rgba(99, 102, 241, 0.4);
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --accent-cyan: #06b6d4;
      --accent-purple: #8b5cf6;
      --accent-emerald: #10b981;
      --accent-rose: #f43f5e;
      --accent-amber: #f59e0b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-subtle: #64748b;
      --sidebar-width: 260px;
    }"""

new_vars = """    :root {
      --bg-gradient: linear-gradient(135deg, #fcfbfe 0%, #f3edf8 50%, #f8f6fc 100%);
      --card-bg: #ffffff;
      --card-border: #e9e5f5;
      --card-hover-border: #c084fc;
      --primary: #7c3aed;
      --primary-hover: #6d28d9;
      --accent-purple: #8b5cf6;
      --accent-cyan: #0284c7;
      --accent-emerald: #059669;
      --accent-rose: #e11d48;
      --accent-amber: #d97706;
      --text-main: #1e1b4b;
      --text-muted: #475569;
      --text-subtle: #64748b;
      --sidebar-width: 260px;
    }"""

content = content.replace(old_vars, new_vars)

# Replace dark inline styles in HTML markup
replacements = [
    ('background: rgba(15, 23, 42, 0.85);', 'background: rgba(255, 255, 255, 0.92);'),
    ('background: rgba(30, 41, 59, 0.7);', 'background: #ffffff; box-shadow: 0 4px 16px rgba(109, 40, 217, 0.04);'),
    ('background: rgba(30, 41, 59, 0.6);', 'background: #ffffff; box-shadow: 0 4px 16px rgba(109, 40, 217, 0.04);'),
    ('background: rgba(30, 41, 59, 0.8);', 'background: #ffffff; box-shadow: 0 4px 16px rgba(109, 40, 217, 0.04);'),
    ('background: rgba(30, 41, 59, 0.85);', 'background: #ffffff; box-shadow: 0 15px 40px rgba(109, 40, 217, 0.08);'),
    ('background: rgba(15, 23, 42, 0.7);', 'background: #f8f7fc; border: 1px solid var(--card-border);'),
    ('background: rgba(15, 23, 42, 0.6);', 'background: #f8f7fc; border: 1px solid var(--card-border);'),
    ('background: rgba(15, 23, 42, 0.4);', 'background: #f8f7fc; border: 1px solid var(--card-border);'),
    ('background: rgba(15, 23, 42, 0.8);', 'background: #ffffff; border: 1px solid var(--card-border);'),
    ('background: rgba(15, 23, 42, 0.95);', 'background: #fcfbfe;'),
    ('background: rgba(15, 23, 42, 0.5);', 'background: #f5f3ff;'),
    ('background: rgba(255, 255, 255, 0.08);', 'background: #f5f3ff; color: var(--primary); border: 1px solid #ddd6fe;'),
    ('background: rgba(255, 255, 255, 0.05);', 'background: #f5f3ff; border: 1px solid #ddd6fe; color: var(--text-main);'),
    ('background: rgba(255, 255, 255, 0.03);', 'background: #f8f7fc; border: 1px solid #ddd6fe;'),
    ('background: rgba(255, 255, 255, 0.02);', 'background: #f8f7fc; border: 1px solid var(--card-border);'),
    ('background: rgba(99, 102, 241, 0.15);', 'background: #f3e8ff; color: var(--primary);'),
    ('background: rgba(99, 102, 241, 0.1);', 'background: #f5f3ff; border-color: #ddd6fe;'),
    ('background: rgba(99, 102, 241, 0.25);', 'background: #f3e8ff; border-color: #c084fc;'),
    ('background: rgba(99, 102, 241, 0.2);', 'background: #f3e8ff; color: var(--primary);'),
    ('background: rgba(6, 182, 212, 0.15);', 'background: #e0f2fe; color: #0284c7;'),
    ('background: rgba(139, 92, 246, 0.15);', 'background: #f3e8ff; color: #7c3aed;'),
    ('background: rgba(244, 63, 94, 0.15);', 'background: #ffe4e6; color: #be123c;'),
    ('background: rgba(245, 158, 11, 0.15);', 'background: #fef3c7; color: #b45309;'),
    ('background: rgba(16, 185, 129, 0.15);', 'background: #d1fae5; color: #047857;'),
    ('background: rgba(59, 130, 246, 0.15);', 'background: #dbeafe; color: #1d4ed8;'),
    ('color: #fff', 'color: #1e1b4b'),
    ('color: #ffffff', 'color: #1e1b4b'),
    ('color: var(--text-main)', 'color: #1e1b4b'),
    ('background:linear-gradient(to right, #fff, var(--text-muted));', 'color: #1e1b4b;'),
    ('background: linear-gradient(to right, #fff, var(--text-muted));', 'color: #1e1b4b;'),
    ('background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, var(--accent-cyan) 100%);', 'color: #1e1b4b;'),
]

# Let's execute clean regex-assisted replacements in index.html
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Root variables updated.")
