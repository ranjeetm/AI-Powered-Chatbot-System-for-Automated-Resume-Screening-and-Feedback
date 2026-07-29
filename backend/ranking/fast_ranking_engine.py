import json

from pathlib import Path

from backend.embeddings.embedding_engine import (
    EmbeddingEngine
)


class FastRankingEngine:

    def __init__(self):

        self.embedding_engine = EmbeddingEngine()

    def rank_resumes(
        self,
        job_description,
        processed_dir="processed_resumes"
    ):

        jd_embedding = (
            self.embedding_engine.generate_embedding(
                job_description
            )
        )

        processed_path = Path(
            processed_dir
        )

        json_files = list(
            processed_path.glob("*.json")
        )

        results = []

        for json_file in json_files:

            with open(
                json_file,
                "r",
                encoding="utf-8"
            ) as f:

                resume_data = json.load(f)

            similarity = (
                self.embedding_engine.calculate_similarity(
                    resume_data["embedding"],
                    jd_embedding
                )
            )

            results.append({

                "file_name":
                    resume_data["file_name"],

                "category":
                    resume_data["category"],

                "score":
                    similarity
            })

        ranked_results = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked_results