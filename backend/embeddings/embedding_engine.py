from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class EmbeddingEngine:

    def __init__(self):

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def generate_embedding(self, text):

        embedding = self.model.encode(text)

        return np.array(embedding)

    def calculate_similarity(
        self,
        resume_embedding,
        jd_embedding
    ):

        similarity = cosine_similarity(
            [resume_embedding],
            [jd_embedding]
        )[0][0]

        return float(similarity)