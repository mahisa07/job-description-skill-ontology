# Job Description Skill Ontology & Requirement Extraction System

**Team Members:** Mahisa S, Kaviya P  
**Project Path:** `C:\Users\DELL\.gemini\antigravity\scratch\job-skill-ontology`

---

## 📌 Project Overview
This AI/NLP-based web application analyzes unstructured job descriptions (via raw text, PDF, or DOCX upload) and transforms them into a structured, interconnected requirement hierarchy and **Skill Ontology Knowledge Graph**.

### Core Architecture Features
- **Document Processing:** Parses Plain Text, PDF (`PyMuPDF`), and DOCX (`python-docx`).
- **NLP Preprocessing & Extraction:** Extracts Job Role, Experience Years, Education, Certifications, Responsibilities, and Technical & Soft Skills.
- **Requirement Classification:** Tags requirements into **REQUIRED**, **PREFERRED**, and **OPTIONAL** with evidence sentences.
- **Skill Normalization:** Maps skill variations (`ML` $\rightarrow$ `Machine Learning`, `Postgres` $\rightarrow$ `PostgreSQL`, `PowerBI` $\rightarrow$ `Power BI`) to canonical taxonomy names.
- **Skill Categorization:** Maps normalized skills to functional categories (`Programming`, `Database`, `Data Visualization`, `AI & Machine Learning`, `Cloud Computing`, `DevOps & Tools`, `Soft Skills`).
- **Skill Ontology Knowledge Graph:** Renders interactive 2D graph visualization of relations:
  - `Job Role` $\rightarrow$ `requires` $\rightarrow$ `Skill`
  - `Skill` $\rightarrow$ `belongs_to` $\rightarrow$ `Category`
  - `Skill` $\rightarrow$ `is_related_to` $\rightarrow$ `Related Skill`
- **Advanced Modules:**
  - **Resume Skill Parser:** Extracts candidate competencies.
  - **Resume vs JD Matcher:** Calculates system-generated match score (`(Matched + 0.5 * Related) / Total Required * 100`).
  - **Explainable Skill Gap Analysis:** Categorizes skills into Direct Matches, Ontology-Transferred Related Skills, and Critical Missing Skill Gaps.
- **Academic Comparison View:** Demonstrates the contrast between traditional flat keyword extraction and ontology-based knowledge graph representation.

---

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, Pydantic, PyMuPDF (fitz), python-docx.
- **Frontend:** HTML5, CSS3 (Glassmorphism & Custom Design Tokens), JavaScript (ES6+), Chart.js, HTML5 Canvas 2D Force Graph Engine.
- **Data & Ontology:** In-Memory JSON persistence layer, extensible Neo4j abstraction layer.

---

## 🚀 How to Run the Application

### 1. Install Dependencies
```bash
cd C:\Users\DELL\.gemini\antigravity\scratch\job-skill-ontology\backend
pip install -r requirements.txt
```

### 2. Start the FastAPI Web Server
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open the Dashboard in Browser
Open your browser and navigate to:  
👉 **`http://127.0.0.1:8000/`**

Interactive OpenAPI Documentation:  
👉 **`http://127.0.0.1:8000/docs`**

---

## 🧪 Manual Verification & Testing Workflow

1. **Dashboard Overview:**
   - Observe pre-loaded KPI metrics for the demo Data Analyst job description.
   - Click **View Full Graph** or switch tabs using the left navigation sidebar.

2. **Analyze Job Description:**
   - Navigate to **Analyze JD**.
   - Click one of the **Load Sample** buttons (`Data Analyst`, `ML Engineer`, or `Full Stack Dev`) or paste custom text/upload a PDF/DOCX file.
   - Click **Extract Requirements & Build Ontology**.
   - Observe instant redirection and updated analytics.

3. **Explore Skill Normalization & Taxonomy:**
   - Navigate to **Skills Explorer**.
   - Search for `ML`, `SQL`, or `PowerBI` in the search bar.
   - Verify that raw mentions are normalized to canonical skill names and assigned categories and requirement levels.

4. **Interactive Skill Ontology Graph:**
   - Navigate to **Skill Ontology Graph**.
   - Click and drag nodes on the canvas.
   - Use the mouse wheel to zoom in/out or click **Reset Canvas View**.

5. **Resume Matcher & Skill Gap Analysis:**
   - Navigate to **Resume Matcher**.
   - Paste sample candidate text (e.g. `"Experienced in Python, SQL, Excel, and Scikit-Learn"`).
   - Click **Run Resume Matcher**.
   - Switch to **Skill Gap Analysis** to view the explainable skill gap matrix and automated upskilling advice.

6. **Academic Comparison:**
   - Navigate to **Academic Comparison** to view the side-by-side comparison between flat keyword lists and ontology knowledge graphs.
