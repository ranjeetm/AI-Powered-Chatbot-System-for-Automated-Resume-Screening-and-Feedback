import json

from pathlib import Path

from backend.extraction.skill_extractor import (
    SkillExtractor
)


extractor = SkillExtractor()


processed_dir = Path(
    "processed_resumes"
)


json_files = list(
    processed_dir.glob("*.json")
)


for json_file in json_files[:5]:

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:

        resume_data = json.load(f)

    skills = extractor.extract_skills(
        resume_data["text"]
    )

    print("\n" + "=" * 50)

    print(
        f"FILE: {resume_data['file_name']}"
    )

    print(
        f"CATEGORY: {resume_data['category']}"
    )

    print("\nEXTRACTED SKILLS:")

    print(skills)