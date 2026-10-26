# Job Description Skill Ontology & Requirement Extraction System

**Team Members:** Mahisa S, Kaviya P

## 🚀 Live Demo

**Deployed Application:** https://job-description-skill-ontology.onrender.com/

## 📌 Project Overview

The Job Description Skill Ontology & Requirement Extraction System is an NLP-based web application that analyzes job descriptions and extracts structured job requirements and skills.

It helps recruiters organize job requirements and enables job seekers to understand required skills, compare resumes with job descriptions, identify skill gaps and assess potential risks in job postings.

## 🎯 Objectives

- Extract meaningful requirements from job descriptions using Natural Language Processing (NLP).
- Classify skills and requirements into appropriate categories.
- Organize skills through an ontology and knowledge graph.
- Compare candidate skills with job requirements.
- Identify matching and missing skills.
- Help users assess suspicious job postings through integrated Trust & Verification checks.

## ✨ Key Features

### 1. Job Description Analysis
- Analyze job descriptions and extract relevant requirements.
- Identify skills, qualifications, experience and responsibilities.
- Categorize requirements according to their importance.

### 2. NLP-Based Requirement Extraction
- Process unstructured job-description text.
- Identify relevant skills and job requirements.
- Support structured analysis of extracted information.

### 3. Skill Ontology and Knowledge Graph
- Organize skills and their relationships.
- Connect skills with relevant categories and job roles.
- Present relationships between skills for easier understanding.

### 4. Resume Matching
- Compare candidate skills against job requirements.
- Identify matching skills.
- Help candidates understand their suitability for a job.

### 5. Skill Gap Analysis
- Identify skills that a candidate already possesses.
- Highlight missing skills required by a job.
- Help candidates identify areas for improvement.

### 6. Integrated Trust & Verification
- Assess available company and recruiter information.
- Apply company-detection checks and suspicious-posting heuristics.
- Display risk indicators to help users evaluate job postings carefully.

*Risk indicators support awareness and do not guarantee that a job posting or recruiter is genuine or fraudulent.*

### 7. HR and Job-Seeker Workflows
- Allow HR users to post job descriptions.
- Notify job seekers when HR users post new opportunities.
- Provide job-related analysis and skill insights.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI, Uvicorn |
| Text Processing | Natural Language Processing (NLP) |
| Skill Organization | Ontology and knowledge graph concepts |
| Data Storage | JSON-based storage |
| Deployment | Render |
| Version Control | Git and GitHub |

## 🏗️ System Workflow

1. The user submits a job description.
2. The system processes the text using NLP techniques.
3. Skills and job requirements are extracted.
4. Requirements are organized into structured categories.
5. Skills and their relationships are represented using the ontology.
6. Candidate skills can be compared with job requirements.
7. Trust & Verification checks assess available information for potential warning signs.
8. The results are displayed through the web interface.

## 💻 Running Locally

### Prerequisites
- Python
- Git
- A web browser

### Clone the Repository

```bash
git clone https://github.com/mahisa07/job-description-skill-ontology.git
cd job-description-skill-ontology
```

### Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

### Run the Backend

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

API documentation, when enabled:

http://127.0.0.1:8000/docs

## 🔮 Future Enhancements

- Improve NLP-based skill extraction.
- Expand the skill ontology with more job roles and skill relationships.
- Improve resume matching and skill-gap recommendations.
- Integrate additional trusted sources for job-posting verification.
- Introduce a dedicated database for more scalable data storage.
