import re
from typing import Tuple, Dict

class SkillNormalizerService:
    # Comprehensive Canonical Mapping Dictionary
    CANONICAL_MAP: Dict[str, str] = {
        # Programming
        "py": "Python",
        "python": "Python",
        "python3": "Python",
        "js": "JavaScript",
        "javascript": "JavaScript",
        "java script": "JavaScript",
        "ts": "TypeScript",
        "typescript": "TypeScript",
        "cpp": "C++",
        "c++": "C++",
        "c#": "C#",
        "csharp": "C#",
        "java": "Java",
        "golang": "Go",
        "go": "Go",
        "r": "R",
        "ruby": "Ruby",
        "php": "PHP",
        "scala": "Scala",

        # Database
        "sql": "SQL",
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "postgre": "PostgreSQL",
        "mysql": "MySQL",
        "mongodb": "MongoDB",
        "mongo": "MongoDB",
        "oracle": "Oracle DB",
        "redis": "Redis",
        "sqlite": "SQLite",
        "neo4j": "Neo4j",
        "dynamodb": "DynamoDB",
        "cassandra": "Cassandra",

        # Analytics & Visualization
        "excel": "Excel",
        "ms excel": "Excel",
        "microsoft excel": "Excel",
        "powerbi": "Power BI",
        "power-bi": "Power BI",
        "power bi": "Power BI",
        "tableau": "Tableau",
        "qlik": "QlikView",
        "looker": "Looker",
        "matplotlib": "Matplotlib",
        "seaborn": "Seaborn",
        "plotly": "Plotly",

        # AI / ML / Data Science
        "ml": "Machine Learning",
        "machine learning": "Machine Learning",
        "machine-learning": "Machine Learning",
        "dl": "Deep Learning",
        "deep learning": "Deep Learning",
        "nlp": "Natural Language Processing",
        "natural language processing": "Natural Language Processing",
        "cv": "Computer Vision",
        "computer vision": "Computer Vision",
        "tf": "TensorFlow",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "keras": "Keras",
        "scikit-learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "scipy": "SciPy",

        # Cloud & DevOps
        "aws": "AWS",
        "amazon web services": "AWS",
        "gcp": "Google Cloud",
        "google cloud": "Google Cloud",
        "azure": "Microsoft Azure",
        "microsoft azure": "Microsoft Azure",
        "docker": "Docker",
        "k8s": "Kubernetes",
        "kubernetes": "Kubernetes",
        "ci/cd": "CI/CD",
        "jenkins": "Jenkins",
        "git": "Git",
        "github": "GitHub",
        "terraform": "Terraform",
        "ansible": "Ansible",

        # Web Development
        "react": "React",
        "reactjs": "React",
        "react.js": "React",
        "angular": "Angular",
        "angularjs": "Angular",
        "vue": "Vue.js",
        "vuejs": "Vue.js",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "express": "Express.js",
        "expressjs": "Express.js",
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "html": "HTML5",
        "html5": "HTML5",
        "css": "CSS3",
        "css3": "CSS3",
        "tailwind": "Tailwind CSS",
        "bootstrap": "Bootstrap",

        # Soft Skills
        "communication": "Communication",
        "communication skills": "Communication",
        "leadership": "Leadership",
        "teamwork": "Teamwork",
        "collaboration": "Teamwork",
        "problem solving": "Problem Solving",
        "problem-solving": "Problem Solving",
        "analytical skills": "Analytical Thinking",
        "critical thinking": "Critical Thinking",
        "time management": "Time Management",
        "agile": "Agile / Scrum"
    }

    # Taxonomy Map (Skill -> Category)
    CATEGORY_MAP: Dict[str, str] = {
        "Python": "Programming",
        "JavaScript": "Programming",
        "TypeScript": "Programming",
        "C++": "Programming",
        "C#": "Programming",
        "Java": "Programming",
        "Go": "Programming",
        "R": "Programming",
        "Ruby": "Programming",
        "PHP": "Programming",
        "Scala": "Programming",

        "SQL": "Database",
        "PostgreSQL": "Database",
        "MySQL": "Database",
        "MongoDB": "Database",
        "Oracle DB": "Database",
        "Redis": "Database",
        "SQLite": "Database",
        "Neo4j": "Database",
        "DynamoDB": "Database",
        "Cassandra": "Database",

        "Excel": "Data Analysis",
        "Pandas": "Data Analysis",
        "NumPy": "Data Analysis",
        "SciPy": "Data Analysis",
        "Analytical Thinking": "Data Analysis",

        "Power BI": "Data Visualization",
        "Tableau": "Data Visualization",
        "QlikView": "Data Visualization",
        "Looker": "Data Visualization",
        "Matplotlib": "Data Visualization",
        "Seaborn": "Data Visualization",
        "Plotly": "Data Visualization",

        "Machine Learning": "AI & Machine Learning",
        "Deep Learning": "AI & Machine Learning",
        "Natural Language Processing": "AI & Machine Learning",
        "Computer Vision": "AI & Machine Learning",
        "TensorFlow": "AI & Machine Learning",
        "PyTorch": "AI & Machine Learning",
        "Keras": "AI & Machine Learning",
        "Scikit-Learn": "AI & Machine Learning",

        "AWS": "Cloud Computing",
        "Google Cloud": "Cloud Computing",
        "Microsoft Azure": "Cloud Computing",

        "Docker": "DevOps & Tools",
        "Kubernetes": "DevOps & Tools",
        "CI/CD": "DevOps & Tools",
        "Jenkins": "DevOps & Tools",
        "Git": "DevOps & Tools",
        "GitHub": "DevOps & Tools",
        "Terraform": "DevOps & Tools",
        "Ansible": "DevOps & Tools",

        "React": "Web Development",
        "Angular": "Web Development",
        "Vue.js": "Web Development",
        "Node.js": "Web Development",
        "Express.js": "Web Development",
        "FastAPI": "Web Development",
        "Django": "Web Development",
        "Flask": "Web Development",
        "HTML5": "Web Development",
        "CSS3": "Web Development",
        "Tailwind CSS": "Web Development",
        "Bootstrap": "Web Development",

        "Communication": "Soft Skills",
        "Leadership": "Soft Skills",
        "Teamwork": "Soft Skills",
        "Problem Solving": "Soft Skills",
        "Critical Thinking": "Soft Skills",
        "Time Management": "Soft Skills",
        "Agile / Scrum": "Soft Skills"
    }

    # Skill Relationships (Skill -> Related Skills list)
    RELATED_SKILLS_MAP: Dict[str, list] = {
        "Python": ["Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "FastAPI"],
        "SQL": ["PostgreSQL", "MySQL", "Database", "Excel"],
        "Excel": ["Power BI", "SQL", "Tableau", "Analytical Thinking"],
        "Power BI": ["Excel", "Tableau", "SQL", "Data Visualization"],
        "Machine Learning": ["Python", "Scikit-Learn", "Deep Learning", "TensorFlow", "PyTorch"],
        "AWS": ["Docker", "Kubernetes", "Google Cloud", "Microsoft Azure", "DevOps"],
        "React": ["JavaScript", "TypeScript", "HTML5", "CSS3", "Node.js"],
        "PostgreSQL": ["SQL", "Database", "Python", "Redis"],
        "Scikit-Learn": ["Python", "Machine Learning", "Pandas", "NumPy"]
    }

    @classmethod
    def normalize_skill(cls, raw_skill: str) -> Tuple[str, str]:
        """
        Takes raw skill text mention and returns (canonical_name, category).
        """
        cleaned = raw_skill.strip().lower()

        # Direct canonical lookup
        if cleaned in cls.CANONICAL_MAP:
            canonical = cls.CANONICAL_MAP[cleaned]
        else:
            # Capitalize neatly if not in dict
            words = raw_skill.strip().split()
            canonical = " ".join(w.capitalize() for w in words)

        category = cls.CATEGORY_MAP.get(canonical, "Tools & Other")
        return canonical, category

    @classmethod
    def get_related_skills(cls, canonical_skill: str) -> list:
        return cls.RELATED_SKILLS_MAP.get(canonical_skill, [])
