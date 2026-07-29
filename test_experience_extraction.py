import json

from pathlib import Path

from backend.extraction.experience_extractor import (
    ExperienceExtractor
)


extractor = ExperienceExtractor()


processed_dir = Path(
    "processed_resumes"
)


json_files = list(
    processed_dir.glob("*.json")
)


for json_file in json_files[:10]:

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:

        resume_data = json.load(f)

    experience_years = (
        extractor.extract_experience_years(
            resume_data["text"]
        )
    )

    job_titles = (
        extractor.extract_job_titles(
            resume_data["text"]
        )
    )

    print("\n" + "=" * 50)

    print(
        f"FILE: {resume_data['file_name']}"
    )

    print(
        f"CATEGORY: {resume_data['category']}"
    )

    print(
        f"\nEXPERIENCE YEARS: "
        f"{experience_years}"
    )

    print(
        "\nJOB TITLES:"
    )

    print(job_titles)