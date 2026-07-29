class EducationExtractor:

    def __init__(self):

        self.degrees = [

            "bachelor of technology",
            "b.tech",
            "bachelor of engineering",
            "b.e",
            "master of science",
            "m.sc",
            "master of technology",
            "m.tech",
            "bachelor of science",
            "b.sc",
            "mba",
            "phd"
        ]

        self.specializations = [

            "computer science",
            "information technology",
            "data science",
            "artificial intelligence",
            "machine learning",
            "electronics",
            "electrical engineering",
            "mechanical engineering"
        ]

        self.certifications = [

            "aws certified",
            "azure certified",
            "google cloud",
            "tensorflow",
            "kubernetes",
            "docker",
            "oracle certified"
        ]

    def extract_degrees(
        self,
        text
    ):

        text = text.lower()

        found_degrees = []

        for degree in self.degrees:

            if degree in text:

                found_degrees.append(
                    degree
                )

        return sorted(
            list(set(found_degrees))
        )

    def extract_specializations(
        self,
        text
    ):

        text = text.lower()

        found_specializations = []

        for specialization in self.specializations:

            if specialization in text:

                found_specializations.append(
                    specialization
                )

        return sorted(
            list(set(found_specializations))
        )

    def extract_certifications(
        self,
        text
    ):

        text = text.lower()

        found_certifications = []

        for certification in self.certifications:

            if certification in text:

                found_certifications.append(
                    certification
                )

        return sorted(
            list(set(found_certifications))
        )