import re

from backend.extraction.skill_extractor import SkillExtractor

from backend.extraction.experience_extractor import ExperienceExtractor

from backend.extraction.education_extractor import EducationExtractor

from backend.extraction.section_parser import ResumeSectionParser


class StructuredResumeParser:

    def __init__(self):

        self.skill_extractor = SkillExtractor()

        self.experience_extractor = ExperienceExtractor()

        self.education_extractor = EducationExtractor()

        self.section_parser = ResumeSectionParser()

    # --------------------------------
    # BASIC INFO EXTRACTION
    # --------------------------------

    def extract_email(self, text):

        normalized_text = text.replace(" ", "")

        pattern = r"[A-Za-z0-9._%+-]+" r"@[A-Za-z0-9.-]+" r"\.[A-Za-z]{2,}"

        match = re.search(pattern, normalized_text)

        return match.group(0) if match else None

    def extract_phone(self, text):

        normalized_text = re.sub(r"\s+", "", text)

        pattern = r"(?:\+91)?" r"[6-9]\d{9}"

        match = re.search(pattern, normalized_text)

        return match.group(0) if match else None

    def extract_linkedin(self, text):

        pattern = r"linkedin\.com/in/" r"[A-Za-z0-9_-]+"

        match = re.search(pattern, text)

        return match.group(0) if match else None

    def extract_github(self, text):

        pattern = r"github\.com/" r"[A-Za-z0-9_-]+"

        match = re.search(pattern, text)

        return match.group(0) if match else None

    def extract_candidate_name(self, text):

        invalid_keywords = {
            "resume",
            "summary",
            "profile",
            "experience",
            "work history",
            "education",
            "skills",
            "contact",
            "linkedin",
            "github",
            "email",
            "phone",
            "university",
            "college",
            "institute",
            "school",
            "objective",
            "certifications",
            "information systems",
            "computer science",
            "data science",
            "machine learning",
            "artificial intelligence",
            "software engineering",
            "engineering",
            "curriculum vitae",
            "developer",
            "engineer",
            "analyst",
            "manager",
            "intern",
        }

        lines = text.split("\n")

        for line in lines[:20]:

            line = line.strip()

            if not line:
                continue

            cleaned = " ".join(line.split())

            lower_cleaned = cleaned.lower()

            # Skip invalid headings
            if any(keyword in lower_cleaned for keyword in invalid_keywords):
                continue

            # Skip emails
            if "@" in cleaned:
                continue

            # Skip URLs
            if "linkedin" in lower_cleaned:
                continue

            if "github" in lower_cleaned:
                continue

            if "http" in lower_cleaned:
                continue

            # Skip digits
            if any(char.isdigit() for char in cleaned):
                continue

            words = cleaned.split()

            # Names usually 2-3 words
            if len(words) < 2 or len(words) > 3:
                continue

            # Alphabetic validation
            valid = all(word.replace("-", "").isalpha() for word in words)

            if not valid:
                continue

            # Prefer title-case names
            proper_case = all(word[0].isupper() for word in words)

            if not proper_case:
                continue

            return cleaned.title()

        return None

    # --------------------------------
    # MAIN PROFILE BUILDER
    # --------------------------------

    def build_candidate_profile(self, resume_data):

        full_text = resume_data["text"]

        # --------------------------------
        # SECTION EXTRACTION
        # --------------------------------

        sections = self.section_parser.extract_sections(full_text)

        # --------------------------------
        # SECTION TEXT
        # --------------------------------

        summary_text = sections.get("summary", "")

        skills_text = sections.get("skills", "")

        experience_text = sections.get("experience", "")

        education_text = sections.get("education", "")

        certifications_text = sections.get("certifications", "")

        # --------------------------------
        # EXPERIENCE CONTEXT
        # --------------------------------

        combined_experience_text = summary_text + " " + experience_text

        # --------------------------------
        # SKILLS EXTRACTION
        # --------------------------------

        skills = self.skill_extractor.extract_skills(skills_text)

        # --------------------------------
        # EXPERIENCE EXTRACTION
        # --------------------------------

        experience_years = self.experience_extractor.extract_experience_years(
            combined_experience_text
        )

        job_titles = self.experience_extractor.extract_job_titles(
            combined_experience_text
        )

        # --------------------------------
        # EDUCATION EXTRACTION
        # --------------------------------

        degrees = self.education_extractor.extract_degrees(education_text)

        specializations = self.education_extractor.extract_specializations(
            education_text
        )

        # --------------------------------
        # CERTIFICATION EXTRACTION
        # --------------------------------

        certifications = self.education_extractor.extract_certifications(
            certifications_text
        )

        # --------------------------------
        # FINAL PROFILE
        # --------------------------------

        candidate_profile = {
            "file_name": resume_data["file_name"],
            "category": resume_data["category"],
            "candidate_name": self.extract_candidate_name(full_text),
            "email": self.extract_email(full_text),
            "phone": self.extract_phone(full_text),
            "linkedin_url": self.extract_linkedin(full_text),
            "github_url": self.extract_github(full_text),
            "skills": skills,
            "experience_years": experience_years,
            "job_titles": job_titles,
            "degrees": degrees,
            "specializations": specializations,
            "certifications": certifications,
            "sections": sections,
            "embedding": resume_data["embedding"],
        }

        return candidate_profile
