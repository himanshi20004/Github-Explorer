import os
import time
import numpy as np
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072


def embed_texts(texts: list[str], task_type="RETRIEVAL_DOCUMENT") -> np.ndarray:
    """Embed a list of texts using Gemini embedding API with batching."""
    all_embeddings = []

    for text in texts:
        try:
            result = client.models.embed_content(
                model=EMBED_MODEL,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=EMBED_DIM,
                ),
            )
            all_embeddings.append(result.embeddings[0].values)
            time.sleep(0.1)
        except Exception as e:
            print(f"[Embedder] Error embedding text: {e}")
            all_embeddings.append([0.0] * EMBED_DIM)

    return np.array(all_embeddings, dtype="float32")


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string."""
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBED_DIM,
        ),
    )
    return np.array(result.embeddings[0].values, dtype="float32").reshape(1, -1)