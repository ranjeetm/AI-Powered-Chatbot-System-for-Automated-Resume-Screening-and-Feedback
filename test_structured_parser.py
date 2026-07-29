import json

from pathlib import Path

from backend.extraction.structured_parser import (
    StructuredResumeParser
)


parser = StructuredResumeParser()


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

    candidate_profile = (
        parser.build_candidate_profile(
            resume_data
        )
    )

    print("\n" + "=" * 60)

    print(
        json.dumps(
            candidate_profile,
            indent=2
        )[:1500]
    )