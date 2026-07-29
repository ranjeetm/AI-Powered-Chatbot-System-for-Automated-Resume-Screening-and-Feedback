from pathlib import Path

from backend.parser.parser import extract_text_from_pdf
from backend.embeddings.embedding_engine import EmbeddingEngine


class RankingEngine:

    def __init__(self):

        self.embedding_engine = EmbeddingEngine()

    def rank_resumes(
        self,
        job_description,
        resume_root_dir="datasets/resumes"
    ):

        jd_embedding = (
            self.embedding_engine.generate_embedding(
                job_description
            )
        )

        results = []

        root_path = Path(
            resume_root_dir
        )

        categories = [
            folder for folder in root_path.iterdir()
            if folder.is_dir()
        ]

        for category in categories:

            pdf_files = list(
                category.glob("*.pdf")
            )

            for pdf_file in pdf_files:

                try:

                    parsed = extract_text_from_pdf(
                        pdf_file
                    )

                    resume_text = parsed.get(
                        "text",
                        ""
                    )

                    if not resume_text.strip():
                        continue

                    resume_embedding = (
                        self.embedding_engine.generate_embedding(
                            resume_text
                        )
                    )

                    similarity = (
                        self.embedding_engine.calculate_similarity(
                            resume_embedding,
                            jd_embedding
                        )
                    )

                    results.append({
                        "file_name": pdf_file.name,
                        "category": category.name,
                        "score": similarity
                    })

                except Exception as e:

                    print(
                        f"Error processing {pdf_file.name}: {e}"
                    )

        ranked_results = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked_results