import spacy

from spacy.matcher import PhraseMatcher


class SkillExtractor:

    def __init__(self):

        self.nlp = spacy.load(
            "en_core_web_sm"
        )

        self.skills = [

            # Programming
            "python",
            "java",
            "c++",
            "javascript",
            "typescript",
            "sql",

            # AI / ML
            "artificial intelligence",
            "ai/ml",
            "ai",
            "ml",
            "machine learning",
            "deep learning",
            "nlp",
            "natural language processing",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "sklearn",
            "classification",
            "prediction models",
            "model evaluation",
            "feature engineering",
            "data preprocessing",
            "chatbot",

            # Data Science
            "data analysis",
            "pandas",
            "numpy",
            "tableau",
            "power bi",
            "matplotlib",
            "streamlit",

            # Backend
            "fastapi",
            "django",
            "flask",
            "rest api",

            # Frontend
            "react",
            "react.js",
            "reactjs",
            "html",
            "css",
            "chakra ui",

            # DevOps / Cloud
            "docker",
            "kubernetes",
            "terraform",
            "aws",
            "azure",
            "gcp",
            "linux",

            # Databases
            "postgresql",
            "postgres",
            "mysql",
            "mongodb",
            "sqlite",
            "database management",

            # HR
            "recruitment",
            "talent acquisition",
            "employee relations",
            "onboarding",
            "leadership",
            "communication",

            # Management
            "project management",
            "stakeholder management",
            "team leadership",
            "event management",
            "public speaking",
            "time management",
            "problem solving",
            "data structures",
            "algorithms",
        ]

        self.matcher = PhraseMatcher(
            self.nlp.vocab,
            attr="LOWER"
        )

        patterns = [

            self.nlp.make_doc(skill)

            for skill in self.skills
        ]

        self.matcher.add(
            "SKILLS",
            patterns
        )

    def extract_skills(
        self,
        text
    ):

        if not text:

            return []

        doc = self.nlp(text)

        matches = self.matcher(doc)

        found_skills = set()

        for match_id, start, end in matches:

            skill = doc[start:end].text

            found_skills.add(
                skill.lower()
            )

        return sorted(
            list(found_skills)
        )
