
from fastembed import TextEmbedding

# Load a lightweight embedding model
embedding_model = TextEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def generate_embedding(text: str) -> list:
    """
    Convert text into a numerical vector.
    """
    embeddings = list(
        embedding_model.embed([text])
    )

    return embeddings[0].tolist()
import numpy as np


def cosine_similarity(vector_a, vector_b):
    """
    Calculate semantic similarity between two vectors.
    """
    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)