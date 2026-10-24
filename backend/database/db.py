import os
import json
import datetime
import uuid
from typing import Dict, List, Optional
from backend.models.schemas import JDAnalysisResponse, SkillMention
from backend.services.requirement_extractor import RequirementExtractorService
from backend.services.requirement_classifier import RequirementClassifierService
from backend.services.ontology_service import OntologyService

import shutil

DEFAULT_DB_DIR = os.path.dirname(__file__)
DATA_DIR = os.getenv("DATA_DIR", DEFAULT_DB_DIR)
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create DATA_DIR {DATA_DIR}: {e}")
        DATA_DIR = DEFAULT_DB_DIR

JDS_FILE_PATH = os.path.join(DATA_DIR, "jds_store.json")
NOTIFS_FILE_PATH = os.path.join(DATA_DIR, "notifications.json")

# Seed newly attached persistent volume if needed
if DATA_DIR != DEFAULT_DB_DIR:
    default_jds = os.path.join(DEFAULT_DB_DIR, "jds_store.json")
    default_notifs = os.path.join(DEFAULT_DB_DIR, "notifications.json")
    if not os.path.exists(JDS_FILE_PATH) and os.path.exists(default_jds):
        try:
            shutil.copy2(default_jds, JDS_FILE_PATH)
        except Exception:
            pass
    if not os.path.exists(NOTIFS_FILE_PATH) and os.path.exists(default_notifs):
        try:
            shutil.copy2(default_notifs, NOTIFS_FILE_PATH)
        except Exception:
            pass

class DatabaseStore:
    _instance = None
    records: Dict[str, JDAnalysisResponse] = {}
    notifications: List[dict] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseStore, cls).__new__(cls)
            cls._instance._load_sample_data()
            cls._instance._load_from_disk()
        return cls._instance

    def _save_to_disk(self):
        try:
            records_json = {}
            for k, v in self.records.items():
                if hasattr(v, 'model_dump'):
                    records_json[k] = v.model_dump()
                elif hasattr(v, 'dict'):
                    records_json[k] = v.dict()
                else:
                    records_json[k] = v
            with open(JDS_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(records_json, f, indent=2)

            with open(NOTIFS_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.notifications, f, indent=2)
        except Exception as e:
            print(f"Error saving DB to disk: {e}")

    def _load_from_disk(self):
        try:
            if os.path.exists(JDS_FILE_PATH):
                with open(JDS_FILE_PATH, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    for k, item in raw_data.items():
                        self.records[k] = JDAnalysisResponse(**item)
            if os.path.exists(NOTIFS_FILE_PATH):
                with open(NOTIFS_FILE_PATH, "r", encoding="utf-8") as f:
                    self.notifications = json.load(f)
        except Exception as e:
            print(f"Error loading DB from disk: {e}")

    def _load_sample_data(self):
        """Preload authentic demo job descriptions as per project specifications."""
        sample_jd_1 = (
            "JOB TITLE: Data Analyst\n"
            "COMPANY: TechNova Solutions\n\n"
            "JOB RESPONSIBILITIES:\n"
            "• Collect, clean, and analyze data from multiple sources.\n"
            "• Develop interactive dashboards and reports using Power BI.\n"
            "• Prepare regular business and performance reports.\n"
            "• Work with cross-functional teams to maintain data quality and accuracy.\n\n"
            "REQUIRED QUALIFICATIONS:\n"
            "• Bachelor's degree in Computer Science, Information Technology, Statistics, Mathematics, Data Science, or a related field.\n"
            "• 1–3 years of experience in data analysis or business intelligence.\n"
            "• Strong knowledge of Python and SQL.\n"
            "• Strong communication and problem solving skills.\n\n"
            "PREFERRED QUALIFICATIONS:\n"
            "• Experience with Pandas and NumPy.\n"
            "• Knowledge of Tableau.\n"
            "• Familiarity with cloud platforms such as AWS or Microsoft Azure.\n"
            "• Experience working with large datasets and Machine Learning."
        )

        sample_jd_2 = (
            "JOB TITLE: Machine Learning Engineer\n"
            "COMPANY: AI Dynamics\n\n"
            "REQUIRED QUALIFICATIONS:\n"
            "• 3+ years of experience in Python, PyTorch, TensorFlow, and SQL.\n"
            "• Experience with Docker, Kubernetes, and AWS is required.\n"
            "• Must have strong problem-solving skills and a Master's Degree in Computer Science.\n\n"
            "PREFERRED QUALIFICATIONS:\n"
            "• Knowledge of Natural Language Processing (NLP) and Computer Vision is a plus."
        )

        sample_jd_3 = (
            "JOB TITLE: Full Stack Developer\n"
            "COMPANY: WebTech Inc\n\n"
            "REQUIRED QUALIFICATIONS:\n"
            "• 2-4 years of experience in JavaScript, React, Node.js, and MongoDB.\n"
            "• Strong teamwork, Git version control, and Agile methodology experience required.\n"
            "• Bachelor's degree in Engineering.\n\n"
            "PREFERRED QUALIFICATIONS:\n"
            "• Knowledge of TypeScript, Docker, and PostgreSQL is preferred."
        )

        self._process_and_save("demo-data-analyst", sample_jd_1, override_role="Data Analyst")
        self._process_and_save("demo-ml-engineer", sample_jd_2, override_role="Machine Learning Engineer")
        self._process_and_save("demo-fullstack-dev", sample_jd_3, override_role="Full Stack Developer")

    def _process_and_save(
        self,
        custom_id: str,
        raw_text: str,
        override_role: Optional[str] = None,
        created_by_email: Optional[str] = "",
        company: Optional[str] = "",
        department: Optional[str] = "",
        location: Optional[str] = "",
        company_url: Optional[str] = "",
        recruiter_name: Optional[str] = "",
        recruiter_email: Optional[str] = "",
        recruiter_profile_url: Optional[str] = "",
        job_posting_url: Optional[str] = "",
        employment_type: Optional[str] = "",
        application_deadline: Optional[str] = "",
        publisher_name: Optional[str] = "",
        required_skills_summary: Optional[str] = "",
        experience_level: Optional[str] = "",
        initial_status: Optional[str] = "Analyzed"
    ) -> JDAnalysisResponse:
        role = override_role or RequirementExtractorService.extract_job_role(raw_text)
        exp = experience_level or RequirementExtractorService.extract_experience(raw_text)
        edu = RequirementExtractorService.extract_education(raw_text)
        certs = RequirementExtractorService.extract_certifications(raw_text)
        resp = RequirementExtractorService.extract_responsibilities(raw_text)
        skills = RequirementExtractorService.extract_all_skills(raw_text)

        cats: Dict[str, List[str]] = {}
        req_cnt, pref_cnt, opt_cnt = 0, 0, 0

        for s in skills:
            cats.setdefault(s.category, []).append(s.canonical_name)
            if s.requirement_level == "REQUIRED":
                req_cnt += 1
            elif s.requirement_level == "PREFERRED":
                pref_cnt += 1
            else:
                opt_cnt += 1

        ontology = OntologyService.build_ontology(role, skills)
        trad_vs_onto = OntologyService.generate_academic_comparison(role, skills)

        classified_reqs, cat_counts, priority_counts = RequirementClassifierService.classify_full_jd(
            raw_text=raw_text,
            skills=skills,
            education=edu,
            experience=exp,
            certifications=certs,
            responsibilities=resp
        )

        # Independent Trust & Verification Assessment (fail-safe)
        trust_res = None
        try:
            from backend.services.trust_verification_service import TrustVerificationService
            trust_res = TrustVerificationService.perform_verification(
                raw_text=raw_text,
                job_role=role,
                company=company,
                company_url=company_url,
                recruiter_name=recruiter_name,
                recruiter_email=recruiter_email,
                recruiter_profile_url=recruiter_profile_url,
                job_posting_url=job_posting_url
            )
        except Exception as e:
            print(f"Non-critical trust verification exception: {e}")

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        res = JDAnalysisResponse(
            id=custom_id,
            timestamp=now_str,
            raw_text=raw_text,
            job_role=role,
            experience=exp,
            education=edu,
            certifications=certs,
            responsibilities=resp,
            total_skills_count=len(skills),
            required_skills_count=req_cnt,
            preferred_skills_count=pref_cnt,
            optional_skills_count=opt_cnt,
            skills=skills,
            skill_categories=cats,
            ontology=ontology,
            traditional_vs_ontology=trad_vs_onto,
            classified_requirements=classified_reqs,
            requirement_category_counts=cat_counts,
            priority_counts=priority_counts,
            created_by_email=created_by_email,
            company=company,
            department=department,
            location=location,
            employment_type=employment_type or "",
            application_deadline=application_deadline or "",
            publisher_name=publisher_name or recruiter_name or created_by_email or "",
            published_at=now_str if initial_status == "Published" else "",
            required_skills_summary=required_skills_summary or "",
            status=initial_status or "Analyzed",
            trust_verification=trust_res
        )

        self.records[custom_id] = res
        self._save_to_disk()
        return res

    def save_jd_analysis(
        self,
        raw_text: str,
        created_by_email: Optional[str] = "",
        company: Optional[str] = "",
        department: Optional[str] = "",
        location: Optional[str] = "",
        custom_id: Optional[str] = None,
        override_role: Optional[str] = None,
        company_url: Optional[str] = "",
        recruiter_name: Optional[str] = "",
        recruiter_email: Optional[str] = "",
        recruiter_profile_url: Optional[str] = "",
        job_posting_url: Optional[str] = ""
    ) -> JDAnalysisResponse:
        new_id = custom_id or f"jd-{uuid.uuid4().hex[:8]}"
        return self._process_and_save(
            new_id,
            raw_text,
            override_role=override_role,
            created_by_email=created_by_email,
            company=company,
            department=department,
            location=location,
            company_url=company_url,
            recruiter_name=recruiter_name,
            recruiter_email=recruiter_email,
            recruiter_profile_url=recruiter_profile_url,
            job_posting_url=job_posting_url
        )

    def get_record(self, jd_id: str) -> Optional[JDAnalysisResponse]:
        return self.records.get(jd_id)

    def get_by_id(self, jd_id: str) -> Optional[JDAnalysisResponse]:
        return self.records.get(jd_id)

    def update_trust_verification(self, jd_id: str, trust_result) -> Optional[JDAnalysisResponse]:
        if jd_id in self.records:
            self.records[jd_id].trust_verification = trust_result
            self._save_to_disk()
            return self.records[jd_id]
        return None

    def save_draft(
        self,
        draft_id: Optional[str],
        job_title: str,
        department: str,
        location: str,
        raw_text: str,
        created_by_email: str,
        company: str,
        experience_level: Optional[str] = "",
        employment_type: Optional[str] = "",
        application_deadline: Optional[str] = "",
        required_skills: Optional[str] = "",
        publisher_name: Optional[str] = ""
    ) -> JDAnalysisResponse:
        target_id = draft_id if (draft_id and draft_id in self.records) else f"jd-{uuid.uuid4().hex[:8]}"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        empty_ontology = {"nodes": [], "edges": []}
        res = JDAnalysisResponse(
            id=target_id,
            timestamp=now_str,
            raw_text=raw_text,
            job_role=job_title or "Untitled Role",
            experience=experience_level or "N/A",
            education=[],
            certifications=[],
            responsibilities=[],
            total_skills_count=0,
            required_skills_count=0,
            preferred_skills_count=0,
            optional_skills_count=0,
            skills=[],
            skill_categories={},
            ontology=empty_ontology,
            traditional_vs_ontology={},
            classified_requirements=[],
            requirement_category_counts={},
            priority_counts={},
            created_by_email=created_by_email,
            company=company,
            department=department,
            location=location,
            employment_type=employment_type or "",
            application_deadline=application_deadline or "",
            publisher_name=publisher_name or created_by_email or "",
            required_skills_summary=required_skills or "",
            status="Draft"
        )

        self.records[target_id] = res
        self._save_to_disk()
        return res

    def publish_jd(
        self,
        jd_id: str,
        publisher_email: Optional[str] = "",
        publisher_name: Optional[str] = "",
        company_name: Optional[str] = ""
    ) -> Optional[JDAnalysisResponse]:
        if jd_id not in self.records:
            return None
        rec = self.records[jd_id]
        rec.status = "Published"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rec.published_at = now_str
        if publisher_email:
            rec.created_by_email = publisher_email
        if publisher_name:
            rec.publisher_name = publisher_name
        if company_name:
            rec.company = company_name

        comp_str = rec.company or "Acme Tech Solutions"
        job_title_str = rec.job_role or "Job Position"
        pub_name = rec.publisher_name or rec.created_by_email or "HR Recruiter"

        if not hasattr(self, 'notifications'):
            self.notifications = []

        # Load all registered job seekers
        try:
            from backend.routes.auth import load_users
            users_repo = load_users()
            job_seekers = [u for u in users_repo.values() if u.get("role") == "user"]
        except Exception as e:
            print(f"Error loading users for notification generation: {e}")
            job_seekers = []

        if not job_seekers:
            job_seekers = [{"email": "user@skillontology.com", "name": "Demo Job Seeker"}]

        # Track existing notifications to prevent duplicates on retry
        existing_keys = set()
        for n in self.notifications:
            r_id = (n.get("recipient_id") or n.get("recipient_email") or "").strip().lower()
            p_id = str(n.get("published_job_id") or n.get("job_description_id") or n.get("jd_id") or "")
            if r_id and p_id:
                existing_keys.add((r_id, p_id))

        for seeker in job_seekers:
            seeker_email = (seeker.get("email") or "").strip().lower()
            if not seeker_email:
                continue
            if (seeker_email, str(jd_id)) in existing_keys:
                continue

            notif_id = f"notif-{uuid.uuid4().hex[:8]}"
            seeker_name = seeker.get("name", "Job Seeker")
            notif = {
                "id": notif_id,
                "notification_id": notif_id,
                "recipient_id": seeker_email,
                "recipient_email": seeker_email,
                "recipient_name": seeker_name,
                "published_job_id": jd_id,
                "job_description_id": jd_id,
                "jd_id": jd_id,
                "title": "New Job Posted!",
                "job_title": f"{job_title_str} – {comp_str}",
                "role_name": job_title_str,
                "company": comp_str,
                "publisher_name": pub_name,
                "department": rec.department or "General",
                "message": f"{comp_str} has published a new job: {job_title_str}. View the job description and analyze its required skills.",
                "created_at": now_str,
                "target_role": "job_seeker",
                "is_read": False
            }
            self.notifications.insert(0, notif)
            existing_keys.add((seeker_email, str(jd_id)))

        self._save_to_disk()
        return rec

    def create_and_publish_job(
        self,
        job_title: str,
        company: str,
        raw_text: str,
        created_by_email: str,
        department: Optional[str] = "",
        location: Optional[str] = "",
        experience_level: Optional[str] = "",
        employment_type: Optional[str] = "",
        application_deadline: Optional[str] = "",
        required_skills: Optional[str] = "",
        publisher_name: Optional[str] = "",
        custom_id: Optional[str] = None
    ) -> JDAnalysisResponse:
        target_id = custom_id or f"jd-{uuid.uuid4().hex[:8]}"
        self._process_and_save(
            custom_id=target_id,
            raw_text=raw_text,
            override_role=job_title,
            created_by_email=created_by_email,
            company=company,
            department=department,
            location=location,
            employment_type=employment_type,
            application_deadline=application_deadline,
            publisher_name=publisher_name or created_by_email,
            required_skills_summary=required_skills,
            experience_level=experience_level,
            initial_status="Published"
        )
        return self.publish_jd(
            jd_id=target_id,
            publisher_email=created_by_email,
            publisher_name=publisher_name,
            company_name=company
        )

    def get_published_records(self) -> List[JDAnalysisResponse]:
        return [r for r in self.records.values() if (r.status or "").lower() == "published"]

    def get_notifications(self, user_email: Optional[str] = None) -> List[dict]:
        if not hasattr(self, 'notifications'):
            self.notifications = []
        if user_email:
            clean_email = user_email.strip().lower()
            return [
                n for n in self.notifications
                if (n.get("recipient_id") or n.get("recipient_email") or "").strip().lower() == clean_email
                or (n.get("target_role") == "job_seeker" and not n.get("recipient_id"))
            ]
        return self.notifications

    def mark_notification_read(self, notif_id: str, user_email: Optional[str] = None) -> bool:
        if not hasattr(self, 'notifications'):
            self.notifications = []
        clean_email = user_email.strip().lower() if user_email else None
        for n in self.notifications:
            if n.get("id") == notif_id or n.get("notification_id") == notif_id:
                if clean_email:
                    recip = (n.get("recipient_id") or n.get("recipient_email") or "").strip().lower()
                    if recip and recip != clean_email:
                        return False
                n["is_read"] = True
                self._save_to_disk()
                return True
        return False

    def mark_all_notifications_read(self, user_email: Optional[str] = None) -> bool:
        if not hasattr(self, 'notifications'):
            self.notifications = []
        clean_email = user_email.strip().lower() if user_email else None
        for n in self.notifications:
            if clean_email:
                recip = (n.get("recipient_id") or n.get("recipient_email") or "").strip().lower()
                if recip == clean_email or (not recip and n.get("target_role") == "job_seeker"):
                    n["is_read"] = True
            else:
                n["is_read"] = True
        self._save_to_disk()
        return True

    def delete_jd(self, jd_id: str) -> bool:
        if jd_id in self.records:
            del self.records[jd_id]
            self._save_to_disk()
            return True
        return False

    def get_jd_analysis(self, jd_id: str) -> Optional[JDAnalysisResponse]:
        return self.records.get(jd_id)

    def get_all_records(self) -> List[JDAnalysisResponse]:
        return list(self.records.values())

    def get_user_records(self, user_email: str) -> List[JDAnalysisResponse]:
        if not user_email:
            return list(self.records.values())
        return [r for r in self.records.values() if r.created_by_email == user_email]

db_store = DatabaseStore()
