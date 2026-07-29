from backend.extraction.skill_extractor import (
    SkillExtractor
)


class WeightedScorer:

    def __init__(self):

        self.skill_extractor = (
            SkillExtractor()
        )

    def calculate_skill_match(
        self,
        resume_text,
        job_description
    ):

        resume_skills = (
            self.skill_extractor.extract_skills(
                resume_text
            )
        )

        jd_skills = (
            self.skill_extractor.extract_skills(
                job_description
            )
        )

        if len(jd_skills) == 0:
            return 0.0

        matched_skills = [

            skill for skill in jd_skills
            if skill in resume_skills
        ]

        skill_match_score = (
            len(matched_skills)
            / len(jd_skills)
        )

        return skill_match_score

    def calculate_final_score(
        self,
        semantic_similarity,
        skill_match_score,
        semantic_weight=0.7,
        skill_weight=0.3
    ):

        final_score = (

            semantic_similarity * semantic_weight

            +

            skill_match_score * skill_weight
        )

        return final_score