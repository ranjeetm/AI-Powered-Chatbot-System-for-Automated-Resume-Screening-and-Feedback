from backend.extraction.skill_extractor import (
    SkillExtractor
)

from backend.extraction.experience_extractor import (
    ExperienceExtractor
)
from backend.scoring.skill_normalizer import (
    normalize_skill,
    normalized_skill_set,
)

import re


class ProfileScorer:

    def __init__(self):

        self.skill_extractor = (
            SkillExtractor()
        )

        self.experience_extractor = (
            ExperienceExtractor()
        )

    def calculate_skill_match(
        self,
        candidate_skills,
        jd_text,
        candidate_text=None,
    ):

        jd_skills = (
            self.skill_extractor.extract_skills(
                jd_text
            )
        )

        if len(jd_skills) == 0:
            return 0.0

        normalized_candidate_skills = normalized_skill_set(
            candidate_skills
        )

        if candidate_text:

            normalized_candidate_skills.update(
                normalized_skill_set(
                    self.skill_extractor.extract_skills(
                        candidate_text
                    )
                )
            )

        normalized_jd_skills = {
            normalize_skill(skill)
            for skill in jd_skills
            if normalize_skill(skill)
        }

        matched_skills = [

            skill for skill in jd_skills
            if normalize_skill(skill) in normalized_candidate_skills
        ]

        return (
            len({
                normalize_skill(skill)
                for skill in matched_skills
            })
            / len(normalized_jd_skills)
        )

    def calculate_title_match(
        self,
        candidate_titles,
        jd_text,
        candidate_category=None,
        candidate_skills=None,
    ):

        jd_text = jd_text.lower()

        normalized_titles = [
            str(title).strip().lower()
            for title in candidate_titles
            if str(title).strip()
        ]

        category = str(candidate_category or "").strip().lower()

        if category:

            normalized_titles.append(category)

        matched_titles = [

            title for title in normalized_titles
            if title in jd_text
        ]

        title_tokens = self._title_tokens(jd_text)

        if not matched_titles and title_tokens:

            candidate_text = " ".join(
                normalized_titles
                + [
                    str(skill).strip().lower()
                    for skill in candidate_skills or []
                    if str(skill).strip()
                ]
            )

            matched_token_count = sum(
                1
                for token in title_tokens
                if token in candidate_text
            )

            if matched_token_count:

                return matched_token_count / len(title_tokens)

        if len(normalized_titles) == 0:
            return 0.0

        return (
            len(matched_titles)
            / len(normalized_titles)
        )

    def calculate_experience_match(
        self,
        candidate_experience,
        required_experience=2
    ):

        if required_experience <= 0:
            return 1.0

        if candidate_experience >= required_experience:
            return 1.0

        return (
            candidate_experience
            / required_experience
        )

    def extract_required_experience(
        self,
        jd_text,
        default_required_experience=2
    ):

        jd_text = (jd_text or "").lower()

        range_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years|yrs)",
            jd_text
        )

        if range_match:
            return float(
                range_match.group(1)
            )

        patterns = [
            r"minimum\s+(\d+(?:\.\d+)?)\s*(?:years|yrs)",
            r"at\s+least\s+(\d+(?:\.\d+)?)\s*(?:years|yrs)",
            r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)\s+of\s+experience",
            r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                jd_text
            )

            if match:

                return float(
                    match.group(1)
                )

        if any(
            term in jd_text
            for term in [
                "fresher",
                "entry level",
                "entry-level",
                "graduate",
                "intern",
                "internship",
                "trainee",
                "junior",
                "0-1 years",
                "0 to 1 years"
            ]
        ):

            return 0.0

        return float(
            default_required_experience
        )

    def calculate_final_score(
        self,
        semantic_similarity,
        skill_match,
        title_match,
        experience_match
    ):

        final_score = (

            semantic_similarity * 0.5

            +

            skill_match * 0.3

            +

            title_match * 0.1

            +

            experience_match * 0.1
        )

        return round(
            final_score * 100,
            2
        )

    def _title_tokens(
        self,
        jd_text,
    ):

        title_terms = {
            "ai/ml": ["ai", "ml"],
            "artificial intelligence": ["ai"],
            "machine learning": ["ml"],
            "ml": ["ml"],
            "ai": ["ai"],
            "engineer": ["engineer"],
            "developer": ["developer"],
            "analyst": ["analyst"],
            "data scientist": ["data", "scientist"],
            "data": ["data"],
        }

        tokens = []

        for term, aliases in title_terms.items():

            if term in jd_text:

                tokens.extend(aliases)

        return sorted(set(tokens))
