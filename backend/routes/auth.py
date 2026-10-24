import os
import json
import re
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

import shutil

DEFAULT_AUTH_DIR = os.path.join(os.path.dirname(__file__), "..", "database")
DATA_DIR = os.getenv("DATA_DIR", DEFAULT_AUTH_DIR)
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create DATA_DIR {DATA_DIR}: {e}")
        DATA_DIR = DEFAULT_AUTH_DIR

USERS_FILE_PATH = os.path.join(DATA_DIR, "users.json")

# Seed newly attached persistent volume if needed
if DATA_DIR != DEFAULT_AUTH_DIR:
    default_users = os.path.join(DEFAULT_AUTH_DIR, "users.json")
    if not os.path.exists(USERS_FILE_PATH) and os.path.exists(default_users):
        try:
            shutil.copy2(default_users, USERS_FILE_PATH)
        except Exception:
            pass

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

SEED_USERS: Dict[str, Dict[str, str]] = {
    "admin@skillontology.com": {
        "name": "Admin User",
        "email": "admin@skillontology.com",
        "password_hash": hash_password("Admin@123"),
        "role": "admin",
        "company_name": "SkillOntology Admin",
        "phone": "+1 (555) 019-2831",
        "job_title": "System Administrator",
        "department": "Platform Operations"
    },
    "user@skillontology.com": {
        "name": "Demo Job Seeker",
        "email": "user@skillontology.com",
        "password_hash": hash_password("User@123"),
        "role": "user",
        "company_name": None,
        "phone": "+1 (555) 432-8765",
        "job_title": "Data Analyst Candidate",
        "department": "Analytics"
    },
    "hr@skillontology.com": {
        "name": "Sarah Jenkins",
        "email": "hr@skillontology.com",
        "password_hash": hash_password("Hr@123"),
        "role": "hr",
        "company_name": "Acme Tech Solutions",
        "phone": "+1 (555) 234-5678",
        "job_title": "HR Manager",
        "department": "Talent Acquisition & HR"
    },
    "recruiter@skillontology.com": {
        "name": "Alex Rivera",
        "email": "recruiter@skillontology.com",
        "password_hash": hash_password("Recruiter@123"),
        "role": "recruiter",
        "company_name": "Global Talent Recruitment",
        "phone": "+1 (555) 876-5432",
        "job_title": "Senior Technical Recruiter",
        "department": "Recruitment Services"
    }
}

USER_REPOSITORY: Dict[str, Dict[str, str]] = {}

def load_users() -> Dict[str, Dict[str, str]]:
    global USER_REPOSITORY
    if not USER_REPOSITORY:
        USER_REPOSITORY = dict(SEED_USERS)
        if os.path.exists(USERS_FILE_PATH):
            try:
                with open(USERS_FILE_PATH, "r", encoding="utf-8") as f:
                    file_users = json.load(f)
                    for email, record in file_users.items():
                        email_clean = email.strip().lower()
                        USER_REPOSITORY[email_clean] = record
            except Exception as e:
                print(f"Error loading users.json: {e}")
    return USER_REPOSITORY

def save_users():
    try:
        os.makedirs(os.path.dirname(USERS_FILE_PATH), exist_ok=True)
        with open(USERS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(USER_REPOSITORY, f, indent=2)
    except Exception as e:
        print(f"Error saving users.json: {e}")

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: Optional[bool] = False
    portal_type: Optional[str] = "user"

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    confirm_password: str
    role: Optional[str] = "user"
    company_name: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    old_email: str
    full_name: str
    email: str
    phone: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    avatar_b64: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    email: str

@router.post("/login")
async def login(req: LoginRequest):
    if not req.email or not req.email.strip():
        raise HTTPException(status_code=400, detail="Please enter your email.")
    if not req.password:
        raise HTTPException(status_code=400, detail="Please enter your password.")

    email_clean = req.email.strip().lower()
    repo = load_users()
    user = repo.get(email_clean)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if user["password_hash"] != hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    safe_slug = re.sub(r'[^a-zA-Z0-9]', '', email_clean.split('@')[0])
    role = user.get("role", "user")
    token = f"auth-token-{safe_slug}-{role}-session"

    return {
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": {
            "name": user.get("name", "User"),
            "email": user.get("email", email_clean),
            "role": role,
            "company_name": user.get("company_name"),
            "phone": user.get("phone", "+1 (555) 234-5678"),
            "job_title": user.get("job_title", "HR Manager" if role in ["hr", "recruiter"] else "Candidate"),
            "department": user.get("department", "Talent Acquisition & HR" if role in ["hr", "recruiter"] else "Analytics"),
            "avatar_b64": user.get("avatar_b64")
        }
    }

@router.post("/register")
async def register(req: RegisterRequest):
    if not req.full_name or not req.full_name.strip():
        raise HTTPException(status_code=400, detail="Please enter your full name.")

    email_clean = req.email.strip().lower()
    if not email_clean or not re.match(r"[^@]+@[^@]+\.[^@]+", email_clean):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    if not req.password:
        raise HTTPException(status_code=400, detail="Please enter a password.")

    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    role = (req.role or "user").strip().lower()
    if role not in ["user", "hr", "recruiter", "admin"]:
        role = "user"

    if role in ["hr", "recruiter"] and (not req.company_name or not req.company_name.strip()):
        raise HTTPException(status_code=400, detail="Company Name is required for HR / Recruiter registration.")

    repo = load_users()
    if email_clean in repo:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    new_user = {
        "name": req.full_name.strip(),
        "email": email_clean,
        "password_hash": hash_password(req.password),
        "role": role,
        "company_name": req.company_name.strip() if req.company_name else None,
        "phone": "+1 (555) 234-5678",
        "job_title": "HR Manager" if role == "hr" else ("Recruiter" if role == "recruiter" else "Candidate"),
        "department": "Talent Acquisition & HR" if role in ["hr", "recruiter"] else "Analytics"
    }

    repo[email_clean] = new_user
    save_users()

    return {
        "success": True,
        "message": f"Account created successfully as {role.upper()}. Please sign in.",
        "user": {
            "name": new_user["name"],
            "email": new_user["email"],
            "role": new_user["role"],
            "company_name": new_user["company_name"],
            "phone": new_user["phone"],
            "job_title": new_user["job_title"],
            "department": new_user["department"]
        }
    }

@router.post("/profile")
async def update_profile(req: ProfileUpdateRequest):
    if not req.full_name or not req.full_name.strip():
        raise HTTPException(status_code=400, detail="Full Name is required.")

    email_clean = req.email.strip().lower()
    if not email_clean or not re.match(r"[^@]+@[^@]+\.[^@]+", email_clean):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    old_email_clean = (req.old_email or "").strip().lower()
    repo = load_users()
    user = repo.get(old_email_clean) or repo.get(email_clean)

    if not user:
        user = {
            "name": req.full_name.strip(),
            "email": email_clean,
            "role": "hr",
            "company_name": req.company_name
        }

    if old_email_clean and email_clean != old_email_clean and email_clean in repo:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    user["name"] = req.full_name.strip()
    user["email"] = email_clean
    user["phone"] = req.phone.strip() if req.phone else ""
    user["company_name"] = req.company_name.strip() if req.company_name else ""
    user["job_title"] = req.job_title.strip() if req.job_title else ""
    user["department"] = req.department.strip() if req.department else ""
    if req.avatar_b64 is not None:
        user["avatar_b64"] = req.avatar_b64

    if old_email_clean in repo and old_email_clean != email_clean:
        del repo[old_email_clean]
    repo[email_clean] = user
    save_users()

    return {
        "success": True,
        "message": "Profile updated successfully.",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "hr"),
            "company_name": user.get("company_name"),
            "phone": user.get("phone", ""),
            "job_title": user.get("job_title", ""),
            "department": user.get("department", ""),
            "avatar_b64": user.get("avatar_b64")
        }
    }

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    if not req.email or not req.email.strip():
        raise HTTPException(status_code=400, detail="Please enter your email.")
    return {
        "success": True,
        "message": "Password reset instructions have been structured for your account."
    }
