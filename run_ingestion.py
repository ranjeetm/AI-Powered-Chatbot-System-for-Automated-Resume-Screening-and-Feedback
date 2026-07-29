import os

from backend.services.resume_ingestion_service import (
    ResumeIngestionService
)

RESUME_DIR = "datasets/resumes/data_science"

service = ResumeIngestionService()

for root, dirs, files in os.walk(
    RESUME_DIR
):

    for file_name in files:

        if not file_name.lower().endswith(
            ".pdf"
        ):
            continue

        file_path = os.path.join(
            root,
            file_name
        )

        category = os.path.basename(
            root
        )

        service.process_resume(
            file_path,
            category
        )

print(
    "\nAll resumes processed successfully."
)