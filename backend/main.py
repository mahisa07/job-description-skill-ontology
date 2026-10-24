import os
import sys

# Ensure project root and backend dir are in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.routes.jd import router as jd_router
from backend.routes.skills import router as skills_router
from backend.routes.ontology import router as ontology_router
from backend.routes.resume import router as resume_router
from backend.routes.matching import router as matching_router
from backend.routes.auth import router as auth_router

app = FastAPI(
    title="Job Description Skill Ontology & Requirement Extraction System",
    description="AI/NLP-driven Job Requirement Extractor, Canonical Skill Normalizer, and Knowledge Graph Platform",
    version="1.0.0"
)

# Configure CORS with deployment environment variable support
cors_origins_env = os.getenv("CORS_ORIGINS", "*").strip()
if cors_origins_env == "*":
    origins = ["*"]
else:
    origins = [orig.strip() for orig in cors_origins_env.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(jd_router)
app.include_router(skills_router)
app.include_router(ontology_router)
app.include_router(resume_router)
app.include_router(matching_router)

# Health check endpoint for Render health probes
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Job Description Skill Ontology & Requirement Extraction System",
        "version": "1.0.0"
    }

# Static directory setup
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({
        "system": "Job Description Skill Ontology & Requirement Extraction System API",
        "status": "Online",
        "api_docs": "/docs",
        "available_endpoints": [
            "/health",
            "/api/jobs/analyze",
            "/api/jobs/history",
            "/api/jobs/{id}",
            "/api/skills/search",
            "/api/skills/categories",
            "/api/ontology/{jd_id}",
            "/api/ontology/{jd_id}/academic-comparison",
            "/api/matching/analyze"
        ]
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
