import re


SKILL_ALIASES = {
    "ai": "artificial intelligence",
    "ai/ml": "machine learning",
    "ml": "machine learning",
    "react.js": "react",
    "reactjs": "react",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "postgre sql": "postgresql",
    "postgres": "postgresql",
    "sql queries": "sql",
    "js": "javascript",
}


def normalize_skill(skill: str) -> str:
    value = str(skill or "").strip().lower()
    value = value.replace("_", " ")
    value = re.sub(r"\s+", " ", value)
    value = value.strip(".,;:()[]{}")

    return SKILL_ALIASES.get(value, value)


def normalized_skill_set(skills) -> set[str]:
    return {
        normalize_skill(skill)
        for skill in skills or []
        if normalize_skill(skill)
    }
