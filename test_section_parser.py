import json

from pathlib import Path

from backend.extraction.section_parser import (
    ResumeSectionParser
)


parser = ResumeSectionParser()


processed_dir = Path(
    "processed_resumes"
)


json_files = list(
    processed_dir.glob("*.json")
)


for json_file in json_files[:3]:

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:

        resume_data = json.load(f)

    sections = parser.extract_sections(
        resume_data["text"]
    )

    print("\n" + "=" * 60)

    print(
        f"FILE: {resume_data['file_name']}"
    )

    for section_name, section_text in (
        sections.items()
    ):

        print("\n" + "-" * 40)

        print(
            f"SECTION: {section_name.upper()}"
        )

        print(
            section_text[:500]
        )