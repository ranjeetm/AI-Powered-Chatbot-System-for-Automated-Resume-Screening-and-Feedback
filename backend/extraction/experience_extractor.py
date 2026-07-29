import re


class ExperienceExtractor:

    def __init__(self):

        self.job_titles = [

            # Data / AI
            "data scientist",
            "machine learning engineer",
            "ml engineer",
            "data analyst",

            # Software
            "software engineer",
            "backend developer",
            "python developer",
            "java developer",

            # DevOps
            "devops engineer",
            "cloud engineer",

            # HR
            "hr specialist",
            "hr manager",
            "hr generalist",
            "recruiter",
            "talent acquisition specialist"
        ]

    def clean_text(
        self,
        text
    ):

        text = text.lower()

        text = re.sub(
            r'[^a-zA-Z0-9\s]',
            ' ',
            text
        )

        text = re.sub(
            r'\s+',
            ' ',
            text
        )

        return text

    def extract_experience_years(
        self,
        text
    ):

        text = self.clean_text(
            text
        )

        patterns = [

            r'(\d+)\s*\+?\s*years',

            r'(\d+)\s*\+?\s*yrs',

            r'(\d+)\s*year',

            r'over\s*(\d+)\s*years',

            r'(\d+)\s*years\s*of\s*experience'
        ]

        max_years = 0

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            for match in matches:

                try:

                    years = int(match)

                    if years > max_years:
                        max_years = years

                except:
                    pass

        return max_years

    def extract_job_titles(
        self,
        text
    ):

        text = self.clean_text(
            text
        )

        found_titles = []

        for title in self.job_titles:

            if title in text:

                found_titles.append(
                    title
                )

        return sorted(
            list(set(found_titles))
        )