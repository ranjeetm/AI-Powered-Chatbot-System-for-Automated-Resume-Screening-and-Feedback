import os
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class EmbeddingEngine:

    def __init__(self):

        self.use_api = os.getenv("USE_HF_INFERENCE_API", "true").lower() == "true"

        self.api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

        self.hf_token = os.getenv("HF_TOKEN")

        self.headers = {}

        if self.hf_token:

            self.headers["Authorization"] = f"Bearer {self.hf_token}"

        self.model = None

        if not self.use_api:

            try:

                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

                logger.info("EmbeddingEngine initialized to use local SentenceTransformer model.")

            except ImportError:

                logger.warning("sentence-transformers not installed; falling back to HF Inference API.")

                self.use_api = True

    def generate_embedding(self, text):

        if self.use_api:

            try:

                # Clean up input text

                payload = {"inputs": [text.strip()]}

                response = requests.post(

                    self.api_url,

                    headers=self.headers,

                    json=payload,

                    timeout=10,

                )

                if response.status_code == 200:

                    result = response.json()

                    if isinstance(result, list) and len(result) > 0:

                        emb = result[0]

                        if isinstance(emb, list):

                            return np.array(emb)

                logger.error(
                    "HF Inference API call failed: %s - %s",
                    response.status_code,
                    response.text,
                )

            except Exception as e:

                logger.error("Error calling HF Inference API: %s", e)

            # Fallback to local model if loaded

            if self.model:

                logger.info("Falling back to local SentenceTransformer model.")

                return np.array(self.model.encode(text))

            raise RuntimeError(
                "Failed to generate embedding: HF Inference API failed and local model not available."
            )

        else:

            return np.array(self.model.encode(text))

    def calculate_similarity(self, resume_embedding, jd_embedding):

        similarity = cosine_similarity(
            [resume_embedding],
            [jd_embedding]
        )[0][0]

        return float(similarity)