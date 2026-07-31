import os
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class EmbeddingEngine:

    def __init__(self):

        self.use_api = os.getenv("USE_HF_INFERENCE_API", "true").lower() == "true"

        self.api_url = os.getenv(
            "HF_API_URL",
            "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
        )

        self.hf_token = os.getenv("HF_TOKEN")

        self.headers = {}

        if self.hf_token:

            self.headers["Authorization"] = f"Bearer {self.hf_token}"
        else:
            logger.warning(
                "HF_TOKEN environment variable is not set! Because Hugging Face has retired "
                "unauthenticated endpoints, calls to the serverless Inference API will fail. "
                "Please generate a free token at https://huggingface.co/settings/tokens and "
                "set it as HF_TOKEN in your environment variables."
            )

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

                if response.status_code == 401:
                    logger.error(
                        "HF Inference API call returned 401 Unauthorized. "
                        "Please verify that your HF_TOKEN is correctly set in your environment variables."
                    )
                else:
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