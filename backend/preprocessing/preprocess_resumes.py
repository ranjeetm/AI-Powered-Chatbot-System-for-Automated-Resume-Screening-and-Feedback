import json

from pathlib import Path

from backend.parser.parser import extract_text_from_pdf
from backend.embeddings.embedding_engine import EmbeddingEngine


class ResumePreprocessor:

    def __init__(self):

        self.embedding_engine = EmbeddingEngine()

    def preprocess_resumes(
        self,
        resume_root_dir="datasets/resumes",
        output_dir="processed_resumes"
    ):

        root_path = Path(
            resume_root_dir
        )

        output_path = Path(
            output_dir
        )

        output_path.mkdir(
            exist_ok=True
        )

        categories = [
            folder for folder in root_path.iterdir()
            if folder.is_dir()
        ]

        total_processed = 0

        for category in categories:

            print(
                f"\nProcessing category: {category.name}"
            )

            pdf_files = list(
                category.glob("*.pdf")
            )

            for pdf_file in pdf_files:

                try:

                    print(
                        f"Processing resume: {pdf_file.name}"
                    )

                    parsed = extract_text_from_pdf(
                        pdf_file
                    )

                    resume_text = parsed.get(
                        "text",
                        ""
                    )

                    if not resume_text.strip():

                        print(
                            f"Skipped empty file: {pdf_file.name}"
                        )

                        continue

                    embedding = (
                        self.embedding_engine.generate_embedding(
                            resume_text
                        )
                    )

                    resume_data = {

                        "file_name": pdf_file.name,

                        "category": category.name,

                        "text": resume_text,

                        "embedding": embedding.tolist()
                    }

                    output_file = (
                        output_path /
                        f"{category.name}_{pdf_file.stem}.json"
                    )

                    with open(
                        output_file,
                        "w",
                        encoding="utf-8"
                    ) as f:

                        json.dump(
                            resume_data,
                            f
                        )

                    total_processed += 1

                except Exception as e:

                    print(
                        f"Error processing {pdf_file.name}: {e}"
                    )

        print("\n" + "=" * 50)
        print(
            f"TOTAL RESUMES PROCESSED: {total_processed}"
        )
        print("=" * 50)