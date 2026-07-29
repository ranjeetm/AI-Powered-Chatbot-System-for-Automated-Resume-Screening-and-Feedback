import re


class ResumeSectionParser:

    def __init__(self):

        self.section_patterns = {

            "summary": [

                "summary",
                "professional summary",
                "profile",
                "objective"
            ],

            "skills": [

                "skills",
                "technical skills",
                "core competencies",
                "technologies",
                "tech stack"
            ],

            "experience": [

                "experience",
                "work experience",
                "professional experience",
                "employment history"
            ],

            "education": [

                "education",
                "academic background",
                "qualification"
            ],

            "certifications": [

                "certifications",
                "licenses",
                "certificates"
            ],

            "projects": [

                "projects",
                "personal projects"
            ]
        }

    # --------------------------------
    # FIND SECTION HEADINGS
    # --------------------------------

    def detect_section_heading(
        self,
        line
    ):

        cleaned_line = (
            line.strip().lower()
        )

        for section_name, keywords in (
            self.section_patterns.items()
        ):

            for keyword in keywords:

                if cleaned_line == keyword:

                    return section_name

        return None

    # --------------------------------
    # EXTRACT SECTIONS
    # --------------------------------

    def extract_sections(
        self,
        text
    ):

        lines = text.splitlines()

        extracted_sections = {}

        current_section = None

        for line in lines:

            stripped_line = line.strip()

            if not stripped_line:
                continue

            detected_section = (
                self.detect_section_heading(
                    stripped_line
                )
            )

            # --------------------------------
            # NEW SECTION FOUND
            # --------------------------------

            if detected_section:

                current_section = (
                    detected_section
                )

                if current_section not in (
                    extracted_sections
                ):

                    extracted_sections[
                        current_section
                    ] = ""

                continue

            # --------------------------------
            # APPEND CONTENT
            # --------------------------------

            if current_section:

                extracted_sections[
                    current_section
                ] += (
                    stripped_line + "\n"
                )

        return extracted_sections